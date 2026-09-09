"""
Q4 bridge tests — transport schema, field mapping, round-trip, capability gate.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from ttod_core.bridge import (
    TEST_REVIEWER_ID,
    TTODBridge,
    assert_field_mapping_complete,
    assert_no_canonical_write_imports,
    field_mapping_coverage,
    quote_schema_property_names,
)
from ttod_core.repository import TTODRepository

FIXTURE = Path(__file__).parent / "fixtures" / "q4_roundtrip.json"
Q3_FIXTURE = Path(__file__).parent / "fixtures" / "q3_minimal_ttod.yml"


class TestFieldMapping(unittest.TestCase):
    def test_every_quote_schema_property_documented(self):
        assert_field_mapping_complete()

    def test_no_silent_drops(self):
        schema_props = quote_schema_property_names()
        mapping = field_mapping_coverage()
        self.assertEqual(schema_props, set(mapping.keys()))


class TestQuoteOut(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.bridge = TTODBridge()

    def test_quote_out_carries_usage_role_pedagogical(self):
        transport = self.bridge.export_quote_out(
            self.fixture["source_quote"],
            self.fixture["snapshot_digest"],
        )
        self.assertEqual(transport["usage_role"], "pedagogical")
        self.assertEqual(transport["quote_id"], "arch-070")
        self.assertEqual(transport["content_digest"], self.fixture["source_quote"]["content_digest"])

    def test_quote_out_preserves_protected_fields(self):
        quote = self.fixture["source_quote"]
        transport = self.bridge.export_quote_out(quote, self.fixture["snapshot_digest"])
        for field in (
            "text",
            "origin",
            "validation",
            "related",
            "wpl_record_id",
            "wpl_record_digest",
            "evidence_snapshot_digest",
        ):
            self.assertEqual(transport.get(field), quote.get(field), field)


class TestProposalIn(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.bridge = TTODBridge()

    def test_proposal_in_preserves_wpl_and_evidence_digests(self):
        transport = self.fixture["proposal_in"]
        proposal = self.bridge.import_proposal_in(transport)
        self.assertEqual(proposal.wpl_record_id, transport["wpl_record_id"])
        self.assertEqual(proposal.wpl_record_digest, transport["wpl_record_digest"])
        self.assertEqual(proposal.evidence_snapshot_digest, transport["evidence_snapshot_digest"])
        self.assertNotIn("id", proposal.candidate_content)

    def test_proposal_in_rejects_pre_accept_activity(self):
        transport = dict(self.fixture["proposal_in"])
        transport["human_review_activities"] = [
            {
                "activity_type": "accept",
                "reviewer_id": "bad",
                "timestamp": "2026-08-18T14:00:00Z",
            }
        ]
        with self.assertRaises(Exception):
            self.bridge.import_proposal_in(transport)


class TestCapabilityGate(unittest.TestCase):
    def test_bridge_has_no_repository_write_imports(self):
        assert_no_canonical_write_imports()


class TestRoundTrip(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.tmp = tempfile.TemporaryDirectory()
        self.ttod_path = Path(self.tmp.name) / "ttod-test.yml"
        shutil.copy(Q3_FIXTURE, self.ttod_path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_full_roundtrip_quote_out_proposal_in_accept(self):
        bridge = TTODBridge()
        quote = self.fixture["source_quote"]

        quote_out = bridge.export_quote_out(quote, self.fixture["snapshot_digest"])
        self.assertEqual(quote_out["usage_role"], "pedagogical")

        proposal = bridge.import_proposal_in(self.fixture["proposal_in"])
        self.assertEqual(
            proposal.wpl_record_digest,
            self.fixture["proposal_in"]["wpl_record_digest"],
        )

        repo = TTODRepository(self.ttod_path)
        reviewer = self.fixture.get("test_reviewer_id", TEST_REVIEWER_ID)
        result = repo.accept_proposal(proposal, reviewer)
        self.assertEqual(result.quote_id, "arch-002")

        root = repo.load()
        accepted = next(q for q in root["quotes"] if q["id"] == "arch-002")
        candidate = self.fixture["proposal_in"]["candidate_content"]
        for field in ("text", "section", "level", "origin", "teaches", "tags"):
            self.assertEqual(accepted.get(field), candidate.get(field), field)

        self.assertEqual(accepted.get("wpl_record_digest"), proposal.wpl_record_digest)
        self.assertEqual(accepted.get("evidence_snapshot_digest"), proposal.evidence_snapshot_digest)
        self.assertEqual(accepted.get("proposal_id"), proposal.proposal_id)


if __name__ == "__main__":
    unittest.main()
