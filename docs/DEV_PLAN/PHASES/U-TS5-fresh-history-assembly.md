<!--
Self-contained runbook. Derived from PHASE-U-FEII-TEACHING-SKELETON-CASCADE.md §5 TS5,
PHASE-U-WEEK0-ORCHESTRATION.md exit, and PHASE-U-WEEK0-REPORT.md closeout leftovers.
-->

# Phase U · TS5 — Assemble the teaching baseline (hello-world integration + fresh-history gate)

**Mode:** single orchestrator, sequential — consumes all Week-0 lane tips  
**Entry:** TS1–TS4c `DONE` on their `skeleton/*` branches (see `PHASE-U-WEEK0-REPORT.md` closeout)  
**Exit (minimum for Week 1):** one branch `skeleton/ts5-hello-world` that contains every hello-world
seam, green `npm run check` + build, leftover decisions recorded.  
**Exit (full TS5):** that tree re-rooted as a fresh-history archive with privacy + isolation probes
green — may file `PARTIAL` if only the minimum exit lands tonight.

---

## 0. Leftover decisions (frozen for this pass)

From `PHASE-U-WEEK0-REPORT.md` / `PHASE-U-TS1-REPORT.md` addenda:

| Leftover | Decision |
| --- | --- |
| TS4c `User` / `UserRole` / `FavoriteEntry` | **Accept** into the assembled `domain.ts` |
| 460-node graph sample | **No client-side cap** — keep honest full sample; performance = assignment depth (R4) |
| `OracleTerminal.test.tsx` | **Rewrite or drop** tests that expect queue/propose/themes UI |
| `Page.astro` (TS4a) + `Page.shell.test.ts` (TS4b) | **Keep both** — SW registration + offline banner from TS4a; shell test must still pass |

---

## 1. Non-negotiable boundaries

- Do **not** merge into `main`. `main` stays the rich instructor reference.
- Do **not** mutate `ttod.yml` / `ttod_core` / `schema` except via existing governed paths (none expected here).
- Worktrees only. Preferred base: `skeleton/ts1-contracts` @ tip, then merge lane tips in order.
- Reports land on the TS5 branch (and may be copied to `main` later via a docs PR).

## 2. Merge order

```text
skeleton/ts1-contracts
  → ts3a-r3b → ts3b-r4 → ts3c-r5
  → ts4a-r6 → ts4b-r7 → ts4c-auth
  = skeleton/ts5-hello-world
```

## 3. Mechanical gates (minimum exit)

| Gate | Proof |
| --- | --- |
| Facets gone | no `wisdom/sections|tags|levels` on branch |
| Graph reduced | no `gsap` / `filterGraph` / `activeTag` in `GraphIsland.svelte` |
| Oracle reduced | no `enqueueOracleQuery` / `propose(` in `OracleTerminal.tsx` |
| PWA stub | `public/sw.js` + manifest present |
| Auth stub | `auth.server.ts` + `/account` routes present |
| Types | `domain.ts` includes Auth types |
| Check/build | `npm run check` + `npm run build` green in `services/frontend` |

## 4. Full TS5 (may be PARTIAL)

- Fresh orphan history / cohort archive (see `scripts/generate-cohort-starter.sh` for precedent).
- Privacy watcher zero findings on the distributed tree.
- Isolation probes: rich reference unreachable from student artifact.
- TS2 (tag/checksum rich reference) if not already done.

## 5. Report

File `docs/DEV_PLAN/PHASE-U-TS5-REPORT.md` with status `DONE` / `PARTIAL` / `BLOCKED`, merge
SHAs, leftover resolutions, and exact commands run.
