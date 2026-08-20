"""
TTOD Exporter Tests (Q2E)

Tests for atomic export mechanics.
"""

import json
import tempfile
import unittest
from pathlib import Path

from ttod_core.canonical import ExportPolicy
from ttod_core.exporter import Exporter, ExportError


class TestExporter(unittest.TestCase):
    """Test atomic export mechanics."""

    def setUp(self):
        self.exporter = Exporter()
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        # Clean up temp directory
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_export_json_creates_file(self):
        """Export creates the target file."""
        data = {
            "meta": {"version": "3.0.0"},
            "quotes": [{"id": "arch-001", "text": "Test"}],
        }
        target_path = self.temp_dir / "ttod.json"
        manifest = self.exporter.export_json(data, target_path)
        self.assertTrue(target_path.exists())

    def test_export_json_filters_by_policy(self):
        """Export filters quotes based on policy."""
        data = {
            "meta": {"version": "3.0.0"},
            "quotes": [
                {"id": "arch-001", "text": "Active", "status": "active"},
                {"id": "arch-002", "text": "Erased", "status": "erased"},
            ],
        }
        target_path = self.temp_dir / "ttod.json"
        policy = ExportPolicy(include_erased=False)
        manifest = self.exporter.export_json(data, target_path, policy)

        # Verify only active quote is in export
        with open(target_path) as f:
            exported = json.load(f)
        self.assertEqual(len(exported["quotes"]), 1)
        self.assertEqual(exported["quotes"][0]["id"], "arch-001")

    def test_export_json_includes_manifest(self):
        """Export includes manifest in output."""
        data = {
            "meta": {"version": "3.0.0"},
            "quotes": [{"id": "arch-001", "text": "Test"}],
        }
        target_path = self.temp_dir / "ttod.json"
        manifest = self.exporter.export_json(data, target_path)

        with open(target_path) as f:
            exported = json.load(f)
        self.assertIn("_manifest", exported)
        self.assertEqual(exported["_manifest"]["algorithm"], "TTOD-C14N-v1")

    def test_export_json_atomic_write(self):
        """Export writes atomically - temp file then rename."""
        data = {
            "meta": {"version": "3.0.0"},
            "quotes": [{"id": "arch-001", "text": "Test"}],
        }
        target_path = self.temp_dir / "ttod.json"

        # Export
        manifest = self.exporter.export_json(data, target_path)

        # Verify target exists and is valid JSON
        self.assertTrue(target_path.exists())
        with open(target_path) as f:
            json.load(f)  # Should not raise

    def test_export_quote_json(self):
        """Export a single quote."""
        quote = {
            "id": "arch-001",
            "text": "Test quote",
            "section": "architecture",
            "level": "advanced",
            "origin": "human",
        }
        target_path = self.temp_dir / "arch-001.json"
        digest = self.exporter.export_quote_json(quote, target_path)

        # Verify file exists and has digest
        self.assertTrue(target_path.exists())
        with open(target_path) as f:
            exported = json.load(f)
        self.assertIn("content_digest", exported)
        self.assertEqual(exported["content_digest"], digest)
        self.assertEqual(len(digest), 64)

    def test_export_quote_json_rejects_invalid_tag(self):
        """Export rejects quote with non-string tag."""
        quote = {
            "id": "arch-001",
            "text": "Test quote",
            "tags": [404],  # Invalid: integer tag
            "section": "architecture",
            "level": "advanced",
            "origin": "human",
        }
        target_path = self.temp_dir / "arch-001.json"

        from ttod_core.canonical import CanonicalizationError
        with self.assertRaises(CanonicalizationError):
            self.exporter.export_quote_json(quote, target_path)

    def test_export_two_runs_byte_identical(self):
        """Two exports of the same data are byte-identical (raw file bytes)."""
        data = {
            "meta": {"version": "3.0.0"},
            "quotes": [
                {"id": "arch-001", "text": "First"},
                {"id": "arch-002", "text": "Second"},
            ],
        }
        target_path1 = self.temp_dir / "ttod1.json"
        target_path2 = self.temp_dir / "ttod2.json"

        self.exporter.export_json(data, target_path1)
        self.exporter.export_json(data, target_path2)

        self.assertEqual(target_path1.read_bytes(), target_path2.read_bytes())
        # Written payload is C14N (compact separators, one trailing newline)
        payload = target_path1.read_bytes()
        self.assertTrue(payload.endswith(b"\n"))
        self.assertNotIn(b": ", payload)

    def test_export_graph_creates_nodes_and_edges(self):
        data = {
            "meta": {"version": "3.0.0"},
            "quotes": [
                {"id": "arch-001", "text": "First", "related": ["arch-002"], "status": "active"},
                {"id": "arch-002", "text": "Second", "status": "active"},
            ],
        }
        target_path = self.temp_dir / "ttod.graph.json"
        self.exporter.export_graph(data, target_path)
        exported = json.loads(target_path.read_text())
        self.assertEqual(exported["projection"], "graph-v1")
        self.assertEqual([n["id"] for n in exported["nodes"]], ["arch-001", "arch-002"])
        self.assertEqual(
            exported["edges"],
            [{"rel": "related", "source": "arch-001", "target": "arch-002"}],
        )

    def test_export_graph_two_runs_byte_identical(self):
        data = {
            "meta": {"version": "3.0.0"},
            "quotes": [
                {"id": "arch-002", "text": "Second", "related": ["arch-001"]},
                {"id": "arch-001", "text": "First"},
            ],
        }
        path1 = self.temp_dir / "g1.json"
        path2 = self.temp_dir / "g2.json"
        self.exporter.export_graph(data, path1)
        self.exporter.export_graph(data, path2)
        self.assertEqual(path1.read_bytes(), path2.read_bytes())

    def test_export_quote_json_rejects_tampered_digest(self):
        quote = {
            "id": "arch-001",
            "text": "Test quote",
            "section": "architecture",
            "level": "advanced",
            "origin": "human",
            "content_digest": "0" * 64,
        }
        target_path = self.temp_dir / "arch-001.json"
        from ttod_core.canonical import CanonicalizationError
        with self.assertRaises(CanonicalizationError):
            self.exporter.export_quote_json(quote, target_path)
        self.assertFalse(target_path.exists())

    def test_export_creates_parent_directory(self):
        """Export creates parent directory if it doesn't exist."""
        data = {
            "meta": {"version": "3.0.0"},
            "quotes": [{"id": "arch-001", "text": "Test"}],
        }
        target_path = self.temp_dir / "subdir" / "ttod.json"

        self.exporter.export_json(data, target_path)
        self.assertTrue(target_path.exists())
        self.assertTrue(target_path.parent.exists())


if __name__ == "__main__":
    unittest.main()
