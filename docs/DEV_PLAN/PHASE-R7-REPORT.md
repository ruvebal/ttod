# Phase R7 Report — continuous testing strategy

**Status: PARTIAL**

R7 has begun on schedule. Backend contracts, governance fixtures, calibration, R4 layout helpers,
and the currently landed R5 terminal behavior have test coverage. The closing gate is intentionally
not claimed: R3b/R4/R5 are not all DONE, Chromium E2E/a11y and CI timing remain outstanding.

## Current evidence

- `tests/test_r7_platform.py` asserts endpoint shapes, rights/lifecycle exclusion, byte-identical
  graph responses, creative citation absence, and disposable proposal governance.
- Calibration used live `nomic-embed-text`: two in-domain queries scored 0.667506770/0.793541377;
  two out-of-domain queries scored 0.508748309/0.529375182. At 0.575 all four expected verdicts pass.
- `r_negative_oracle_propose_no_active.json` drives a real request against a disposable proposal
  directory and asserts proposed/blackbox with no canonical or accepted ID.
- Existing R1 tests cover unavailable MCP fail-closed behavior; R1's report records a successful
  live Streamable HTTP `/mcp` call. A reusable R7-owned live-stack transport harness remains due.
- R4 has deterministic join/filter/layout tests. R5 currently has SSE boundary tests and Testing
  Library coverage for creative disclosure, explicit-only proposal, live `?tag=` submit context,
  grounded citations, and offline queueing.
- The first full `npx vitest run` exposed an R4 test-runner integration defect: its Node test file
  matches Vitest discovery and makes Vitest fail after the assertions pass. This was reported to
  the R4/integration owner rather than patched from R7.

## Remaining gates

R3b route/a11y integration, hydrated R4 interaction, assembled-app Chromium Playwright with axe,
R7-owned live R1→R2 harness, and measured sharded CI wall time. Closing cold review also waits for
the assembled suite. `docs/testing-strategy.md` records the agreed test layers and CI ownership.

## Files touched

- `tests/fixtures/r_oracle_threshold_calibration.json`
- `tests/fixtures/r_negative_oracle_propose_no_active.json`
- `tests/test_r7_platform.py`
- `docs/testing-strategy.md`
- `docs/DEV_PLAN/PHASE-R7-REPORT.md`

## Structural findings / safe resume

The live MCP transport proof currently lives in R1 execution evidence rather than a repeatable
R7 harness; do not confuse Compose wiring with that proof. Continue pairing as R3b/R4/R5 reports
close, then add Chromium-only Playwright+axe, run the full contract suite, measure wall time, cold
review, and only then consider DONE.
