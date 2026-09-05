import tempfile
import unittest
from pathlib import Path

import yaml

from services.mcp.server import RetrievalService


def fake_embed(text):
    lowered = text.lower()
    return [float(lowered.count("simple")), float(lowered.count("boundary")), 1.0]


class RetrievalServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.source = Path(self.temp.name) / "ttod.yml"
        self.data = {
            "quotes": [
                {"id": "a-001", "text": "Simple things", "section": "architecture", "tags": ["simple"], "origin": "human", "status": "active", "related": ["a-002"], "rights": {"access": "public", "license": "x", "holder": "h"}},
                {"id": "a-002", "text": "Boundary", "section": "architecture", "tags": ["boundary"], "origin": "studio", "status": "active", "rights": {"access": "public", "license": "x", "holder": "h"}},
                {"id": "a-003", "text": "Secret simple", "section": "architecture", "tags": ["simple"], "origin": "human", "status": "active", "rights": {"access": "restricted"}},
                {"id": "a-004", "text": "Old simple", "section": "architecture", "tags": ["simple"], "origin": "human", "status": "deprecated", "rights": {"access": "public", "license": "x", "holder": "h"}},
                {"id": "a-005", "text": "Unresolved", "section": "architecture", "tags": [], "origin": "human", "status": "active"},
                {"id": "a-006", "text": "Empty rights simple", "section": "architecture", "tags": ["simple"], "origin": "human", "status": "active", "rights": {}},
            ]
        }
        self.source.write_text(yaml.safe_dump(self.data), encoding="utf-8")
        self.service = RetrievalService(self.source, fake_embed)

    def tearDown(self):
        self.temp.cleanup()

    def test_search_filters_rights_and_lifecycle_and_preserves_origin_and_scores(self):
        result = self.service.semantic_search("simple", top_k=5)
        self.assertEqual([item["id"] for item in result["results"]], ["a-001", "a-002"])
        self.assertEqual(result["results"][0]["origin"], "human")
        self.assertIsInstance(result["results"][0]["score"], float)
        self.assertEqual(result["indexedQuotes"], 2)

    def test_unchanged_source_reuses_index_and_ranking_is_deterministic(self):
        first_snapshot = self.service.refresh()
        first = self.service.semantic_search("boundary")
        second_snapshot = self.service.refresh()
        second = self.service.semantic_search("boundary")
        self.assertIs(first_snapshot, second_snapshot)
        self.assertEqual(first, second)

    def test_digest_change_refreshes_index(self):
        before = self.service.refresh()
        self.data["quotes"][1]["text"] = "Simple boundary"
        self.source.write_text(yaml.safe_dump(self.data), encoding="utf-8")
        after = self.service.refresh()
        self.assertNotEqual(before.digest, after.digest)

    def test_filters_and_graph_neighborhood(self):
        filtered = self.service.semantic_search("simple", context_tag="simple", section="architecture")
        self.assertEqual([item["id"] for item in filtered["results"]], ["a-001"])
        graph = self.service.graph_neighborhood(quote_id="a-001")
        self.assertEqual(graph["seedIds"], ["a-001"])
        self.assertEqual({node["id"] for node in graph["nodes"]}, {"a-001", "a-002"})
        self.assertEqual(graph["edges"], [{"source": "a-001", "target": "a-002", "rel": "related"}])

    def test_validation(self):
        with self.assertRaises(ValueError):
            self.service.semantic_search(" ")
        with self.assertRaises(ValueError):
            self.service.graph_neighborhood()


if __name__ == "__main__":
    unittest.main()
