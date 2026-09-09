<!--
Phase U TS4a report — R6 PWA/local-operations hello-world seam.
Follows cascade-forge evidence-state discipline (status first; claims checked live).
Executed on branch skeleton/ts4a-r6, worktree /Users/ruvebal/src/ttod-skeleton-ts4a,
forked from skeleton/ts1-contracts@47f15da9. Never touched main.
-->

# Phase U · TS4a Report — R6 PWA hello-world stub

**Status:** DONE

**Scope executed:** the five seam additions named in
[`PHASES/U-TS4a-r6-pwa-hello-world.md`](PHASES/U-TS4a-r6-pwa-hello-world.md) §4 — `public/sw.js`,
feature-checked registration in `layouts/Page.astro`, `manifest.webmanifest`, one visible
online/offline boundary, and `ASSIGNMENT.md` — plus the §11 evidence file.

**Date:** 2026-09-09

**Implementer:** this session (TS4a engineer), worktree only

**Independent verifier:** pending

**Owner:** `@crea-comm.net`

**Explicit non-scope (confirmed):** this lane did **not** follow
[`PHASES/R6-pwa-cicd-audit.md`](PHASES/R6-pwa-cicd-audit.md) from §3 onward. No deploy workflow,
no Scaleway reference, no GitHub secret, no Lighthouse CI gate.

---

## 1. Entry gate

TS1 is filed **DONE** (`PHASE-U-TS1-REPORT.md`). Branch created as specified:

```text
cd /Users/ruvebal/src/ttod
git worktree add ../ttod-skeleton-ts4a -b skeleton/ts4a-r6 skeleton/ts1-contracts
# HEAD 47f15da9  TS1: run CI on skeleton/** branches, not only main.
```

`public/sw.js` did not exist on `main` (or on the TS1 fork). This lane added a stub; it did not
reduce existing PWA code.

## 2. What landed

| Path | Change |
| --- | --- |
| `services/frontend/public/sw.js` | **new** — `install` / `activate` / `fetch` logging; Cache-First for exactly `/visual-system/tokens.css`; `/api/*` explicitly skipped; comment that full Cache-First-static / Network-First-API is the assignment |
| `services/frontend/public/manifest.webmanifest` | **new** — name, one icon (`/visual-system/favicon.svg`), theme `#fbf8f1`, `display: standalone` |
| `services/frontend/public/ASSIGNMENT.md` | **new** — outcomes, constraints, acceptance criteria, prohibited shortcuts |
| `services/frontend/src/layouts/Page.astro` | **additive** — manifest link, feature-checked `navigator.serviceWorker.register('/sw.js')`, sticky network banner driven by `navigator.onLine` + `online`/`offline` |

**Untouched, as required:**

| Check | Result |
| --- | --- |
| `git diff main -- services/frontend/src/lib/db.ts` | empty |
| `git diff main -- caddy/Caddyfile` | empty |
| `git diff skeleton/ts1-contracts -- .github/` | empty — this lane created no workflow |
| Caddy `@serviceWorker path /sw.js` + `Cache-Control: max-age=0, no-cache` | confirmed present at `caddy/Caddyfile` lines 11–12; not edited |

`caddy/Caddyfile` already reserved `/sw.js`. The stub uses that path.

## 3. Confirmation — no deploy, no secrets, no Lighthouse CI

This lane's diff does not add or modify any file under `.github/workflows/`.

Inherited workflows from TS1/`main` (`ci.yml`, `public-docs-pages.yml`) were not edited. No
`deploy.yml` was created. No `secrets.*`, Scaleway, SSH key, or Lighthouse CI reference exists in
any file this lane added (the only mentions of secrets/deploy/Lighthouse are **prohibitions** in
`ASSIGNMENT.md`).

## 4. Mechanical gates (§5) — live evidence

Verification command (the runbook's `npm run preview` is not a script in this package; the Node
adapter's `npm start` is the equivalent). Home (`/en/`) SSR-fetches the backend, so the check used
`/en/docs/`, which still goes through `Page.astro` and does not need the API:

```text
cd services/frontend
npm run check   # 0 errors
npm run build
HOST=127.0.0.1 PORT=4334 npm start
# open http://127.0.0.1:4334/en/docs/
```

| Gate | Result |
| --- | --- |
| SW registers | **pass** — `navigator.serviceWorker.ready` → `http://127.0.0.1:4334/sw.js`, state `activated`; controller is that script; scope `/` |
| One cache proof | **pass** — Cache Storage `ttod-pwa-stub-v1` holds exactly `http://127.0.0.1:4334/visual-system/tokens.css`. Repeat fetch: Resource Timing `transferSize: 0`, `encodedBodySize: 1017`, `workerStart > 0` (service worker served the body; no network bytes) |
| Manifest valid | **pass at stub depth** — `GET /manifest.webmanifest` → 200 `application/manifest+json`; Chromium `Page.getAppManifest` parsed `display: kStandalone`, name TTOD, theme paper; `Page.getInstallabilityErrors` returned `[]`. Automation did not photograph a native install-prompt chrome; Lighthouse's full icon-size check remains **assignment** depth (the stub's single SVG is named as insufficient in `ASSIGNMENT.md`) |
| Boundary observable | **pass** — CDP `Network.emulateNetworkConditions({offline:true})` flipped the banner from online (light) to offline (ink). Screenshots: [`evidence/ts4a-online-banner.png`](evidence/ts4a-online-banner.png), [`evidence/ts4a-offline-banner.png`](evidence/ts4a-offline-banner.png) |
| No deploy content | **pass** — §3 |
| `lib/db.ts` untouched | **pass** — §2 |
| Caddy untouched | **pass** — §2 |

CDP dump (Application-panel equivalent; the automation browser does not expose DevTools UI):

