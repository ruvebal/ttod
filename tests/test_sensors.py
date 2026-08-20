"""
Q5 policy sensor tests — one positive + one negative fixture per sensor.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ttod_core.repository import RepositoryError, TTODRepository
from ttod_core.sensors import (
    SELF_DERIVED_NOT_EVIDENCE,
    check_digest_transfer,
    check_evidence_admissibility,
    check_higher_law_erasure,
    check_human_acceptance,
    check_immutable_id_lifecycle,
    check_observed_declared_generation,
    check_rights_public_export,
    check_shared_snapshot_equality,
    check_sibling_process_quotation,
    reject_ordinary_deletion,
)
from ttod_core.sensors.types import (
    DIGEST_MISMATCH,
    DUPLICATE_CANONICAL_ID,
    FORBIDDEN_SUPPORTS_EDGE,
    GENERATION_METHOD_MISMATCH,
    MISSING_HUMAN_ACCEPTANCE,
    ORDINARY_DELETION_FORBIDDEN,
    RIGHTS_BLOCK_PUBLIC_EXPORT,
    SNAPSHOT_DIGEST_MISMATCH,
)

FIXTURES = Path(__file__).parent / "fixtures"
Q3_FIXTURE = FIXTURES / "q3_minimal_ttod.yml"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class TestSiblingProcessQuotation(unittest.TestCase):
    def test_negative_athanor_wpl_edge(self):
        edge = _load("q5_sibling_negative_athanor_wpl.json")
        result = check_sibling_process_quotation(edge)
        self.assertFalse(result.passed)
        self.assertEqual(result.code, FORBIDDEN_SUPPORTS_EDGE)

    def test_positive_ahmes_edge(self):
        edge = _load("q5_sibling_positive_ahmes.json")
        result = check_sibling_process_quotation(edge)
        self.assertTrue(result.passed)


class TestEvidenceAdmissibility(unittest.TestCase):
    def test_arch052_inadmissible_for_athanor_architecture(self):
        data = _load("q5_admissibility_negative_arch052.json")
        result = check_evidence_admissibility(data["claim_domain"], data["quote"])
        self.assertFalse(result.passed)
        self.assertEqual(result.code, SELF_DERIVED_NOT_EVIDENCE)
        self.assertFalse(result.details["evidence_admissible"])
        self.assertEqual(result.details["independence_reason"], SELF_DERIVED_NOT_EVIDENCE)
        self.assertEqual(data["quote"]["id"], "arch-052")

    def test_arch052_admissible_for_pedagogical_domain(self):
        data = _load("q5_admissibility_positive_pedagogical.json")
        result = check_evidence_admissibility(data["claim_domain"], data["quote"])
        self.assertTrue(result.passed)
        self.assertTrue(result.details["evidence_admissible"])


class TestRightsPublicExport(unittest.TestCase):
    def test_negative_restricted(self):
        data = _load("q5_rights_negative_restricted.json")
        result = check_rights_public_export(data["quote"])
        self.assertFalse(result.passed)
        self.assertEqual(result.code, RIGHTS_BLOCK_PUBLIC_EXPORT)

    def test_negative_unresolved(self):
        data = _load("q5_rights_negative_unresolved.json")
        result = check_rights_public_export(data["quote"])
        self.assertFalse(result.passed)

    def test_positive_complete_public_rights(self):
        data = _load("q5_rights_positive_public.json")
        result = check_rights_public_export(data["quote"])
        self.assertTrue(result.passed)


class TestObservedDeclaredGeneration(unittest.TestCase):
    def test_negative_mismatch(self):
        data = _load("q5_generation_negative_mismatch.json")
        result = check_observed_declared_generation(data["proposal"], data["observed_method"])
        self.assertFalse(result.passed)
        self.assertEqual(result.code, GENERATION_METHOD_MISMATCH)

    def test_positive_match(self):
        data = _load("q5_generation_positive_match.json")
        result = check_observed_declared_generation(data["proposal"], data["observed_method"])
        self.assertTrue(result.passed)


class TestHumanAcceptance(unittest.TestCase):
    def test_negative_active_blackbox_without_review(self):
        data = _load("q5_human_acceptance_negative_blackbox.json")
        result = check_human_acceptance(data["quote"])
        self.assertFalse(result.passed)
        self.assertEqual(result.code, MISSING_HUMAN_ACCEPTANCE)

    def test_positive_validated_blackbox(self):
        data = _load("q5_human_acceptance_positive_validated.json")
        result = check_human_acceptance(data["quote"])
        self.assertTrue(result.passed)


class TestImmutableIdLifecycle(unittest.TestCase):
    def test_negative_duplicate_ids(self):
        data = _load("q5_lifecycle_negative_duplicate_id.json")
        result = check_immutable_id_lifecycle(data["quotes"])
        self.assertFalse(result.passed)
        self.assertEqual(result.code, DUPLICATE_CANONICAL_ID)

    def test_positive_deprecated_retirement(self):
        data = _load("q5_lifecycle_positive_deprecated.json")
        result = check_immutable_id_lifecycle(data["quotes"])
        self.assertTrue(result.passed)


class TestHigherLawErasure(unittest.TestCase):
    def test_negative_ordinary_deletion_forbidden(self):
        data = _load("q5_erasure_negative_ordinary_delete.json")
        result = reject_ordinary_deletion(operation=data["operation"])
        self.assertFalse(result.passed)
        self.assertEqual(result.code, ORDINARY_DELETION_FORBIDDEN)

    def test_positive_authorized_tombstone(self):
        data = _load("q5_erasure_positive_tombstone.json")
        result = check_higher_law_erasure(
            data["quote"],
            authority=data["authority"],
            decision_ref=data["decision_ref"],
        )
        self.assertTrue(result.passed)

    def test_repository_has_no_delete_path(self):
        """Repository exposes erase, not delete — ordinary deletion unavailable."""
        repo = TTODRepository(Q3_FIXTURE)
        self.assertFalse(hasattr(repo, "delete_quote"))
        self.assertTrue(hasattr(repo, "erase_quote"))


class TestDigestTransfer(unittest.TestCase):
    def test_negative_tampered_digest(self):
        data = _load("q5_digest_negative_tampered.json")
        result = check_digest_transfer(data["quote"])
        self.assertFalse(result.passed)
        self.assertEqual(result.code, DIGEST_MISMATCH)

    def test_positive_valid_digest(self):
        data = _load("q5_digest_positive_valid.json")
        result = check_digest_transfer(data["quote"])
        self.assertTrue(result.passed)


class TestSharedSnapshotEquality(unittest.TestCase):
    def test_negative_different_digests_claimed_equal(self):
        data = _load("q5_snapshot_negative_different.json")
        result = check_shared_snapshot_equality(
            data["digest_a"],
            data["digest_b"],
            claimed_equal=data["claimed_equal"],
        )
        self.assertFalse(result.passed)
        self.assertEqual(result.code, SNAPSHOT_DIGEST_MISMATCH)

    def test_positive_equal_digests(self):
        data = _load("q5_snapshot_positive_equal.json")
        result = check_shared_snapshot_equality(
            data["digest_a"],
            data["digest_b"],
            claimed_equal=data["claimed_equal"],
        )
        self.assertTrue(result.passed)


class TestErasureRepositoryIntegration(unittest.TestCase):
    """Authorized erasure via Q3 repository on disposable copy."""

    def test_erase_produces_valid_tombstone(self):
        import shutil

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ttod-test.yml"
            shutil.copy(Q3_FIXTURE, path)
            repo = TTODRepository(path)
            repo.erase_quote(
                "arch-001",
                authority="test-fixture-authority-q5-NOT-HUMAN",
                decision_ref="REF-Q5-FIXTURE-001",
            )
            root = repo.load()
            erased = next(q for q in root["quotes"] if q["id"] == "arch-001")
            result = check_higher_law_erasure(
                erased,
                authority="test-fixture-authority-q5-NOT-HUMAN",
                decision_ref="REF-Q5-FIXTURE-001",
            )
            self.assertTrue(result.passed)
            self.assertIn("REDACTED", erased["text"])


if __name__ == "__main__":
    unittest.main()
