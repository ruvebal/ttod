from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from services.backend.app.config import REPOSITORY_ROOT, Settings
from services.backend.app.favorites import RedisFavoriteStore
from services.backend.app.models import FavoriteEntry
from services.backend.app.main import create_app
from services.backend.app.oracle import (
    CREATIVE_PROMPT,
    FastMCPRetrievalClient,
    OracleService,
    build_user_prompt,
    detect_language,
    normalize_retrieval_envelope,
    thematic_frame,
)
from services.backend.app.storage import SnapshotService


class FakeOllama:
    def __init__(self):
        self.prompt = ""
        self.system = ""

    async def generate(self, prompt, system):
        self.prompt = prompt
        self.system = system
        yield "answer"


class FakeRetrieval:
    async def semantic_retrieval(self, query, *, top_k, context_tag, section):
        return {"results": [{
            "id": "wis-001", "text": "Nearest wisdom", "section": "wisdom",
            "tags": ["simplicity"], "origin": "human", "score": 0.1,
        }], "indexDigest": "digest", "indexedQuotes": 1}


class FakeFavorites:
    def __init__(self):
        self.entries: dict[str, dict[str, FavoriteEntry]] = {}

    def save(self, user_id: str, quote_id: str) -> FavoriteEntry:
        user_entries = self.entries.setdefault(user_id, {})
        entry = user_entries.setdefault(
            quote_id, FavoriteEntry(userId=user_id, quoteId=quote_id, savedAt="2026-01-01T00:00:00+00:00")
        )
        return entry

    def list(self, user_id: str) -> list[FavoriteEntry]:
        return list(self.entries.get(user_id, {}).values())

    def remove(self, user_id: str, quote_id: str) -> bool:
        return self.entries.get(user_id, {}).pop(quote_id, None) is not None


