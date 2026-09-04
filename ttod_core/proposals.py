"""
TTOD Proposals and Human-Review Workflow (Q2P)

Proposal lifecycle and human-review gates.

Core safety property: **a machine may propose but may not accept**.

This module:
- Allocates proposal_id (UUID/URN) at creation - NEVER a canonical section-number ID
- Implements explicit status machine (proposed → needs_revision | accepted | rejected | withdrawn)
- Maintains append-only review activities list (never mutated or deleted)
- Requires identified human reviewer for accept transitions
- Passes through rights/origin/provenance fields unmodified
- Preserves WPL/evidence digests byte-for-byte

This module does NOT:
- Write to ttod.yml
- Compute or reserve canonical section-number IDs
- Mutate canonical state
- Backfill or infer missing rights/origin fields
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ProposalStatus(Enum):
    """Proposal status machine - explicit enum, not free-text."""

    PROPOSED = "proposed"
    NEEDS_REVISION = "needs_revision"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

    # Valid transitions
    _TRANSITIONS = {
        PROPOSED: {NEEDS_REVISION, ACCEPTED, REJECTED, WITHDRAWN},
        NEEDS_REVISION: {PROPOSED, REJECTED, WITHDRAWN},
        ACCEPTED: set(),  # Terminal state
        REJECTED: set(),  # Terminal state
        WITHDRAWN: set(),  # Terminal state
    }

    def can_transition_to(self, new_status: "ProposalStatus") -> bool:
        """Check if transition is valid."""
        transitions = {
            ProposalStatus.PROPOSED: {ProposalStatus.NEEDS_REVISION, ProposalStatus.ACCEPTED, ProposalStatus.REJECTED, ProposalStatus.WITHDRAWN},
            ProposalStatus.NEEDS_REVISION: {ProposalStatus.PROPOSED, ProposalStatus.REJECTED, ProposalStatus.WITHDRAWN},
            ProposalStatus.ACCEPTED: set(),
            ProposalStatus.REJECTED: set(),
            ProposalStatus.WITHDRAWN: set(),
        }
        return new_status in transitions.get(self, set())


class ReviewActivityType(Enum):
    """Types of review activities."""

    COMMENT = "comment"
    REVISION_REQUEST = "revision_request"
    ACCEPT = "accept"
    REJECT = "reject"
    WITHDRAW = "withdraw"


@dataclass(frozen=True)
class ReviewActivity:
    """A single review activity - immutable, append-only."""

    activity_type: ReviewActivityType
    reviewer_id: str
    timestamp: str
    comment: Optional[str] = None
    decision_reason: Optional[str] = None

    def __post_init__(self):
        """Validate required fields based on activity type."""
        if self.activity_type == ReviewActivityType.ACCEPT:
            if not self.reviewer_id or self.reviewer_id.strip() == "":
                raise ValueError("Accept activity requires a non-empty reviewer_id")
        if self.activity_type == ReviewActivityType.REVISION_REQUEST and not self.comment:
            raise ValueError("Revision request requires a comment")


@dataclass
class Proposal:
    """A TTOD proposal record."""

    proposal_id: str
    status: ProposalStatus = ProposalStatus.PROPOSED
    candidate_content: Dict[str, Any] = field(default_factory=dict)
    proposer_kind: str = ""
    proposer_id: str = ""
    generation_method: str = ""
    wpl_record_id: Optional[str] = None
    wpl_record_digest: Optional[str] = None
    evidence_snapshot_id: Optional[str] = None
    evidence_snapshot_digest: Optional[str] = None
    human_review_activities: List[ReviewActivity] = field(default_factory=list)
    accepted_quote_id: Optional[str] = None
    created_at: str = ""

    def __post_init__(self):
        """Initialize created_at if not provided."""
        if not self.created_at:
            object.__setattr__(self, "created_at", datetime.utcnow().isoformat() + "Z")

    def add_review_activity(self, activity: ReviewActivity) -> None:
        """
        Append a review activity to the audit trail.

        This is append-only - activities are never mutated or deleted.
        """
        # Validate status transition
        new_status = self._infer_status_from_activity(activity)
        if new_status and not self.status.can_transition_to(new_status):
            raise ValueError(
                f"Invalid status transition: {self.status.value} → {new_status.value}"
            )

        # Append activity
        self.human_review_activities.append(activity)

        # Update status if activity implies a change
        if new_status:
            self.status = new_status

        # Set accepted_quote_id on accept
        if activity.activity_type == ReviewActivityType.ACCEPT:
            # This is a placeholder - Q3 will fill in the actual canonical ID
            # during the atomic acceptance transaction
            self.accepted_quote_id = "PENDING_ATOMIC_ALLOCATION"

    def request_revision(self, reviewer_id: str, comment: str) -> None:
        """Request revision of the proposal."""
        activity = ReviewActivity(
            activity_type=ReviewActivityType.REVISION_REQUEST,
            reviewer_id=reviewer_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            comment=comment,
        )
        self.add_review_activity(activity)

    def accept(self, reviewer_id: str, decision_reason: Optional[str] = None) -> None:
        """
        Accept the proposal with identified human reviewer.

        This marks the proposal as accepted but does NOT:
        - Write to ttod.yml
        - Allocate a canonical section-number ID
        - Mutate canonical state

        The atomic acceptance transaction is Q3's responsibility.
        """
        activity = ReviewActivity(
            activity_type=ReviewActivityType.ACCEPT,
            reviewer_id=reviewer_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            comment=decision_reason,
            decision_reason=decision_reason,
        )
        self.add_review_activity(activity)

    def reject(self, reviewer_id: str, decision_reason: Optional[str] = None) -> None:
        """Reject the proposal."""
        activity = ReviewActivity(
            activity_type=ReviewActivityType.REJECT,
            reviewer_id=reviewer_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            decision_reason=decision_reason,
        )
        self.add_review_activity(activity)

    def withdraw(self, reviewer_id: str, decision_reason: Optional[str] = None) -> None:
        """Withdraw the proposal."""
        activity = ReviewActivity(
            activity_type=ReviewActivityType.WITHDRAW,
            reviewer_id=reviewer_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            decision_reason=decision_reason,
        )
        self.add_review_activity(activity)

    def add_comment(self, reviewer_id: str, comment: str) -> None:
        """Add a comment to the proposal."""
        activity = ReviewActivity(
            activity_type=ReviewActivityType.COMMENT,
            reviewer_id=reviewer_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            comment=comment,
        )
        self.add_review_activity(activity)

    def _infer_status_from_activity(self, activity: ReviewActivity) -> Optional[ProposalStatus]:
        """Infer new status from activity type."""
        mapping = {
            ReviewActivityType.REVISION_REQUEST: ProposalStatus.NEEDS_REVISION,
            ReviewActivityType.ACCEPT: ProposalStatus.ACCEPTED,
            ReviewActivityType.REJECT: ProposalStatus.REJECTED,
            ReviewActivityType.WITHDRAW: ProposalStatus.WITHDRAWN,
        }
        return mapping.get(activity.activity_type)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict.

        Optional provenance fields that are unset are omitted (absent), never
        serialized as JSON null — proposal.schema.json types them as string,
        so null fails validate_proposal().
        """
        payload: Dict[str, Any] = {
            "proposal_id": self.proposal_id,
            "status": self.status.value,
            "candidate_content": self.candidate_content,
            "proposer_kind": self.proposer_kind,
            "proposer_id": self.proposer_id,
            "generation_method": self.generation_method,
            "human_review_activities": [
                {
                    key: value
                    for key, value in {
                        "activity_type": a.activity_type.value,
                        "reviewer_id": a.reviewer_id,
                        "timestamp": a.timestamp,
                        "comment": a.comment,
                        "decision_reason": a.decision_reason,
                    }.items()
                    if value is not None
                }
                for a in self.human_review_activities
            ],
            "created_at": self.created_at,
        }
        optional = {
            "wpl_record_id": self.wpl_record_id,
            "wpl_record_digest": self.wpl_record_digest,
            "evidence_snapshot_id": self.evidence_snapshot_id,
            "evidence_snapshot_digest": self.evidence_snapshot_digest,
            "accepted_quote_id": self.accepted_quote_id,
        }
        for key, value in optional.items():
            if value is not None:
                payload[key] = value
        return payload


