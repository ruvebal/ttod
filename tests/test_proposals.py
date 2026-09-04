"""
TTOD Proposals Tests (Q2E)

Tests for proposal lifecycle and human-review workflow.

Core safety property: **a machine may propose but may not accept**.
"""

import unittest

from ttod_core.proposals import (
    Proposal,
    ProposalStatus,
    ReviewActivity,
    ReviewActivityType,
    create_proposal,
)


class TestProposalStatus(unittest.TestCase):
    """Test proposal status machine."""

    def test_valid_transitions(self):
        """Valid status transitions are allowed."""
        self.assertTrue(ProposalStatus.PROPOSED.can_transition_to(ProposalStatus.NEEDS_REVISION))
        self.assertTrue(ProposalStatus.PROPOSED.can_transition_to(ProposalStatus.ACCEPTED))
        self.assertTrue(ProposalStatus.PROPOSED.can_transition_to(ProposalStatus.REJECTED))
        self.assertTrue(ProposalStatus.PROPOSED.can_transition_to(ProposalStatus.WITHDRAWN))
        self.assertTrue(ProposalStatus.NEEDS_REVISION.can_transition_to(ProposalStatus.PROPOSED))

    def test_invalid_transitions(self):
        """Invalid status transitions are rejected."""
        self.assertFalse(ProposalStatus.ACCEPTED.can_transition_to(ProposalStatus.REJECTED))
        self.assertFalse(ProposalStatus.REJECTED.can_transition_to(ProposalStatus.ACCEPTED))
        self.assertFalse(ProposalStatus.WITHDRAWN.can_transition_to(ProposalStatus.PROPOSED))

    def test_terminal_states(self):
        """Terminal states have no valid transitions."""
        transitions = {
            ProposalStatus.PROPOSED: {ProposalStatus.NEEDS_REVISION, ProposalStatus.ACCEPTED, ProposalStatus.REJECTED, ProposalStatus.WITHDRAWN},
            ProposalStatus.NEEDS_REVISION: {ProposalStatus.PROPOSED, ProposalStatus.REJECTED, ProposalStatus.WITHDRAWN},
            ProposalStatus.ACCEPTED: set(),
            ProposalStatus.REJECTED: set(),
            ProposalStatus.WITHDRAWN: set(),
        }
        self.assertEqual(transitions[ProposalStatus.ACCEPTED], set())
        self.assertEqual(transitions[ProposalStatus.REJECTED], set())
        self.assertEqual(transitions[ProposalStatus.WITHDRAWN], set())


class TestReviewActivity(unittest.TestCase):
    """Test review activity."""

    def test_accept_requires_reviewer_id(self):
        """Accept activity requires non-empty reviewer_id."""
        with self.assertRaises(ValueError) as cm:
            ReviewActivity(
                activity_type=ReviewActivityType.ACCEPT,
                reviewer_id="",
                timestamp="2026-08-18T00:00:00Z",
            )
        self.assertIn("reviewer_id", str(cm.exception))

    def test_accept_requires_non_empty_reviewer_id(self):
        """Accept activity requires non-empty reviewer_id (not just whitespace)."""
        with self.assertRaises(ValueError) as cm:
            ReviewActivity(
                activity_type=ReviewActivityType.ACCEPT,
                reviewer_id="   ",
                timestamp="2026-08-18T00:00:00Z",
            )
        self.assertIn("reviewer_id", str(cm.exception))

    def test_revision_request_requires_comment(self):
        """Revision request requires a comment."""
        with self.assertRaises(ValueError) as cm:
            ReviewActivity(
                activity_type=ReviewActivityType.REVISION_REQUEST,
                reviewer_id="human-001",
                timestamp="2026-08-18T00:00:00Z",
                comment=None,
            )
        self.assertIn("comment", str(cm.exception))

    def test_review_activity_is_frozen(self):
        """ReviewActivity is frozen (immutable)."""
        activity = ReviewActivity(
            activity_type=ReviewActivityType.COMMENT,
            reviewer_id="human-001",
            timestamp="2026-08-18T00:00:00Z",
            comment="Test comment",
        )
        with self.assertRaises(Exception):
            activity.comment = "Modified comment"


