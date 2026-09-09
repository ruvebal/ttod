# Phase U · TS4b Report — R7 testing hello-world seam

**Status: DONE**
**Branch:** `skeleton/ts4b-r7` (worktree `/Users/ruvebal/src/ttod-skeleton-ts4b`, forked from `skeleton/ts1-contracts` @ `47f15da9`)
**Date:** 2026-09-09

TS3 islands were still the rich reference on this branch; the component test therefore targets
R3a's `Page.astro` shell (no edits to graph/oracle source). Contract and a11y ran against the
already-up R3a Compose stack on `http://127.0.0.1:18080` (studio `HTTP_PORT` override). Tests
never open repository-root `ttod.yml`.

## Four tests

| Layer | Path | Result |
| --- | --- | --- |
| Unit | `services/frontend/src/content/wisdom.frequencies.test.ts` | pass — disposable `WisdomEntry` fixtures; `frequencies()` counts + alpha sort |
| Component | `services/frontend/src/layouts/Page.shell.test.ts` | pass — AstroContainer render of English shell (`lang`, title, slotted `main`) |
| Route/contract | `services/frontend/e2e/wisdom-sample.contract.spec.ts` | pass — live `GET /api/v1/wisdom/sample` matches `WisdomEntry` shape |
| A11y | `services/frontend/e2e/a11y-docs.spec.ts` | pass — axe on `/en/docs/`, Playwright `chromium` only |

Existing `layout.test.mjs` and `sse.test.ts` are byte-identical to `main` and still pass
(`node --test` 2/2; Vitest 8/8 including prior island tests).

If the live stack is down, the contract and a11y specs **skip** with an explicit PARTIAL
message — they do not mock the corpus or read `ttod.yml`. GitHub-hosted runners have no
Compose backend, so the contract test is expected to skip there; the a11y spec runs against
the job's `node ./dist/server/entry.mjs` (`/en/docs/` does not fetch the corpus).

## CI workflow diff

TS1's `typecheck-and-build` job is unchanged in order: `npm ci` → `npm run check` →
`npm run build`. Added after build:

```diff
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -1,4 +1,4 @@
-name: Frontend — typecheck and build
+name: Frontend — typecheck, build, and hello-world tests
@@ -35,3 +35,29 @@
       - run: npm run check
       - run: npm run build
+
+      - name: Unit and component tests
+        run: npx vitest run
+
+      - name: Install Playwright Chromium
+        run: npx playwright install --with-deps chromium
+
+      - name: Route contract and a11y (chromium)
+        env:
+          HOST: 127.0.0.1
+          PORT: 4321
+          E2E_BASE_URL: http://127.0.0.1:4321
+          E2E_BACKEND_URL: http://127.0.0.1:8000
+        run: |
+          node ./dist/server/entry.mjs &
+          ... wait for /en/docs/ ...
+          npx playwright test --project=chromium \
+            e2e/wisdom-sample.contract.spec.ts \
+            e2e/a11y-docs.spec.ts
```

Playwright is filtered to the two new specs so the rich-reference `e2e/i18n-routes.spec.ts`
(full-stack) does not fail the skeleton CI. No Firefox/WebKit project was added.

Supporting (not a replacement of TS1): `vitest.config.ts` now uses `getViteConfig` so
`Page.astro` can compile; `package.json` adds `test` and `test:e2e:hello-world` scripts.

## Measured local wall-clock (not estimated)

Machine: Tanit, worktree `ttod-skeleton-ts4b`, frontend already `npm ci`'d, Playwright
Chromium already installed (install step was a no-op, 0.6s).

| Slice | Wall-clock |
| --- | --- |
| Four new layers + existing Vitest file (`npx vitest run` + two Playwright specs) | **4.329 s** |
| Full local analogue of the CI job after `npm ci`: `check` + `build` + Vitest + two Playwright specs + `layout.test.mjs` | **9.426 s** |
| `npx vitest run` | 0.92 s (8 passed / 4 files) |
| Playwright chromium hello-world (2 specs, 2 workers) | 2.1 s (2 passed) |

Transcript (second measured run, 2026-09-09 12:51 local):

```
npm run check     → 0 errors
npm run build     → Server built in 1.53s
npx vitest run    → Test Files  4 passed (4) / Tests  8 passed (8) / Duration  920ms
playwright        → 2 passed (2.1s)
node --test layout.test.mjs → pass 2
local_ci_analogue_wall_s=9.426
```

Unit 5 budget is **5 minutes**. 9.4 s locally leaves headroom for cold `npm ci` +
`playwright install --with-deps chromium` on `ubuntu-latest`. If a cold CI run exceeds
5 minutes at only four tests, that is a flag, not something to accept silently.

## ASSIGNMENT.md

Canonical file: [`services/frontend/ASSIGNMENT-testing.md`](../../services/frontend/ASSIGNMENT-testing.md).

### Learning outcomes

- Testing Trophy layering (unit `frequencies()`, rendered `Page.astro` shell, live HTTP
  contract, in-suite axe).
- Contract testing: shape against `domain.ts`, never quote values.
- Accessibility-in-the-suite (`@axe-core/playwright` on chromium).
- CI economics: PR feedback under 5 minutes; shard/cut before accepting a slower gate.

### Constraints

Chromium only; disposable fixtures only; reuse Vitest + Testing Library + Playwright; do not
rewrite `layout.test.mjs` / `sse.test.ts`.

### Acceptance criteria

Risk-based plan (hello-world vs assignment-depth: facet browse, graph `?tag=` URL state,
oracle streaming disclosure); interaction E2E beyond this smoke; flake-control evidence;
measured 5-minute budget as coverage grows.

### Prohibited shortcuts

No skip-flaky-test / `--force` as a substitute for fixing flakes; no implementation-detail
tests; no mocking `/api/v1/wisdom/sample` and no loading `ttod.yml` in frontend tests; no
extra browser matrix at hello-world depth.

## Files changed (this lane)

- `services/frontend/src/content/wisdom.frequencies.test.ts` (new)
- `services/frontend/src/layouts/Page.shell.test.ts` (new)
- `services/frontend/e2e/wisdom-sample.contract.spec.ts` (new)
- `services/frontend/e2e/a11y-docs.spec.ts` (new)
- `services/frontend/ASSIGNMENT-testing.md` (new)
- `.github/workflows/ci.yml` (extended)
- `services/frontend/vitest.config.ts` (AstroContainer)
- `services/frontend/package.json` (test scripts)
- `docs/DEV_PLAN/PHASE-U-TS4b-REPORT.md` (this file)

**Not touched:** `layout.test.mjs`, `sse.test.ts`, `ttod.yml`, `services/backend/**`,
`services/mcp/**`, `ttod_core/**`, graph/oracle component source, `main`.
