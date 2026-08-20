"""
TTOD policy sensors (Q5) — adversarial boundary checks.

Each sensor is deterministic, single-purpose, and backed by positive + negative fixtures.
Sensors read/inspect only; they never mutate ttod.yml.
"""

from ttod_core.sensors.types import (
    SELF_DERIVED_NOT_EVIDENCE,
    SensorResult,
    SensorVerdict,
)
from ttod_core.sensors.independence import (
    check_evidence_admissibility,
    check_shared_snapshot_equality,
    check_sibling_process_quotation,
)
from ttod_core.sensors.lifecycle import (
    ERASED_TOMBSTONE_TEXT,
    check_higher_law_erasure,
    check_human_acceptance,
    check_immutable_id_lifecycle,
    reject_ordinary_deletion,
)
from ttod_core.sensors.provenance import check_digest_transfer, check_observed_declared_generation
from ttod_core.sensors.rights import check_rights_public_export

__all__ = [
    "SELF_DERIVED_NOT_EVIDENCE",
    "SensorResult",
    "SensorVerdict",
    "ERASED_TOMBSTONE_TEXT",
    "check_sibling_process_quotation",
    "check_evidence_admissibility",
    "check_rights_public_export",
    "check_observed_declared_generation",
    "check_human_acceptance",
    "check_immutable_id_lifecycle",
    "check_higher_law_erasure",
    "reject_ordinary_deletion",
    "check_digest_transfer",
    "check_shared_snapshot_equality",
]