def create_proposal(
    candidate_content: Dict[str, Any],
    proposer_kind: str,
    proposer_id: str,
    generation_method: str,
    wpl_record_id: Optional[str] = None,
    wpl_record_digest: Optional[str] = None,
    evidence_snapshot_id: Optional[str] = None,
    evidence_snapshot_digest: Optional[str] = None,
) -> Proposal:
    """
    Create a new proposal with a UUID proposal_id.

    This function:
    - Allocates a UUID proposal_id (NEVER a canonical section-number ID)
    - Does NOT write to ttod.yml
    - Does NOT compute or reserve a canonical ID
    - Passes through all fields exactly as received
    """
    # Ensure candidate_content does not contain a canonical id
    if "id" in candidate_content:
        raise ValueError(
            "candidate_content must not contain a canonical 'id' field. "
            "Use proposal_id instead."
        )

    proposal = Proposal(
        proposal_id=str(uuid.uuid4()),
        candidate_content=candidate_content,
        proposer_kind=proposer_kind,
        proposer_id=proposer_id,
        generation_method=generation_method,
        wpl_record_id=wpl_record_id,
        wpl_record_digest=wpl_record_digest,
        evidence_snapshot_id=evidence_snapshot_id,
        evidence_snapshot_digest=evidence_snapshot_digest,
    )

    return proposal
