# PWA Task 7 — unit and component tests for the offline boundary

## Status

Added on 2026-10-08 on branch `pwa-task7-offline-tests`, stacked on Task 6 `f16bed1`. Two new test files cover the offline queue and the network banner separately. No production file changes: `src/lib/db.ts` and `src/layouts/Page.astro` are untouched.

## The two test surfaces

| Surface | Code under test | Test file | Environment | Cases |
| --- | --- | --- | --- | --- |
| Offline queue | `services/frontend/src/lib/db.ts` | `src/lib/db.test.ts` | Node | 3 |
| Network banner | `#ttod-network-boundary` and its script in `src/layouts/Page.astro` | `src/layouts/Page.test.ts` | jsdom | 4 (2 per locale) |

Each test file sits next to the code it tests, like the existing Oracle tests. The queue tests never touch the DOM and the banner tests never touch IndexedDB, so a failure points at one surface.

## Queue tests

What they prove:

1. `enqueueOracleQuery` stores an `oracle-query` entry with `synced: false`, and `listUnsyncedEntries` returns it.
2. Pending entries are listed in the order they were enqueued. Entry IDs are random, so this order can only come from the `queueOrder` number assigned at enqueue time.
3. `markEntrySynced` removes an entry from the pending list and leaves the others in their original order.

**IndexedDB stand-in.** `db.ts` uses transactions, a unique `queueOrder` index, a reverse cursor and an upgrade handler. A hand-written mock would have to re-implement those, and the tests would then check the mock. The tests use the `fake-indexeddb` dev dependency instead, an in-memory IndexedDB implementation:

- `import 'fake-indexeddb/auto'` installs the `indexedDB` global before `db.ts` runs, so the real queue code executes unchanged.
- `beforeEach` assigns `globalThis.indexedDB = new IDBFactory()`, giving every test an empty database so entries cannot leak between cases.

The version-1 migration, blocked upgrades and aborted transactions are not repeated here; the Playwright queue cases in `e2e/pwa-queue-reconnect.spec.ts` already cover them in a real browser.

## Banner tests

What they prove, for English and Spanish:

1. Dispatching `offline` on `window` sets `data-state="offline"`; dispatching `online` sets it back to `online`.
2. In both states the banner shows its text label (`Offline` / `Online`, `Sin conexión` / `En línea`) and keeps `role="status"` and `aria-live="polite"`. The state is readable text in a live region, so it does not depend on colour.

**How the banner is reached.** The banner's logic is a `<script>` inside `Page.astro`, so it cannot be imported as a module. The test imports the layout as text (`Page.astro?raw`), extracts the banner `<p>` and the script body, resolves the `{lang === 'es' ? … : …}` label expressions for the locale under test, places the banner in the jsdom document and runs the layout's own script.

**Network simulation.**

- `vi.spyOn(navigator, 'onLine', 'get')` controls what `navigator.onLine` reports.
- `window.dispatchEvent(new Event('offline'))` and `new Event('online')` trigger the listeners the script registers.
- `afterEach` restores the spy.

jsdom has no `navigator.serviceWorker`, so the script's `'serviceWorker' in navigator` guard skips registration. The tests therefore run with no service worker, no cache and no real network change.

Rendering the layout through Astro's experimental container API was tried first and dropped: it required changing the shared Vitest config and did not execute the layout script in the test.

## Why simulate instead of disconnecting

- **Deterministic.** The test decides the exact moment the state changes, so there is no waiting on a network stack and no timing-dependent failure.
- **Fast.** The seven new cases run in milliseconds with no browser or server to start.
- **Runs anywhere.** CI needs no network access, no browser install and no service worker for these checks.
- **Isolated.** A failure here means the queue rules or the banner script changed, not that a network or cache condition differed.

Real offline behaviour — the service worker serving cached pages, queued queries replaying on reconnect — remains covered by the Playwright suites. These tests complement them; they do not replace them.

## Limitations

- The banner test reads `Page.astro`'s source text. It proves the script's behaviour against the authored markup, not the HTML Astro finally emits; `e2e/pwa-lifecycle.spec.ts` checks the rendered page.
- Only the `{lang === 'es' ? 'a' : 'b'}` expression form is resolved. If the banner markup becomes more dynamic, the test needs a real render.
- Keyboard operability and reduced-motion are not asserted: the banner is a non-interactive status message with no animation.
- `npm install` also rewrote `"peer": true` flags on existing lockfile entries. No package version changed apart from adding `fake-indexeddb` 6.2.5.

## Verification — 2026-10-08

| Check | Result |
| --- | --- |
| `npm test` | 13 passed in 4 files (6 existing, 3 queue, 4 banner) |
| `npm run check` | 0 errors, 0 warnings, 0 hints |
| `npm run build` | Passed |
| `npm run pwa:guard` | Passed, including its 8 browser cases |
| `make check` | Passed |

Before being added to the project, the banner test was checked against deliberately broken copies of the layout: removing the `offline` listener failed all four banner cases, and removing `role="status"` failed two.

## AI-use and review record

AI assistance (Claude Code) read the task sheet, `db.ts` and `Page.astro`, finished both test files and checked them in a disposable copy of the frontend, diagnosed a missing `// @vitest-environment jsdom` line, ran the checks in the table above and drafted this note. The developer created the branch, installed `fake-indexeddb`, did a draft for both test and ran the tests.
