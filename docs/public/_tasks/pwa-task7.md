---
title: "Unit and component tests for the offline boundary"
seam: pwa
team_number: 4
team_name: "PWA & Local Operations"
task_number: 7
area: "Testing"
verb: keep
layout: default
lang: en
alt_lang_missing: true
---

# Assignment — Team 4, Task 7: Unit and component tests for the offline boundary

**Seam:** pwa · **Team:** 4 · **Task:** 7 of ~10
**Area(s):** Testing · **Verb served:** keep

## 1. Curriculum map

This task exercises **Unit 5 — Testing strategy**, specifically the application of unit and component testing to verify state transitions and data flow in offline-first applications. The curriculum emphasizes that tests must simulate environmental conditions (like network status) rather than relying on external infrastructure, a core principle for verifying PWA behavior in a CI environment.

## 2. Worked example, from the real TTOD app

The existing codebase provides two distinct surfaces for testing, which must be treated separately:

1.  **The Offline Queue Logic:** `services/frontend/src/lib/db.ts` exports `enqueueOracleQuery`, `listUnsyncedEntries`, and `markEntrySynced`. These functions manipulate the `OfflineLogEntry` type defined in `services/frontend/src/types/domain.ts`. The logic for ordering and flushing is contained within these helper functions and their interaction with IndexedDB.
2.  **The Visual Boundary:** `services/frontend/src/layouts/Page.astro` renders the `#ttod-network-boundary` banner. This component listens to `window` `online` and `offline` events to toggle the `data-state` attribute between `'online'` and `'offline'`.

A test for this task must target these two surfaces independently. For example, a unit test for `db.ts` would mock the IndexedDB interface to verify that `enqueueOracleQuery` correctly appends to the queue and that `listUnsyncedEntries` returns them in the expected order, without requiring a browser or network. A component test for `Page.astro` would simulate the dispatch of `online`/`offline` events on the `window` object and assert that the DOM element `#ttod-network-boundary` updates its `data-state` attribute accordingly.

## 3. What "done" looks like

**Visible result:** The offline boundary (queue + banner) has at least one real test.

**What it includes:**
*   Testing the queue's ordering/flush logic directly, separately from the banner's visual online/offline state.
*   Unit tests for `services/frontend/src/lib/db.ts` verifying that `OfflineLogEntry` items are enqueued, listed, and marked as synced correctly.
*   Component tests for `services/frontend/src/layouts/Page.astro` verifying that the `#ttod-network-boundary` banner reflects the correct `data-state` based on simulated network events.

**What has to be done:**
*   Simulate online/offline events in the test environment rather than requiring an actual network change to verify behavior.
*   Ensure the tests run within the local quality gate defined by the module's CI/CD constraints (no external network dependencies).
*   Verify that the tests do not rely on the service worker (`services/frontend/public/sw.js`) being active, as the tests target the application logic and UI state, not the browser's caching layer.

## 4. Success criteria (functional)

*   **Queue Logic Verification:** Tests confirm that `enqueueOracleQuery` adds an entry to the queue, `listUnsyncedEntries` retrieves it, and `markEntrySynced` updates its status, preserving the `synced` flag semantics defined in `services/frontend/src/types/domain.ts`.
*   **Banner State Verification:** Tests confirm that dispatching an `offline` event on `window` results in the `#ttod-network-boundary` element having `data-state='offline'`, and dispatching an `online` event results in `data-state='online'`.
*   **Isolation:** The tests pass in a headless environment without an active service worker or actual network disconnection, proving that the logic is decoupled from the browser's native offline capabilities.

## 5. Quality criteria (the part that's new)

*   **Code Organization:** Tests must be colocated with the code they test or follow the project's established test directory structure. Unit tests for `db.ts` should be separate from component tests for `Page.astro` to maintain clear boundaries between logic and presentation.
*   **AI-use/Process Documentation:** Document the specific mocks used for IndexedDB and the `window` event listeners. Explain why simulating events is preferred over actual network disconnection in a CI context (reliability, speed, determinism).
*   **Test Shape (Trophy-not-Pyramid):** Focus on high-value integration points (the queue flush logic and the banner state transition) rather than testing every internal helper function. The "trophy" is the verified behavior of the offline boundary as a whole, not the coverage of every line in `db.ts`.
*   **Accessibility:** The component tests must verify that the `#ttod-network-boundary` element maintains its accessible name and label regardless of the `data-state`. The banner must remain keyboard-operable and not rely on color alone to convey the online/offline status, adhering to the global Definition of Done: *keyboard-operable, one accessible name or label, no meaning carried by color alone, respects reduced-motion preferences*.
*   **Defensible Oral Defense:** Be prepared to explain why testing the queue logic in isolation is critical for verifying the "flush on reconnect" acceptance criterion, even if the actual flush is triggered by a service worker event. Explain how simulating `window` events allows you to test the UI's reaction to network changes without the flakiness of real network conditions.

## Closing

> "A system without clear layers is like a house without walls: technically functional, emotionally devastating."
> — TTOD `qa-003`, *qa-tooling*

Testing the queue and the banner as one tangled thing would prove nothing about either. Keeping them as two separate test surfaces — one pure logic, one DOM state — is what makes each result trustworthy on its own.