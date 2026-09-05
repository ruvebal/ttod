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

## 2026-09-05 closure-audit pass — Chromium/axe E2E suite added and run live

R3b, R4, and R5 are now all `DONE` (reference build), so the closing E2E/a11y gate itself no
longer needs to wait — only the CI-wall-clock gate does (it needs R6's workflow files, which
remain deliberately unimplemented, see
[`DECISIONS/R6-DEFERRED-STUDENT-OWNED.md`](DECISIONS/R6-DEFERRED-STUDENT-OWNED.md)). This pass
built `services/frontend/playwright.config.ts` (chromium project only, per §2.2) and
`services/frontend/e2e/i18n-routes.spec.ts`, folding `@axe-core/playwright` into the same specs
rather than a separate audit, and ran it against a genuinely live local stack — not mocks:

- **MCP** (`services/mcp/server.py`) and **backend** (`uvicorn services.backend.app.main:app`) run
  bare-metal on this machine (Tanit), `OLLAMA_BASE_URL=http://localhost:11434`,
  `OLLAMA_MODEL=qwen3.8:27b`, `OLLAMA_EMBED_MODEL=nomic-embed-text` — both already pulled.
- **Frontend** built (`npm run build`) with a local-only `services/frontend/.env`
  (`BACKEND_URL=http://localhost:8000`, gitignored via the existing `.env*` pattern) and served via
  `node ./dist/server/entry.mjs`. This surfaced a real, previously-undocumented finding: with
  `output: 'server'`, Astro/Vite still inline `import.meta.env.BACKEND_URL` at **build** time, not
  read it at server-start time — the variable must be present in `.env` (or the shell) *before*
  `astro build`, exporting it only before `node entry.mjs` has no effect. Worth carrying into
  `R3a-ONBOARDING.md` or the cohort-starter's own README so students don't hit the same "fetch
  failed to `http://backend:8000`" trap.
- `npx playwright install chromium` — installed Chrome for Testing 153.0.8010.12 (playwright
  chromium v1243); no prior working install existed in this environment.

**First run: 8 of 15 tests failed.** Every failure was the same real axe violation —
`landmark-one-main` ("Document does not have a main landmark") — on `/en/` and `/es/` (R3a's
hello-world), `/{locale}/quote` (R3a), `/{locale}/graph` (R4), and `/{locale}/oracle` (R5).
`Page.astro`'s `<body>` is just `<slot />` with no wrapping landmark, and only R3b's own
`wisdom`/`docs` pages had independently wrapped their content in `<main class="ttod-shell">` —
R3a/R4/R5 had not. This is exactly the class of defect the R7 runbook's cold-review discipline
exists to catch (a real test, not code-reading, found it) — **fixed** by wrapping each affected
page's content in `<main>` (`src/pages/en/index.astro`, `src/pages/es/index.astro`,
`src/pages/[locale]/quote.astro`, `src/pages/[locale]/graph.astro`,
`src/pages/[locale]/oracle.astro`), rebuilt, re-ran: **15/15 passed, wall-clock 3.1s** (`8 workers`,
Playwright's own summary line: `11.98s user 2.89s system 412% cpu 3.605 total`).

**What this suite actually proves, precisely so it isn't overclaimed:** default-locale fallback
(`/` → `/en/`), both locales' `<html lang>` resolving correctly, zero axe violations on `/`,
`/quote`, `/wisdom`, `/docs`, `/graph`, `/oracle` for both `en`/`es`, and `/quote` genuinely
round-tripping a live sample through backend→`ttod_core` (not a fixture). **What it does not yet
cover**, so a future session doesn't assume it does: R4's `?tag=<slug>` URL-sync-across-islands
test, R5's SSE-streaming-state and creative-vs-grounded-disclosure test, and the nightly
R1↔R2-live-transport contract harness this report already flagged as due — those interaction-level
tests remain unwritten, only the shells' initial render and static routing are proven here.

## Remaining gates

R4's `?tag=` URL-sync test, R5's SSE-streaming/mode-disclosure test, R7's own live R1→R2 transport
harness, and **measured sharded CI wall time — genuinely blocked on R6's CI workflow files, which
remain deliberately unimplemented** (not a testing gap, a scope boundary; see the R6 decision
record). Closing cold review also waits for those. `docs/testing-strategy.md` records the agreed
test layers and CI ownership.

**Status stays PARTIAL** — not because the E2E/a11y gate is unfinished (it now passes, 15/15,
against the live stack), but because the CI-wall-clock gate structurally cannot be honestly closed
without R6, and the interaction-level R4/R5 tests above remain unwritten. Promoting to `DONE` would
require either those tests plus a genuine CI measurement (which needs R6) — this report does not
pretend otherwise.

## Files touched

- `tests/fixtures/r_oracle_threshold_calibration.json`
- `tests/fixtures/r_negative_oracle_propose_no_active.json`
- `tests/test_r7_platform.py`
- `docs/testing-strategy.md`
- `docs/DEV_PLAN/PHASE-R7-REPORT.md`
- `services/frontend/playwright.config.ts` (new)
- `services/frontend/e2e/i18n-routes.spec.ts` (new)
- `services/frontend/src/pages/en/index.astro`, `es/index.astro`,
  `[locale]/quote.astro`, `[locale]/graph.astro`, `[locale]/oracle.astro` (added `<main>` landmark)

## Structural findings / safe resume

The live MCP transport proof currently lives in R1 execution evidence rather than a repeatable
R7 harness; do not confuse Compose wiring with that proof. The `landmark-one-main` defect above
was structural (spanned three lanes' pages, not one) and has been fixed and re-verified live, not
just patched and assumed correct. Remaining resume work: R4's URL-sync test, R5's streaming/mode
tests, the R1↔R2 live-transport harness, and — only once R6 exists — the sharded CI wall-clock
measurement and closing cold review before `DONE` can be honestly claimed.
