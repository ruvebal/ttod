"""Token registry (Phase AA2): per-user session index (F55) and PAT revocation (F5, AA0 D7 b).

Follows the Web Atelier React authentication lesson: a session is revoked by deleting its row;
a signed token (PAT) "stays valid until it expires (needs denylist for true revoke)". So every PAT
carries a `jti`, the user's issued jtis are indexed, and revoking writes `ttod:pat:deny:{jti}` for
the token's remaining life (bounded by the PAT TTL).

Redis keys: ttod:user:{id}:sessions (SET of sids) · ttod:user:{id}:pats (SET of jtis) ·
ttod:pat:deny:{jti} (string, TTL). Sids that expire by TTL stay in the SET until the next read
prunes them (AuthService.user_sessions); no cron.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Protocol


class TokenRegistry(Protocol):
    def add_session(self, user_id: str, sid: str, ttl_seconds: int) -> None: ...
    def remove_session(self, user_id: str, sid: str) -> None: ...
    def sessions(self, user_id: str) -> set[str]: ...
    def add_pat(self, user_id: str, jti: str, ttl_seconds: int) -> None: ...
    def pats(self, user_id: str) -> set[str]: ...
    def deny_pat(self, jti: str, ttl_seconds: int) -> None: ...
    def is_pat_denied(self, jti: str) -> bool: ...
    def clear_pats(self, user_id: str) -> None: ...


class MemoryTokenRegistry:
    def __init__(self) -> None:
        self._sessions: dict[str, set[str]] = {}
        self._pats: dict[str, set[str]] = {}
        self._denied: dict[str, float] = {}
        self._lock = threading.Lock()

    def add_session(self, user_id: str, sid: str, ttl_seconds: int) -> None:
        with self._lock:
            self._sessions.setdefault(user_id, set()).add(sid)

    def remove_session(self, user_id: str, sid: str) -> None:
        with self._lock:
            self._sessions.get(user_id, set()).discard(sid)

    def sessions(self, user_id: str) -> set[str]:
        with self._lock:
            return set(self._sessions.get(user_id, set()))

    def add_pat(self, user_id: str, jti: str, ttl_seconds: int) -> None:
        with self._lock:
            self._pats.setdefault(user_id, set()).add(jti)

    def pats(self, user_id: str) -> set[str]:
        with self._lock:
            return set(self._pats.get(user_id, set()))

    def deny_pat(self, jti: str, ttl_seconds: int) -> None:
        with self._lock:
            self._denied[jti] = time.monotonic() + ttl_seconds

    def is_pat_denied(self, jti: str) -> bool:
        with self._lock:
            until = self._denied.get(jti)
            if until is None:
                return False
            if until <= time.monotonic():
                del self._denied[jti]
                return False
            return True

    def clear_pats(self, user_id: str) -> None:
        with self._lock:
            self._pats.pop(user_id, None)


class RedisTokenRegistry:
    def __init__(self, client: Any):
        self.client = client

    @staticmethod
    def _sessions_key(user_id: str) -> str:
        return f"ttod:user:{user_id}:sessions"

    @staticmethod
    def _pats_key(user_id: str) -> str:
        return f"ttod:user:{user_id}:pats"

    def add_session(self, user_id: str, sid: str, ttl_seconds: int) -> None:
        key = self._sessions_key(user_id)
        pipe = self.client.pipeline()
        pipe.sadd(key, sid)
        pipe.expire(key, ttl_seconds)  # the index never outlives the newest session
        pipe.execute()

    def remove_session(self, user_id: str, sid: str) -> None:
        self.client.srem(self._sessions_key(user_id), sid)

    def sessions(self, user_id: str) -> set[str]:
        return {m.decode() if isinstance(m, bytes) else m for m in self.client.smembers(self._sessions_key(user_id))}

    def add_pat(self, user_id: str, jti: str, ttl_seconds: int) -> None:
        key = self._pats_key(user_id)
        pipe = self.client.pipeline()
        pipe.sadd(key, jti)
        pipe.expire(key, ttl_seconds)
        pipe.execute()

    def pats(self, user_id: str) -> set[str]:
        return {m.decode() if isinstance(m, bytes) else m for m in self.client.smembers(self._pats_key(user_id))}

    def deny_pat(self, jti: str, ttl_seconds: int) -> None:
        self.client.set(f"ttod:pat:deny:{jti}", "1", ex=ttl_seconds)

    def is_pat_denied(self, jti: str) -> bool:
        return bool(self.client.exists(f"ttod:pat:deny:{jti}"))

    def clear_pats(self, user_id: str) -> None:
        self.client.delete(self._pats_key(user_id))
