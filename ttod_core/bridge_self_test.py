"""
Bridge round-trip runner — separated from bridge.py so transport layer has no write imports.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from ttod_core.bridge import TEST_REVIEWER_ID, TTODBridge
from ttod_core.repository import TTODRepository


def run_bridge_self_test(fixture_path: Path, ttod_path: Path) -> Dict[str, Any]:
    """
    Quote-out → proposal-in → human accept round-trip on disposable copies.

    Requires a disposable ttod.yml path; never the live repository root file.
    """
    fixture = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    bridge = TTODBridge()
    quote_out = bridge.export_quote_out(fixture["source_quote"], fixture["snapshot_digest"])
    proposal = bridge.import_proposal_in(fixture["proposal_in"])
    repo = TTODRepository(ttod_path)
    reviewer = fixture.get("test_reviewer_id", TEST_REVIEWER_ID)
    accept_result = repo.accept_proposal(proposal, reviewer)
    return {
        "quote_out_id": quote_out["quote_id"],
        "proposal_id": proposal.proposal_id,
        "accepted_quote_id": accept_result.quote_id,
        "usage_role": quote_out["usage_role"],
        "wpl_record_digest_preserved": proposal.wpl_record_digest
        == fixture["proposal_in"]["wpl_record_digest"],
    }
