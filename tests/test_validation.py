"""
TTOD Validation Core Tests (Q2V)

Tests for the strict validation and invariant engine.
Runs every Q1 fixture through the full validator with exact-code assertions,
plus additional fixtures for invariants this phase adds beyond raw JSON Schema.
"""

import json
import unittest
from pathlib import Path

from ttod_core.validation import TTODValidator, DiagnosticCode, ValidationResult

SCHEMA_DIR = Path(__file__).parent.parent / "schema"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestQuoteValidation(unittest.TestCase):
    """Test single quote validation."""

    def setUp(self):
        self.validator = TTODValidator(schema_dir=SCHEMA_DIR, strict=False)

    def test_positive_legacy_read_passes(self):
        """Legacy-read record should validate."""
        with open(FIXTURES_DIR / "q1_positive_legacy_read.json") as f:
            quote = json.load(f)
        result = self.validator.validate_quote(quote)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_positive_v3_human_passes(self):
        """v3 human-authored record should validate."""
        with open(FIXTURES_DIR / "q1_positive_v3_human.json") as f:
            quote = json.load(f)
        result = self.validator.validate_quote(quote)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_positive_v3_reviewed_blackbox_passes(self):
        """v3 reviewed-blackbox record should validate."""
        with open(FIXTURES_DIR / "q1_positive_v3_reviewed_blackbox.json") as f:
            quote = json.load(f)
        result = self.validator.validate_quote(quote)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_positive_deprecated_passes(self):
        """Deprecated record should validate."""
        with open(FIXTURES_DIR / "q1_positive_deprecated.json") as f:
            quote = json.load(f)
        result = self.validator.validate_quote(quote)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_positive_erasure_tombstone_passes(self):
        """Erasure-tombstone record should validate."""
        with open(FIXTURES_DIR / "q1_positive_erasure_tombstone.json") as f:
            quote = json.load(f)
        result = self.validator.validate_quote(quote)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_negative_missing_review_blackbox_fails(self):
        """Blackbox without human review should fail."""
        with open(FIXTURES_DIR / "q1_negative_missing_review_blackbox.json") as f:
            quote = json.load(f)
        result = self.validator.validate_quote(quote)
        self.assertFalse(result.is_valid)
        # Should have MISSING_REVIEW error from schema
        error_codes = [e.code for e in result.errors]
        self.assertIn(DiagnosticCode.MISSING_REVIEW, error_codes)

    def test_negative_non_string_tag_fails(self):
        """Numeric tag should fail."""
        with open(FIXTURES_DIR / "q1_negative_non_string_tag.json") as f:
            quote = json.load(f)
        result = self.validator.validate_quote(quote)
        self.assertFalse(result.is_valid)
        error_codes = [e.code for e in result.errors]
        self.assertIn(DiagnosticCode.NON_STRING_TAG, error_codes)

    def test_origin_unresolved_fails(self):
        """Missing origin should emit ORIGIN_UNRESOLVED, not silently count as human."""
        quote = {
            "id": "test-001",
            "schema_version": "3.0.0",
            "text": "Test quote",
            "section": "architecture",
            "level": "advanced",
            # origin is missing
        }
        result = self.validator.validate_quote(quote)
        self.assertFalse(result.is_valid)
        error_codes = [e.code for e in result.errors]
        self.assertIn(DiagnosticCode.ORIGIN_UNRESOLVED, error_codes)

    def test_invalid_origin_fails(self):
        """Invalid origin value should emit ORIGIN_UNRESOLVED."""
        quote = {
            "id": "test-001",
            "schema_version": "3.0.0",
            "text": "Test quote",
            "section": "architecture",
            "level": "advanced",
            "origin": "invalid-origin",
        }
        result = self.validator.validate_quote(quote)
        self.assertFalse(result.is_valid)
        error_codes = [e.code for e in result.errors]
        self.assertIn(DiagnosticCode.ORIGIN_UNRESOLVED, error_codes)

    def test_invalid_digest_format_fails(self):
        """Invalid digest format should fail."""
        quote = {
            "id": "test-001",
            "schema_version": "3.0.0",
            "content_digest": "not-a-valid-digest",
            "text": "Test quote",
            "section": "architecture",
            "level": "advanced",
            "origin": "human",
        }
        result = self.validator.validate_quote(quote)
        self.assertFalse(result.is_valid)
        error_codes = [e.code for e in result.errors]
        self.assertIn(DiagnosticCode.TYPE_ERROR, error_codes)


