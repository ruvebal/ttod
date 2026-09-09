<!--
Self-contained runbook. Derived from PHASE-U-FEII-TEACHING-SKELETON-CASCADE.md §5 TS1 and
PHASE-U-WEEK0-ORCHESTRATION.md — that orchestration document is normative; regenerate this one if
it changes. Generated as part of the Week-0 skeleton-generator pass.
-->

# Phase U · TS1 — Freeze the subtraction contract

**Mode:** single orchestrator, sequential — blocks every other Week-0 lane
**Owner:** professor or one designated TA/agent session (not split across people — the whole
point is one consistent contract every other lane reads from)
**Entry:** Phase V and this orchestration approved by the product owner (§5 of the orchestration
document)
**Exit:** a published subtraction/keep table for all five seams, `domain.ts` confirmed frozen, a
CI skeleton (branch protection + lint/typecheck/build workflow) live on the branch every later
lane forks from

---

## 0. What this phase actually is

TS1 is not implementation — it is the single decision-making pass that makes every later lane's
work mechanical instead of a judgment call. Every other Week-0 lane (TS3a/b/c, TS4a/b) reads its
"what to keep, what to cut, what becomes a student assignment" instructions from this phase's
output. Get this wrong and five lane owners independently improvise five different definitions of
"hello-world."

**Do not start TS3/TS4 work before this phase files as done.** Phase U §4 states this explicitly:
TS3 and TS4 "may run in parallel only after TS1 freezes shared contracts and assigns
non-overlapping files."

## 1. Required reading (context only — this runbook is self-contained)

- `PHASE-U-FEII-TEACHING-SKELETON-CASCADE.md` §1 (pedagogical invariants), §2 (hello-world depth
  contract table), §5 TS1.
- `PHASE-U-WEEK0-ORCHESTRATION.md` §1–§4 — the concrete keep/cut table this runbook operationalizes.
- `AGENTS.md` — non-negotiable rules (never mutate `ttod.yml`, etc. — not directly at risk here,
  but the same discipline applies to any script that touches the frontend tree).

## 2. Non-negotiable boundaries

- **Read-only against `main`.** This phase reads the reference build to decide what to keep; it
  does not edit it. All output (the subtraction table, the CI workflow file, any `domain.ts`
  amendment) lands on a new branch, e.g. `skeleton/ts1-contracts`, never committed to `main`.
- **`domain.ts` is confirmed, not rewritten, unless a genuine gap is found.** The seven interfaces
  already in `services/frontend/src/types/domain.ts` (`WisdomEntry`, `GraphNode`, `GraphLink`,
  `OracleQueryPayload`, `OracleResponseChunk`, `OracleProposeRequest`, `OfflineLogEntry`) already
  cover every contract R3b/R4/R5/R6 need. Expect to tag this file frozen as-is; if TS3/TS4's own
  reading surfaces a real gap, add to it, never remove or rename a field a later lane depends on
  without flagging it back to this phase.
- **No canonical mutation.** Nothing in this phase touches `ttod.yml`, `schema/`, or `ttod_core/`.
- **CI skeleton has no test content and no deploy step.** TS1 stands up the gate (lint, typecheck,
  build) — TS4b (R7) owns adding actual test content to it later; TS4a (R6) owns any later CI
  orchestration beyond this minimal gate. Neither a deploy job nor any secret reference belongs in
  this skeleton — see R6's own decision record on why: production credentials are instructor-only,
  and Deliverable 1 has no deploy requirement at all.

## 3. Domain contract slice

No new types. Confirm these seven interfaces exist, unchanged, in
`services/frontend/src/types/domain.ts`, and that every lane's runbook (TS3a/b/c, TS4a/b) cites
the correct one(s) for its own scope:

| Interface | Used by |
| --- | --- |
| `WisdomEntry` | TS3a (content), TS3b (graph node join) |
| `GraphNode`, `GraphLink` | TS3b |
| `OracleQueryPayload`, `OracleResponseChunk`, `OracleProposeRequest` | TS3c |
| `OfflineLogEntry` | TS3c, TS4a |

## 4. Scope — what TS1 produces

1. **Per-seam subtraction table.** For each of R3b/R4/R5/R6/R7, using
   `PHASE-U-WEEK0-ORCHESTRATION.md` §4's table as the starting point, write the *exact* function,
   block, or route to remove from the hello-world branch and the *exact* one-sentence acceptance
   criterion that becomes that seam's student assignment. This is the artifact TS3a/b/c and TS4a/b
   each read as their own §4 "Scope" input — do not leave it as prose; a table a lane owner can
   check off item-by-item is the deliverable.
2. **`domain.ts` freeze confirmation.** Read the file, confirm no lane needs a shape it doesn't
   already have, tag the commit (or note the confirmation in the phase report) as frozen.
3. **CI skeleton.** One workflow file (e.g. `.github/workflows/ci.yml`) in the style of the
   existing `public-docs-pages.yml` (explicit `permissions:`, path-scoped `on:` triggers, no
   inline secrets): `npm run build` and a typecheck/lint step for `services/frontend`. No test
   step yet (TS4b adds it), no deploy step ever in the student artifact.
