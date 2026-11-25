"""One JSON line per HTTP request, tied together by a request id (AA5, F48 / I16).

Caddy stamps every proxied request with its own `X-Request-ID` (a UUID, see `caddy/Caddyfile`), so a
client cannot choose the id that ends up in the logs. The backend keeps a well-formed incoming id,
mints one otherwise (a request that reached it directly, or a test), returns it on the response and
logs one line:

    {"ts": "...", "event": "http", "request_id": "...", "method": "GET", "path": "/health", "status": 200, "ms": 3.1}

Only the path is logged, never the query string or headers: a query can carry a search a student
typed, and headers carry session cookies. `ms` is the time until the response *starts*: for a streamed
Oracle answer that is the time to first byte, not the whole stream.

The Compose health probe (`/health` from inside the container, every 10 s, no request id) is not logged
when it succeeds: it was ~8,600 lines a day of noise. A `/health` through Caddy, or any failure, is.
"""

from __future__ import annotations

import json
import logging
import re
import sys
import time
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, Request

REQUEST_ID_HEADER = "X-Request-ID"
_WELL_FORMED = re.compile(r"[A-Za-z0-9._-]{8,128}")

access_logger = logging.getLogger("ttod.access")
if not access_logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter("%(message)s"))
    access_logger.addHandler(_handler)
    access_logger.setLevel(logging.INFO)
    access_logger.propagate = False


def request_id_of(request: Request) -> str:
    incoming = request.headers.get(REQUEST_ID_HEADER, "")
    # fullmatch: `match` with `$` would also accept a trailing newline (cold review AA5, F7).
    return incoming if _WELL_FORMED.fullmatch(incoming) else uuid.uuid4().hex


def install_access_log(app: FastAPI) -> None:
    @app.middleware("http")
    async def access_log(request: Request, call_next):
        probe = request.url.path == "/health" and REQUEST_ID_HEADER not in request.headers
        request_id = request_id_of(request)
        request.state.request_id = request_id
        started = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            if not (probe and status == 200):
                _log(request, request_id, status, started)


def _log(request: Request, request_id: str, status: int, started: float) -> None:
    access_logger.info(json.dumps({
        "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "event": "http",
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status": status,
        "ms": round((time.perf_counter() - started) * 1000, 1),
    }))
