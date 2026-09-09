#!/usr/bin/env python3
"""
TTOD Phase Q1 Schema Contract Tests

JSON Schema is the contract. Tests assert stable error *codes* derived from
the ValidationError shape (validator + path + missing property), never a
prose substring. Cross-record and policy checks that JSON Schema cannot
express are asserted as schema-pass + deferred layer, not as fake failures.
"""

import json
import unittest
from pathlib import Path

from jsonschema import ValidationError, validate

SCHEMA_DIR = Path(__file__).parent.parent / "schema"
FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Codes JSON Schema itself can emit (Q1 gate).
MISSING_REVIEW = "MISSING_REVIEW"
NON_STRING_TAG = "NON_STRING_TAG"
CANONICAL_ID_FORBIDDEN = "CANONICAL_ID_FORBIDDEN"
ORIGIN_UNRESOLVED = "ORIGIN_UNRESOLVED"
RIGHTS_INCOMPLETE_FOR_PUBLIC = "RIGHTS_INCOMPLETE_FOR_PUBLIC"

# Codes deferred to later phases (fixtures exist; schema must not invent them).
RELATED_TARGET_NOT_FOUND = "RELATED_TARGET_NOT_FOUND"
ANCESTRY_TARGET_NOT_FOUND = "ANCESTRY_TARGET_NOT_FOUND"
DIGEST_MISMATCH = "DIGEST_MISMATCH"
SELF_DERIVED_NOT_EVIDENCE = "SELF_DERIVED_NOT_EVIDENCE"


def schema_error_code(error: ValidationError) -> str:
    """Map a jsonschema ValidationError to a stable Q1 diagnostic code."""
    validator = error.validator
    instance = error.instance
    path = [str(p) for p in error.path]
    message = error.message

    if validator == "not" and isinstance(instance, dict) and "id" in instance:
        return CANONICAL_ID_FORBIDDEN

    if validator == "required":
        if "'validation'" in message:
            return MISSING_REVIEW
        if "'origin'" in message:
            return ORIGIN_UNRESOLVED
        if "'license'" in message or "'holder'" in message:
            return RIGHTS_INCOMPLETE_FOR_PUBLIC

    if validator == "type" and "tags" in path:
        return NON_STRING_TAG

    if validator == "enum" and "origin" in path:
        return ORIGIN_UNRESOLVED

    raise AssertionError(
        f"Unmapped schema error (validator={validator!r} path={path} message={message!r})"
    )


def load_json(name: str):
    with open(FIXTURES_DIR / name) as handle:
        return json.load(handle)


