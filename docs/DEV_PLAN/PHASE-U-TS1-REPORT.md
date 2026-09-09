<!--
Phase U TS1 report — subtraction contract, domain.ts freeze, CI skeleton.
Follows cascade-forge evidence-state discipline (status first; claims checked live).
Executed on branch skeleton/ts1-contracts, worktree ../ttod-skeleton-ts1, off main@f83fa908.
-->

# Phase U · TS1 Report — subtraction contract frozen

**Status:** DONE

**Scope executed:** the four TS1 deliverables named in
[`PHASES/U-TS1-subtraction-and-contracts.md`](PHASES/U-TS1-subtraction-and-contracts.md) §4 —
subtraction table, `domain.ts` freeze, CI skeleton, non-overlap confirmation — plus the two items
this report originally held at PARTIAL: the real GitHub Actions run on a pushed branch, and branch
protection on `main`.

**Date:** 2026-09-09 (the day before Week 1 starts)

**Implementer:** this session (orchestrator role — TS1 is contract/table/CI-skeleton work, not
student-facing application code; per `PHASE-U-WEEK0-ORCHESTRATION.md` §5's delegation note, the
actual hello-world *code* lanes TS3a–TS4c should be handed to local-Ollama-backed sessions, not
run by this session — see §6)

**Independent verifier:** pending

**Owner:** `@crea-comm.net`

---

## 1. Pre-flight — the dirty-tree blocker from PHASE-U-WEEK0-REPORT.md §6.1

Re-verified live before touching anything: `domain.ts` was still 62 working lines vs. 58 committed
on `main` (the same Oracle `locale`/`themes`/`tags` WIP the Week-0 report flagged, unchanged since
that report was filed). Reviewed the full diff (8 files, backend + frontend + tests, +223/-37) —
coherent, tested, not a scratch file: locale-aware Oracle prompts, thematic-anchor surfacing on
unmatched queries, an explicit "never a debugging assistant" system-prompt constraint, and a wider
FastMCP retrieval timeout for cold-index builds (directly relevant to `PHASE-TS0-REPORT.md`'s own
cold-start finding).

**Product-owner decision: commit it, then run TS1.** Committed as `f83fa908` on `main` — 8 files,
+223/-37. `domain.ts` is now honestly **62 lines on the committed tip**, and that is this report's
frozen baseline, not the original 58.

## 2. Domain contract — frozen at 67 lines on `skeleton/ts1-contracts` (`main` stays at 62)

Confirmed live in the worktree (`git worktree add ../ttod-skeleton-ts1 -b skeleton/ts1-contracts
main`, off `f83fa908`):

```text
$ wc -l services/frontend/src/types/domain.ts
62 services/frontend/src/types/domain.ts   # as committed to main (f83fa908)
```

All seven original interfaces (`WisdomEntry`, `GraphNode`, `GraphLink`, `OracleQueryPayload`,
`OracleResponseChunk`, `OracleProposeRequest`, `OfflineLogEntry`) are present, plus three
deliberate additions now part of the frozen contract:

| Interface | Added field | Type |
| --- | --- | --- |
| `OracleQueryPayload` | `locale` | `'en' \| 'es'` (optional) |
| `OracleResponseChunk` | `themes`, `tags` | `string[]` (optional, both) |
| `OracleProposeRequest` | `locale` | `'en' \| 'es'` (optional) |