4. **Branch protection.** Configure (or document the exact settings to configure, if this
   runbook's executor lacks repo-admin access) branch protection on whichever branch becomes the
   Week-1 collaboration base: require the CI skeleton to pass and ≥1 review before merge.
5. **Non-overlapping file assignment.** Confirm TS3a/b/c and TS4a/b's touched-path budgets (each
   lane's own §7) do not overlap — they should not, by construction, since each targets a
   different component tree, but TS1 is the checkpoint that catches it before five branches start
   in parallel.

## 5. Mechanical gates

| Gate | Required proof |
| --- | --- |
| Subtraction table complete | all five seams have a named keep/cut/assignment split, not left as "TBD" |
| `domain.ts` frozen | confirmed unchanged (or amendments listed with reason) and referenced by file/line in each lane's §3 |
| CI skeleton green | a real PR against the branch shows the lint/typecheck/build workflow passing |
| No overlap | touched-path budgets of TS3a/b/c/TS4a/b reviewed side by side, zero shared files |
| No secrets | CI skeleton file contains no `${{ secrets.* }}` reference at all — there is nothing to deploy yet |

## 6. Rollback and mutation law

- If this phase's own work accidentally touches `main`, revert immediately — TS1's output is a
  branch and a document, never a `main` commit.
- Nothing here writes to `ttod.yml`, `schema/`, `ttod_core/`, or `services/backend/**`/`services/mcp/**`.

## 7. Touched-path budget

**Allowed:** `docs/DEV_PLAN/PHASES/U-TS1-subtraction-and-contracts.md` (this file, for recording
the subtraction table if not kept elsewhere), `.github/workflows/ci.yml` (new), `services/frontend/src/types/domain.ts`
(amend only if a genuine gap is found — expect no change).

**Forbidden:** any file under `services/frontend/src/components/`, `src/pages/`, `src/lib/`,
`services/backend/**`, `services/mcp/**`, `ttod_core/**`, `ttod.yml`, `schema/**` — TS1 decides
what happens to these files, it does not edit them itself.

## 8. Post-phase review

Before filing done, have a second reader (not the author of the subtraction table) check that
every "cut" line in the table genuinely corresponds to Phase U §2's "deliberately absent" column
for that seam — a cut that removes something Phase U's own contract table lists as
*instructor-provided* would under-deliver the hello-world seam, not just simplify it.

## 9. Phase report status enum

- **DONE** — subtraction table published for all five seams, `domain.ts` frozen, CI skeleton
  green on a real PR, branch protection configured, no file-path overlap between later lanes.
- **PARTIAL** — name exactly which of the four deliverables (table / freeze / CI / protection) is
  missing.
- **BLOCKED** — product-owner approval from the orchestration document's §5 has not landed.

## 10. Exact commands

```bash
cd /Users/ruvebal/src/ttod
git worktree add ../ttod-skeleton-ts1 -b skeleton/ts1-contracts main
cd ../ttod-skeleton-ts1
wc -l services/frontend/src/types/domain.ts   # expect 58 on committed main — confirm unchanged before editing anything
```

If the working tree shows more than 58 lines, stop: either commit the deliberate contract amendment
on a branch first, or discard the WIP before claiming a freeze.

## 11. Report requirements

File `docs/DEV_PLAN/PHASE-U-TS1-REPORT.md`: status (§9), the published subtraction table (or a
link to it), `domain.ts` freeze confirmation, the CI workflow file's path and a link/screenshot of
one passing run, branch-protection settings applied, and explicit confirmation that TS3a/b/c and
TS4a/b's touched-path budgets do not overlap.

## 12. Agent prompt — paste this into a fresh agent session with no other file open

```text
Act as TTOD Phase U TS1 orchestrator. Work only inside a new git worktree on branch
skeleton/ts1-contracts, never on main. This runbook (docs/DEV_PLAN/PHASES/U-TS1-subtraction-and-contracts.md)
is self-contained; also read PHASE-U-WEEK0-ORCHESTRATION.md §1-4 for the concrete per-lane
keep/cut starting table.

First, read services/frontend/src/types/domain.ts and confirm it already contains WisdomEntry,
GraphNode, GraphLink, OracleQueryPayload, OracleResponseChunk, OracleProposeRequest, and
OfflineLogEntry. Do not rewrite it. Only add a field if a genuine gap surfaces, and say exactly
why.

Produce a subtraction table for R3b, R4, R5, R6, and R7: for each, name the exact function/block/
route to remove for hello-world depth and the one-sentence acceptance criterion that becomes the
student assignment for it. Ground every line in the actual files (read
services/frontend/src/components/graph/GraphIsland.svelte,
services/frontend/src/components/oracle/OracleTerminal.tsx and sse.ts, and the wisdom pages under
services/frontend/src/pages/[locale]/wisdom/) — do not write generic placeholders.

Add .github/workflows/ci.yml: lint/typecheck + npm run build for services/frontend, styled like
the existing .github/workflows/public-docs-pages.yml (explicit permissions, path-scoped triggers,
no secrets, no deploy step — there is nothing to deploy at this stage). Verify it via a real PR on
your worktree branch and record the passing run.

Confirm no two of R3b/R4/R5/R6/R7's expected touched-path budgets overlap (they target
GraphIsland.svelte, OracleTerminal.tsx/sse.ts, the wisdom pages, a new public/sw.js, and a new
test suite respectively — they should not collide by construction, but say so explicitly with
the actual paths).

File docs/DEV_PLAN/PHASE-U-TS1-REPORT.md with status (DONE/PARTIAL/BLOCKED per this runbook's §9),
the full subtraction table, the domain.ts freeze confirmation, the CI workflow evidence, and the
no-overlap confirmation.
```