class TestRootValidation(unittest.TestCase):
    """Test root document validation with cross-record checks."""

    def setUp(self):
        self.validator = TTODValidator(schema_dir=SCHEMA_DIR, strict=False)

    def test_root_structure_validates(self):
        """Valid root structure should pass."""
        root = {
            "meta": {
                "title": "The Tao of Development",
                "version": "3.0.0",
                "total_quotes": 1,
                "last_id_by_section": {"architecture": 1}
            },
            "sections": [
                {
                    "id": "architecture",
                    "prefix": "arch",
                    "name": "Architecture"
                }
            ],
            "tag_taxonomy": {},
            "collections": {},
            "lessons": [],
            "quotes": [
                {
                    "id": "arch-001",
                    "schema_version": "3.0.0",
                    "text": "Test quote",
                    "section": "architecture",
                    "level": "advanced",
                    "origin": "human"
                }
            ]
        }
        result = self.validator.validate_root(root)
        if not result.is_valid:
            print(f"Root validation failed:")
            for e in result.errors:
                print(f"  ERROR {e.code}: {e.message}")
            for w in result.warnings:
                print(f"  WARNING {w.code}: {w.message}")
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_duplicate_id_fails(self):
        """Duplicate quote IDs should fail."""
        root = {
            "meta": {
                "title": "The Tao of Development",
                "version": "3.0.0",
                "total_quotes": 2,
                "last_id_by_section": {"arch": 1}
            },
            "sections": [
                {
                    "id": "architecture",
                    "prefix": "arch",
                    "name": "Architecture"
                }
            ],
            "tag_taxonomy": {},
            "collections": {},
            "lessons": {},
            "quotes": [
                {
                    "id": "arch-001",
                    "schema_version": "3.0.0",
                    "text": "First quote",
                    "section": "architecture",
                    "level": "advanced",
                    "origin": "human"
                },
                {
                    "id": "arch-001",  # Duplicate ID
                    "schema_version": "3.0.0",
                    "text": "Second quote",
                    "section": "architecture",
                    "level": "advanced",
                    "origin": "human"
                }
            ]
        }
        result = self.validator.validate_root(root)
        self.assertFalse(result.is_valid)
        error_codes = [e.code for e in result.errors]
        self.assertIn(DiagnosticCode.DUPLICATE_ID, error_codes)

    def test_prefix_section_mismatch_fails(self):
        """Quote ID prefix not matching section should fail."""
        root = {
            "meta": {
                "title": "The Tao of Development",
                "version": "3.0.0",
                "total_quotes": 1,
                "last_id_by_section": {"arch": 1}
            },
            "sections": [
                {
                    "id": "architecture",
                    "prefix": "arch",
                    "name": "Architecture"
                }
            ],
            "tag_taxonomy": {},
            "collections": {},
            "lessons": {},
            "quotes": [
                {
                    "id": "wis-001",  # Wrong prefix for architecture section
                    "schema_version": "3.0.0",
                    "text": "Test quote",
                    "section": "architecture",
                    "level": "advanced",
                    "origin": "human"
                }
            ]
        }
        result = self.validator.validate_root(root)
        self.assertFalse(result.is_valid)
        error_codes = [e.code for e in result.errors]
        self.assertIn(DiagnosticCode.PREFIX_SECTION_MISMATCH, error_codes)

    def test_meta_count_mismatch_warns(self):
        """Meta count mismatch should warn in non-strict mode."""
        root = {
            "meta": {
                "title": "The Tao of Development",
                "version": "3.0.0",
                "total_quotes": 1,
                "last_id_by_section": {"architecture": 999}  # Wrong count
            },
            "sections": [
                {
                    "id": "architecture",
                    "prefix": "arch",
                    "name": "Architecture"
                }
            ],
            "tag_taxonomy": {},
            "collections": {},
            "lessons": [],
            "quotes": [
                {
                    "id": "arch-001",
                    "schema_version": "3.0.0",
                    "text": "Test quote",
                    "section": "architecture",
                    "level": "advanced",
                    "origin": "human"
                }
            ]
        }
        result = self.validator.validate_root(root)
        # Should be valid in non-strict mode (warning only)
        self.assertTrue(result.is_valid)
        warning_codes = [w.code for w in result.warnings]
        self.assertIn(DiagnosticCode.META_COUNT_MISMATCH, warning_codes)

    def test_meta_count_mismatch_fails_in_strict_mode(self):
        """Meta count mismatch should fail in strict mode."""
        strict_validator = TTODValidator(schema_dir=SCHEMA_DIR, strict=True)
        root = {
            "meta": {
                "title": "The Tao of Development",
                "version": "3.0.0",
                "total_quotes": 1,
                "last_id_by_section": {"architecture": 999}  # Wrong count
            },
            "sections": [
                {
                    "id": "architecture",
                    "prefix": "arch",
                    "name": "Architecture"
                }
            ],
            "tag_taxonomy": {},
            "collections": {},
            "lessons": [],
            "quotes": [
                {
                    "id": "arch-001",
                    "schema_version": "3.0.0",
                    "text": "Test quote",
                    "section": "architecture",
                    "level": "advanced",
                    "origin": "human"
                }
            ]
        }
        result = strict_validator.validate_root(root)
        self.assertFalse(result.is_valid)
        error_codes = [e.code for e in result.errors]
        self.assertIn(DiagnosticCode.META_COUNT_MISMATCH, error_codes)

    def test_tag_not_in_taxonomy_warns(self):
        """Tag not in taxonomy should warn in non-strict mode."""
        root = {
            "meta": {
                "title": "The Tao of Development",
                "version": "3.0.0",
                "total_quotes": 1,
                "last_id_by_section": {"architecture": 1}
            },
            "sections": [
                {
                    "id": "architecture",
                    "prefix": "arch",
                    "name": "Architecture"
                }
            ],
            "tag_taxonomy": {
                "architecture": ["boundaries"]
            },
            "collections": {},
            "lessons": [],
            "quotes": [
                {
                    "id": "arch-001",
                    "schema_version": "3.0.0",
                    "text": "Test quote",
                    "section": "architecture",
                    "level": "advanced",
                    "tags": ["undeclared-tag"],  # Not in taxonomy
                    "origin": "human"
                }
            ]
        }
        result = self.validator.validate_root(root)
        # Should be valid in non-strict mode (warning only)
        if not result.is_valid:
            print(f"Tag taxonomy validation failed:")
            for e in result.errors:
                print(f"  ERROR {e.code}: {e.message}")
            for w in result.warnings:
                print(f"  WARNING {w.code}: {w.message}")
        self.assertTrue(result.is_valid)
        warning_codes = [w.code for w in result.warnings]
        self.assertIn(DiagnosticCode.TAG_NOT_IN_TAXONOMY, warning_codes)

    def test_dangling_related_fails(self):
        """Dangling related target should fail."""
        root = {
            "meta": {
                "title": "The Tao of Development",
                "version": "3.0.0",
                "total_quotes": 1,
                "last_id_by_section": {"arch": 1}
            },
            "sections": [
                {
                    "id": "architecture",
                    "prefix": "arch",
                    "name": "Architecture"
                }
            ],
            "tag_taxonomy": {},
            "collections": {},
            "lessons": {},
            "quotes": [
                {
                    "id": "arch-001",
                    "schema_version": "3.0.0",
                    "text": "Test quote",
                    "section": "architecture",
                    "level": "advanced",
                    "related": ["arch-999"],  # Dangling reference
                    "origin": "human"
                }
            ]
        }
        result = self.validator.validate_root(root)
        self.assertFalse(result.is_valid)
        error_codes = [e.code for e in result.errors]
        self.assertIn(DiagnosticCode.RELATED_TARGET_NOT_FOUND, error_codes)

    def test_broken_ancestry_fails(self):
        """Broken ancestry reference should fail."""
        root = {
            "meta": {
                "title": "The Tao of Development",
                "version": "3.0.0",
                "total_quotes": 1,
                "last_id_by_section": {"arch": 1}
            },
            "sections": [
                {
                    "id": "architecture",
                    "prefix": "arch",
                    "name": "Architecture"
                }
            ],
            "tag_taxonomy": {},
            "collections": {},
            "lessons": {},
            "quotes": [
                {
                    "id": "arch-001",
                    "schema_version": "3.0.0",
                    "text": "Test quote",
                    "section": "architecture",
                    "level": "advanced",
                    "immediate_parent_refs": ["arch-999"],  # Dangling reference
                    "origin": "human"
                }
            ]
        }
        result = self.validator.validate_root(root)
        self.assertFalse(result.is_valid)
        error_codes = [e.code for e in result.errors]
        self.assertIn(DiagnosticCode.ANCESTRY_TARGET_NOT_FOUND, error_codes)

    def test_rights_incomplete_for_public_fails(self):
        """Missing rights fields for public export should fail."""
        root = {
            "meta": {
                "title": "The Tao of Development",
                "version": "3.0.0",
                "total_quotes": 1,
                "last_id_by_section": {"arch": 1}
            },
            "sections": [
                {
                    "id": "architecture",
                    "prefix": "arch",
                    "name": "Architecture"
                }
            ],
            "tag_taxonomy": {},
            "collections": {},
            "lessons": {},
            "quotes": [
                {
                    "id": "arch-001",
                    "schema_version": "3.0.0",
                    "text": "Test quote",
                    "section": "architecture",
                    "level": "advanced",
                    "origin": "human",
                    "rights": {
                        "access": "public"
                        # Missing license and holder
                    }
                }
            ]
        }
        result = self.validator.validate_root(root)
        self.assertFalse(result.is_valid)
        error_codes = [e.code for e in result.errors]
        self.assertIn(DiagnosticCode.RIGHTS_INCOMPLETE_FOR_PUBLIC, error_codes)

    def test_collection_target_not_found_fails(self):
        """Collection referencing non-existent quote should fail."""
        root = {
            "meta": {
                "title": "The Tao of Development",
                "version": "3.0.0",
                "total_quotes": 1,
                "last_id_by_section": {"arch": 1}
            },
            "sections": [
                {
                    "id": "architecture",
                    "prefix": "arch",
                    "name": "Architecture"
                }
            ],
            "tag_taxonomy": {},
            "collections": {
                "daily_wisdom": {
                    "ids": ["arch-999"]  # Dangling reference
                }
            },
            "lessons": {},
            "quotes": [
                {
                    "id": "arch-001",
                    "schema_version": "3.0.0",
                    "text": "Test quote",
                    "section": "architecture",
                    "level": "advanced",
                    "origin": "human"
                }
            ]
        }
        result = self.validator.validate_root(root)
        self.assertFalse(result.is_valid)
        error_codes = [e.code for e in result.errors]
        self.assertIn(DiagnosticCode.COLLECTION_TARGET_NOT_FOUND, error_codes)

    def test_lifecycle_consistency_fails(self):
        """Deprecated by non-existent quote should fail."""
        root = {
            "meta": {
                "title": "The Tao of Development",
                "version": "3.0.0",
                "total_quotes": 1,
                "last_id_by_section": {"arch": 1}
            },
            "sections": [
                {
                    "id": "architecture",
                    "prefix": "arch",
                    "name": "Architecture"
                }
            ],
            "tag_taxonomy": {},
            "collections": {},
            "lessons": {},
            "quotes": [
                {
                    "id": "arch-001",
                    "schema_version": "3.0.0",
                    "text": "Test quote",
                    "section": "architecture",
                    "level": "advanced",
                    "origin": "human",
                    "status": "deprecated",
                    "deprecated_by": "arch-999"  # Dangling reference
                }
            ]
        }
        result = self.validator.validate_root(root)
        self.assertFalse(result.is_valid)
        error_codes = [e.code for e in result.errors]
        self.assertIn(DiagnosticCode.DEPRECATED_BY_NOT_FOUND, error_codes)


