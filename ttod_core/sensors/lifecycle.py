"""Lifecycle sensors: human acceptance, immutable ID, higher-law erasure."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ttod_core.sensors.types import (
    CANONICAL_ID_REUSE,
    DUPLICATE_CANONICAL_ID,
    ERASE_AUDIT_INCOMPLETE,
    ERASE_UNAUTHORIZED,
    ERASED_CONTENT_RETAINED,
    MISSING_HUMAN_ACCEPTANCE,
    ORDINARY_DELETION_FORBIDDEN,
    SILENT_REMOVAL_FORBIDDEN,
    SensorResult,
)

ERASED_TOMBSTONE_TEXT = "[REDACTED - legally erased under higher-law authority]"

REVIEWED_ORIGINS = frozenset({"blackbox", "mixed"})


def check_human_acceptance(quote: Dict[str, Any]) -> SensorResult:
    """Blackbox/mixed-origin active quotes require identified human acceptance."""
    status = quote.get("status", "active")
    if status != "active":
        return SensorResult.ok("human_acceptance", f"Non-active status '{status}'")

    origin = quote.get("origin")
    if origin not in REVIEWED_ORIGINS:
        return SensorResult.ok("human_acceptance", f"Origin '{origin}' not subject to review gate")

    validation = quote.get("validation") or {}
    if validation.get("status") != "validated":
        return SensorResult.fail(
            "human_acceptance",
            MISSING_HUMAN_ACCEPTANCE,
            "blackbox/mixed content requires validation.status=validated",
            quote_id=quote.get("id"),
        )

    for field in ("reviewer_id", "activity_id"):
        if not validation.get(field):
            return SensorResult.fail(
                "human_acceptance",
                MISSING_HUMAN_ACCEPTANCE,
                f"Missing validation.{field} for active {origin} quote",
                quote_id=quote.get("id"),
            )

    return SensorResult.ok("human_acceptance", "Human acceptance recorded")


def check_immutable_id_lifecycle(
    quotes: List[Dict[str, Any]],
    *,
    prior_fingerprints: Optional[Dict[str, str]] = None,
    removed_ids: Optional[List[str]] = None,
) -> SensorResult:
    """
    Canonical IDs are unique, never reused with different content, never silently removed.

    prior_fingerprints maps quote_id -> content_digest for reuse detection.
    removed_ids lists IDs removed without deprecation tombstone path.
    """
    seen: Dict[str, str] = {}
    for quote in quotes:
        quote_id = quote.get("id")
        if not quote_id:
            continue
        digest = quote.get("content_digest", quote.get("text", ""))
        if quote_id in seen:
            return SensorResult.fail(
                "immutable_id_deprecation",
                DUPLICATE_CANONICAL_ID,
                f"Duplicate canonical ID: {quote_id}",
                quote_id=quote_id,
            )
        seen[quote_id] = str(digest)

        if prior_fingerprints and quote_id in prior_fingerprints:
            if prior_fingerprints[quote_id] != str(digest):
                return SensorResult.fail(
                    "immutable_id_deprecation",
                    CANONICAL_ID_REUSE,
                    f"Canonical ID reused with different content: {quote_id}",
                    quote_id=quote_id,
                )

    if removed_ids:
        for quote_id in removed_ids:
            quote = next((q for q in quotes if q.get("id") == quote_id), None)
            if quote is None:
                return SensorResult.fail(
                    "immutable_id_deprecation",
                    SILENT_REMOVAL_FORBIDDEN,
                    f"Quote {quote_id} removed without deprecated/erased tombstone",
                    quote_id=quote_id,
                )
            if quote.get("status") not in {"deprecated", "erased"}:
                return SensorResult.fail(
                    "immutable_id_deprecation",
                    SILENT_REMOVAL_FORBIDDEN,
                    f"Quote {quote_id} retired without lifecycle status",
                    quote_id=quote_id,
                    status=quote.get("status"),
                )

    return SensorResult.ok("immutable_id_deprecation", "ID lifecycle rules satisfied")


def reject_ordinary_deletion(*, operation: str) -> SensorResult:
    """Ordinary deletion always fails — positive requirement for erasure sensor suite."""
    if operation == "delete":
        return SensorResult.fail(
            "higher_law_erasure",
            ORDINARY_DELETION_FORBIDDEN,
            "Ordinary deletion is forbidden; use authorized erasure tombstone path",
        )
    return SensorResult.ok("higher_law_erasure", "Operation is not ordinary deletion")


def check_higher_law_erasure(
    quote: Dict[str, Any],
    *,
    authority: Optional[str] = None,
    decision_ref: Optional[str] = None,
) -> SensorResult:
    """
    Validate authorized erasure tombstone shape.

    Erasure replaces public content with a tombstone but retains auditable authority
    metadata. Original personal content must not remain in text/teaches fields.
    """
    if quote.get("status") != "erased":
        if authority or decision_ref:
            return SensorResult.fail(
                "higher_law_erasure",
                ERASE_UNAUTHORIZED,
                "Erasure authority provided but quote is not in erased status",
            )
        return SensorResult.ok("higher_law_erasure", "Quote not in erased state")

    text = quote.get("text", "")
    if text != ERASED_TOMBSTONE_TEXT:
        return SensorResult.fail(
            "higher_law_erasure",
            ERASED_CONTENT_RETAINED,
            "Erased quote must use standard tombstone text; personal content must not remain",
            quote_id=quote.get("id"),
            text_preview=text[:80],
        )

    for content_field in ("teaches", "subsection", "authorship_assertion"):
        value = quote.get(content_field)
        if value and "erasure" not in str(value).lower() and len(str(value)) > 40:
            return SensorResult.fail(
                "higher_law_erasure",
                ERASED_CONTENT_RETAINED,
                f"Field '{content_field}' appears to retain pre-erasure content",
                quote_id=quote.get("id"),
            )

    audit_present = any(
        quote.get(field)
        for field in (
            "erasure_authority",
            "erasure_decision_ref",
            "reason",
            "effective_at",
        )
    )
    if not audit_present:
        return SensorResult.fail(
            "higher_law_erasure",
            ERASE_AUDIT_INCOMPLETE,
            "Erasure tombstone missing auditable authority/decision metadata",
            quote_id=quote.get("id"),
        )

    if authority is not None and not authority.strip():
        return SensorResult.fail(
            "higher_law_erasure",
            ERASE_UNAUTHORIZED,
            "Erasure requires non-empty authority",
        )
    if decision_ref is not None and not decision_ref.strip():
        return SensorResult.fail(
            "higher_law_erasure",
            ERASE_UNAUTHORIZED,
            "Erasure requires non-empty decision reference",
        )

    return SensorResult.ok(
        "higher_law_erasure",
        "Authorized erasure tombstone valid",
        quote_id=quote.get("id"),
    )
