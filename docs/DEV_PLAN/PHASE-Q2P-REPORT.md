# Phase Q2P Report — proposal and human-review workflow

**Execution date:** 2026-08-18
**State:** DONE
**Mode:** parallel lane (runs alongside Q2V, Q2E)
**Entry:** Q1 DONE (PHASE-Q1-REPORT.md filed 2026-08-18)

## 1. Exact commands and exit codes

```bash
$ . .venv/bin/activate && python -m unittest discover -s tests -p 'test_proposals.py' -v
test_accept_requires_identified_human ... ok
test_accept_with_valid_reviewer_succeeds ... ok
test_create_proposal_allocates_uuid ... ok
test_create_proposal_passes_through_fields ... ok
test_create_proposal_rejects_canonical_id ... ok
test_invalid_status_transition_fails ... ok
test_no_canonical_id_allocation ... ok
test_no_code_path_writes_ttod_yml ... ok
test_review_activities_append_only ... ok
test_to_dict_serialization ... ok
test_unresolved_origin_pass_through_unchanged ... ok
test_unresolved_rights_pass_through_unchanged ... ok
test_wpl_digests_pass_through_byte_for_byte ... ok
test_invalid_transitions ... ok
test_terminal_states ... ok
test_valid_transitions ... ok
test_accept_requires_non_empty_reviewer_id ... ok
test_accept_requires_reviewer_id ... ok
test_review_activity_is_frozen ... ok
test_revision_request_requires_comment ... ok

----------------------------------------------------------------------
Ran 20 tests in 0.001s

OK
```
Exit code: 0

## 2. Proposal ID allocation

**Implementation**: `create_proposal()` allocates a UUID (`str(uuid.uuid4())`) as `proposal_id`.

**No canonical ID allocation**: This module has no function that computes or reserves a canonical section-number ID (e.g., `arch-001`). The `accept()` method sets `accepted_quote_id` to `"PENDING_ATOMIC_ALLOCATION"` as a placeholder for Q3 to fill during the atomic acceptance transaction.

**Test proof**: `test_no_canonical_id_allocation` inspects source code and verifies no patterns suggesting canonical ID allocation (`last_id_by_section`, `next.*id`, `max.*id`).

## 3. Status machine

**Implementation**: `ProposalStatus` enum with explicit transition rules:

- `PROPOSED` → `NEEDS_REVISION | ACCEPTED | REJECTED | WITHDRAWN`
- `NEEDS_REVISION` → `PROPOSED | REJECTED | WITHDRAWN`
- `ACCEPTED` → (terminal)
- `REJECTED` → (terminal)
- `WITHDRAWN` → (terminal)

Invalid transitions (e.g., `REJECTED → ACCEPTED`) are hard errors at the code level via `can_transition_to()` validation.

**Test proof**: `test_valid_transitions`, `test_invalid_transitions`, `test_terminal_states`.

## 4. Append-only review activities

**Implementation**: `ReviewActivity` is a frozen dataclass (`@dataclass(frozen=True)`). Activities are appended to `human_review_activities` list and never mutated or deleted.

**Test proof**: `test_review_activities_append_only` verifies activities are immutable (frozen) and that the list grows with each addition.

## 5. Identified-human acceptance

**Implementation**: `ReviewActivity.__post_init__()` validates that `ACCEPT` activity type requires a non-empty `reviewer_id`. Empty or whitespace-only reviewer_id raises `ValueError`.

**Test proof**: `test_accept_requires_reviewer_id`, `test_accept_requires_non_empty_reviewer_id`, `test_accept_with_valid_reviewer_succeeds`.

**No silent accept**: The `accept()` method does NOT write to `ttod.yml` or allocate a canonical ID. It only marks the proposal as accepted and sets a placeholder `accepted_quote_id`. The atomic acceptance transaction is Q3's responsibility.

## 6. Rights and provenance pass-through

**Implementation**: `create_proposal()` passes through all fields exactly as received:
- `source_refs`, `origin`, `rights`, `related`, ancestry fields are never backfilled or inferred
- `wpl_record_id`/`wpl_record_digest` and `evidence_snapshot_digest` pass through byte-for-byte

**Test proof**: 
- `test_unresolved_rights_pass_through_unchanged` - empty `rights` dict remains empty
- `test_unresolved_origin_pass_through_unchanged` - missing `origin` stays missing
- `test_wpl_digests_pass_through_byte_for_byte` - digests are exactly as provided

## 7. No code path writes ttod.yml

**Implementation**: This module contains no file I/O operations that write to `ttod.yml`. It only models the proposal lifecycle in memory.

**Test proof**: `test_no_code_path_writes_ttod_yml` inspects source code and verifies no `open()`, `write()`, or `dump()` calls in any public function.

## 8. Files touched

**Created:**
- `ttod_core/proposals.py` — proposal lifecycle, status machine, review activities
- `tests/test_proposals.py` — 20 tests covering all invariants

**Modified:**
- `ttod_core/__init__.py` — already created by Q2V, no changes needed

**Forbidden (not touched):**
- `ttod_core/validation.py` — Q2V's file
- `ttod_core/canonical.py` — Q2E's file
- `ttod_core/exporter.py` — Q2E's file
- `cli.py` — Q3's file
- `ttod.yml` — canonical data
- `schema/*.json` — frozen by Q1

## 9. Q1-interface concerns

None escalated. Confirmed that `schema/proposal.schema.json` rejects canonical `id` field via `not` constraint before proceeding.

## 10. Safe resume point for Q3

Q2P is DONE. The proposal workflow library is ready for Q3 to wire into the CLI. Q3 can:
- Import `Proposal`, `ProposalStatus`, `ReviewActivity`, `create_proposal` from `ttod_core.proposals`
- Implement the atomic acceptance transaction that:
  - Takes the repository lock
  - Re-reads the live snapshot
  - Allocates the next unused section ID
  - Validates every root invariant
  - Writes atomically to `ttod.yml`
- Wire proposal commands to CLI with proper human-identity validation

## 11. Gate status

| Gate | Required proof | Status |
| --- | --- | --- |
| Review | Blackbox/mixed proposal without identified human acceptance cannot become active | **GREEN** — accept requires non-empty reviewer_id, tested |
| Capability | Model can propose but cannot accept (module-level proof) | **GREEN** — no code path writes ttod.yml or allocates canonical ID, tested |
