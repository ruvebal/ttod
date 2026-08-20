"""Rights and public-export sensor."""

from __future__ import annotations

from typing import Any, Dict

from ttod_core.canonical import ExportPolicy
from ttod_core.sensors.types import RIGHTS_BLOCK_PUBLIC_EXPORT, SensorResult


def check_rights_public_export(quote: Dict[str, Any], *, public_export: bool = True) -> SensorResult:
    """
    Unresolved or restricted item rights block public export — no override flag.

    Uses ExportPolicy.should_include as the mechanical gate; adds explicit rights
    completeness checks for public-access records.
    """
    if not public_export:
        return SensorResult.ok("rights_public_export", "Non-public export path")

    policy = ExportPolicy(public_export=True, include_restricted=False)
    if not policy.should_include(quote):
        return SensorResult.fail(
            "rights_public_export",
            RIGHTS_BLOCK_PUBLIC_EXPORT,
            "Record blocked from public export by lifecycle/rights policy",
            quote_id=quote.get("id"),
            rights=quote.get("rights"),
            status=quote.get("status", "active"),
        )

    rights = quote.get("rights")
    if rights is None:
        return SensorResult.fail(
            "rights_public_export",
            RIGHTS_BLOCK_PUBLIC_EXPORT,
            "Unresolved rights block public export",
            quote_id=quote.get("id"),
        )

    access = rights.get("access") if isinstance(rights, dict) else None
    if access == "restricted":
        return SensorResult.fail(
            "rights_public_export",
            RIGHTS_BLOCK_PUBLIC_EXPORT,
            "Restricted access blocks public export",
            quote_id=quote.get("id"),
        )

    if access == "public":
        for field in ("license", "holder"):
            if not rights.get(field):
                return SensorResult.fail(
                    "rights_public_export",
                    RIGHTS_BLOCK_PUBLIC_EXPORT,
                    f"Public export requires rights.{field}",
                    quote_id=quote.get("id"),
                )

    return SensorResult.ok("rights_public_export", "Eligible for public export")
