"""AA5 lane A: health tells the truth about Redis (F27); shore secrets fail closed (F28)."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock

import redis
from fastapi.testclient import TestClient

from services.backend.app.config import REPOSITORY_ROOT, Settings
from services.backend.app.favorites import MemoryFavoriteStore
from services.backend.app.main import create_app
from services.backend.app.proposal_drafts import FilesystemProposalDraftStore
from services.backend.app.sessions import MemorySessionStore
from services.backend.app.users import MemoryUserStore


class HealthRedisTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.settings = Settings(
            ttod_path=REPOSITORY_ROOT / "ttod.yml",
            schema_dir=REPOSITORY_ROOT / "schema",
            proposal_dir=Path(temp.name),
            redis_url="redis://unused",
            ollama_model="test-model",
        )
        self.proposal_dir = Path(temp.name)

    def _client(self, ping):
        shore = MagicMock()
        shore.ping.side_effect = ping
        app = create_app(
            self.settings,
            users=MemoryUserStore(),
            sessions=MemorySessionStore(),
            favorites=MemoryFavoriteStore(),
            proposals=FilesystemProposalDraftStore(self.proposal_dir),
            redis_client=shore,
        )
        return TestClient(app)

    def test_health_redis_down_returns_503(self):
        response = self._client(redis.RedisError("down")).get("/health")
        self.assertEqual(response.status_code, 503)
        body = response.json()
        self.assertEqual(body["redis"], "down")
        self.assertEqual(body["status"], "degraded")

    def test_health_redis_down_body_is_sanitized(self):
        # Regression guard: redis_ping already swallows the error, so this pins the body shape.
        # The real leak on /health (repository exception text, main.py) is F47, lane B.
        response = self._client(redis.RedisError("secret-host:6379 refused")).get("/health")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("secret-host", response.text)

    def test_health_redis_up_returns_200(self):
        response = self._client(lambda: True).get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["redis"], "ok")


class SecretsFailClosedTests(unittest.TestCase):
    def test_empty_secret_fails_boot_when_redis_is_set(self):
        for missing in ("TTOD_SESSION_SECRET", "TTOD_PAT_SECRET"):
            env = {
                "REDIS_URL": "redis://redis:6379/0",
                "TTOD_SESSION_SECRET": "s" * 40,
                "TTOD_PAT_SECRET": "p" * 40,
                missing: "",
            }
            with self.subTest(missing=missing), mock.patch.dict(os.environ, env, clear=True):
                with self.assertRaisesRegex(RuntimeError, missing):
                    Settings.from_env()

    def test_empty_secret_is_generated_without_redis(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            settings = Settings.from_env()
        self.assertGreaterEqual(len(settings.session_secret), 32)
        self.assertNotEqual(settings.session_secret, settings.pat_secret)

    def test_set_secrets_are_used_verbatim_with_redis(self):
        env = {"REDIS_URL": "redis://redis:6379/0", "TTOD_SESSION_SECRET": "s" * 40, "TTOD_PAT_SECRET": "p" * 40}
        with mock.patch.dict(os.environ, env, clear=True):
            settings = Settings.from_env()
        self.assertEqual(settings.session_secret, "s" * 40)
        self.assertEqual(settings.pat_secret, "p" * 40)


if __name__ == "__main__":
    unittest.main()
