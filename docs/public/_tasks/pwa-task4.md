---
title: "An offline queue that flushes once the connection returns"
seam: pwa
team_number: 4
team_name: "PWA & Local Operations"
task_number: 4
area: "PWA/Offline"
verb: keep
layout: default
lang: en
---

# Assignment — Team 4, Task 4: An offline queue that flushes once the connection returns

**Seam:** pwa · **Team:** 4 · **Task:** 4 of ~10
**Area(s):** PWA/Offline · **Verb served:** keep

## 1. Curriculum map

This task exercises the **PWA / local operations** unit of web-atelier-udit FE II, specifically the learning outcomes regarding **Service-worker lifecycle** and **Caching strategies** as defined in the module's `ASSIGNMENT.md`. It directly supports the "Offline queue flush on reconnect" acceptance criterion, requiring students to demonstrate how `install`, `activate`, and `fetch` events coordinate with network state changes to ensure data integrity.

## 2. Worked example, from the real TTOD app

The existing implementation in `services/frontend/src/lib/db.ts` already establishes the foundation for this task. It exports `enqueueOracleQuery`, `listUnsyncedEntries`, and `markEntrySynced`, operating on the `OfflineLogEntry` type defined in `services/frontend/src/types/domain.ts` (line 61). Additionally, `services/frontend/src/layouts/Page.astro` already registers the service worker via `navigator.serviceWorker.register('/sw.js')` and renders the `#ttod-network-boundary` banner driven by `window` online/offline events. This task extends these existing mechanisms rather than creating new ones.

## 3. What "done" looks like

**Visible result:** Actions taken offline (such as an Oracle query from Team 3) are queued and replayed once the connection returns, in order.

**What it includes:**
*   Extension of `src/lib/db.ts`'s existing queue, which you own and Team 3 calls into.
*   Coordination of the exact interface with Team 3 to ensure compatibility.
*   Confirmation that ordering is preserved and successes are marked synced, not silently retried forever.

**What has to be done:**
*   Read and extend the existing `OfflineLogEntry` queue in `src/lib/db.ts`; do not rewrite it out from under Team 3.
*   Implement the flush logic that triggers when the `online` event fires or the service worker observes a restored network.
*   Ensure the `synced` flag semantics are respected: successful flushes mark entries as synced, preventing infinite retry loops.

## 4. Success criteria (functional)

*   **Offline queue flush on reconnect:** Work queued while offline (at least Oracle queries via `OfflineLogEntry`) is flushed when `online` fires or the service worker observes a restored network.
*   **Flag semantics preserved:** The existing `synced` flag semantics are not dropped; successful flushes mark entries as synced, and failed attempts do not result in silent infinite retries.
*   **Ordering preserved:** Queued actions are replayed in the order they were enqueued.

## 5. Quality criteria (the part that's new)

*   **Code organization:** Extend the existing `OfflineLogEntry` type in `src/types/domain.ts` and the IndexedDB helpers in `src/lib/db.ts`. Do not invent a second queue or edit the domain freeze without a documented contract change.
*   **AI-use/process documentation:** Document the design choices made in extending the queue, particularly how the flush logic interacts with the service worker's lifecycle events.
*   **Test shape:** Per R7's Trophy-not-Pyramid doctrine, tests should focus on the integration of the queue with the service worker's network state changes, not just unit tests of the queue in isolation. Every mention of testing links [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/).
*   **Accessibility:** This task inherits the global Definition of Done: keyboard-operable, one accessible name or label, no meaning carried by color alone, respects reduced-motion preferences.
*   **Oral defense:** A defensible answer explains how the flush logic ensures data integrity without violating the "extend, do not replace" constraint, and how the `synced` flag prevents infinite retries while preserving ordering.

## Closing

> "The river updates the stones; it does not shatter them."
> — TTOD `wis-009`, *wisdom*

This quote captures the essence of extending the existing `OfflineLogEntry` queue: the flush logic updates the state of queued entries without destroying the existing structure or semantics, ensuring continuity and growth rather than disruption.