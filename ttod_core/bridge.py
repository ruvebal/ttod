"""
TTOD Bridge — Phase Q4 transport layer.

Serialization adapter over Q3 proposal/accept surfaces. Adds NO canonical write
capability, ID allocation, or TTODRepository import.
"""

from __future__ import annotations

import inspect
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ttod_core.canonical import Canonicalizer
from ttod_core.proposals import Proposal, ProposalStatus, ReviewActivity, ReviewActivityType
from ttod_core.validation import TTODValidator

CONTRACT_VERSION = "1.0.0"
TEST_REVIEWER_ID = "test-fixture-reviewer-q4-NOT-HUMAN"

_CANONICAL_ID_PATTERN = re.compile(r"^[a-z]+-\d+$")
_UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


class BridgeError(Exception):
    """Bridge adapter error."""


def field_mapping_coverage() -> Dict[str, str]:
    """
    Mapping from quote.schema.json fields to transport fields or documented exclusions.

    Used by tests to prove no silent drops.
    """
    return {
        "id": "quote_id",
        "schema_version": "excluded (contract_version in transfer_metadata)",
        "content_digest": "content_digest",
        "text": "text",
        "section": "section",
        "subsection": "subsection",
        "level": "level",
        "tags": "tags",
        "teaches": "teaches",
        "show_when": "show_when",
        "origin": "origin",
        "authorship_assertion": "excluded (not in transport v1)",
        "validation": "validation",
        "source_refs": "source_refs",
        "evidence_snapshot_digest": "evidence_snapshot_digest",
        "wpl_record_id": "wpl_record_id",
        "wpl_record_digest": "wpl_record_digest",
        "rights": "rights",
        "related": "related",
        "relation_edges": "relation_edges",
        "status": "status",
        "deprecated_by": "deprecated_by",
        "superseded_by": "superseded_by",
        "reason": "reason",
        "effective_at": "effective_at",
        "immediate_parent_refs": "immediate_parent_refs",
        "root_source_refs": "root_source_refs",
        "proposal_id": "proposal_id",
        "lesson": "excluded (legacy field; not in transport v1)",
        "source": "excluded (legacy field; not in transport v1)",
        "created_at": "created_at",
    }


def quote_schema_property_names(schema_dir: Optional[Path] = None) -> Set[str]:
    """Load property names from quote.schema.json."""
    root = schema_dir or Path(__file__).parent.parent / "schema"
    with open(root / "quote.schema.json", encoding="utf-8") as handle:
        schema = json.load(handle)
    return set(schema.get("properties", {}).keys())


def assert_field_mapping_complete(schema_dir: Optional[Path] = None) -> None:
    """Raise BridgeError if any quote.schema property lacks mapping documentation."""
    schema_props = quote_schema_property_names(schema_dir)
    mapping = field_mapping_coverage()
    missing = schema_props - set(mapping.keys())
    if missing:
        raise BridgeError(f"quote.schema properties missing from field_mapping_coverage: {sorted(missing)}")


def assert_no_canonical_write_imports() -> None:
    """Prove bridge module cannot import TTODRepository write paths."""
    import ast

    import ttod_core.bridge as bridge_module

    tree = ast.parse(inspect.getsource(bridge_module))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if "repository" in node.module or node.module.startswith("ttod_core.repository"):
                raise BridgeError(f"bridge module must not import from {node.module}")
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("ttod_core.repository"):
                    raise BridgeError(f"bridge module must not import {alias.name}")


