"""AA2: abuse budgets (F3/F20), signed fallback off (F4), PAT denylist (F5, AA0 D7 b), oracle
behind a session with dual-write (F24/F26), change-password + profile with a per-user session
index (F55). Test names follow the contract in PHASES/AA2-auth-throttle-and-fallback.exit-gate.sh.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from services.backend.app.auth import SESSION_COOKIE_NAME, AuthService, SessionClaims
from services.backend.app.config import REPOSITORY_ROOT, Settings
from services.backend.app.main import create_app
from services.backend.app.oracle import OracleService
from services.backend.app.proposal_drafts import FilesystemProposalDraftStore
from services.backend.app.revocation import MemoryTokenRegistry, RedisTokenRegistry
from services.backend.app.sessions import MemorySessionStore
from services.backend.app.storage import SnapshotService
from services.backend.app.throttle import DEFAULT_BUDGETS, Budget, RedisThrottle, budgets_from_env
from services.backend.app.users import MemoryUserStore

PASSWORD = "correct-horse-battery"


class FakeOllama:
    async def generate(self, prompt, system):
        yield "answer"


class FakeRetrieval:
    async def semantic_retrieval(self, query, *, top_k, context_tag, section):
        return {"results": [], "indexDigest": "test", "indexedQuotes": 0}


class SpyProposalStore(FilesystemProposalDraftStore):
    def __init__(self, proposal_dir: Path):
        super().__init__(proposal_dir)
        self.saved: list[str] = []

    def save(self, proposal) -> None:
        self.saved.append(proposal.proposal_id)
        super().save(proposal)


class AA2Case(unittest.TestCase):
    def build(self, **budgets: Budget) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        merged = dict(DEFAULT_BUDGETS)
        merged.update({name.replace("_", "-"): budget for name, budget in budgets.items()})
        self.settings = Settings(
            ttod_path=REPOSITORY_ROOT / "ttod.yml",
            schema_dir=REPOSITORY_ROOT / "schema",
            proposal_dir=Path(temp.name),
            ollama_model="test-model",
            trust_forwarded_for=True,
            throttle_budgets=merged,
        )
        snapshots = SnapshotService(self.settings.ttod_path, self.settings.schema_dir)
        oracle = OracleService(self.settings, snapshots, FakeOllama(), FakeRetrieval())
        self.users = MemoryUserStore()
        self.sessions = MemorySessionStore()
        self.proposals = SpyProposalStore(Path(temp.name))
        self.app = create_app(
            self.settings, oracle, users=self.users, sessions=self.sessions, proposals=self.proposals
        )
        self.client = TestClient(self.app)

    def register(self, email: str, ip: str = "203.0.113.7") -> str:
        response = self.client.post(
            "/api/v1/auth/register", json={"email": email, "password": PASSWORD},
            headers={"x-forwarded-for": ip},
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()["session_token"]

    def login(self, email: str, password: str = PASSWORD, ip: str = "203.0.113.7"):
        return self.client.post(
            "/api/v1/auth/login", json={"email": email, "password": password},
            headers={"x-forwarded-for": ip},
        )

    def as_user(self, token: str) -> dict[str, str]:
        return {SESSION_COOKIE_NAME: token}


class ThrottleTests(AA2Case):
    def test_throttle_register_returns_429_after_the_ip_budget(self):
        self.build(register_ip=Budget(2, 3600))
        self.register("a@example.test")
        self.register("b@example.test")
        third = self.client.post(
            "/api/v1/auth/register", json={"email": "c@example.test", "password": PASSWORD},
            headers={"x-forwarded-for": "203.0.113.7"},
        )
        self.assertEqual(third.status_code, 429)
        self.assertEqual(third.headers["retry-after"], "3600")
        other_ip = self.client.post(
            "/api/v1/auth/register", json={"email": "d@example.test", "password": PASSWORD},
            headers={"x-forwarded-for": "198.51.100.9"},
        )
        self.assertEqual(other_ip.status_code, 201)

    def test_throttle_login_per_account_counts_every_attempt(self):
        self.build(account=Budget(3, 300))
        self.register("victim@example.test")
        for _ in range(3):
            self.assertIn(self.login("victim@example.test", "wrong-password").status_code, {401})
        # The right password does not reset the counter: the budget is spent.
        self.assertEqual(self.login("victim@example.test").status_code, 429)

    def test_throttle_login_per_ip_spans_accounts(self):
        self.build(login_ip=Budget(2, 300))
        self.assertEqual(self.login("x1@example.test").status_code, 401)
        self.assertEqual(self.login("x2@example.test").status_code, 401)
        self.assertEqual(self.login("x3@example.test").status_code, 429)
        self.assertEqual(self.login("x3@example.test", ip="198.51.100.9").status_code, 401)

    def test_throttle_proposal_returns_429_after_the_user_budget(self):
        self.build(proposal_user=Budget(1, 3600))
        token = self.register("writer@example.test")
        body = {"text": "A short candidate.", "section": "wisdom", "level": "beginner", "lang": "en"}
        first = self.client.post("/api/v1/proposals", json=body, cookies=self.as_user(token))
        self.assertEqual(first.status_code, 201, first.text)
        second = self.client.post("/api/v1/proposals", json=body, cookies=self.as_user(token))
        self.assertEqual(second.status_code, 429)

    def test_throttle_budgets_read_from_env(self):
        budgets = budgets_from_env({"TTOD_THROTTLE_REGISTER_IP": "9/60"})
        self.assertEqual(budgets["register-ip"], Budget(9, 60))
        self.assertEqual(budgets["login-ip"], DEFAULT_BUDGETS["login-ip"])


class SignedFallbackTests(AA2Case):
    def _signed_blob(self, auth: AuthService) -> str:
        # An AuthService without a store issues the legacy signed blob.
        return auth.issue_session(SessionClaims(user_id="usr-x", email="x@example.test", roles=("student",)))

    def _store_less(self) -> AuthService:
        s = self.settings
        return AuthService(s.session_secret, s.session_ttl_seconds, s.admin_email, s.admin_password_hash,
                           s.pat_secret, s.pat_ttl_seconds)

    def test_signed_fallback_off_refuses_a_valid_signed_blob(self):
        self.build()
        blob = self._signed_blob(self._store_less())
        self.assertEqual(self.client.get("/api/v1/auth/session", cookies=self.as_user(blob)).status_code, 401)

    def test_signed_fallback_off_can_be_reenabled_explicitly(self):
        self.build()
        s = self.settings
        auth = AuthService(s.session_secret, s.session_ttl_seconds, s.admin_email, s.admin_password_hash,
                           s.pat_secret, s.pat_ttl_seconds, sessions=MemorySessionStore(), allow_signed_fallback=True)
        blob = self._signed_blob(self._store_less())
        self.assertIsNotNone(auth.read_session(blob))


class PatDenylistTests(AA2Case):
    def issue(self, token: str) -> str:
        response = self.client.post("/api/v1/auth/token", cookies=self.as_user(token))
        self.assertEqual(response.status_code, 200)
        return response.json()["access_token"]

    def bearer(self, pat: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {pat}"}

    def test_pat_denylist_revoked_token_is_401_before_it_expires(self):
        self.build()
        pat = self.issue(self.register("api@example.test"))
        self.assertEqual(self.client.get("/api/v1/wisdom/random", headers=self.bearer(pat)).status_code, 200)
        self.assertEqual(self.client.delete("/api/v1/auth/token", headers=self.bearer(pat)).status_code, 204)
        self.assertEqual(self.client.get("/api/v1/wisdom/random", headers=self.bearer(pat)).status_code, 401)

    def test_pat_denylist_logout_all_revokes_every_pat_and_session(self):
        self.build()
        token = self.register("many@example.test")
        pats = [self.issue(token), self.issue(token)]
        self.assertEqual(self.client.post("/api/v1/auth/logout-all", cookies=self.as_user(token)).status_code, 204)
        for pat in pats:
            self.assertEqual(self.client.get("/api/v1/wisdom/random", headers=self.bearer(pat)).status_code, 401)
        self.assertEqual(self.client.get("/api/v1/auth/session", cookies=self.as_user(token)).status_code, 401)

    def test_pat_denylist_password_change_revokes_pats(self):
        self.build()
        token = self.register("rotate@example.test")
        pat = self.issue(token)
        changed = self.client.post("/api/v1/auth/password", cookies=self.as_user(token),
                                   json={"current_password": PASSWORD, "new_password": "a-brand-new-secret"})
        self.assertEqual(changed.status_code, 200, changed.text)
        self.assertEqual(self.client.get("/api/v1/wisdom/random", headers=self.bearer(pat)).status_code, 401)

    def test_pat_denylist_refuses_legacy_tokens_without_jti(self):
        self.build()
        s = self.settings
        legacy = AuthService(s.session_secret, s.session_ttl_seconds, s.admin_email, s.admin_password_hash,
                             s.pat_secret, s.pat_ttl_seconds)._pat_serializer.dumps({"sub": "usr-1", "typ": "pat"})
        self.assertEqual(self.client.get("/api/v1/wisdom/random", headers=self.bearer(legacy)).status_code, 401)


class OracleSessionTests(AA2Case):
    def test_oracle_requires_session_for_stream_and_propose(self):
        self.build()
        stream = self.client.post("/api/v1/oracle/stream", json={"query": "q", "sessionHistory": [], "locale": "en"})
        self.assertEqual(stream.status_code, 401)
        propose = self.client.post("/api/v1/oracle/propose", json={"query": "q", "creativeAnswer": "a"})
        self.assertEqual(propose.status_code, 401)
        self.assertEqual(self.proposals.saved, [])

    def test_oracle_requires_session_stream_works_when_signed_in(self):
        self.build()
        token = self.register("asker@example.test")
        stream = self.client.post("/api/v1/oracle/stream", cookies=self.as_user(token),
                                  json={"query": "q", "sessionHistory": [], "locale": "en"})
        self.assertEqual(stream.status_code, 200)
        self.assertIn("text/event-stream", stream.headers["content-type"])

    def test_oracle_propose_dual_write_goes_through_the_app_store(self):
        self.build()
        token = self.register("poet@example.test")
        response = self.client.post("/api/v1/oracle/propose", cookies=self.as_user(token),
                                    json={"query": "What should this teach?", "creativeAnswer": "A new candidate."})
        self.assertEqual(response.status_code, 201, response.text)
        body = response.json()
        self.assertEqual(self.proposals.saved, [body["proposal_id"]])
        self.assertNotIn("stored_at", body)  # no server path in the response

    def test_oracle_propose_dual_write_shares_the_proposal_budget(self):
        self.build(proposal_user=Budget(1, 3600))
        token = self.register("eager@example.test")
        body = {"query": "q", "creativeAnswer": "a"}
        self.assertEqual(self.client.post("/api/v1/oracle/propose", json=body, cookies=self.as_user(token)).status_code, 201)
        self.assertEqual(self.client.post("/api/v1/oracle/propose", json=body, cookies=self.as_user(token)).status_code, 429)


class PasswordChangeTests(AA2Case):
    def change(self, token: str, current: str, new: str, **extra):
        return self.client.post("/api/v1/auth/password", cookies=self.as_user(token),
                                json={"current_password": current, "new_password": new, **extra})

    def test_password_change_rotates_caller_and_revokes_other_sessions(self):
        self.build()
        laptop = self.register("owner@example.test")
        phone = self.login("owner@example.test").json()["session_token"]
        response = self.change(laptop, PASSWORD, "a-brand-new-secret")
        self.assertEqual(response.status_code, 200, response.text)
        rotated = response.json()["session_token"]
        self.assertNotEqual(rotated, laptop)
        self.assertEqual(self.client.get("/api/v1/auth/session", cookies=self.as_user(rotated)).status_code, 200)
        self.assertEqual(self.client.get("/api/v1/auth/session", cookies=self.as_user(laptop)).status_code, 401)
        self.assertEqual(self.client.get("/api/v1/auth/session", cookies=self.as_user(phone)).status_code, 401)
        self.assertEqual(self.login("owner@example.test").status_code, 401)  # old password
        self.assertEqual(self.login("owner@example.test", "a-brand-new-secret").status_code, 200)

    def test_password_change_wrong_current_is_401_with_login_text_and_throttled(self):
        self.build(account=Budget(3, 300))
        token = self.register("careful@example.test")
        for _ in range(3):
            wrong = self.change(token, "not-my-password", "a-brand-new-secret")
            self.assertEqual(wrong.status_code, 401)
            self.assertEqual(wrong.json()["detail"], "Invalid email or password")
        self.assertEqual(self.change(token, PASSWORD, "a-brand-new-secret").status_code, 429)

    def test_password_change_keeps_others_when_asked(self):
        self.build()
        laptop = self.register("calm@example.test")
        phone = self.login("calm@example.test").json()["session_token"]
        response = self.change(laptop, PASSWORD, "a-brand-new-secret", revoke_others=False)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/api/v1/auth/session", cookies=self.as_user(phone)).status_code, 200)
        self.assertEqual(self.client.get("/api/v1/auth/session", cookies=self.as_user(laptop)).status_code, 401)

    def test_password_change_rejects_overlong_new_password(self):
        self.build()
        token = self.register("long@example.test")
        self.assertEqual(self.change(token, PASSWORD, "x" * 73).status_code, 422)

    def test_password_change_requires_a_session(self):
        self.build()
        anonymous = self.client.post("/api/v1/auth/password", json={"current_password": "a", "new_password": "b" * 8})
        self.assertEqual(anonymous.status_code, 401)

    def test_password_change_profile_display_name_round_trips(self):
        self.build()
        token = self.register("named@example.test")
        self.assertNotIn("display_name", self.client.get("/api/v1/auth/session", cookies=self.as_user(token)).json())
        patched = self.client.patch("/api/v1/auth/profile", cookies=self.as_user(token), json={"display_name": "  Ada  "})
        self.assertEqual(patched.status_code, 200)
        self.assertEqual(patched.json()["display_name"], "Ada")
        self.assertEqual(self.client.get("/api/v1/auth/session", cookies=self.as_user(token)).json()["display_name"], "Ada")
        self.assertEqual(self.client.patch("/api/v1/auth/profile", cookies=self.as_user(token),
                                           json={"display_name": "<b>x</b>"}).status_code, 422)


class ReviewAmendmentTests(AA2Case):
    """Cold review (PASS-WITH-AMENDMENTS) fixes: F1, F2, F9, F11."""

    def test_throttle_login_trusts_forwarded_for_only_when_told(self):
        import os
        from unittest import mock
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(Settings.from_env().trust_forwarded_for)  # code default: off (F1)
        with mock.patch.dict(os.environ, {"TTOD_TRUST_FORWARDED_FOR": "1"}, clear=True):
            self.assertTrue(Settings.from_env().trust_forwarded_for)  # Compose sets it

    def test_password_change_revokes_sessions_issued_before_the_index_existed(self):
        self.build()
        token = self.register("legacy@example.test")
        user_id = self.client.get("/api/v1/auth/session", cookies=self.as_user(token)).json()["id"]
        # A pre-AA2 session: a valid row in the store that the per-user index never saw.
        claims = self.sessions.get(token)
        self.sessions.put("legacy-sid", claims, ttl_seconds=3600)
        self.assertEqual(self.client.get("/api/v1/auth/session", cookies=self.as_user("legacy-sid")).status_code, 200)
        changed = self.client.post("/api/v1/auth/password", cookies=self.as_user(token),
                                   json={"current_password": PASSWORD, "new_password": "a-brand-new-secret"})
        self.assertEqual(changed.status_code, 200)
        self.assertEqual(self.client.get("/api/v1/auth/session", cookies=self.as_user("legacy-sid")).status_code, 401)
        self.assertTrue(user_id)

    def test_password_change_profile_rejects_invisible_and_rtl_characters(self):
        self.build()
        token = self.register("unicode@example.test")
        for bad in ["Ada\u202e", "A\u200bda"]:
            response = self.client.patch("/api/v1/auth/profile", cookies=self.as_user(token), json={"display_name": bad})
            self.assertEqual(response.status_code, 422, bad)
        ok = self.client.patch("/api/v1/auth/profile", cookies=self.as_user(token), json={"display_name": "Zoë"})
        self.assertEqual(ok.json()["display_name"], "Zoë")

    def test_oracle_propose_dual_write_indexes_the_draft_in_redis(self):
        from services.backend.app.proposal_drafts import DualWriteProposalDraftStore
        from services.backend.tests.test_shore_stores import FakeRedis as ShoreFakeRedis
        self.build()
        redis = ShoreFakeRedis()
        dual = DualWriteProposalDraftStore(self.settings.proposal_dir, client=redis)
        snapshots = SnapshotService(self.settings.ttod_path, self.settings.schema_dir)
        app = create_app(self.settings, OracleService(self.settings, snapshots, FakeOllama(), FakeRetrieval()),
                         users=self.users, sessions=self.sessions, proposals=dual)
        client = TestClient(app)
        token = self.register("indexed@example.test")
        response = client.post("/api/v1/oracle/propose", cookies=self.as_user(token),
                               json={"query": "q", "creativeAnswer": "A candidate."})
        self.assertEqual(response.status_code, 201, response.text)
        proposal_id = response.json()["proposal_id"]
        self.assertTrue(any(proposal_id in key for key in redis.kv), redis.kv.keys())
        self.assertTrue(any(proposal_id in members for members in redis.sets.values()))
        self.assertTrue((self.settings.proposal_dir / f"{proposal_id}.json").exists())


class SessionIndexTests(AA2Case):
    def test_session_index_prunes_sids_whose_row_expired(self):
        self.build()
        token = self.register("index@example.test")
        second = self.login("index@example.test").json()["session_token"]
        user_id = self.client.get("/api/v1/auth/session", cookies=self.as_user(token)).json()["id"]
        self.sessions.delete(second)  # simulate TTL expiry of one row
        s = self.settings
        svc = AuthService(s.session_secret, s.session_ttl_seconds, s.admin_email, s.admin_password_hash,
                          s.pat_secret, s.pat_ttl_seconds, users=self.users, sessions=self.sessions,
                          registry=MemoryTokenRegistry())
        svc._registry.add_session(user_id, token, 60)
        svc._registry.add_session(user_id, second, 60)
        self.assertEqual(svc.user_sessions(user_id), {token})
        self.assertEqual(svc._registry.sessions(user_id), {token})

    def test_session_index_logout_removes_the_sid(self):
        self.build()
        token = self.register("bye@example.test")
        self.assertEqual(self.client.post("/api/v1/auth/logout", cookies=self.as_user(token)).status_code, 204)
        self.assertEqual(self.client.get("/api/v1/auth/session", cookies=self.as_user(token)).status_code, 401)


class FakeRedis:
    """Just enough Redis for the throttle and the registry."""

    def __init__(self):
        self.kv: dict[str, str] = {}
        self.sets: dict[str, set[str]] = {}
        self.ttl: dict[str, int] = {}

    def incr(self, key):
        self.kv[key] = str(int(self.kv.get(key, "0")) + 1)
        return int(self.kv[key])

    def expire(self, key, seconds, nx=False):
        if nx and key in self.ttl:
            return False
        self.ttl[key] = seconds
        return True

    def set(self, key, value, ex=None):
        self.kv[key] = value
        if ex:
            self.ttl[key] = ex

    def exists(self, key):
        return int(key in self.kv)

    def delete(self, key):
        self.kv.pop(key, None)
        self.sets.pop(key, None)

    def sadd(self, key, member):
        self.sets.setdefault(key, set()).add(member)

    def srem(self, key, member):
        self.sets.get(key, set()).discard(member)

    def smembers(self, key):
        return set(self.sets.get(key, set()))

    def pipeline(self):
        return _Pipe(self)


class _Pipe:
    def __init__(self, redis):
        self.redis, self.calls = redis, []

    def __getattr__(self, name):
        return lambda *a, **k: self.calls.append((name, a, k))

    def execute(self):
        return [getattr(self.redis, n)(*a, **k) for n, a, k in self.calls]


class RedisBackendsTests(unittest.TestCase):
    def test_throttle_redis_counts_per_hashed_key_and_sets_the_window(self):
        redis = FakeRedis()
        throttle = RedisThrottle(redis)
        budget = Budget(2, 60)
        self.assertTrue(throttle.hit("login-ip", "203.0.113.7", budget))
        self.assertTrue(throttle.hit("login-ip", "203.0.113.7", budget))
        self.assertFalse(throttle.hit("login-ip", "203.0.113.7", budget))
        (key,) = redis.kv
        self.assertNotIn("203.0.113.7", key)  # IPs and emails never appear in key names
        self.assertEqual(redis.ttl[key], 60)

    def test_session_index_redis_registry_round_trip(self):
        registry = RedisTokenRegistry(FakeRedis())
        registry.add_session("u1", "sid-a", 60)
        registry.add_pat("u1", "jti-a", 60)
        self.assertEqual(registry.sessions("u1"), {"sid-a"})
        registry.deny_pat("jti-a", 60)
        self.assertTrue(registry.is_pat_denied("jti-a"))
        registry.clear_pats("u1")
        self.assertEqual(registry.pats("u1"), set())


if __name__ == "__main__":
    unittest.main()
