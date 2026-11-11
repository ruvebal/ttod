"""AA5 lane B: sanitized health bodies (F47), Redis pool knobs (F46), request ids and JSON access logs (F48)."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from fastapi.testclient import TestClient

from services.backend.app.config import REPOSITORY_ROOT, Settings
from services.backend.app.favorites import MemoryFavoriteStore
from services.backend.app.main import create_app
from services.backend.app.proposal_drafts import FilesystemProposalDraftStore
from services.backend.app.redis_client import create_redis_client
from services.backend.app.sessions import MemorySessionStore
from services.backend.app.users import MemoryUserStore


def _app(tmp: str):
    settings = Settings(ttod_path=REPOSITORY_ROOT / "ttod.yml", schema_dir=REPOSITORY_ROOT / "schema",
                        proposal_dir=Path(tmp), ollama_model="test-model")
    return create_app(settings, users=MemoryUserStore(), sessions=MemorySessionStore(),
                      favorites=MemoryFavoriteStore(), proposals=FilesystemProposalDraftStore(Path(tmp)))


class HealthBodyTests(unittest.TestCase):
    def test_health_body_sanitized_when_repository_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = _app(tmp)
            secret = "/srv/ttod/secret-path.yml: connection to http://10.0.0.7:9999 refused"
            with mock.patch("services.backend.app.main.SnapshotService.health", side_effect=RuntimeError(secret)), \
                 self.assertLogs("services.backend.app.main", level="ERROR") as logs:
                response = TestClient(app).get("/health")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "TTOD repository unavailable"})
        self.assertNotIn("10.0.0.7", response.text)
        self.assertNotIn("secret-path", response.text)
        self.assertIn("secret-path", "\n".join(logs.output))  # the reason is kept, in the log


class RedisPoolTests(unittest.TestCase):
    def test_redis_pool_knobs_reach_the_connection_pool(self):
        client = create_redis_client("redis://localhost:6399/0")
        kwargs = client.connection_pool.connection_kwargs
        self.assertEqual(kwargs["socket_timeout"], 2.0)
        self.assertEqual(kwargs["socket_connect_timeout"], 2.0)
        self.assertEqual(kwargs["health_check_interval"], 30)
        self.assertEqual(client.connection_pool.max_connections, 50)

    def test_redis_pool_knobs_follow_the_environment(self):
        env = {"TTOD_REDIS_SOCKET_TIMEOUT": "0.5", "TTOD_REDIS_MAX_CONNECTIONS": "7"}
        with mock.patch.dict(os.environ, env):
            client = create_redis_client("redis://localhost:6399/0")
        self.assertEqual(client.connection_pool.connection_kwargs["socket_timeout"], 0.5)
        self.assertEqual(client.connection_pool.max_connections, 7)


class RequestIdTests(unittest.TestCase):
    def _get(self, headers=None):
        with tempfile.TemporaryDirectory() as tmp:
            client = TestClient(_app(tmp))
            with self.assertLogs("ttod.access", level="INFO") as logs:
                response = client.get("/api/v1/wisdom/sample?q=student-search", headers=headers or {})
        lines = [json.loads(line.split(":", 2)[2]) for line in logs.output]
        return response, lines

    def test_request_id_is_minted_returned_and_logged_as_json(self):
        response, lines = self._get()
        rid = response.headers["X-Request-ID"]
        self.assertRegex(rid, r"^[0-9a-f]{32}$")
        self.assertEqual(len(lines), 1)
        line = lines[0]
        self.assertEqual({k: line[k] for k in ("event", "request_id", "method", "path", "status")},
                         {"event": "http", "request_id": rid, "method": "GET", "path": "/api/v1/wisdom/sample", "status": 200})
        self.assertIsInstance(line["ms"], float)
        self.assertNotIn("student-search", json.dumps(line))  # the query string is never logged

    def test_request_id_from_the_proxy_is_kept(self):
        response, lines = self._get({"X-Request-ID": "caddy-0f8e-4c1a-9d2b"})
        self.assertEqual(response.headers["X-Request-ID"], "caddy-0f8e-4c1a-9d2b")
        self.assertEqual(lines[0]["request_id"], "caddy-0f8e-4c1a-9d2b")

    def test_request_id_malformed_is_replaced(self):
        response, lines = self._get({"X-Request-ID": "bad id\n{\"inject\":1}"})
        self.assertRegex(response.headers["X-Request-ID"], r"^[0-9a-f]{32}$")
        self.assertEqual(lines[0]["request_id"], response.headers["X-Request-ID"])


if __name__ == "__main__":
    unittest.main()