class QuoteOutAdapter:
    """Canonical quote → quote-out transport payload."""

    TRANSPORT_FIELDS = {
        "quote_id",
        "text",
        "content_digest",
        "snapshot_digest",
        "origin",
        "usage_role",
        "section",
        "subsection",
        "level",
        "tags",
        "teaches",
        "show_when",
        "validation",
        "rights",
        "related",
        "relation_edges",
        "status",
        "deprecated_by",
        "superseded_by",
        "reason",
        "effective_at",
        "immediate_parent_refs",
        "root_source_refs",
        "proposal_id",
        "source_refs",
        "evidence_snapshot_digest",
        "wpl_record_id",
        "wpl_record_digest",
        "created_at",
        "transfer_metadata",
    }

    def to_transport(
        self,
        quote: Dict[str, Any],
        snapshot_digest: str,
        transfer_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if "id" not in quote:
            raise BridgeError("Quote missing required field: id")

        mapping = field_mapping_coverage()
        transport: Dict[str, Any] = {
            "usage_role": "pedagogical",
            "snapshot_digest": snapshot_digest,
            "transfer_metadata": {
                "transfer_id": transfer_id or str(uuid.uuid4()),
                "exported_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "exporter_version": "3.0.0",
                "contract_version": CONTRACT_VERSION,
            },
        }

        for schema_field, transport_field in mapping.items():
            if transport_field.startswith("excluded"):
                continue
            if schema_field == "id":
                transport["quote_id"] = quote["id"]
            elif schema_field in quote:
                transport[transport_field] = quote[schema_field]

        for key in ("tags", "related", "relation_edges", "immediate_parent_refs", "root_source_refs", "source_refs"):
            transport.setdefault(key, quote.get(key, []))

        return transport

    def validate_transport(self, transport: Dict[str, Any]) -> None:
        schema_path = Path(__file__).parent.parent / "schema" / "transport_quote_out_v1.json"
        with open(schema_path, encoding="utf-8") as handle:
            schema = json.load(handle)

        from jsonschema import ValidationError, validate

        try:
            validate(instance=transport, schema=schema)
        except ValidationError as exc:
            raise BridgeError(f"Transport validation failed: {exc.message}") from exc

        if transport.get("usage_role") != "pedagogical":
            raise BridgeError("usage_role must be 'pedagogical'")
        if "id" in transport:
            raise BridgeError("Transport must use quote_id, not id")


class ProposalInAdapter:
    """Proposal-in transport → TTOD Proposal (import only; no accept)."""

    def from_transport(self, transport: Dict[str, Any]) -> Proposal:
        self._validate_transport_schema(transport)

        candidate = dict(transport.get("candidate_content", {}))
        if "id" in candidate:
            raise BridgeError("candidate_content must not contain canonical 'id' field")

        for activity in transport.get("human_review_activities", []):
            if activity.get("activity_type") == "accept":
                raise BridgeError("proposal-in must not carry pre-accept review activities")

        proposer = transport.get("proposer", {})
        proposal = Proposal(
            proposal_id=transport["proposal_id"],
            status=ProposalStatus(transport.get("status", "proposed")),
            candidate_content=candidate,
            proposer_kind=proposer.get("system", "athanor"),
            proposer_id=proposer.get("identity", "athanor-system"),
            generation_method=f"bridge-v{CONTRACT_VERSION}",
            wpl_record_id=transport.get("wpl_record_id"),
            wpl_record_digest=transport.get("wpl_record_digest"),
            evidence_snapshot_id=transport.get("evidence_snapshot_id"),
            evidence_snapshot_digest=transport.get("evidence_snapshot_digest"),
            created_at=transport.get("created_at") or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )

        for raw in transport.get("human_review_activities", []):
            proposal.add_review_activity(
                ReviewActivity(
                    activity_type=ReviewActivityType(raw["activity_type"]),
                    reviewer_id=raw.get("reviewer_id", ""),
                    timestamp=raw.get("timestamp") or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                    comment=raw.get("comment"),
                    decision_reason=raw.get("decision_reason"),
                )
            )

        return proposal

    def to_transport(self, proposal: Proposal) -> Dict[str, Any]:
        """Serialize a TTOD Proposal to proposal-in transport (for outbox simulation)."""
        return {
            "proposal_id": proposal.proposal_id,
            "candidate_content": dict(proposal.candidate_content),
            "proposer": {
                "identity": proposal.proposer_id,
                "system": proposal.proposer_kind,
            },
            "status": proposal.status.value,
            "created_at": proposal.created_at,
            "human_review_activities": [
                {
                    "activity_type": a.activity_type.value,
                    "reviewer_id": a.reviewer_id,
                    "timestamp": a.timestamp,
                    "comment": a.comment,
                    "decision_reason": a.decision_reason,
                }
                for a in proposal.human_review_activities
            ],
            "wpl_record_id": proposal.wpl_record_id,
            "wpl_record_digest": proposal.wpl_record_digest,
            "evidence_snapshot_digest": proposal.evidence_snapshot_digest,
            "transfer_metadata": {
                "transfer_id": str(uuid.uuid4()),
                "received_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "source_system": "ttod",
                "contract_version": CONTRACT_VERSION,
            },
        }

    def _validate_transport_schema(self, transport: Dict[str, Any]) -> None:
        schema_path = Path(__file__).parent.parent / "schema" / "transport_proposal_in_v1.json"
        with open(schema_path, encoding="utf-8") as handle:
            schema = json.load(handle)

        from jsonschema import ValidationError, validate

        try:
            validate(instance=transport, schema=schema)
        except ValidationError as exc:
            raise BridgeError(f"Transport validation failed: {exc.message}") from exc

        proposal_id = transport.get("proposal_id", "")
        if not proposal_id:
            raise BridgeError("proposal_id is required")
        if _CANONICAL_ID_PATTERN.match(proposal_id):
            raise BridgeError("proposal_id must be UUID/URN, not canonical section-number ID")
        if not _UUID_PATTERN.match(proposal_id):
            raise BridgeError("proposal_id must be a UUID in transport v1")


class TTODBridge:
    """Facade for quote-out and proposal-in operations."""

    def __init__(self):
        self.quote_out = QuoteOutAdapter()
        self.proposal_in = ProposalInAdapter()
        self.canonicalizer = Canonicalizer()

    def export_quote_out(self, quote: Dict[str, Any], snapshot_digest: str) -> Dict[str, Any]:
        transport = self.quote_out.to_transport(quote, snapshot_digest)
        self.quote_out.validate_transport(transport)
        return transport

    def import_proposal_in(self, transport: Dict[str, Any]) -> Proposal:
        return self.proposal_in.from_transport(transport)

    def protected_quote_out_fields(self) -> List[str]:
        """Fields that must survive quote-out (excluding transfer_metadata)."""
        return sorted(QuoteOutAdapter.TRANSPORT_FIELDS - {"transfer_metadata", "usage_role"})


def compare_protected_fields(
    before: Dict[str, Any],
    after: Dict[str, Any],
    *,
    ignore: Optional[Set[str]] = None,
) -> List[str]:
    """Return list of field names that differ unexpectedly."""
    ignore = ignore or set()
    mismatches: List[str] = []
    for key in before:
        if key in ignore:
            continue
        if before.get(key) != after.get(key):
            mismatches.append(key)
    return mismatches

