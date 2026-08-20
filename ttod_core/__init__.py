"""
TTOD Core — validation, canonicalization, and proposal handling.

This package provides the core library modules for TTOD v3:
- validation: strict validation and invariant engine (Q2V)
- canonical: TTOD-C14N-v1 canonicalization and digest computation (Q2E)
- proposals: proposal and human-review workflow (Q2P)
"""

__version__ = "3.0.0"

from ttod_core.sensors import check_evidence_admissibility  # noqa: F401 — public Q5 surface
from ttod_core.bridge import TTODBridge  # noqa: F401 — public Q4 surface
from ttod_core.repository import TTODRepository  # noqa: F401 — public Q3 surface
