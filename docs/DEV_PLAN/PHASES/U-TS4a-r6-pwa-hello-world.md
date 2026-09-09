<!--
Self-contained runbook. Derived from PHASE-U-FEII-TEACHING-SKELETON-CASCADE.md §2, §5 TS4,
PHASES/R6-pwa-cicd-audit.md (re-scoped — see §0), and PHASE-U-WEEK0-ORCHESTRATION.md — that
orchestration document is normative; regenerate this one if it changes. Generated as part of the
Week-0 skeleton-generator pass.
-->

# Phase U · TS4a — R6 PWA/local-operations hello-world seam

**Mode:** student lane (or instructor-built if executed before cohort start), 1 owner — may run
parallel to all of TS3
**Entry:** TS1 `DONE`
**Exit:** a minimal service-worker registration stub, an installable manifest, and one observable
local/offline boundary — explicitly **not** the full `PHASES/R6-pwa-cicd-audit.md` scope

---

## 0. What this phase is, and what it deliberately is not

**This is not the same document as `PHASES/R6-pwa-cicd-audit.md`.** That runbook targets the rich
instructor reference: Scaleway `stg` deployment, real API tokens and SSH keys in GitHub Actions
secrets, a signed deploy-decision record, Linux CI evidence for a production pipeline. **None of
that belongs in the FE II student artifact.** Per that same document's own §2.4, production
secrets are "instructor-only, never distributed," and Phase U's own hello-world contract (§2) puts
"caching strategy, installability quality, offline queue policy, performance budgets, CI/CD design
and evidence" in the *student assignment depth* column — meaning students build a **local**
CI/CD workflow (lint, typecheck, test, no deploy job) as their assignment, not a deployment
pipeline as their starting scaffold.

Read this distinction twice before starting: this phase provides the smallest possible
**stub** — enough to observe and discuss a local/offline boundary — not a working offline app.
Phase U §5 TS4 says it directly: "Do not build the full PWA, performance programme, CI/CD
solution, or test matrix for students."

**No `public/sw.js` exists on `main` today** (confirmed by direct search of the reference build)
— there is nothing to reduce here, only a stub to add, unlike TS3a/b/c's subtraction work.

## 1. Required reading

