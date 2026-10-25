from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Protocol

import redis

from .models import FavoriteEntry


class FavoriteStore(Protocol):
    def save(self, user_id: str, quote_id: str) -> FavoriteEntry: ...
    def list(self, user_id: str) -> list[FavoriteEntry]: ...
    def remove(self, user_id: str, quote_id: str) -> bool: ...


class RedisFavoriteStore:
    """Persists user preferences without duplicating the governed corpus."""

    def __init__(self, redis_url: str, *, client: Any | None = None):
        self.client = client or redis.Redis.from_url(redis_url, decode_responses=True)

    @staticmethod
    def _key(user_id: str) -> str:
        return f"ttod:favorites:{user_id}"

    def save(self, user_id: str, quote_id: str) -> FavoriteEntry:
        existing = self.client.hget(self._key(user_id), quote_id)
        saved_at = existing or datetime.now(timezone.utc).isoformat()
        self.client.hset(self._key(user_id), quote_id, saved_at)
        return FavoriteEntry(userId=user_id, quoteId=quote_id, savedAt=saved_at)

    def list(self, user_id: str) -> list[FavoriteEntry]:
        values = self.client.hgetall(self._key(user_id))
        return [
            FavoriteEntry(userId=user_id, quoteId=quote_id, savedAt=saved_at)
            for quote_id, saved_at in sorted(values.items(), key=lambda item: item[1], reverse=True)
        ]

    def remove(self, user_id: str, quote_id: str) -> bool:
        return bool(self.client.hdel(self._key(user_id), quote_id))