class FakeRedis:
    def __init__(self):
        self.values: dict[str, dict[str, str]] = {}

    def hget(self, key: str, field: str) -> str | None:
        return self.values.get(key, {}).get(field)

    def hset(self, key: str, field: str, value: str) -> None:
        self.values.setdefault(key, {})[field] = value

    def hgetall(self, key: str) -> dict[str, str]:
        return self.values.get(key, {})

    def hdel(self, key: str, field: str) -> int:
        return int(self.values.get(key, {}).pop(field, None) is not None)


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.settings = Settings(
            ttod_path=REPOSITORY_ROOT / "ttod.yml", schema_dir=REPOSITORY_ROOT / "schema",
            proposal_dir=Path(self.temp.name), ollama_model="test-model",
        )
        self.snapshots = SnapshotService(self.settings.ttod_path, self.settings.schema_dir)
        self.ollama = FakeOllama()
        self.oracle = OracleService(self.settings, self.snapshots, self.ollama, FakeRetrieval())
        self.favorites = FakeFavorites()
        self.client = TestClient(create_app(self.settings, self.oracle, self.favorites))

    def tearDown(self):
        self.temp.cleanup()

    def test_health_schema_and_public_projections(self):
        self.assertEqual(self.client.get("/health").status_code, 200)
        self.assertIn("properties", self.client.get("/api/v1/schema/definitions").json()["quote"])
        wisdom = self.client.get("/api/v1/wisdom/sample").json()
        self.assertTrue(wisdom)
        self.assertTrue(all(q["rights"]["license"] and "validation" not in q for q in wisdom))
        graph = self.client.get("/api/v1/graph").json()
        self.assertTrue(graph["nodes"])
        self.assertTrue(all(n["status"] == "active" for n in graph["nodes"]))

    def test_graph_is_byte_deterministic(self):
        self.assertEqual(self.client.get("/api/v1/graph").content, self.client.get("/api/v1/graph").content)

    def test_reviewer_queue_requires_reviewer_or_instructor_role(self):
        student = {"Authorization": "Bearer " + json.dumps({"userId": "student-1", "roles": ["student"]})}
        reviewer = {"Authorization": "Bearer " + json.dumps({"userId": "reviewer-1", "roles": ["reviewer"]})}
        instructor = {"Authorization": "Bearer " + json.dumps({"userId": "instructor-1", "roles": ["instructor"]})}

        self.assertEqual(self.client.get("/api/v1/proposals", headers=student).status_code, 403)
        self.assertEqual(self.client.get("/api/v1/proposals", headers=reviewer).status_code, 200)
        self.assertEqual(self.client.get("/api/v1/proposals", headers=instructor).status_code, 200)

    def test_creative_stream_discloses_mode_without_citations(self):
        response = self.client.post(
            "/api/v1/oracle/stream",
            json={"query": "unmatched", "sessionHistory": [], "locale": "en"},
        )
        envelope = json.loads(response.text.removeprefix("data: ").strip())
        self.assertEqual(envelope["mode"], "creative")
        self.assertNotIn("citedQuoteIds", envelope)
        self.assertEqual(envelope["themes"], ["wisdom"])
        self.assertEqual(envelope["tags"], ["simplicity"])
        self.assertIn("MUST NOT", self.ollama.system)
        self.assertIn("koan", self.ollama.system.lower())
        self.assertIn("Thematic anchors — knowledge areas: wisdom", self.ollama.prompt)
        self.assertIn("Thematic anchors — tags: simplicity", self.ollama.prompt)
        self.assertIn("Respond in en.", self.ollama.system)

    def test_locale_overrides_heuristic_language(self):
        self.assertEqual(detect_language("The router hangs", "es"), "es")
        self.assertEqual(detect_language("¿Cómo simplifico?", "en"), "en")

    def test_thematic_frame_and_creative_prompt_forbid_debugging(self):
        ranked = [{
            "id": "ops-001", "text": "x", "section": "ops", "tags": ["observability", "ops"],
            "origin": "human", "score": 0.4,
        }]
        frame = thematic_frame(ranked)
        self.assertEqual(frame, {"themes": ["ops"], "tags": ["observability", "ops"]})
        prompt = build_user_prompt(
            query="router hangs", session_history=[], ranked=ranked, frame=frame, grounded=False,
        )
        self.assertIn("below threshold", prompt)
        self.assertIn("MUST NOT", CREATIVE_PROMPT)

    def test_oracle_propose_cannot_activate_or_allocate_canonical_id(self):
        response = self.client.post("/api/v1/oracle/propose", json={
            "query": "What should this teach?", "creativeAnswer": "A new candidate answer.",
            "locale": "en",
        }, headers={"Authorization": "Bearer test-user"})
        self.assertEqual(response.status_code, 201)
        proposal = response.json()
        self.assertEqual(proposal["status"], "proposed")
        self.assertEqual(proposal["candidate_content"]["origin"], "blackbox")
        self.assertEqual(proposal["candidate_content"]["lang"], "en")
        self.assertEqual(proposal["candidate_content"]["tags"], ["simplicity"])
        self.assertNotIn("id", proposal["candidate_content"])
        persisted = json.loads(next(Path(self.temp.name).glob("*.json")).read_text())
        self.assertEqual(persisted["status"], "proposed")
        self.assertNotEqual(persisted.get("status"), "active")
        self.assertNotIn("accepted_quote_id", persisted)

    def test_r2_envelope_normalization(self):
        payload = {"results": [{
            "id": "wis-001", "text": "x", "section": "wisdom", "tags": [],
            "origin": "human", "score": 0.8,
        }], "indexDigest": "abc", "indexedQuotes": 1, "ignored": True}
        self.assertEqual(set(normalize_retrieval_envelope(payload)), {"results", "indexDigest", "indexedQuotes"})

    def test_favorites_are_authenticated_isolated_and_idempotent(self):
        student = {"Authorization": "Bearer " + json.dumps({"userId": "student-1", "roles": ["student"]})}
        other = {"Authorization": "Bearer " + json.dumps({"userId": "student-2", "roles": ["student"]})}
        quote_id = self.client.get("/api/v1/wisdom/sample").json()[0]["id"]

        self.assertEqual(self.client.post("/api/v1/favorites", json={"quoteId": quote_id}).status_code, 401)
        first = self.client.post("/api/v1/favorites", json={"quoteId": quote_id}, headers=student)
        second = self.client.post("/api/v1/favorites", json={"quoteId": quote_id}, headers=student)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.json(), first.json())
        self.assertEqual(self.client.get("/api/v1/favorites", headers=student).json()[0]["quoteId"], quote_id)
        self.assertEqual(self.client.get("/api/v1/favorites", headers=other).json(), [])
        self.assertEqual(self.client.delete(f"/api/v1/favorites/{quote_id}", headers=student).status_code, 200)
        self.assertEqual(self.client.get("/api/v1/favorites", headers=student).json(), [])

    def test_favorites_reject_unknown_or_non_public_quote(self):
        student = {"Authorization": "Bearer " + json.dumps({"userId": "student-1", "roles": ["student"]})}
        response = self.client.post("/api/v1/favorites", json={"quoteId": "missing"}, headers=student)
        self.assertEqual(response.status_code, 404)

    def test_redis_favorite_store_is_idempotent_and_persistent(self):
        store = RedisFavoriteStore("redis://unused", client=FakeRedis())
        first = store.save("student-1", "wis-001")
        second = store.save("student-1", "wis-001")
        self.assertEqual(first, second)
        self.assertEqual(store.list("student-1"), [first])
        self.assertTrue(store.remove("student-1", "wis-001"))
        self.assertFalse(store.remove("student-1", "wis-001"))

    def test_mcp_unavailable_fails_closed(self):
        import asyncio
        client = FastMCPRetrievalClient("http://127.0.0.1:1")
        with self.assertRaisesRegex(RuntimeError, "MCP semantic retrieval unavailable"):
            asyncio.run(client.semantic_retrieval("query", top_k=5, context_tag=None, section=None))


if __name__ == "__main__":
    unittest.main()
