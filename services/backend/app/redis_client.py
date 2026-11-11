"""Shared Redis client for shore stores (users, sessions, favorites, proposals)."""

from __future__ import annotations

import os
from typing import Any

import redis


def pool_options() -> dict[str, Any]:
    """Connection-pool knobs (AA5, F46 / I14), overridable by env. Without timeouts a hung Redis
    holds every request thread until the OS gives up; with them a request fails fast with the 503
    the shore APIs already answer, and the health check reports `redis: down`."""
    return {
        "socket_timeout": float(os.getenv("TTOD_REDIS_SOCKET_TIMEOUT", "2")),
        "socket_connect_timeout": float(os.getenv("TTOD_REDIS_CONNECT_TIMEOUT", "2")),
        "health_check_interval": int(os.getenv("TTOD_REDIS_HEALTH_CHECK_INTERVAL", "30")),
        "max_connections": int(os.getenv("TTOD_REDIS_MAX_CONNECTIONS", "50")),
    }


def create_redis_client(redis_url: str, *, client: Any | None = None) -> Any:
    """Return a decode_responses client, or an injected test double."""
    if client is not None:
        return client
    if not redis_url.strip():
        raise ValueError("REDIS_URL is empty")
    return redis.Redis.from_url(redis_url, decode_responses=True, **pool_options())


def redis_ping(client: Any) -> bool:
    try:
        return bool(client.ping())
    except redis.RedisError:
        return False