```json
{
  "controller": "http://127.0.0.1:4334/sw.js",
  "readyState": "activated",
  "registration": {
    "scope": "http://127.0.0.1:4334/",
    "scriptURL": "http://127.0.0.1:4334/sw.js",
    "state": "activated",
    "installing": false,
    "waiting": false
  },
  "cacheKeys": ["ttod-pwa-stub-v1"],
  "cachedAssets": ["http://127.0.0.1:4334/visual-system/tokens.css"],
  "manifestHref": "http://127.0.0.1:4334/manifest.webmanifest"
}
```

The stub still does **not** Cache-First the rest of the static set, does **not** Network-First
`/api/*`, and does **not** flush `OfflineLogEntry`. That is intentional: a starter that already
satisfied those criteria would leak the assignment (Phase U §2 / this runbook §8).

## 5. `ASSIGNMENT.md`

Filed at [`services/frontend/public/ASSIGNMENT.md`](../../services/frontend/public/ASSIGNMENT.md).
Reproduced in full:

```markdown
# Assignment — PWA / local operations (R6)

This repository ships a **hello-world stub**: one service worker, one installable
manifest, and one visible online/offline banner. It is enough to observe a
local/offline boundary. It is **not** a finished PWA, performance programme, or
CI/CD pipeline.

Read `public/sw.js` before you start. Comments in that file name what is
deliberately unimplemented.

## Learning outcomes

After this assignment you can:

1. **Service-worker lifecycle** — explain `install`, `activate`, and `fetch`,
   and show where your worker claims clients and updates its cache name.
2. **Caching strategies** — choose and implement Cache-First for static assets
   and Network-First for `/api/*`, and justify why API responses must not be
   Cache-First.
3. **Installability** — produce a manifest that a Chromium browser treats as
   installable (Add to Home Screen / install prompt), including icon sizes
   Lighthouse actually checks.
4. **CI/CD design** — design a *local* quality gate (lint, typecheck, unit,
   component, E2E) that stays under Unit 5's five-minute wall-clock budget.
   There is **no deploy job** in this course artifact.

## Constraints

- **Extend, do not replace, `OfflineLogEntry`.** If you add an offline queue,
  reuse the existing type in `src/types/domain.ts` and the IndexedDB helpers in
  `src/lib/db.ts`. Do not invent a second queue, and do not edit the domain
  freeze without a documented contract change.
- **Respect the existing Caddy `/sw.js` route.** `caddy/Caddyfile` already
  matches `@serviceWorker path /sw.js` and sets
  `Cache-Control: max-age=0, no-cache`. Do not change those headers, duplicate
  the matcher, or serve the worker from a different path.
- **No cloud AI, no heavy external database, no production secrets.** The
  walking-skeleton stack needs none of those for local PWA work.
- **Keep the stub honest.** Do not silently finish the whole assignment in a
  "small refactor" of `sw.js` without documenting the design you chose.

## Acceptance criteria

Your work is done when all of the following are true:

1. **Cache-First static / Network-First API.** The service worker applies
   Cache-First to the static asset set the app needs to render offline, and
   Network-First (network, then cache fallback) to `/api/*`. A repeat load of a
   static asset is served from Cache Storage; an API call still hits the
   network when it is available.
2. **Offline queue flush on reconnect.** Work queued while offline (at least
   Oracle queries via `OfflineLogEntry`) is flushed when `online` fires or the
   service worker observes a restored network. Do not drop the existing
   `synced` flag semantics.
3. **Installability.** The web app manifest passes Lighthouse's installability
   check (name, display `standalone`, theme color, and the icon sizes that
   check requires — the stub's single SVG is not enough).
4. **CI under five minutes.** A GitHub Actions workflow on the student branch
   gates lint, typecheck, unit, component, and E2E tests with a wall-clock
   budget under five minutes (Unit 5's own budget, reused verbatim). The
   workflow has **no deploy job** and references **no secret**.

## Prohibited shortcuts

- No framework-generated black-box service worker (`astro-offline`, Workbox
  injectManifest with an opaque preset, etc.) unless you document that choice
  in this file and can still explain every caching decision in your own words.
- No deploy job of any kind: no Scaleway, no SSH keys, no `deploy.yml`, no
  GitHub `secrets.*` in a workflow this assignment adds.
- No Lighthouse CI gate that fails the pipeline on performance budgets until
  you have designed those budgets yourself (that *is* part of the assignment;
  it is not part of the starter).
- No Cache-First for `/api/*`, even "just for the stub."
- Do not edit `caddy/Caddyfile` to make the worker easier to cache.

## Starter inventory (do not delete)

| Path | Role |
| --- | --- |
| `public/sw.js` | Lifecycle logging + Cache-First for `/visual-system/tokens.css` only |
| `public/manifest.webmanifest` | Name, one icon, theme color, `display: standalone` |
| `src/layouts/Page.astro` | Feature-checked `navigator.serviceWorker.register('/sw.js')` and the online/offline banner |
| `src/lib/db.ts` | Existing `OfflineLogEntry` queue — read and extend, do not rewrite |
| `caddy/Caddyfile` | `/sw.js` is already reserved with `no-cache` — leave it |
```

## 6. Lessons for the next phase

- `Page.astro` is the shared shell. TS3a should treat the manifest link, SW registration, and
  network banner as already present and not rebase them away.
- The home page still depends on a live backend. PWA checks that only load `/en/` will fail for
  the wrong reason (SSR fetch), not because the worker is missing. `/en/docs/` is the honest
  no-API seam for this stub.
- Chromium accepted the SVG icon with empty installability errors; Lighthouse's 192/512 PNG
  requirement is left as assignment depth on purpose.

## 7. `ttod.yml`

Unchanged. No canonical mutation.
