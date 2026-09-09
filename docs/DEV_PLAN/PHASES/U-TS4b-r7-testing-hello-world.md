<!--
Self-contained runbook. Derived from PHASE-U-FEII-TEACHING-SKELETON-CASCADE.md §2, §5 TS4,
PHASES/R7-testing-strategy.md, and PHASE-U-WEEK0-ORCHESTRATION.md — that orchestration document is
normative; regenerate this one if it changes. Generated as part of the Week-0 skeleton-generator
pass.
-->

# Phase U · TS4b — R7 testing hello-world seam

**Mode:** continuous, cross-cutting — starts the moment TS1 lands, does not wait for TS3a/b/c or
TS4a to finish (same "start immediately" design as the rich-reference R7 runbook)
**Entry:** TS1 `DONE` (the CI skeleton this lane plugs test content into must exist)
**Exit:** one unit test, one component test, one route/contract smoke test, one accessibility
assertion — wired into TS1's CI skeleton, not a comprehensive suite

---

## 0. What this phase is, and how it differs from the rich-reference R7 runbook

`PHASES/R7-testing-strategy.md` targets the assembled rich reference: Playwright E2E across the
*whole* app, full contract-test coverage, measured CI wall-clock time as a closing gate after
R3b/R4/R5 are `DONE`. **This seam is smaller and earlier:** Phase U's own contract (§2) asks for
exactly four representative tests — "one unit test, one component test, one live route/contract
smoke test, one accessibility assertion" — proving each testing *layer* exists and is wired into
CI, not proving comprehensive coverage. The comprehensive version is explicitly the student
assignment ("risk-based testing strategy, interaction E2E, contract breadth, flake control,
performance/accessibility gates, review evidence").

**This lane does pair with TS3a/b/c and TS4a as their stubs land**, same continuous spirit as the
rich-reference R7 — but because every TS3/TS4 lane here is a *small, bounded* reduction (not a
multi-week build), in practice this seam's four representative tests can mostly be written once
TS1's CI skeleton exists, using whatever of TS3a/b/c/TS4a has already landed as the target, and
backfilled against the rest as those lanes finish. Do not block on "nothing is done yet" — R3a's
existing endpoints (already `DONE` by definition of the cohort-start gate) are an immediate,
available target for the unit/contract test if the other Week-0 lanes are still in flight.

## 1. Required reading

- `PHASE-U-FEII-TEACHING-SKELETON-CASCADE.md` §2 (R7's row).
- `PHASES/R7-testing-strategy.md` §0–§2 only, for boundaries that still apply (never run tests
  against the real `ttod.yml`; use disposable fixtures) — its §3 onward targets the larger, later
  closing gate, not this seam.
- `web-atelier-udit/web-foundations/docs/lessons/en/feii/unit-5-testing-strategy/index.md` — this
  seam reuses that lesson's stack (Vitest + RTL + Playwright, chromium-only, sharded) and its own
  CI budget number (**PR feedback under 5 minutes wall-clock**) verbatim, not a reinvented one.
- Existing test precedent already in this repo: `services/frontend/src/components/graph/layout.test.mjs`,
  `services/frontend/src/components/oracle/sse.test.ts`, `services/frontend/e2e/` — read these
  before writing new tests; match their existing conventions rather than introducing a new style.

## 2. Non-negotiable boundaries

- **Work on `skeleton/ts4b-r7`, forked from `skeleton/ts1-contracts`.**
- **Never run any test against the live, repository-root `ttod.yml`.** Any test that would
  exercise a write path uses a disposable fixture, per `PHASES/R7-testing-strategy.md` §2.1 —
  restated in full here because it is the one rule most likely to be violated by an eager
  contract test against `/api/v1/wisdom/sample`.
- **`chromium` project only for the E2E/route smoke test**, matching Unit 5 and the rich-reference
  R7 runbook's own convention — do not add a cross-browser matrix at hello-world depth.
- **Do not edit `layout.test.mjs` or `sse.test.ts`.** These already exist and already pass; this
  seam adds new, different representative tests, it does not rewrite the ones already there.
- **This seam does not modify TS3a/b/c or TS4a's own component code** to make it more testable —
  if a real testability gap is found in another lane's stub, report it back to that lane's owner
  (mirroring `PHASES/R6-pwa-cicd-audit.md` §7's rule: "if packaging reveals a bug in one of them,
  file it back to that lane's report, don't silently patch it").

## 3. Domain contract slice

No new types — this seam tests against whatever of `domain.ts`'s existing shapes the target lane
already uses (e.g. `WisdomEntry` for a content contract test, `GraphNode`/`GraphLink` for a graph
unit test).

## 4. Scope — the four representative tests

1. **Unit test** — one pure-function test outside the two that already exist. Candidate: a small
   function in `services/frontend/src/content/wisdom.ts` (e.g. `frequencies()`, which is already
   unused after TS3a's cut and currently has no test — a good, real, low-risk target).
2. **Component test** — one Testing-Library-style render test for whichever of R4/R5's reduced
   islands has landed first. If both are still in flight, default to R3a's already-`DONE`
   `Page.astro` shell rendering correctly for one locale.
3. **Route/contract smoke test** — one test hitting a real local endpoint (e.g. `GET
   /api/v1/wisdom/sample` against the locally running backend, or a Playwright visit to
   `/en/wisdom/`) and asserting the response shape matches `domain.ts`, per contract-testing
   practice from Unit 5 §6.
4. **Accessibility assertion** — one `axe`-based (or equivalent) check on a single rendered route,
   matching the shared FE II accessibility baseline (semantic structure, keyboard operation,
   visible focus, non-color cues).
5. **Wire into TS1's CI skeleton** — extend `.github/workflows/ci.yml` (TS1's output) with a test
   step: lint/typecheck first (already there), then these four tests. Measure and record the
   actual wall-clock time; it must stay under 5 minutes total per Unit 5's own budget — if it
   doesn't at only four tests, that is worth flagging (something is unusually slow), not silently
   accepting.

**`ASSIGNMENT.md`** (new, `services/frontend/ASSIGNMENT-testing.md` or `e2e/ASSIGNMENT.md`):
learning outcomes (Testing Trophy layering, contract testing, accessibility-in-the-suite, CI
economics), constraints (chromium-only, disposable fixtures only, reuse the existing Vitest/RTL/
Playwright setup — do not introduce Cypress or a different runner), acceptance criteria (a
risk-based test plan naming what is and isn't tested and why, interaction-level E2E beyond the one
smoke test, flake-control evidence, the CI budget maintained as coverage grows), prohibited
shortcuts (no `--force`/skip-flaky-test patterns as a substitute for fixing flakiness, no testing
implementation details instead of behavior).

## 5. Mechanical gates

| Gate | Required proof |
| --- | --- |
| Four tests exist | one unit, one component, one route/contract, one a11y — each passing locally |
| Wired into CI | TS1's `.github/workflows/ci.yml` runs all four on every PR |
| CI budget | total wall-clock time measured and reported, under 5 minutes |
| No `ttod.yml` writes | none of the four tests touch the repository-root `ttod.yml` |
| Existing tests unchanged | `layout.test.mjs` and `sse.test.ts` still pass, byte-identical to `main` |
| chromium-only | no other browser project configured for the E2E/smoke test |

## 6. Rollback and mutation law

- Any test that would need to mutate data uses a disposable fixture copy, never the real
  repository file — restated because it is this seam's single highest-risk mistake to make under
  time pressure.
- If a test proves flaky on first three runs, fix the cause (per Unit 5 §3's four documented
  causes) before wiring it into the required CI gate — a flaky required check trains the class to
  ignore red CI, which Unit 5 itself identifies as the actual failure mode worth avoiding.

## 7. Touched-path budget

**Allowed:** one new unit test file (e.g. under `services/frontend/src/content/`), one new
component test, one new route/contract test (under `services/frontend/e2e/` or the existing test
directory convention), one new a11y test, `.github/workflows/ci.yml` (extending TS1's file, not
replacing it), a new `ASSIGNMENT.md`.

**Forbidden:** `layout.test.mjs`, `sse.test.ts`, any component/page source file in another lane's
territory (report issues back instead of patching), `services/backend/**`, `services/mcp/**`,
`ttod_core/**`, `ttod.yml`.

## 8. Post-phase review

A second reader runs all four tests fresh (not trusting a prior green run) and confirms the
measured CI time is real, not estimated — matching the discipline `PHASES/R6-pwa-cicd-audit.md` §8
already establishes for this repo ("measure and report the actual number, don't estimate it").

## 9. Phase report status enum

- **DONE** — all §5 gates pass, `ASSIGNMENT.md` filed, measured (not estimated) CI time reported.
- **PARTIAL** — name exactly which of the four test layers or the CI-wiring gate is missing.
- **BLOCKED** — TS1 has not filed `DONE` (no CI skeleton to wire into).

## 10. Exact commands

```bash
cd /Users/ruvebal/src/ttod
git worktree add ../ttod-skeleton-ts4b -b skeleton/ts4b-r7 skeleton/ts1-contracts
cd ../ttod-skeleton-ts4b/services/frontend
npx vitest run                       # unit + component
npx playwright test --project=chromium   # route/contract smoke + a11y
```

## 11. Report requirements

File `docs/DEV_PLAN/PHASE-U-TS4b-REPORT.md`: status (§9), the four tests' file paths, the
CI workflow diff, the actual measured wall-clock time for a real run (link or transcript), and the
`ASSIGNMENT.md` content.

## 12. Agent prompt — paste this into a fresh agent session with no other file open

```text
Act as TTOD Phase U TS4b engineer. Work only inside a new git worktree on branch skeleton/ts4b-r7,
forked from skeleton/ts1-contracts (never main). This runbook
(docs/DEV_PLAN/PHASES/U-TS4b-r7-testing-hello-world.md) is self-contained. This lane is
continuous — do not wait for TS3a/b/c or TS4a to all finish; use whatever has already landed
(R3a's existing backend endpoints are available immediately) and backfill against the rest.

Read services/frontend/src/components/graph/layout.test.mjs and
services/frontend/src/components/oracle/sse.test.ts first to match this repo's existing test
conventions — do not edit either file.

Write exactly four new tests: one unit test (a good target: content/wisdom.ts's frequencies()
function, currently untested), one component test (whichever of the reduced graph/oracle islands
has landed; if neither has, test Page.astro's shell rendering for one locale instead), one route/
contract smoke test (hit a real local endpoint, e.g. GET /api/v1/wisdom/sample, and assert the
response matches the WisdomEntry shape in src/types/domain.ts), and one accessibility assertion
(axe or equivalent) on a single rendered route. Use Playwright's chromium project only, matching
this repo's existing convention — do not add other browsers.

Never write a test that touches the real repository-root ttod.yml — use a disposable fixture if
any test needs write-path behavior.

Extend .github/workflows/ci.yml (written by TS1 — do not replace it) with a step running these
four tests after the existing lint/typecheck/build steps. Measure the actual wall-clock time of a
real CI run; it must stay under 5 minutes total per this course's own Unit 5 budget — report the
real number, do not estimate it.

Write an ASSIGNMENT.md (services/frontend/ASSIGNMENT-testing.md or alongside e2e/): learning
outcomes (Testing Trophy layering, contract testing, accessibility-in-the-suite, CI economics),
constraints (chromium-only, disposable fixtures only, reuse Vitest/RTL/Playwright — no new
runner), acceptance criteria (risk-based test plan, interaction E2E beyond this one smoke test,
flake-control evidence, budget maintained as coverage grows), prohibited shortcuts (no
skip-flaky-test patterns, no testing implementation details instead of behavior).

File docs/DEV_PLAN/PHASE-U-TS4b-REPORT.md with status (DONE/PARTIAL/BLOCKED per this
runbook's §9), the four test file paths, the CI workflow diff, the real measured wall-clock time,
and the ASSIGNMENT.md content.
```
