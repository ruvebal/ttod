---
title: "Service worker registration and an installable manifest"
seam: pwa
team_number: 4
team_name: "PWA & Local Operations"
task_number: 1
area: "PWA/Offline"
verb: keep
layout: default
lang: en
---

# Assignment — Team 4, Task 1: Service worker registration and an installable manifest

**Seam:** pwa · **Team:** 4 · **Task:** 1 of ~10
**Area(s):** PWA/Offline · **Verb served:** keep

## 1. Curriculum map

This task exercises the foundational concepts of **Unit 3 — Frontend Architecture & Routing** (specifically the client-side runtime environment and asset management) and introduces the lifecycle concepts that will be tested in **Unit 5 — Testing strategy** ([Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/)). While the specific PWA unit link is not yet published in the `assignments.md` "Lessons for these tasks" section, the underlying mechanics of service worker registration and manifest validation are core to the frontend architecture curriculum.

## 2. Worked example, from the real TTOD app

The existing implementation in `services/frontend/src/layouts/Page.astro` already registers the service worker via `navigator.serviceWorker.register('/sw.js')` and renders the `#ttod-network-boundary` banner. The service worker itself, located at `services/frontend/public/sw.js`, currently implements a `CACHE_NAME` of `'ttod-pwa-stub-v1'` and a `PROOF_ASSET` of `'/visual-system/tokens.css'`. It handles `install`, `activate`, and `fetch` events, but only caches that single asset.

*Out of scope for this task: the manifest's own icon-size completeness and Lighthouse installability check are Task 5's deliverable ("Install-quality checks"). This task's own scope is the lifecycle behavior of the already-registered worker — install/activate/fetch, client claiming, and cache-name versioning — not the manifest's content.*

## 3. What "done" looks like

**Visible result:** You can demonstrate that the service worker lifecycle (`install`, `activate`, `fetch`) behaves correctly. Specifically, you can show the worker claiming clients and updating its cache name on a new version.

**What it includes:** Explaining the lifecycle is itself a learning outcome. The defense will ask you to walk through what happens when the token/cache version changes. You must be able to articulate why the cache name is updated and how old caches are cleaned up.

**What has to be done:**
1.  **Deliberately trigger an update:** Change the `CACHE_NAME` in `services/frontend/public/sw.js` (e.g., to `'ttod-pwa-stub-v2'`), reload the page, and confirm that the old cache (`ttod-pwa-stub-v1`) is cleaned up during the `activate` event, not silently accumulated.
2.  **Verify registration:** Confirm that `navigator.serviceWorker.register('/sw.js')` in `services/frontend/src/layouts/Page.astro` is still correctly wired and that the `#ttod-network-boundary` banner reflects the online/offline state driven by `window` online/offline events.

## 4. Success criteria (functional)

1.  **Service-worker lifecycle:** You can explain `install`, `activate`, and `fetch`, and show where your worker claims clients and updates its cache name.
2.  **Cache cleanup:** After a `CACHE_NAME` change and reload, the previous cache no longer appears in `caches.keys()` — old caches are deleted during `activate`, not silently accumulated.

## 5. Quality criteria (the part that's new)

*   **Code Organization:** The service worker logic in `services/frontend/public/sw.js` must remain modular. The cache cleanup logic in the `activate` event handler should be explicit and commented to show the intent of removing old caches.
*   **AI-use/process documentation:** Document any changes made to the manifest or service worker in your commit messages or a brief note in your PR description, explaining *why* the cache name was changed and *how* you verified the cleanup.
*   **Test shape:** Per R7's Trophy-not-Pyramid doctrine, focus on an integration test that registers the worker, forces a `CACHE_NAME` change, and asserts the old cache key is gone from `caches.keys()` after `activate`. Unit tests for the individual event handlers are less valuable than verifying this end-to-end lifecycle behavior.
*   **Accessibility:** The app must remain keyboard-operable, have one accessible name or label, no meaning carried by color alone, and respect reduced-motion preferences. This is inherited from the global Definition of Done and is not unique to this task.
*   **Oral defense:** Be prepared to explain the difference between `install`, `activate`, and `fetch` events. Explain why the cache name is changed and how the `activate` event ensures old caches are removed.

## Closing

> "The river updates the stones; it does not shatter them."
> — TTOD `wis-009`, *wisdom*

This quote connects to the task's requirement to update the cache name and clean up old caches without breaking the existing functionality. The service worker's lifecycle should update the cache (the river) without destroying the app's ability to function (the stones).

## Finding: Real, uncounted module scope

The module's own `ASSIGNMENT.md` includes a full, numbered, assessed Acceptance criterion for **CI/CD design** (Acceptance criterion 4): "A GitHub Actions workflow on the student branch gates lint, typecheck, unit, component, and E2E tests with a wall-clock budget under five minutes (Unit 5's own budget, reused verbatim). The workflow has **no deploy job** and references **no secret**." This is a separate learning outcome and is not covered by any board row or tasks.md prose for Team 4. It should be addressed in a separate task or as part of the broader CI/CD setup, not absorbed into this task.