- `PHASE-U-FEII-TEACHING-SKELETON-CASCADE.md` §2 (R6's row — read this over
  `PHASES/R6-pwa-cicd-audit.md`'s own scope, which is for the rich reference, not this seam).
- `PHASES/R6-pwa-cicd-audit.md` §2.1–§2.4 only, for the non-negotiable boundaries that still apply
  even at hello-world depth (no cloud AI, no heavy external DB, secrets discipline) — skip its §3
  onward (deploy-specific scope) entirely.
- `caddy/Caddyfile` line 11 — the `@serviceWorker path /sw.js` route already reserved, confirming
  the infrastructure expects this file to eventually exist.
- `services/frontend/src/lib/db.ts` — the `OfflineLogEntry` mechanism this seam's stub may
  reference (read-only; TS3c's own lane decides what still calls it).

## 2. Non-negotiable boundaries

- **Work on `skeleton/ts4a-r6`, forked from `skeleton/ts1-contracts`.**
- **No deploy job, ever, in this lane's output.** No `.github/workflows/deploy.yml`, no Scaleway
  reference, no secret of any kind.
- **No Lighthouse CI gate at this stage** — that is explicitly student assignment depth (§2's
  "performance budgets"), not part of the seam being provided.
- **Do not edit `lib/db.ts`.** If the stub needs to reference `OfflineLogEntry`, import the type,
  do not modify the file that defines the sync mechanism — that coordination is TS3c's call (see
  `PHASES/U-TS3c-r5-oracle-hello-world.md` §0).
- **Do not touch the backend or Caddy's TLS/port configuration.** The `/sw.js` route rule already
  exists in `caddy/Caddyfile`; confirm it, do not duplicate or change it.

## 3. Domain contract slice

No new types. This seam may reference (not redefine) `OfflineLogEntry` from `domain.ts` if the
stub demonstrates queuing at all — Phase U's contract only requires "one observable local/offline
boundary," which can be satisfied by a service worker that logs a cache-hit/miss to the console or
renders a visible offline banner, without necessarily wiring a full queue-flush cycle.

## 4. Scope — what this seam adds

1. **`services/frontend/public/sw.js`** — a minimal service worker: register, log its lifecycle
   events (`install`, `activate`, `fetch`), and cache exactly one static asset as a proof of
   concept (Cache-First). Explicit stub: comment clearly in the file that Cache-First for the full
   static asset set and Network-First for `/api/*` are the assignment, not implemented here.
2. **Registration** — a small script (in the page shell or a dedicated module) calling
   `navigator.serviceWorker.register('/sw.js')`, gated behind a feature check so it never breaks a
   browser without SW support.
3. **PWA manifest stub** — `manifest.webmanifest` with name, one icon, theme color, `display:
   "standalone"` — enough for "Add to Home Screen" to appear, not a polished install experience.
4. **One observable boundary** — a visible, honest UI element (e.g. an "Offline" banner using
   `navigator.onLine` and the `online`/`offline` events) that a learner can toggle in devtools and
   see change — this is the "one observable local/offline boundary" Phase U's contract names.
5. **`ASSIGNMENT.md`** (new, `services/frontend/public/ASSIGNMENT.md` or alongside the manifest):
   learning outcomes (service worker lifecycle, caching strategies, installability, CI/CD design),
   constraints (must extend, not replace, the `OfflineLogEntry` mechanism if queuing is added;
   must respect the existing `/sw.js` Caddy route — do not change its cache headers), acceptance
   criteria (Cache-First static / Network-First `/api/*`, offline queue flush on reconnect,
   install manifest passes Lighthouse's installability check, a CI workflow gating lint/typecheck/
   unit/component/E2E under 5 minutes wall-clock — reused verbatim from Unit 5's own budget),
   prohibited shortcuts (no framework-generated black-box service worker without documenting that
   choice explicitly, no deploy job of any kind).

## 5. Mechanical gates

| Gate | Required proof |
| --- | --- |
| SW registers | devtools Application panel shows the service worker registered and activated |
| One cache proof | at least one asset is served from cache on a repeat load (visible in devtools Network panel) |
| Manifest valid | browser install prompt / "Add to Home Screen" is available |
| Boundary observable | toggling devtools Network to "Offline" visibly changes the UI |
| No deploy content | no file under `.github/workflows/` created by this lane references a secret or a deploy step |
| `lib/db.ts` untouched | `git diff main -- services/frontend/src/lib/db.ts` empty |
| Caddy untouched | `git diff main -- caddy/Caddyfile` empty |

## 6. Rollback and mutation law

- Nothing in this seam touches `ttod.yml`, `schema/`, `ttod_core/`, or any backend service.
- If the stub's cache list ever includes an API response, it must be Network-First (fetch, fall
  back to cache), never Cache-First for anything under `/api/*` — even a stub must not teach the
  wrong default.

## 7. Touched-path budget

**Allowed:** `services/frontend/public/sw.js` (new), `services/frontend/public/manifest.webmanifest`
(new), a small registration snippet in `services/frontend/src/layouts/Page.astro` (additive only —
coordinate with TS3a if this file is also touched there, per TS1's overlap check), a new
`ASSIGNMENT.md`.

**Forbidden:** `.github/workflows/deploy.yml` or any file referencing a secret, `lib/db.ts`,
`caddy/Caddyfile`, anything under `components/graph/`, `components/oracle/`,
`services/backend/**`, `services/mcp/**`.

## 8. Post-phase review

A second reader confirms the stub is genuinely a stub — it should not accidentally already satisfy
the full assignment (a stub that already does Cache-First/Network-First correctly for the whole
app leaks the answer, exactly the failure mode Phase U §2 warns about: "a starter is too rich if it
satisfies the corresponding assessed acceptance criteria without meaningful student design").

## 9. Phase report status enum

- **DONE** — all §5 gates pass, `ASSIGNMENT.md` filed, no deploy content anywhere in the branch.
- **PARTIAL** — name exactly which gate is unmet.
- **BLOCKED** — TS1 has not filed `DONE`.

## 10. Exact commands

```bash
cd /Users/ruvebal/src/ttod
git worktree add ../ttod-skeleton-ts4a -b skeleton/ts4a-r6 skeleton/ts1-contracts
cd ../ttod-skeleton-ts4a/services/frontend
npm run build && npm run preview
# open devtools > Application > Service Workers, confirm registration; toggle Network > Offline
```

## 11. Report requirements

File `docs/DEV_PLAN/PHASE-U-TS4a-REPORT.md`: status (§9), confirmation no deploy-related
file or secret reference exists anywhere in the branch, a real devtools screenshot showing SW
registration and one cached asset, and the `ASSIGNMENT.md` content.

## 12. Agent prompt — paste this into a fresh agent session with no other file open

```text
Act as TTOD Phase U TS4a engineer. Work only inside a new git worktree on branch skeleton/ts4a-r6,
forked from skeleton/ts1-contracts (never main). This runbook
(docs/DEV_PLAN/PHASES/U-TS4a-r6-pwa-hello-world.md) is self-contained.

CRITICAL: do not follow docs/DEV_PLAN/PHASES/R6-pwa-cicd-audit.md's scope — that document targets
a rich instructor reference with a real Scaleway deployment and production secrets. None of that
belongs here. Build only a minimal stub: no deploy workflow, no secrets, no Lighthouse CI gate.

Confirm no public/sw.js exists yet on main (it doesn't) — you are adding a stub, not reducing
existing code. Create services/frontend/public/sw.js: register/install/activate/fetch lifecycle
logging, and cache exactly one static asset as a Cache-First proof of concept — comment clearly
that the full Cache-First-static/Network-First-API policy is the student assignment, not
implemented here. Add a small feature-checked registration call
(navigator.serviceWorker.register) somewhere sensible in the page shell. Add
services/frontend/public/manifest.webmanifest with name, one icon, theme color, and
display: "standalone". Add one visible UI element that changes based on navigator.onLine / the
online and offline events, so toggling devtools Network to Offline is observable.

Do not edit services/frontend/src/lib/db.ts or caddy/Caddyfile at all. Do not create any
.github/workflows file that references a secret or includes a deploy step.

Write services/frontend/public/ASSIGNMENT.md (or alongside the manifest): learning outcomes
(service worker lifecycle, caching strategies, installability, CI/CD design), constraints (extend
rather than replace OfflineLogEntry if queuing is added; respect the existing Caddy /sw.js route
without changing its headers), acceptance criteria (real Cache-First/Network-First split, offline
queue flush, Lighthouse installability pass, a sub-5-minute CI workflow per Unit 5's budget),
prohibited shortcuts (no black-box generated SW without documenting the choice, no deploy job).

Verify via devtools: the service worker registers and activates, one asset is served from cache on
a repeat load, the manifest enables an install prompt, and toggling Network to Offline visibly
changes the UI.

File docs/DEV_PLAN/PHASE-U-TS4a-REPORT.md with status (DONE/PARTIAL/BLOCKED per this
runbook's §9), confirmation no deploy content exists anywhere in the branch, a devtools screenshot,
and the ASSIGNMENT.md content.
```
