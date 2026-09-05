"""
TTOD Canonicalization Tests (Q2E)

Tests for TTOD-C14N-v1 canonicalization and digest computation.
"""

import json
import math
import unittest

from ttod_core.canonical import Canonicalizer, CanonicalizationError, ExportPolicy, SnapshotManifest


class TestCanonicalizer(unittest.TestCase):
    """Test TTOD-C14N-v1 canonicalization."""

    def setUp(self):
        self.canonicalizer = Canonicalizer()

    def test_normalize_string_nfc(self):
        """String normalization to NFC."""
        # Test composed vs decomposed forms
        composed = "café"
        decomposed = "cafe\u0301"
        self.assertEqual(
            self.canonicalizer.normalize_string(decomposed),
            self.canonicalizer.normalize_string(composed),
        )

    def test_normalize_recursively_strings(self):
        """Recursive normalization of strings in nested structures."""
        obj = {"text": "café", "nested": {"value": "naïve"}}
        normalized = self.canonicalizer.normalize_recursively(obj)
        self.assertEqual(normalized["text"], self.canonicalizer.normalize_string("café"))
        self.assertEqual(normalized["nested"]["value"], self.canonicalizer.normalize_string("naïve"))

    def test_normalize_recursively_objects_sorted_keys(self):
        """Object keys are sorted lexicographically."""
        obj = {"z": 1, "a": 2, "m": 3}
        normalized = self.canonicalizer.normalize_recursively(obj)
        keys = list(normalized.keys())
        self.assertEqual(keys, ["a", "m", "z"])

    def test_normalize_recursively_arrays_preserve_order(self):
        """Array order is preserved."""
        obj = {"items": [3, 1, 2]}
        normalized = self.canonicalizer.normalize_recursively(obj)
        self.assertEqual(normalized["items"], [3, 1, 2])

    def test_normalize_recursively_rejects_non_string_identifier(self):
        """Non-string identifier fields are rejected."""
        obj = {"id": 123, "text": "test"}
        with self.assertRaises(CanonicalizationError) as cm:
            self.canonicalizer.normalize_recursively(obj)
        self.assertIn("id", str(cm.exception))

    def test_normalize_recursively_rejects_non_string_tag(self):
        """Non-string tags are rejected."""
        obj = {"tags": [404, "valid"]}
        with self.assertRaises(CanonicalizationError) as cm:
            self.canonicalizer.normalize_recursively(obj)
        self.assertIn("Tag", str(cm.exception))

    def test_normalize_recursively_rejects_nan(self):
        """NaN is rejected."""
        obj = {"value": float("nan")}
        with self.assertRaises(CanonicalizationError) as cm:
            self.canonicalizer.normalize_recursively(obj)
        self.assertIn("Non-finite", str(cm.exception))

    def test_normalize_recursively_rejects_infinity(self):
        """Infinity is rejected."""
        obj = {"value": float("inf")}
        with self.assertRaises(CanonicalizationError) as cm:
            self.canonicalizer.normalize_recursively(obj)
        self.assertIn("Non-finite", str(cm.exception))

    def test_to_canonical_json_compact_separators(self):
        """Canonical JSON uses compact separators."""
        obj = {"a": 1, "b": 2}
        json_bytes = self.canonicalizer.to_canonical_json(obj)
        json_str = json_bytes.decode("utf-8")
        # No spaces after colons or commas
        self.assertNotIn(": ", json_str)
        self.assertNotIn(", ", json_str)

    def test_to_canonical_json_terminal_newline(self):
        """Canonical JSON ends with exactly one newline."""
        obj = {"a": 1}
        json_bytes = self.canonicalizer.to_canonical_json(obj)
        self.assertTrue(json_bytes.endswith(b"\n"))
        # Only one newline
        self.assertFalse(json_bytes.endswith(b"\n\n"))

    def test_to_canonical_json_sorted_keys(self):
        """Canonical JSON has sorted keys."""
        obj = {"z": 1, "a": 2, "m": 3}
        json_bytes = self.canonicalizer.to_canonical_json(obj)
        json_str = json_bytes.decode("utf-8")
        # "a" should come before "z"
        self.assertLess(json_str.index('"a"'), json_str.index('"z"'))

    def test_compute_content_digest(self):
        """Content digest computation."""
        quote = {
            "id": "arch-001",
            "text": "Test quote",
            "section": "architecture",
            "level": "advanced",
            "lang": "en",
            "origin": "human",
        }
        digest = self.canonicalizer.compute_content_digest(quote)
        # Digest should be 64 hex characters
        self.assertEqual(len(digest), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in digest))

    def test_compute_content_digest_excludes_digest_fields(self):
        """Content digest excludes digest fields from projection."""
        quote_with_digest = {
            "id": "arch-001",
            "text": "Test quote",
            "content_digest": "a" * 64,
            "section": "architecture",
            "level": "advanced",
            "lang": "en",
            "origin": "human",
        }
        quote_without_digest = {
            "id": "arch-001",
            "text": "Test quote",
            "section": "architecture",
            "level": "advanced",
            "lang": "en",
            "origin": "human",
        }
        digest1 = self.canonicalizer.compute_content_digest(quote_with_digest)
        digest2 = self.canonicalizer.compute_content_digest(quote_without_digest)
        # Digests should be the same since digest field is excluded
        self.assertEqual(digest1, digest2)

    def test_compute_snapshot_digest(self):
        """Snapshot digest computation."""
        quotes = [
            {"id": "arch-002", "text": "Second"},
            {"id": "arch-001", "text": "First"},
        ]
        digest = self.canonicalizer.compute_snapshot_digest(
            quotes,
            schema_version="3.0.0",
            taxonomy_digest="a" * 64,
            collection_policy_digest="b" * 64,
        )
        self.assertEqual(len(digest), 64)

    def test_compute_snapshot_digest_sorts_quotes(self):
        """Snapshot digest sorts quotes by ID."""
        quotes1 = [
            {"id": "arch-002", "text": "Second"},
            {"id": "arch-001", "text": "First"},
        ]
        quotes2 = [
            {"id": "arch-001", "text": "First"},
            {"id": "arch-002", "text": "Second"},
        ]
        digest1 = self.canonicalizer.compute_snapshot_digest(
            quotes1,
            schema_version="3.0.0",
            taxonomy_digest="a" * 64,
            collection_policy_digest="b" * 64,
        )
        digest2 = self.canonicalizer.compute_snapshot_digest(
            quotes2,
            schema_version="3.0.0",
            taxonomy_digest="a" * 64,
            collection_policy_digest="b" * 64,
        )
        # Digests should be the same since quotes are sorted
        self.assertEqual(digest1, digest2)

    def test_verify_content_digest_detects_tampering(self):
        """Stored digest that does not match TTOD-C14N-v1 is rejected."""
        quote = {
            "id": "arch-001",
            "text": "Test quote",
            "section": "architecture",
            "level": "advanced",
            "lang": "en",
            "origin": "human",
            "content_digest": "0" * 64,
        }
        with self.assertRaises(CanonicalizationError) as caught:
            self.canonicalizer.verify_content_digest(quote)
        self.assertIn("tampering", str(caught.exception))

    def test_verify_content_digest_accepts_match(self):
        quote = {
            "id": "arch-001",
            "text": "Test quote",
            "section": "architecture",
            "level": "advanced",
            "lang": "en",
            "origin": "human",
        }
        expected = self.canonicalizer.compute_content_digest(quote)
        quote["content_digest"] = expected
        self.assertEqual(self.canonicalizer.verify_content_digest(quote), expected)

    def test_q1_negative_digest_mismatch_fixture(self):
        from pathlib import Path
        fixture = Path(__file__).parent / "fixtures" / "q1_negative_digest_mismatch.json"
        with open(fixture) as handle:
            quote = json.load(handle)
        with self.assertRaises(CanonicalizationError):
            self.canonicalizer.verify_content_digest(quote)

    def test_determinism_two_exports_byte_identical(self):
        """Two exports of the same input are byte-identical."""
        obj = {
            "z": 1,
            "a": 2,
            "nested": {"m": 3, "b": 4},
            "array": [3, 1, 2],
        }
        bytes1 = self.canonicalizer.to_canonical_json(obj)
        bytes2 = self.canonicalizer.to_canonical_json(obj)
        self.assertEqual(bytes1, bytes2)

    def test_determinism_byte_diff_test(self):
        """Byte-level diff test for determinism."""
        obj = {
            "id": "arch-001",
            "text": "café",
            "tags": ["architecture", "boundaries"],
            "level": "advanced",
            "lang": "en",
        }
        bytes1 = self.canonicalizer.to_canonical_json(obj)
        bytes2 = self.canonicalizer.to_canonical_json(obj)
        # Byte-identical
        self.assertEqual(bytes1, bytes2)
        # Verify by comparing hex
        self.assertEqual(bytes1.hex(), bytes2.hex())


