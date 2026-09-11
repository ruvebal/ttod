---
title: "Cache-first vs. network-first policy for the right routes"
seam: offline
team_number: 4
team_name: "offline"
task_number: 3
area: "PWA/Offline"
verb: keep
layout: default
lang: en
alt_lang_missing: true
---

# Assignment — Team 4, Task 3: Cache-first vs. network-first policy for the right routes

**Seam:** offline · **Team:** 4 · **Task:** 3 of ~10
**Area(s):** PWA/Offline · **Verb served:** keep

## 1. Curriculum map

This task exercises the core concepts of **Unit 5 — Testing strategy** (specifically the verification of runtime behavior in offline conditions) and the broader PWA lifecycle concepts covered in the web-atelier-udit FE II curriculum. While the specific "Caching Strategies" unit link is not yet published in the `assignments.md` "Lessons for these tasks" section, the functional verification of cache behavior is a direct application of the testing principles established in Unit 5.

## 2. Worked example, from the real TTOD app

The starter code in `services/frontend/public/sw.js` already implements a minimal, correct instance of this pattern. It defines `CACHE_NAME='ttod-pwa-stub-v1'` and implements a `fetch` event listener that applies **Cache-First** logic exclusively to the asset `/visual-system/tokens.css` (referenced as `PROOF_ASSET`). This file demonstrates the exact mechanism you must extend: checking the cache first, falling back to the network if the cache is empty, and updating the cache with the network response. Your task is to generalize this specific, single-asset logic into a policy that correctly distinguishes between static assets and API routes, while preserving the existing behavior for `tokens.css`.

## 3. What "done" looks like

**Visible result:**
Static assets (CSS, JS, images) load instantly from the Cache Storage API on subsequent visits, even when the network is slow or unavailable. API responses (e.g., `/api/*`) are always fetched from the network when available, ensuring data freshness, and only fall back to a cached version if the network request fails.

**What it includes:**
- An updated `fetch` handler in `services/frontend/public/sw.js` that inspects the request URL.
- A **Cache-First** strategy applied to static asset paths (e.g., `/visual-system/*`, `/assets/*`).
- A **Network-First** strategy applied to `/api/*` paths.
- Explicit exclusion of `/api/*` routes from the Cache-First logic, preventing stale data from being served when the network is available.
- Documentation of the chosen strategy in the code comments, explaining why API responses must not be Cache-First.

**What has to be done:**
1. Read `services/frontend/public/sw.js` fully. Note the existing `fetch` listener and the `PROOF_ASSET` constant.
2. Modify the `fetch` event listener to check the request URL.
3. Implement a helper function or inline logic to determine if a request is a static asset or an API call.
4. For static assets: Use the existing Cache-First logic (cache first, then network, then update cache).
5. For API calls: Implement Network-First logic (network first, then cache fallback).
6. Ensure the existing `tokens.css` behavior remains unchanged (it is a static asset and should remain Cache-First).
7. Test the behavior by toggling network conditions in the browser DevTools (Offline/Slow 3G) and verifying that static assets load from cache while API calls attempt the network first.

## 4. Success criteria (functional)

- **Cache-First static / Network-First API.** The service worker applies Cache-First to the static asset set the app needs to render offline, and Network-First (network, then cache fallback) to `/api/*`.
- **Repeat load of a static asset is served from Cache Storage.** When a static asset is requested a second time, the response is served from the Cache Storage API without hitting the network.
- **API call still hits the network when it is available.** When an API endpoint is requested and the network is available, the response is fetched from the network, not from the cache.
- **No Cache-First for `/api/*`.** API responses are never served from the cache when the network is available, preventing stale data.

## 5. Quality criteria (the part that's new)

- **Code organization:** The caching logic should be modular and readable. Avoid duplicating the cache-check logic; use helper functions or clear conditional branches.
- **AI-use/process documentation:** If you use AI assistance to generate the caching logic, document the specific prompt and the reasoning behind the chosen strategy in your commit message or a local note. You must be able to explain every caching decision in your own words during the oral defense.
- **Test shape:** Per the Testing Trophy (not Pyramid) doctrine, write integration tests that verify the end-to-end behavior of the service worker in an offline/online scenario. Unit tests for the helper functions that determine the caching strategy are also appropriate. Link [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/) for guidance on testing service workers.
- **Accessibility:** This task inherits the global Definition of Done: keyboard-operable, one accessible name or label, no meaning carried by color alone, respects reduced-motion preferences. While caching is a backend concern, ensure that the offline banner (rendered in `Page.astro`) remains accessible and correctly reflects the network state.
- **Oral defense:** Be prepared to explain why Cache-First is appropriate for static assets but dangerous for API responses. Discuss the trade-offs of Network-First vs. Stale-While-Revalidate and why you chose Network-First for this task.

## Closing

> "Verify Before You Fix - Not every symptom is a disease."
> — TTOD `arch-027`, *architecture*

This task requires you to verify the actual runtime behavior of the service worker in different network conditions before assuming that a caching strategy is working correctly. The "symptom" of slow loading or stale data is not always a bug in the code; it may be a misconfiguration of the caching policy. Trust the code, verify the runtime.