class TestProposalValidation(unittest.TestCase):
    """Test proposal validation."""

    def setUp(self):
        self.validator = TTODValidator(schema_dir=SCHEMA_DIR, strict=False)

    def test_negative_canonical_id_in_proposal_fails(self):
        """Proposal with canonical id should fail."""
        with open(FIXTURES_DIR / "q1_negative_canonical_id_in_proposal.json") as f:
            proposal = json.load(f)
        result = self.validator.validate_proposal(proposal)
        self.assertFalse(result.is_valid)
        error_codes = [e.code for e in result.errors]
        # Debug: print actual codes
        if DiagnosticCode.CANONICAL_ID_FORBIDDEN not in error_codes:
            print(f"Expected CANONICAL_ID_FORBIDDEN, got: {error_codes}")
            for e in result.errors:
                print(f"  {e.code}: {e.message}")
        self.assertIn(DiagnosticCode.CANONICAL_ID_FORBIDDEN, error_codes)


def _minimal_root(quotes, **overrides):
    """Build a v3 root around quote records for cross-record checks."""
    root = {
        "meta": {
            "title": "The Tao of Development",
            "version": "3.0.0",
            "total_quotes": len(quotes),
            "last_id_by_section": {},
        },
        "sections": [
            {"id": "architecture", "prefix": "arch", "name": "Architecture"},
            {"id": "wisdom", "prefix": "wis", "name": "Wisdom"},
            {"id": "images", "prefix": "img", "name": "Images"},
        ],
        "tag_taxonomy": {},
        "collections": {},
        "lessons": [],
        "quotes": quotes,
    }
    root.update(overrides)
    return root


