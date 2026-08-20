"""Provenance sensors: generation method and digest transfer."""

from __future__ import annotations

from typing import Any, Dict

from ttod_core.canonical import CanonicalizationError, Canonicalizer
from ttod_core.sensors.types import DIGEST_MISMATCH, GENERATION_METHOD_MISMATCH, SensorResult


def check_observed_declared_generation(
    proposal: Dict[str, Any],
    observed_method: str,
) -> SensorResult:
    """Flag when declared generation_method disagrees with observable evidence."""
    declared = proposal.get("generation_method")
    if declared is None:
        proposer = proposal.get("proposer") or {}
        declared = proposer.get("generation_method")

    if declared != observed_method:
        return SensorResult.fail(
            "observed_declared_generation",
            GENERATION_METHOD_MISMATCH,
            f"Declared '{declared}' != observed '{observed_method}'",
            declared=declared,
            observed=observed_method,
        )

    return SensorResult.ok(
        "observed_declared_generation",
        "Declared generation method matches observation",
        declared=declared,
    )


def check_digest_transfer(quote: Dict[str, Any]) -> SensorResult:
    """Re-assert Q2E digest integrity with adversarial tamper detection."""
    if "content_digest" not in quote:
        return SensorResult.ok("digest_transfer", "No stored digest to verify")

    try:
        Canonicalizer().verify_content_digest(quote)
    except CanonicalizationError as exc:
        return SensorResult.fail(
            "digest_transfer",
            DIGEST_MISMATCH,
            str(exc),
            quote_id=quote.get("id"),
        )

    return SensorResult.ok("digest_transfer", "content_digest verified")