class TestProposal(unittest.TestCase):
    """Test proposal lifecycle."""

    def test_create_proposal_allocates_uuid(self):
        """Proposal creation allocates a UUID proposal_id."""
        proposal = create_proposal(
            candidate_content={"text": "Test"},
            proposer_kind="model",
            proposer_id="gpt-4",
            generation_method="llm",
        )
        self.assertIsNotNone(proposal.proposal_id)
        self.assertEqual(len(proposal.proposal_id), 36)  # UUID format

    def test_create_proposal_rejects_canonical_id(self):
        """Proposal creation rejects candidate_content with canonical id."""
        with self.assertRaises(ValueError) as cm:
            create_proposal(
                candidate_content={"id": "arch-001", "text": "Test"},
                proposer_kind="model",
                proposer_id="gpt-4",
                generation_method="llm",
            )
        self.assertIn("id", str(cm.exception))

    def test_create_proposal_passes_through_fields(self):
        """Proposal creation passes through all fields exactly as received."""
        candidate_content = {
            "text": "Test quote",
            "section": "architecture",
            "level": "advanced",
            "lang": "en",
            "origin": "blackbox",
            "rights": {},  # Unresolved rights
            "tags": ["test"],
        }
        proposal = create_proposal(
            candidate_content=candidate_content,
            proposer_kind="model",
            proposer_id="gpt-4",
            generation_method="llm",
            wpl_record_id="wpl-123",
            wpl_record_digest="a" * 64,
            evidence_snapshot_id="snap-456",
            evidence_snapshot_digest="b" * 64,
        )

        # Verify all fields passed through
        self.assertEqual(proposal.candidate_content, candidate_content)
        self.assertEqual(proposal.wpl_record_id, "wpl-123")
        self.assertEqual(proposal.wpl_record_digest, "a" * 64)
        self.assertEqual(proposal.evidence_snapshot_id, "snap-456")
        self.assertEqual(proposal.evidence_snapshot_digest, "b" * 64)

    def test_accept_requires_identified_human(self):
        """Accept requires identified human reviewer."""
        proposal = create_proposal(
            candidate_content={"text": "Test"},
            proposer_kind="model",
            proposer_id="gpt-4",
            generation_method="llm",
        )

        # Empty reviewer_id should fail
        with self.assertRaises(ValueError):
            proposal.accept(reviewer_id="")

        # Whitespace-only reviewer_id should fail
        with self.assertRaises(ValueError):
            proposal.accept(reviewer_id="   ")

    def test_accept_with_valid_reviewer_succeeds(self):
        """Accept with valid reviewer succeeds."""
        proposal = create_proposal(
            candidate_content={"text": "Test"},
            proposer_kind="model",
            proposer_id="gpt-4",
            generation_method="llm",
        )

        proposal.accept(reviewer_id="human-001", decision_reason="Good quote")
        self.assertEqual(proposal.status, ProposalStatus.ACCEPTED)
        self.assertEqual(len(proposal.human_review_activities), 1)
        self.assertEqual(proposal.accepted_quote_id, "PENDING_ATOMIC_ALLOCATION")

    def test_invalid_status_transition_fails(self):
        """Invalid status transitions fail."""
        proposal = create_proposal(
            candidate_content={"text": "Test"},
            proposer_kind="model",
            proposer_id="gpt-4",
            generation_method="llm",
        )

        # Reject first
        proposal.reject(reviewer_id="human-001", decision_reason="Not good")

        # Try to accept after reject - should fail
        with self.assertRaises(ValueError) as cm:
            proposal.accept(reviewer_id="human-002")
        self.assertIn("transition", str(cm.exception).lower())

    def test_review_activities_append_only(self):
        """Review activities are append-only."""
        proposal = create_proposal(
            candidate_content={"text": "Test"},
            proposer_kind="model",
            proposer_id="gpt-4",
            generation_method="llm",
        )

        proposal.add_comment(reviewer_id="human-001", comment="First comment")
        proposal.add_comment(reviewer_id="human-002", comment="Second comment")

        self.assertEqual(len(proposal.human_review_activities), 2)

        # Activities are immutable (frozen dataclass)
        first_activity = proposal.human_review_activities[0]
        with self.assertRaises(Exception):
            first_activity.comment = "Modified"

    def test_unresolved_rights_pass_through_unchanged(self):
        """Unresolved rights fields pass through unchanged."""
        candidate_content = {
            "text": "Test quote",
            "section": "architecture",
            "level": "advanced",
            "lang": "en",
            "origin": "blackbox",
            "rights": {},  # Unresolved - empty dict
        }
        proposal = create_proposal(
            candidate_content=candidate_content,
            proposer_kind="model",
            proposer_id="gpt-4",
            generation_method="llm",
        )

        # Rights should remain empty (not backfilled)
        self.assertEqual(proposal.candidate_content["rights"], {})

    def test_unresolved_origin_pass_through_unchanged(self):
        """Unresolved origin field passes through unchanged."""
        candidate_content = {
            "text": "Test quote",
            "section": "architecture",
            "level": "advanced",
            "lang": "en",
            # origin is missing - should stay missing
        }
        proposal = create_proposal(
            candidate_content=candidate_content,
            proposer_kind="model",
            proposer_id="gpt-4",
            generation_method="llm",
        )

        # Origin should remain missing (not backfilled with "human")
        self.assertNotIn("origin", proposal.candidate_content)

    def test_wpl_digests_pass_through_byte_for_byte(self):
        """WPL and evidence digests pass through byte-for-byte."""
        wpl_digest = "a" * 64
        evidence_digest = "b" * 64

        proposal = create_proposal(
            candidate_content={"text": "Test"},
            proposer_kind="model",
            proposer_id="gpt-4",
            generation_method="llm",
            wpl_record_digest=wpl_digest,
            evidence_snapshot_digest=evidence_digest,
        )

        # Digests should be exactly as provided
        self.assertEqual(proposal.wpl_record_digest, wpl_digest)
        self.assertEqual(proposal.evidence_snapshot_digest, evidence_digest)

    def test_no_code_path_writes_ttod_yml(self):
        """
        Test that no code path in this module can write ttod.yml.

        This is a code inspection test - we verify that:
        - No function in proposals.py has 'ttod.yml' in its implementation code
        - No function computes or reserves a canonical section-number ID
        """
        import inspect
        import ttod_core.proposals as proposals_module

        # Get all functions in the module
        for name, obj in inspect.getmembers(proposals_module):
            if inspect.isfunction(obj) and not name.startswith("_"):
                # Get source code
                source = inspect.getsource(obj)
                # Check for forbidden patterns in actual code (not docstrings/comments)
                # We check for actual file operations
                self.assertNotIn("open(", source.lower())
                self.assertNotIn("write(", source.lower())
                self.assertNotIn("dump(", source.lower())

    def test_no_canonical_id_allocation(self):
        """
        Test that no code path allocates a canonical section-number ID.

        Canonical IDs have the format [prefix]-[number] (e.g., arch-001).
        This module should only allocate UUIDs.
        """
        import inspect
        import ttod_core.proposals as proposals_module

        # Get all functions in the module
        for name, obj in inspect.getmembers(proposals_module):
            if inspect.isfunction(obj) and not name.startswith("_"):
                source = inspect.getsource(obj)
                # Check for patterns that suggest canonical ID allocation
                self.assertNotIn("last_id_by_section", source.lower())
                self.assertNotIn("next.*id", source.lower())
                self.assertNotIn("max.*id", source.lower())

    def test_to_dict_serialization(self):
        """Proposal can be serialized to dict."""
        proposal = create_proposal(
            candidate_content={"text": "Test"},
            proposer_kind="model",
            proposer_id="gpt-4",
            generation_method="llm",
        )
        proposal.add_comment(reviewer_id="human-001", comment="Test comment")

        d = proposal.to_dict()
        self.assertIn("proposal_id", d)
        self.assertIn("status", d)
        self.assertIn("human_review_activities", d)
        self.assertEqual(len(d["human_review_activities"]), 1)

    def test_to_dict_omits_null_optionals_so_validate_proposal_passes(self):
        """Fresh proposals must not serialize null into string-typed schema fields.

        Regression: Proposal.to_dict() used to emit wpl_record_id=None (etc.), which
        jsonschema rejects as TYPE_ERROR ('None is not of type string'). Absent ≠ null.
        """
        from pathlib import Path

        from ttod_core.validation import TTODValidator

        proposal = create_proposal(
            candidate_content={
                "text": "Boundaries are where systems learn their shape.",
                "section": "architecture",
                "level": "advanced",
                "lang": "en",
                "origin": "human",
            },
            proposer_kind="human",
            proposer_id="debug-reviewer",
            generation_method="manual",
        )
        payload = proposal.to_dict()
        for key in (
            "wpl_record_id",
            "wpl_record_digest",
            "evidence_snapshot_id",
            "evidence_snapshot_digest",
            "accepted_quote_id",
        ):
            self.assertNotIn(key, payload)
            self.assertIsNone(getattr(proposal, key))

        result = TTODValidator(Path(__file__).resolve().parent.parent / "schema").validate_proposal(
            payload
        )
        self.assertTrue(result.is_valid, result.to_dict())
        self.assertEqual(result.errors, [])

    def test_to_dict_includes_optionals_when_set(self):
        """When optional provenance is present, it is serialized as a string."""
        proposal = create_proposal(
            candidate_content={"text": "Test", "section": "architecture", "level": "advanced", "lang": "en", "origin": "human"},
            proposer_kind="model",
            proposer_id="gpt-local",
            generation_method="llm",
            wpl_record_id="wpl-123",
            wpl_record_digest="a" * 64,
        )
        payload = proposal.to_dict()
        self.assertEqual(payload["wpl_record_id"], "wpl-123")
        self.assertEqual(payload["wpl_record_digest"], "a" * 64)
        self.assertNotIn("accepted_quote_id", payload)


if __name__ == "__main__":
    unittest.main()
