# PHASE-Y1-REPORT.md

**Status:** VERIFYING — awaiting cold review
**Runbook:** [`PHASES/Y1-layout-decision.md`](PHASES/Y1-layout-decision.md)
**Decision:** [`DECISIONS/Y1-2026-09-20-AGENTIC-LAYOUT.md`](../DECISIONS/Y1-2026-09-20-AGENTIC-LAYOUT.md)

## Checklist result

- [x] Flat siblings — *adopted from the recommended default*
- [x] `public-docs-i18n` → **pack** — *departs from the default; evidence: skill + a script only it uses*
- [x] Collection `dear_tree` — *adopted from the recommended default*
- [x] `report-steward/` frozen

The product owner delegated the full Y cycle on 2026-09-20; these rows are adopted on that
delegation, not chosen row-by-row, and may be overturned before Y2 merges.

## Reconsidered upcoming phases (from Y0's findings)

- **Y2 is no longer a no-op.** One real move: the script into the pack, with its root constant
  fixed and the landing retargeted; then the legibility test on the final tree.
- **New finding:** `main`'s `agentic/README.md` has been stale since AG2 (says `ide-mcp/` does not
  exist). Y0's rewrite fixes it; the PR should say so.
- Y3/Y4 unchanged.

## Evidence

Negative-control legibility run (old README → 3 contradictions found; new README → none), and
the `git grep` showing the script's only consumer is the skill — both in the decision file.
No file moved in this phase.
