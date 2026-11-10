"""Abuse budgets (F3 / F20, Phase AA2): fixed-window counters, Redis in Compose, memory in tests.

A budget is `limit` hits per `window` seconds for one (bucket, key) pair, e.g. register attempts
per client IP, or login attempts per account. Every attempt counts, successful or not, so an
attacker cannot reset the counter by mixing in a correct password.
"""

from __future__ import annotations

import hashlib
import os
import threading
import time
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class Budget:
    limit: int
    window: int  # seconds


# Classroom defaults. A whole cohort often shares one school NAT address, so the per-IP budgets fit
# a class of ~40 signing up and in during one lesson; the per-account budget is what stops guessing.
DEFAULT_BUDGETS: dict[str, Budget] = {
    "login-ip": Budget(100, 300),      # login attempts per client IP per 5 min
    "account": Budget(10, 300),        # login + password-change attempts per account per 5 min
    "register-ip": Budget(40, 3600),   # new accounts per client IP per hour
    "proposal-user": Budget(20, 3600), # proposals (form + oracle) per user per hour
}


def budgets_from_env(env: dict[str, str] | None = None) -> dict[str, Budget]:
    """Read overrides such as TTOD_THROTTLE_REGISTER_IP="10/3600" (limit/window seconds)."""
    env = os.environ if env is None else env
    budgets = dict(DEFAULT_BUDGETS)
    for name in DEFAULT_BUDGETS:
        var = f"TTOD_THROTTLE_{name.upper().replace('-', '_')}"
        raw = env.get(var, "").strip()
        if not raw:
            continue
        limit, _, window = raw.partition("/")
        try:
            budgets[name] = Budget(int(limit), int(window))
        except ValueError:
            raise ValueError(f'{var}="{raw}" must be "limit/window-seconds", e.g. "40/3600"') from None
        if budgets[name].limit <= 0 or budgets[name].window <= 0:
            raise ValueError(f'{var}="{raw}" must have a positive limit and window')
    return budgets


class Throttle(Protocol):
    def hit(self, bucket: str, key: str, budget: Budget) -> bool:
        """Count one attempt; True while the budget still allows it."""
        ...


class MemoryThrottle:
    def __init__(self) -> None:
        self._hits: dict[tuple[str, str], tuple[float, int]] = {}
        self._lock = threading.Lock()

    def hit(self, bucket: str, key: str, budget: Budget) -> bool:
        now = time.monotonic()
        with self._lock:
            start, count = self._hits.get((bucket, key), (now, 0))
            if now - start >= budget.window:
                start, count = now, 0
            count += 1
            self._hits[(bucket, key)] = (start, count)
        return count <= budget.limit


class RedisThrottle:
    def __init__(self, client: Any):
        self.client = client

    def hit(self, bucket: str, key: str, budget: Budget) -> bool:
        # The key is hashed so emails and IPs never sit in Redis key names.
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]
        redis_key = f"ttod:throttle:{bucket}:{digest}"
        # One MULTI: the counter and its expiry land together, so a failure between two calls can
        # never leave a counter without TTL (a permanent lockout). NX keeps the first window.
        pipe = self.client.pipeline()
        pipe.incr(redis_key)
        pipe.expire(redis_key, budget.window, nx=True)
        count, _ = pipe.execute()
        return int(count) <= budget.limit