**Post-freeze cleanup, on the branch only (`fec0e11b`):** per TS1's own §2 boundary — "any
`domain.ts` amendment... lands on a new branch... never committed to `main`" — a light DRY/
formatting pass landed on `skeleton/ts1-contracts` itself, not `main`: extracted the repeated
`'en' | 'es'` union into `export type Locale`, added three section-grouping comments (Wisdom &
graph / Oracle / Offline). Structurally identical contract (`Locale` *is* `'en' | 'es'` — no
consumer-visible change), re-verified via `npm run check` + `npm run build`, both clean. New line
count on the branch: **67**. Every later lane (TS3a–TS4c) forks from `skeleton/ts1-contracts`, not
`main` directly (confirmed — see each runbook's own §10), so this is the contract they inherit;
`main`'s 62-line version is undisturbed as the read-only reference.

**Consequence for TS3c:** `PHASES/U-TS3c-r5-oracle-hello-world.md`'s own domain-contract slice
explicitly deferred these fields ("no `locale`/`themes`/`tags` until TS1 deliberately freezes an
amended commit") — that condition is now true. TS3c's runbook should be read as including these
three fields in its hello-world contract before that lane opens. **Not yet edited into that file
by this report** — flagged here rather than silently amended, since TS3c's own author should
confirm the hello-world *keep* scope for `themes`/`tags` display, not just the type contract.

No other gap surfaced. `GraphNode`/`GraphLink`/`WisdomEntry`/`OfflineLogEntry` needed no changes.

## 3. CI skeleton — added and verified locally (not yet pushed for a real PR run)

Added `.github/workflows/ci.yml` on the worktree branch, styled after the existing
`public-docs-pages.yml` precedent (path-scoped triggers, explicit `permissions: contents: read`,
no secrets, no deploy step):

```yaml
name: Frontend — typecheck and build
on:
  pull_request: { paths: ["services/frontend/**", ".github/workflows/ci.yml"] }
  push: { branches: [main], paths: ["services/frontend/**", ".github/workflows/ci.yml"] }
  workflow_dispatch:
permissions:
  contents: read
jobs:
  typecheck-and-build:
    runs-on: ubuntu-latest
    defaults: { run: { working-directory: services/frontend } }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "22", cache: "npm", cache-dependency-path: services/frontend/package-lock.json }
      - run: npm ci
      - run: npm run check
      - run: npm run build
```

**Judgment call:** no `.nvmrc`/`engines` field pins a Node version anywhere in the repo — chose
`"22"` (current LTS, satisfies Astro 5's `>=18.20.8 / >=20.3.0 / >=22.0.0` requirement). No `lint`
script exists in `services/frontend/package.json` (only `dev`/`build`/`start`/`check`) — the
skeleton runs `npm run check` (Astro's own typecheck) in place of a separate lint step; TS4b (R7)
can add a real lint step later if one gets configured.

**Verified locally, in the worktree, on the amended `domain.ts`:**

```text
$ npm ci                 → 619 packages installed, 0 errors
$ npm run check           → Result (30 files): 0 errors, 0 warnings, 0 hints
$ npm run build           → build complete, server + client bundles emitted, no errors
```

**Real Actions run (2026-09-09 ignitor closeout, product-owner "go"):** branch
`skeleton/ts1-contracts` pushed; draft PR https://github.com/ruvebal/ttod/pull/1
(`typecheck-and-build` pass, 28s and 37s). **Do not merge that PR to `main`.** It is CI evidence
only. The public-docs `build` check also passed on the same PR because the branch is ahead of
`origin/main` by the already-committed local `main` tip; that is not a TS1 deliverable.

## 4. Subtraction table — grounded live in this worktree, not assumed from prior prose

For each seam, the exact symbol/route to remove and the one-sentence acceptance criterion that
becomes the student assignment. Re-verified against the live tree at `f83fa908` (all counts below
are freshly re-run, not copied from `PHASE-U-WEEK0-REPORT.md`):

### R3b — content (`services/frontend/src/pages/[locale]/wisdom/`)

Phase U §2 and `PHASES/U-TS3a-r3b-content-hello-world.md` §4 are the authority: hello-world is
**index + one detail**, both locales; taxonomy browsing is assignment depth. An earlier draft of
this table inverted that (kept the three facet routes). Corrected here before any TS3a session
opens, so a lane owner cannot inherit the wrong keep/cut.

| File | Lines | Cut for hello-world | Kept | Becomes assignment |
| --- | --- | --- | --- | --- |
| `index.astro` | 21 | nothing — already near hello-world depth | listing route, locale, empty-state | pagination/sort |
| `[slug].astro` | 19 | nothing — already near hello-world depth | detail route, locale guard | richer metadata / facet cross-links |
| `sections/[section].astro` | 10 | **Remove the file from the hello-world branch entirely** | — | section browse |
| `tags/[tag].astro` | 10 | **Remove the file** | — | tag browse |
| `levels/[level].astro` | 10 | **Remove the file** | — | level browse |
| `content/wisdom.ts` `frequencies()` | — | do not delete the function | keep unused | facet routes call it again |

**One-sentence acceptance criterion:** `/en/wisdom/` and `/es/wisdom/` plus one real detail page
render live backend data; `sections/`, `tags/`, and `levels/` directories do not exist on the
hello-world branch.

### R4 — graph (`components/graph/GraphIsland.svelte`, 104 lines)

| Symbol | Line(s) | Cut | Becomes assignment |
| --- | --- | --- | --- |
| `import { gsap } from 'gsap'` + its two call sites (entrance animation L32, `hover()` L40-41) | 3, 32, 40-41 | Yes | GSAP entrance/hover animation |
| `filterGraph`, `setTag`, `activeTag` `<select>` (L72) | 5, 25, 72 | Yes | tag-filter dropdown |
| `syncFromUrl` + `popstate` listener (L21, 45-46, 64) | 21, 45-46, 64 | Yes | URL-state synchronization |
| `.legend` block (markup L78 + CSS L100-102) | 78, 100-102 | Optional (cheap, already accessible via `<title>`) — keep unless the lane owner wants one more small cut | origin-color legend, if cut |
| `selectNode`, `<aside>` detail panel, `role="button"`/`tabindex`/`aria-label`/`onkeydown` on each node (L84) | kept throughout | **No — this is the hello-world contract itself** | — |

**One-sentence acceptance criterion:** fetch real graph data, lay it out via the existing
`radialLayout`, and let a user click exactly one node to see its text in an accessible `<aside>` —
no filter, no URL state, no GSAP.

### R5 — oracle (`components/oracle/OracleTerminal.tsx`, 325 lines + `sse.ts`, 63 lines)

Re-verified **after** the locale/themes/tags commit — `sse.ts` now also validates `themes`/`tags`
(§2), which is additive to the contract, not a new cut target.

| Symbol | Line(s) | Cut | Becomes assignment |
| --- | --- | --- | --- |
| `enqueueOracleQuery`, `flushQueue`, the `online`/`offline` listener (L149, 165, 186-190) | Yes | offline queue + flush-on-reconnect |
| `historyFrom`, `sessionHistory` wiring (L92, 214) | Yes | exchange-history context sent to the Oracle |
| `propose()` button + its saving/saved states (L293) | Yes | propose/escalation UI |
| `useReducedMotion` (`framer-motion`, L1, 104) | **No — accessibility baseline, instructor-provided** | — |
| One prompt in, one streamed response out, one cited-quote render | **No — this is the hello-world contract itself** | — |

**One-sentence acceptance criterion:** send one query, stream one response, render cited quote IDs
when grounded — no offline queue, no propose UI, no multi-turn history.

### R6 — PWA (new; `services/frontend/public/sw.js` confirmed absent)

**One-sentence acceptance criterion:** a manifest stub + minimal service-worker registration (or an
explicit stub contract if the lane owner defers the SW itself) exists and is reachable — full
Cache-First/Network-First policy and install-quality work is the assignment.

### R7 — testing (new; no test suite exists yet for this seam)

**One-sentence acceptance criterion:** one unit test, one component test, one route/contract smoke
test, and one accessibility assertion each exist and pass — risk-based strategy and full E2E
breadth is the assignment. This CI skeleton (§3) is exactly where TS4b plugs that fourth test layer
in next.

### TS4c — Auth (new module, no existing reference — confirmed, not assumed)

```text
$ find services/frontend/src -iname "*account*" -o -iname "*auth*"   → (nothing)
$ find services/backend/app -iname "*auth*"                          → (nothing)
```

Confirmed: nothing exists to subtract from. TS4c is a genuine new build per its own runbook — not
part of this subtraction table by construction.

## 5. Branch protection — applied 2026-09-09 (product-owner "go")

Applied on `main` via `gh api` (not on `skeleton/ts1-contracts`; that branch is a teaching
worktree, not the merge target):

- Require status checks to pass: `typecheck-and-build` (strict, so the branch must be up to date)
- Require 1 approving review; dismiss stale reviews
- `enforce_admins`: false (owner can still emergency-bypass; students cannot)
- Force pushes and deletions: disabled

Settings retrieved live after apply; `main` was previously unprotected.

**Addendum — 2026-09-09, later the same day: a real gap found and fixed.** Opening PR #2 (a sync
PR for 3 pre-existing commits on `main` unrelated to the teaching skeleton — see
`docs/DEV_PLAN/INDEX.md`'s Phase U row) surfaced that `.github/workflows/ci.yml` only ever existed
on `skeleton/ts1-contracts`, never on `main` itself. Branch protection requires the
`typecheck-and-build` check for *every* PR into `main` — including ordinary, teaching-unrelated
ones — but a PR whose branch doesn't contain that workflow file can never produce the check, so it
was stuck at commit-status `pending` forever, silently unmergeable. Fixed by adding the identical
`ci.yml` to `main` directly (commit `88eda966` on the sync PR branch) — confirmed live via `gh pr
checks 2`: `typecheck-and-build` went from absent to `pass` (52s) after the fix. This does not
change TS1's own rule that *contract amendments* (subtraction, `domain.ts`) stay off `main` — a
plain CI skeleton with no contract content is a different, ordinary repo-hygiene fix.

**Second addendum, same investigation: a deeper instance of the same bug class.** Opening PR #3
(the agentic pack — `.github/workflows/proposal-accept.yml`, PR template, `gh-review-queue.sh`,
none of which touch `services/frontend/**`) showed the fix above wasn't sufficient on its own:
`ci.yml`'s `pull_request` trigger was still **path-filtered** to `services/frontend/**`, so *any*
PR outside that path — not just ones missing the file entirely — would hit the identical
stuck-forever symptom. A required status check that's path-filtered simply never reports when the
paths don't match; GitHub does not treat that as "not applicable," it blocks the merge on a check
permanently stuck at "Expected." Fixed by dropping the `paths:` filter from `pull_request:`
entirely (commit `23fd310d` on the sync branch, `99da8557` added the same fix directly to PR #3's
own branch so it wasn't dependent on PR #2 merging first) — `push:` stays path-filtered since it
doesn't gate merges. Confirmed live: both PR #2 and PR #3 now show `typecheck-and-build pass`
(29s each). **Lesson for TS5 and any future required-check workflow: a required status check's
triggering event must never be path-filtered, only its job's actual work may be conditional.**

## 6. Non-overlap check — confirmed, live paths

| Lane | Primary edit target |
| --- | --- |
| TS3a (R3b) | `services/frontend/src/pages/[locale]/wisdom/**` |
| TS3b (R4) | `services/frontend/src/components/graph/GraphIsland.svelte` |
| TS3c (R5) | `services/frontend/src/components/oracle/OracleTerminal.tsx`, `sse.ts` |
| TS4a (R6) | `services/frontend/public/sw.js` (new), manifest |
| TS4b (R7) | new test files under each component's own directory; extends `.github/workflows/ci.yml` |
| TS4c (Auth) | `services/backend/app/auth.py` (new), `services/frontend/src/lib/auth.server.ts` (new), `[locale]/account/**` (new) — the only lane touching `services/backend/**` |

Zero shared primary-edit files. Soft coordination only: TS4a may add a registration snippet to
`layouts/Page.astro` (read, not owned, by every other lane); TS4b extends this report's `ci.yml`
additively.

## 7. Delegation note — what this session did vs. what should move to local Ollama

Per `PHASE-U-WEEK0-ORCHESTRATION.md` §5's own answer ("use local Ollama `qwen3.8:27b` as much as
possible, delegate workload"), and the workspace's own no-cloud-AI-for-shipped-work principle
(`/src/CLAUDE.md`): this session executed TS1 directly because its output is contract/table/CI-
skeleton work — the same category as every other planning document in this dev plan, not
student-facing application code. **TS3a/b/c and TS4a/b/c are different in kind** — they write the
actual hello-world code students will read and learn from — and should be handed to local-Ollama-
backed sessions per each runbook's own §12 paste-ready prompt, not run by this session. This report
does not open any of those lanes.

## 8. Explicit non-claims

This report does **not** claim:

- Draft PR #1 should be merged to `main` (it must not)
- TS3c's runbook file was left stale — the frozen `Locale` / `themes` / `tags` slice was applied
  in the ignitor closeout so TS3c sessions inherit the contract
- Any TS3/TS4 lane has been opened by *this report's original pass* (the ignitor closeout starts
  them separately)
- Phase U overall is DONE (still PROPOSED at programme level)

## 9. Resume rule

| Status | Meaning | Next action |
| --- | --- | --- |
| **DONE (current)** | Subtraction table, `domain.ts` freeze, CI green on PR #1, branch protection on `main`, no path overlap | Ignite TS3a (sequential among TS3) and TS4a/TS4b/TS4c (parallel, gated only on TS1). Hold TS3b/TS3c until TS3a files `DONE`. |
| **PARTIAL** | Named deliverable missing | Finish that deliverable before opening later lanes |
| **BLOCKED** | External dependency | Clear it; do not open later lanes |

---

## Addendum — 2026-09-09, TS4c contract amendment (not folded into the freeze yet)

`skeleton/ts4c-auth` @ `445f3257` added these types to `services/frontend/src/types/domain.ts` on
**that branch only**, as the runbook required (propose, do not assume they were already frozen):

- `UserRole` (`'student' | 'reviewer' | 'instructor'`)
- `User` (`id`, `email`, `displayName`, `role`)
- `FavoriteEntry` (`userId`, `quoteId`, `savedAt`)

The session cookie is still not a domain type. `skeleton/ts1-contracts` remains at 67 lines
without these. **TS5 assembly must either cherry-pick this amendment onto the freeze branch or
reject it** — it is not silently part of the TS1 freeze. Later TS3 lanes forked from
`skeleton/ts1-contracts` and do not have these types; that is expected.

## Addendum — 2026-09-09, TS3b graph-scale flag (no client-side cap)

`skeleton/ts3b-r4` @ `bfea9da7` kept `radialLayout(allNodes)` with no `filterGraph` and no
client-side truncation. Live `/en/graph/` against Compose `:18080` rendered **460 nodes / 665
edges** — the full sample, not Phase U §2's "tiny real node/edge neighborhood." Truncating in the
island would hide real data; a backend sample cap is a TS1/TS5 decision, not a TS3b one.

## Addendum — 2026-09-09, TS3c leftover rich-reference Oracle tests

`skeleton/ts3c-r5` @ `5a16a98f` left `OracleTerminal.test.tsx` untouched. Two tests still expect
the cut queue/themes UI and fail against the reduced terminal. `sse.test.ts` stays green.
**TS5 / TS4b backfill:** drop or rewrite that file when assembling; do not restore queue/propose
calls to make it pass.
