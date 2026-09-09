"""
Phase S S1′ — lang field, translation_of invariants, read-path propagation.

Fixtures under tests/fixtures/s1_* are frozen by
docs/DEV_PLAN/PHASE-S-TTOD-BILINGUAL-CONTENT-MODEL.md — do not invent aliases.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ttod_core.bridge import QuoteOutAdapter, assert_field_mapping_complete, field_mapping_coverage
from ttod_core.canonical import Canonicalizer
from ttod_core.exporter import Exporter
from ttod_core.repository import TTODRepository, compute_derived_metadata
from ttod_core.validation import DiagnosticCode, TTODValidator

FIXTURES = Path(__file__).parent / "fixtures"
SCHEMA = Path(__file__).parent.parent / "schema"


def _load(name: str):
    with open(FIXTURES / name, encoding="utf-8") as handle:
        return json.load(handle)


class TestS1TranslationFixtures(unittest.TestCase):
    def setUp(self):
        self.validator = TTODValidator(SCHEMA, strict=False)
        self.strict = TTODValidator(SCHEMA, strict=True)

    def test_positive_translation_pair_clean(self):
        result = self.validator.validate_root(_load("s1_positive_translation_pair.json"))
        self.assertTrue(result.is_valid, result.to_dict())
        self.assertEqual(result.errors, [])
        self.assertEqual(result.warnings, [])

    def test_missing_lang_is_type_error(self):
        result = self.validator.validate_quote(_load("s1_negative_missing_lang.json"))
        self.assertIn(DiagnosticCode.TYPE_ERROR, [e.code for e in result.errors])

    def test_locale_suffix_id_is_type_error(self):
        result = self.validator.validate_quote(_load("s1_negative_locale_suffix_id.json"))
        self.assertIn(DiagnosticCode.TYPE_ERROR, [e.code for e in result.errors])

    def test_translation_target_unresolved(self):
        result = self.validator.validate_root(
            _load("s1_negative_translation_target_unresolved.json")
        )
        self.assertIn(DiagnosticCode.TRANSLATION_TARGET_UNRESOLVED, [e.code for e in result.errors])

    def test_translation_target_inactive(self):
        result = self.validator.validate_root(
            _load("s1_negative_translation_target_inactive.json")
        )
        self.assertIn(DiagnosticCode.TRANSLATION_TARGET_INACTIVE, [e.code for e in result.errors])

    def test_translation_same_language(self):
        result = self.validator.validate_root(
            _load("s1_negative_translation_same_language.json")
        )
        self.assertIn(DiagnosticCode.TRANSLATION_SAME_LANGUAGE, [e.code for e in result.errors])

    def test_translation_self_target(self):
        result = self.validator.validate_root(_load("s1_negative_translation_self_target.json"))
        self.assertIn(DiagnosticCode.TRANSLATION_SELF_TARGET, [e.code for e in result.errors])

    def test_translation_chain(self):
        result = self.validator.validate_root(_load("s1_negative_translation_chain.json"))
        self.assertIn(DiagnosticCode.TRANSLATION_CHAIN, [e.code for e in result.errors])

    def test_translation_duplicate_active(self):
        result = self.validator.validate_root(
            _load("s1_negative_translation_duplicate_active.json")
        )
        self.assertIn(DiagnosticCode.TRANSLATION_DUPLICATE_ACTIVE, [e.code for e in result.errors])

    def test_translation_section_mismatch_warning_non_strict(self):
        result = self.validator.validate_root(
            _load("s1_warning_translation_section_mismatch.json")
        )
        self.assertEqual(result.errors, [], result.to_dict())
        self.assertIn(
            DiagnosticCode.TRANSLATION_SECTION_MISMATCH,
            [w.code for w in result.warnings],
        )

    def test_translation_section_mismatch_error_under_strict(self):
        result = self.strict.validate_root(_load("s1_warning_translation_section_mismatch.json"))
        self.assertIn(
            DiagnosticCode.TRANSLATION_SECTION_MISMATCH,
            [e.code for e in result.errors],
        )


class TestS1ReadPath(unittest.TestCase):
    def test_field_mapping_includes_lang(self):
        mapping = field_mapping_coverage()
        self.assertEqual(mapping.get("lang"), "lang")
        assert_field_mapping_complete()

    def test_to_transport_emits_lang(self):
        quote = {
            "id": "arch-901",
            "text": "Boundaries are where systems learn their shape.",
            "section": "architecture",
            "level": "advanced",
            "lang": "es",
            "origin": "human",
            "content_digest": "a" * 64,
        }
        transport = QuoteOutAdapter().to_transport(quote, snapshot_digest="b" * 64)
        self.assertEqual(transport.get("lang"), "es")

    def test_graph_nodes_project_lang(self):
        data = {
            "meta": {"version": "3.1.0"},
            "quotes": [
                {
                    "id": "arch-901",
                    "section": "architecture",
                    "origin": "human",
                    "status": "active",
                    "text": "Hello",
                    "lang": "en",
                },
                {
                    "id": "arch-902",
                    "section": "architecture",
                    "origin": "human",
                    "status": "active",
                    "text": "Hola",
                    "lang": "es",
                    "relation_edges": [
                        {"target": "arch-901", "relation_type": "translation_of"}
                    ],
                },
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "graph.json"
            Exporter(Canonicalizer()).export_graph(data, target)
            exported = json.loads(target.read_text())
        by_id = {n["id"]: n for n in exported["nodes"]}
        self.assertEqual(by_id["arch-901"]["lang"], "en")
        self.assertEqual(by_id["arch-902"]["lang"], "es")
        self.assertIn(
            {"source": "arch-902", "target": "arch-901", "rel": "translation_of"},
            exported["edges"],
        )

    def test_derived_metadata_language_breakdown(self):
        root = _load("s1_positive_translation_pair.json")
        derived = compute_derived_metadata(root)
        self.assertEqual(derived.language_counts["en"], 1)
        self.assertEqual(derived.language_counts["es"], 1)
        self.assertEqual(derived.languages, ["en", "es"])


if __name__ == "__main__":
    unittest.main()
