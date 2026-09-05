# TTOD Oracle testing strategy

R7 follows the Testing Trophy: most frontend confidence comes from component/integration tests,
with focused pure-function tests below and a small Chromium Playwright layer above. Vitest,
Testing Library, MSW, Playwright Chromium, and `@axe-core/playwright` are the fixed toolchain.

Backend contract tests assert response shape and governance invariants, never corpus values or
counts. The nightly contract job should start the local stack and exercise real `/api/v1/*` and
R1→R2 Streamable HTTP `/mcp`; PR jobs run typecheck then unit/component tests. R6 owns workflow
files and should shard Chromium E2E last, keeping total PR feedback under five minutes.

Tests must use disposable proposal directories and must never mutate root `ttod.yml`. Creative
responses must have no citations and must be visually disclosed; proposals require explicit user
action and remain `proposed`/`blackbox`. Accessibility assertions belong inside ordinary E2E specs.

The empirical threshold fixture records model, query, measured top score, and expected verdict so
changes to model/corpus/threshold are reviewed as calibration changes rather than silently shifting
behavior.