class TestQuoteSchema(unittest.TestCase):
    """Test quote.schema.json validation."""

    def setUp(self):
        with open(SCHEMA_DIR / "quote.schema.json") as handle:
            self.schema = json.load(handle)

    def test_positive_legacy_read_passes(self):
        validate(instance=load_json("q1_positive_legacy_read.json"), schema=self.schema)

    def test_positive_v3_human_passes(self):
        validate(instance=load_json("q1_positive_v3_human.json"), schema=self.schema)

    def test_positive_v3_reviewed_blackbox_passes(self):
        validate(instance=load_json("q1_positive_v3_reviewed_blackbox.json"), schema=self.schema)

    def test_positive_deprecated_passes(self):
        validate(instance=load_json("q1_positive_deprecated.json"), schema=self.schema)

    def test_positive_erasure_tombstone_passes(self):
        validate(instance=load_json("q1_positive_erasure_tombstone.json"), schema=self.schema)

    def test_negative_missing_review_blackbox_fails(self):
        with self.assertRaises(ValidationError) as caught:
            validate(
                instance=load_json("q1_negative_missing_review_blackbox.json"),
                schema=self.schema,
            )
        self.assertEqual(schema_error_code(caught.exception), MISSING_REVIEW)

    def test_negative_missing_origin_fails(self):
        """Absent origin fails as ORIGIN_UNRESOLVED, not as a blackbox review error."""
        with self.assertRaises(ValidationError) as caught:
            validate(
                instance=load_json("q1_negative_missing_origin.json"),
                schema=self.schema,
            )
        self.assertEqual(schema_error_code(caught.exception), ORIGIN_UNRESOLVED)

    def test_negative_non_string_tag_fails(self):
        with self.assertRaises(ValidationError) as caught:
            validate(
                instance=load_json("q1_negative_non_string_tag.json"),
                schema=self.schema,
            )
        self.assertEqual(schema_error_code(caught.exception), NON_STRING_TAG)

    def test_negative_missing_rights_public_export_fails(self):
        with self.assertRaises(ValidationError) as caught:
            validate(
                instance=load_json("q1_negative_missing_rights_public_export.json"),
                schema=self.schema,
            )
        self.assertEqual(schema_error_code(caught.exception), RIGHTS_INCOMPLETE_FOR_PUBLIC)

    def test_negative_dangling_related_passes_schema_deferred_q2v(self):
        validate(instance=load_json("q1_negative_dangling_related.json"), schema=self.schema)
        self.assertEqual(RELATED_TARGET_NOT_FOUND, "RELATED_TARGET_NOT_FOUND")

    def test_negative_broken_ancestry_passes_schema_deferred_q2v(self):
        validate(instance=load_json("q1_negative_broken_ancestry.json"), schema=self.schema)
        self.assertEqual(ANCESTRY_TARGET_NOT_FOUND, "ANCESTRY_TARGET_NOT_FOUND")

    def test_negative_digest_mismatch_passes_schema_deferred_q2v(self):
        validate(instance=load_json("q1_negative_digest_mismatch.json"), schema=self.schema)
        self.assertEqual(DIGEST_MISMATCH, "DIGEST_MISMATCH")

    def test_negative_sibling_output_evidence_passes_schema_deferred_q5(self):
        validate(instance=load_json("q1_negative_sibling_output_evidence.json"), schema=self.schema)
        self.assertEqual(SELF_DERIVED_NOT_EVIDENCE, "SELF_DERIVED_NOT_EVIDENCE")

    def test_negative_arch_052_self_corroboration_passes_schema_deferred_q5(self):
        validate(
            instance=load_json("q1_negative_arch_052_self_corroboration.json"),
            schema=self.schema,
        )
        self.assertEqual(SELF_DERIVED_NOT_EVIDENCE, "SELF_DERIVED_NOT_EVIDENCE")


class TestProposalSchema(unittest.TestCase):
    """Test proposal.schema.json validation."""

    def setUp(self):
        with open(SCHEMA_DIR / "proposal.schema.json") as handle:
            self.schema = json.load(handle)

    def test_negative_canonical_id_in_proposal_fails(self):
        with self.assertRaises(ValidationError) as caught:
            validate(
                instance=load_json("q1_negative_canonical_id_in_proposal.json"),
                schema=self.schema,
            )
        self.assertEqual(schema_error_code(caught.exception), CANONICAL_ID_FORBIDDEN)


class TestTtodSchema(unittest.TestCase):
    """Test ttod.schema.json validation."""

    def setUp(self):
        with open(SCHEMA_DIR / "ttod.schema.json") as handle:
            self.schema = json.load(handle)
        with open(SCHEMA_DIR / "quote.schema.json") as handle:
            quote_schema = json.load(handle)
        self.schema["properties"]["quotes"]["items"] = quote_schema

    def test_root_structure_validates(self):
        root = {
            "meta": {
                "title": "The Tao of Development",
                "version": "3.0.0",
                "total_quotes": 1,
                "last_id_by_section": {"arch": 1},
            },
            "sections": [
                {
                    "id": "architecture",
                    "prefix": "arch",
                    "name": "Architecture",
                }
            ],
            "quotes": [
                {
                    "id": "arch-001",
                    "schema_version": "3.0.0",
                    "text": "Test quote",
                    "section": "architecture",
                    "level": "advanced",
                    "lang": "en",
                    "origin": "human",
                }
            ],
        }
        validate(instance=root, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
