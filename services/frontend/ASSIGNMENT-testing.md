# Assignment — Testing (R7 hello-world)

This starter ships **four representative tests**, one per Testing Trophy layer, wired into CI.
They prove the *layers exist*. They are not a complete strategy.

## Learning outcomes

- **Testing Trophy layering.** Place confidence where it is cheap and behavior-shaped: a pure
  unit (`frequencies()`), a rendered shell (component), a live HTTP contract, and an in-suite
  accessibility assertion. Do not invert this into a pyramid of framework-internal units.
- **Contract testing.** Assert *shape* against `src/types/domain.ts` on a real local endpoint
  (`GET /api/v1/wisdom/sample` → `WisdomEntry`). Never assert specific quote texts, IDs, or
  counts from the governed corpus.
- **Accessibility-in-the-suite.** `@axe-core/playwright` runs inside the normal Chromium E2E
  job, not as a pre-submission audit. Semantic structure, keyboard operation, visible focus, and
  non-color cues remain the FE II baseline; axe is the automated floor, not the ceiling.
- **CI economics.** PR feedback must stay **under 5 minutes wall-clock**. Cheap `check` +
  `build` first, then unit/component, then chromium-only Playwright. As coverage grows, shard
  or cut before silently accepting a slower gate.

## Constraints

- **Chromium only.** Do not add Firefox/WebKit projects unless a filed cross-browser bug
  requires it.
- **Disposable fixtures only.** Tests must never write (or "temporarily edit") repository-root
  `ttod.yml`. Read-path contract tests hit the live R3a HTTP API. Write-path tests use a
  disposable copy.
- **Reuse this runner stack.** Vitest + Testing Library + Playwright + `@axe-core/playwright`.
  Do not introduce Cypress, Jest, or a second E2E runner.
- **Do not rewrite** `src/components/graph/layout.test.mjs` or
  `src/components/oracle/sse.test.ts` — extend with new files.

## Acceptance criteria

A passing submission includes all of:

1. **A risk-based test plan** naming what is tested, what is not, and why (hello-world vs
   assignment-depth: facet browse, graph tag-filter URL state, oracle streaming disclosure,
   flake budget as coverage grows).
2. **Interaction-level E2E** beyond this one route smoke (for example: graph click-to-select,
   oracle ask → streamed chunk, locale switch that preserves the journey).
3. **Flake-control evidence** — three consecutive green runs of any new E2E, or a documented
   fix for a named cause (timing, shared state, network, isolation) rather than a retry loop.
4. **The 5-minute CI budget maintained** as the suite grows — measure wall-clock, do not
   estimate.

## Prohibited shortcuts

- No `--force`, `test.fixme`, or skip-the-flaky-test patterns as a substitute for fixing
  flakiness. A required check that is red "sometimes" trains the class to ignore CI.
- No testing implementation details (private fields, CSS class names, mock call counts) when
  a role, heading, or HTTP shape would prove the behavior.
- No mocking `/api/v1/wisdom/sample` with a hand-written corpus in the contract test, and no
  loading `ttod.yml` inside frontend tests.
- No expanding the Playwright browser matrix at hello-world depth.

## How to run

```bash
cd services/frontend
npx vitest run                       # unit + component (and existing island tests)
npx playwright test --project=chromium \
  e2e/wisdom-sample.contract.spec.ts e2e/a11y-docs.spec.ts
```

Contract and a11y tests need a live stack (`make up` from the repo root). Studio port
overrides (`HTTP_PORT=18080`) are probed automatically. If the stack is down, those two tests
**skip** — that is PARTIAL, not a green mock.