class TestQ1FixturesThroughValidator(unittest.TestCase):
    """Replay every Q1 fixture through the full validator with exact codes."""

    def setUp(self):
        self.validator = TTODValidator(schema_dir=SCHEMA_DIR, strict=False)

    def test_q1_positive_quotes_pass_validate_quote(self):
        for name in (
            "q1_positive_legacy_read.json",
            "q1_positive_v3_human.json",
            "q1_positive_v3_reviewed_blackbox.json",
            "q1_positive_deprecated.json",
            "q1_positive_erasure_tombstone.json",
        ):
            with self.subTest(name=name):
                with open(FIXTURES_DIR / name) as handle:
                    quote = json.load(handle)
                result = self.validator.validate_quote(quote)
                self.assertTrue(result.is_valid, [e.message for e in result.errors])
                self.assertEqual(len(result.errors), 0)

    def test_q1_negative_missing_review_code(self):
        with open(FIXTURES_DIR / "q1_negative_missing_review_blackbox.json") as handle:
            quote = json.load(handle)
        result = self.validator.validate_quote(quote)
        self.assertFalse(result.is_valid)
        self.assertIn(DiagnosticCode.MISSING_REVIEW, [e.code for e in result.errors])

    def test_q1_negative_missing_origin_code(self):
        with open(FIXTURES_DIR / "q1_negative_missing_origin.json") as handle:
            quote = json.load(handle)
        result = self.validator.validate_quote(quote)
        self.assertFalse(result.is_valid)
        self.assertIn(DiagnosticCode.ORIGIN_UNRESOLVED, [e.code for e in result.errors])

    def test_q1_negative_non_string_tag_code(self):
        with open(FIXTURES_DIR / "q1_negative_non_string_tag.json") as handle:
            quote = json.load(handle)
        result = self.validator.validate_quote(quote)
        self.assertFalse(result.is_valid)
        self.assertIn(DiagnosticCode.NON_STRING_TAG, [e.code for e in result.errors])

    def test_q1_negative_digest_mismatch_code(self):
        with open(FIXTURES_DIR / "q1_negative_digest_mismatch.json") as handle:
            quote = json.load(handle)
        result = self.validator.validate_quote(quote)
        self.assertFalse(result.is_valid)
        self.assertIn(DiagnosticCode.DIGEST_MISMATCH, [e.code for e in result.errors])

    def test_q1_negative_dangling_related_via_root(self):
        with open(FIXTURES_DIR / "q1_negative_dangling_related.json") as handle:
            quote = json.load(handle)
        result = self.validator.validate_root(_minimal_root([quote]))
        self.assertFalse(result.is_valid)
        self.assertIn(DiagnosticCode.RELATED_TARGET_NOT_FOUND, [e.code for e in result.errors])

    def test_q1_negative_broken_ancestry_via_root(self):
        with open(FIXTURES_DIR / "q1_negative_broken_ancestry.json") as handle:
            quote = json.load(handle)
        result = self.validator.validate_root(_minimal_root([quote]))
        self.assertFalse(result.is_valid)
        self.assertIn(DiagnosticCode.ANCESTRY_TARGET_NOT_FOUND, [e.code for e in result.errors])

    def test_q1_negative_missing_rights_via_root(self):
        with open(FIXTURES_DIR / "q1_negative_missing_rights_public_export.json") as handle:
            quote = json.load(handle)
        result = self.validator.validate_root(_minimal_root([quote]))
        self.assertFalse(result.is_valid)
        self.assertIn(DiagnosticCode.RIGHTS_INCOMPLETE_FOR_PUBLIC, [e.code for e in result.errors])

    def test_q1_negative_canonical_id_in_proposal(self):
        with open(FIXTURES_DIR / "q1_negative_canonical_id_in_proposal.json") as handle:
            proposal = json.load(handle)
        result = self.validator.validate_proposal(proposal)
        self.assertFalse(result.is_valid)
        self.assertIn(DiagnosticCode.CANONICAL_ID_FORBIDDEN, [e.code for e in result.errors])

    def test_missing_origin_visible_on_validate_root(self):
        """Q0 bug: omitted origin must surface on the document, not only per-quote."""
        quotes = [
            {
                "id": "arch-001",
                "schema_version": "3.0.0",
                "text": "Has origin",
                "section": "architecture",
                "level": "advanced",
                "origin": "human",
            },
            {
                "id": "arch-002",
                "schema_version": "3.0.0",
                "text": "Missing origin",
                "section": "architecture",
                "level": "advanced",
            },
        ]
        result = self.validator.validate_root(_minimal_root(quotes))
        self.assertFalse(result.is_valid)
        self.assertIn(DiagnosticCode.ORIGIN_UNRESOLVED, [e.code for e in result.errors])

    def test_lesson_list_target_not_found(self):
        quotes = [
            {
                "id": "arch-001",
                "schema_version": "3.0.0",
                "text": "Test",
                "section": "architecture",
                "level": "advanced",
                "origin": "human",
            }
        ]
        root = _minimal_root(
            quotes,
            lessons=[{"id": "lesson-a", "quote_ids": ["arch-999"]}],
        )
        result = self.validator.validate_root(root)
        self.assertFalse(result.is_valid)
        self.assertIn(DiagnosticCode.LESSON_TARGET_NOT_FOUND, [e.code for e in result.errors])


if __name__ == "__main__":
    unittest.main()
