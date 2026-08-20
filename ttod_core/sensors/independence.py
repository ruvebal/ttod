"""Independence sensors: sibling quotation, evidence admissibility, shared snapshot."""

from __future__ import annotations

from typing import Any, Dict, List, Set

from ttod_core.sensors.types import (
    FORBIDDEN_SUPPORTS_EDGE,
    SELF_DERIVED_NOT_EVIDENCE,
    SIBLING_OUTPUT_EVIDENCE,
    SNAPSHOT_DIGEST_MISMATCH,
    SensorResult,
)

FORBIDDEN_EDGE_TRIPLES = {
    ("AthanorDraft", "supports", "WPLClaim"),
    ("WPLDraft", "supports", "AthanorDecision"),
}

ATHANOR_PLAN_SOURCE_MARKERS = (
    "athanor/docs/dev_plan/",
    "athanor-phase-2",
    "athanor-plan",
    "athanor phase 2",
)

ARCHITECTURE_CLAIM_DOMAINS = frozenset({"athanor_architecture", "wpl_architecture", "wpl"})


def check_sibling_process_quotation(edge: Dict[str, Any]) -> SensorResult:
    """
    Reject forbidden cross-process supports edges and sibling-only evidence.

    Contract §3 rejected edges:
    - AthanorDraft -> supports -> WPLClaim
    - WPLDraft -> supports -> AthanorDecision
    - TTODQuote(source=AthanorPlan) -> supports -> AthanorDecision
    - quotation whose evidence resolves only to sibling output or TTOD copy
    """
    subject = edge.get("subject_kind", "")
    predicate = edge.get("predicate", "")
    obj = edge.get("object_kind", "")
    triple = (subject, predicate, obj)

    if triple in FORBIDDEN_EDGE_TRIPLES:
        return SensorResult.fail(
            "sibling_process_quotation",
            FORBIDDEN_SUPPORTS_EDGE,
            f"Forbidden supports edge: {subject} -> {predicate} -> {obj}",
            edge=triple,
        )

    if (
        subject == "TTODQuote"
        and edge.get("quote_source_kind") == "AthanorPlan"
        and predicate == "supports"
        and obj == "AthanorDecision"
    ):
        return SensorResult.fail(
            "sibling_process_quotation",
            FORBIDDEN_SUPPORTS_EDGE,
            "TTODQuote sourced from AthanorPlan cannot support AthanorDecision",
        )

    resolution = edge.get("evidence_resolution", {})
    resolves_only_to = resolution.get("resolves_only_to")
    if resolves_only_to in {"sibling_output", "ttod_copy"}:
        return SensorResult.fail(
            "sibling_process_quotation",
            SIBLING_OUTPUT_EVIDENCE,
            f"Evidence resolves only to {resolves_only_to}",
            evidence_resolution=resolution,
        )

    return SensorResult.ok("sibling_process_quotation", "Edge admissible")


def _quote_ancestry_points_to_athanor_plan(quote: Dict[str, Any]) -> bool:
    """Detect Athanor-plan derivation from ancestry fields — no quote-ID special casing."""
    source = str(quote.get("source", "")).lower()
    lesson = str(quote.get("lesson", "")).lower()
    teaches = str(quote.get("teaches", "")).lower()

    if any(marker in source for marker in ATHANOR_PLAN_SOURCE_MARKERS):
        return True
    if "athanor" in lesson and "phase" in lesson:
        return True

    for ref_list in (
        quote.get("immediate_parent_refs") or [],
        quote.get("root_source_refs") or [],
    ):
        for ref in ref_list:
            ref_lower = str(ref).lower()
            if any(marker in ref_lower for marker in ATHANOR_PLAN_SOURCE_MARKERS):
                return True

    if "athanor phase 2" in teaches:
        return True

    return False


def check_evidence_admissibility(claim_domain: str, quote: Dict[str, Any]) -> SensorResult:
    """
    Determine whether a quote may serve as evidence for a claim.

    arch-052-shaped records (Athanor Phase 2 plan ancestry) are pedagogically valid
    but inadmissible as evidence for Athanor/WPL architecture claims.
    """
    domain = claim_domain.lower()
    derived_from_plan = _quote_ancestry_points_to_athanor_plan(quote)

    if domain in ARCHITECTURE_CLAIM_DOMAINS and derived_from_plan:
        return SensorResult.fail(
            "evidence_admissibility",
            SELF_DERIVED_NOT_EVIDENCE,
            "Quote derived from Athanor plan cannot corroborate Athanor/WPL architecture claims",
            evidence_admissible=False,
            independence_reason=SELF_DERIVED_NOT_EVIDENCE,
            claim_domain=claim_domain,
            quote_id=quote.get("id"),
        )

    return SensorResult.ok(
        "evidence_admissibility",
        "Evidence admissible for claim domain",
        evidence_admissible=True,
        independence_reason=None,
        claim_domain=claim_domain,
    )


def check_shared_snapshot_equality(
    digest_a: str,
    digest_b: str,
    *,
    claimed_equal: bool = True,
) -> SensorResult:
    """Compare snapshot digests byte-for-byte — not fuzzy content similarity."""
    equal = digest_a == digest_b
    if claimed_equal and not equal:
        return SensorResult.fail(
            "shared_snapshot_equality",
            SNAPSHOT_DIGEST_MISMATCH,
            "Claimed-equal snapshots have different digests",
            digest_a=digest_a,
            digest_b=digest_b,
        )
    if not claimed_equal and equal:
        return SensorResult.fail(
            "shared_snapshot_equality",
            SNAPSHOT_DIGEST_MISMATCH,
            "Snapshots claimed different but digests match",
            digest_a=digest_a,
            digest_b=digest_b,
        )
    return SensorResult.ok(
        "shared_snapshot_equality",
        "Snapshot digest comparison matches claim",
        digests_equal=equal,
    )
