# Phase U · TS5 report — hello-world assembly (minimum exit)

**Status:** `PARTIAL`  
**Date:** 2026-09-09  
**Branch:** `skeleton/ts5-hello-world`  
**Worktree:** `/Users/ruvebal/src/ttod-skeleton-ts5`  
**Runbook:** [`PHASES/U-TS5-fresh-history-assembly.md`](PHASES/U-TS5-fresh-history-assembly.md)

`main` was not touched. Full TS5 (orphan fresh history, privacy watcher, isolation probes, TS2
rich-reference tag) remains open.

---

## 1. What landed (Week-1 minimum)

All seven Week-0 lane tips were merge-assembled onto `skeleton/ts5-hello-world` (base
`skeleton/ts1-contracts` @ `47f15da9`) in order:

`ts3a-r3b` → `ts3b-r4` → `ts3c-r5` → `ts4a-r6` → `ts4b-r7` → `ts4c-auth`

Every merge was clean (ort, no conflict resolution). Tip after assembly + Oracle test rewrite:

| Ref | SHA |
| --- | --- |
| Merge tip (pre-test fix) | `5acd0e5e` |
| Runbook commit | `528092c4` |
| Final tip | `3021be4c` (+ this docs fix if amended further — prefer `git rev-parse skeleton/ts5-hello-world`) |

### Leftover resolutions

| Leftover | Decision | Evidence |
| --- | --- | --- |
| TS4c `User` / `UserRole` / `FavoriteEntry` | **Accept** | present in `services/frontend/src/types/domain.ts` |
| 460-node graph sample | **No client-side cap** | unchanged from TS3b; performance = R4 assignment depth |
| `OracleTerminal.test.tsx` | **Rewrite** for hello-world | queue/propose assertions removed; stream + error path covered |
| `Page.astro` + `Page.shell.test.ts` | **Keep both** | TS4a SW/offline banner + TS4b shell test; vitest green |

---

## 2. Mechanical gates

| Gate | Result |
| --- | --- |
| Facet routes gone | no `wisdom/sections|tags|levels` |
| Graph reduced | no `gsap` / `filterGraph` / `activeTag` in `GraphIsland.svelte` |
| Oracle reduced | no `enqueueOracleQuery` / `propose(` in `OracleTerminal.tsx` |
| PWA stub | `public/sw.js` + `manifest.webmanifest` |
| Auth stub | `auth.server.ts` + `/account` routes + backend `auth.py` |
| Auth types on `domain.ts` | yes |
| `npm run check` | 0 errors |
| `npm run build` | Complete |
| `npm test` (vitest) | 4 files / 8 tests passed |
| Backend auth suite | `PYTHONPATH=. pytest services/backend/tests/test_backend.py` → 10 passed |

---

## 3. Still open (full TS5 / Week-0 programme)

1. **Fresh-history archive** — orphan / cohort-starter style re-root (see
   `scripts/generate-cohort-starter.sh` precedent); not done tonight.
2. **TS2** — tag/checksum rich instructor reference outside student reach.
3. **Privacy watcher** + isolation probes against the distributed tree.
4. **Push** `skeleton/ts5-hello-world` (and optionally remaining lane tips) to origin.
5. **Do not merge** this branch into `main` as an ordinary PR — `main` stays the rich reference.

---

## 4. Commands run

```bash
git worktree add ../ttod-skeleton-ts5 -b skeleton/ts5-hello-world skeleton/ts1-contracts
# merge ts3a → ts3b → ts3c → ts4a → ts4b → ts4c (all clean)
cd services/frontend && npm ci && npm test && npm run check && npm run build
cd ../.. && PYTHONPATH=. services/backend/.venv/bin/python -m pytest services/backend/tests/test_backend.py -q
```

---

## 5. Product-owner note

§5 of `PHASE-U-WEEK0-ORCHESTRATION.md` was confirmed unblocked (approve / Week 1 = 2026-09-10 /
delegate). This report is the first TS5 assembly evidence for that Week 1 start — a working
teaching tree on `skeleton/ts5-hello-world`, not yet the history-isolated student archive.
