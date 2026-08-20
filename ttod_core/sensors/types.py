"""Shared sensor result types and stable codes."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class SensorVerdict(Enum):
    PASS = "pass"
    FAIL = "fail"


# Independence / evidence codes (contract §3)
SELF_DERIVED_NOT_EVIDENCE = "SELF_DERIVED_NOT_EVIDENCE"
SIBLING_OUTPUT_EVIDENCE = "SIBLING_OUTPUT_EVIDENCE"
FORBIDDEN_SUPPORTS_EDGE = "FORBIDDEN_SUPPORTS_EDGE"

# Rights
RIGHTS_BLOCK_PUBLIC_EXPORT = "RIGHTS_BLOCK_PUBLIC_EXPORT"

# Provenance
GENERATION_METHOD_MISMATCH = "GENERATION_METHOD_MISMATCH"
DIGEST_MISMATCH = "DIGEST_MISMATCH"
SNAPSHOT_DIGEST_MISMATCH = "SNAPSHOT_DIGEST_MISMATCH"

# Lifecycle
MISSING_HUMAN_ACCEPTANCE = "MISSING_HUMAN_ACCEPTANCE"
DUPLICATE_CANONICAL_ID = "DUPLICATE_CANONICAL_ID"
CANONICAL_ID_REUSE = "CANONICAL_ID_REUSE"
SILENT_REMOVAL_FORBIDDEN = "SILENT_REMOVAL_FORBIDDEN"
ORDINARY_DELETION_FORBIDDEN = "ORDINARY_DELETION_FORBIDDEN"
ERASE_AUDIT_INCOMPLETE = "ERASE_AUDIT_INCOMPLETE"
ERASED_CONTENT_RETAINED = "ERASED_CONTENT_RETAINED"
ERASE_UNAUTHORIZED = "ERASE_UNAUTHORIZED"


@dataclass(frozen=True)
class SensorResult:
    """Outcome of a single policy sensor evaluation."""

    sensor: str
    verdict: SensorVerdict
    code: str = "OK"
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.verdict == SensorVerdict.PASS

    @classmethod
    def ok(cls, sensor: str, message: str = "", **details: Any) -> "SensorResult":
        return cls(
            sensor=sensor,
            verdict=SensorVerdict.PASS,
            message=message,
            details=dict(details),
        )

    @classmethod
    def fail(
        cls,
        sensor: str,
        code: str,
        message: str,
        **details: Any,
    ) -> "SensorResult":
        return cls(
            sensor=sensor,
            verdict=SensorVerdict.FAIL,
            code=code,
            message=message,
            details=dict(details),
        )