class TestExportPolicy(unittest.TestCase):
    """Test export policy."""

    def test_should_include_active(self):
        """Active records are always included."""
        policy = ExportPolicy()
        record = {"status": "active"}
        self.assertTrue(policy.should_include(record))

    def test_should_exclude_erased_by_default(self):
        """Erased records are excluded by default."""
        policy = ExportPolicy()
        record = {"status": "erased"}
        self.assertFalse(policy.should_include(record))

    def test_should_include_erased_when_flagged(self):
        """Erased records are included when flag is set."""
        policy = ExportPolicy(include_erased=True)
        record = {"status": "erased"}
        self.assertTrue(policy.should_include(record))

    def test_should_exclude_deprecated_when_flagged(self):
        """Deprecated records are excluded when flag is set."""
        policy = ExportPolicy(include_deprecated=False)
        record = {"status": "deprecated"}
        self.assertFalse(policy.should_include(record))

    def test_should_exclude_restricted_in_public_export(self):
        """Restricted records are excluded in public export."""
        policy = ExportPolicy(public_export=True)
        record = {"status": "active", "rights": {"access": "restricted"}}
        self.assertFalse(policy.should_include(record))

    def test_should_include_restricted_in_non_public_export(self):
        """Restricted records are included in non-public export."""
        policy = ExportPolicy(public_export=False)
        record = {"status": "active", "rights": {"access": "restricted"}}
        self.assertTrue(policy.should_include(record))


class TestSnapshotManifest(unittest.TestCase):
    """Test snapshot manifest."""

    def test_to_dict(self):
        """Manifest can be serialized to dict."""
        manifest = SnapshotManifest(
            source_file_digest="a" * 64,
            record_count=42,
            snapshot_digest="b" * 64,
        )
        d = manifest.to_dict()
        self.assertEqual(d["algorithm"], "TTOD-C14N-v1")
        self.assertEqual(d["record_count"], 42)
        self.assertIn("generated_at", d)


if __name__ == "__main__":
    unittest.main()
