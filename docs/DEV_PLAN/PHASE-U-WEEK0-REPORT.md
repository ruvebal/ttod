<!--
Phase U Week-0 generator report — TS1/TS3/TS4 lane runbooks only.
No skeleton branch, worktree, subtraction, or CI skeleton was created.
Follows cascade-forge evidence-state discipline (status first; claims checked live).
-->

# Phase U Week-0 Report — skeleton generator (TS1/TS3/TS4 runbooks)

**Status:** DONE

**Scope executed:** the generator pass named by
[`PHASE-U-WEEK0-ORCHESTRATION.md`](PHASE-U-WEEK0-ORCHESTRATION.md) — produce six self-contained
lane runbooks under `PHASES/U-*.md`, verify keep/cut claims against the live `services/frontend`
tree, file this report. **No** `skeleton/*` branch, worktree, `domain.ts` freeze commit, CI
workflow, or hello-world subtraction was performed. Nothing was committed.

**Date:** 2026-09-09

**Implementer:** Cursor agent session (cascade-forge)

**Independent verifier:** pending (generator docs only; lane execution still gated by
orchestration §5)

**Owner:** `@crea-comm.net`

---

## 1. What this pass is (and is not)

| This pass | Not this pass |
| --- | --- |
| Week-0 **generator** — mold the six runbooks (R0-shaped) | TS1 subtraction/contracts **execution** |
| Ground keep/cut tables against live files | Opening `skeleton/ts1-contracts` or any parallel lane |
| Evidence-state report with a closed status enum | TS5 fresh-history assembly |

Lane execution remains **BLOCKED** until the product owner answers the three §5 questions in the
orchestration document (approve runbooks, Week-1 green date, lane ownership). That gate is
unchanged by this report's `DONE`.

---

## 2. Documents read before claiming verification

1. `docs/DEV_PLAN/PHASE-U-WEEK0-ORCHESTRATION.md` (full)
2. `docs/DEV_PLAN/PHASE-U-FEII-TEACHING-SKELETON-CASCADE.md` §§1–2, §4–5 (invariants, hello-world
   depth table, orchestration graph, TS1/TS3/TS4 packages)
3. All six `docs/DEV_PLAN/PHASES/U-TS*.md` runbooks (full)
4. `docs/DEV_PLAN/PHASE-V-FEII-COHORT-COLLABORATION-AND-ASSESSMENT.md` §1 (Week-0 prerequisite table)
5. `docs/DEV_PLAN/PHASE-R0-REPORT.md` (report shape / non-claims discipline)
6. `docs/DEV_PLAN/PHASE-TS0-REPORT.md` (TS0 still `VERIFYING` — input context only)
7. `AGENTS.md` (non-mutation of `ttod.yml` / canonical paths)
8. Live tree under `services/frontend/src/` and `.github/workflows/public-docs-pages.yml`

---

## 3. Live grounding — commands and results (this session)

Committed tip checked: `39b62a18` (`main`, ahead of `origin/main` by 2). Orchestration originally
cited `dadacc93`; line counts below are from the **committed** tree at `HEAD`, not assumed from
prose.

```text
$ wc -l services/frontend/src/types/domain.ts
# git show HEAD:… → 58 lines; seven export interfaces present
# working tree (uncommitted) → 62 lines (+ locale?/themes?/tags? on Oracle shapes)

$ wc -l \
  services/frontend/src/pages/[locale]/wisdom/[slug].astro \
  …/wisdom/index.astro \
  …/sections/[section].astro …/tags/[tag].astro …/levels/[level].astro \
  services/frontend/src/components/graph/GraphIsland.svelte \
  services/frontend/src/components/oracle/OracleTerminal.tsx \
  services/frontend/src/components/oracle/sse.ts
# 19, 21, 10, 10, 10, 104, 325, 63

$ test -f services/frontend/public/sw.js; echo $?
# missing (NO_SW) — TS4a "add stub, do not subtract" claim holds

$ head -n 30 .github/workflows/public-docs-pages.yml
# path-scoped on:, permissions: contents: read — TS1 CI precedent exists

$ rg -n "gsap|filterGraph|setTag|syncFromUrl|hover" \
  services/frontend/src/components/graph/GraphIsland.svelte
# tag filter + URL state + GSAP hover/entrance all present — TS3b cut list is real

$ rg -n "enqueueOracleQuery|flushQueue|propose\(|useReducedMotion" \
  services/frontend/src/components/oracle/OracleTerminal.tsx
# offline queue, flush, propose UI, reduced-motion all present — TS3c cut/keep list is real
```

| Claim (orchestration §1 / §4) | Verified? |
| --- | --- |
| Seven domain interfaces already exist | Yes on committed `main` |
| `GraphIsland.svelte` ≈ 104 lines, full feature set | Yes (104) |
| `OracleTerminal.tsx` + `sse.ts` ≈ 325 + 63 | Yes |
| Wisdom `[slug]` 19; three facet routes 10 each | Yes; also `index.astro` = 21 (kept, already near hello-world) |
| No `public/sw.js` yet | Yes |
| CI precedent = `public-docs-pages.yml` | Yes; no `ci.yml` yet (TS1's job) |

---

## 4. Generated / verified runbooks

| File | Lane | Entry gate | Report file (standardized this pass) |
| --- | --- | --- | --- |
| `PHASES/U-TS1-subtraction-and-contracts.md` | sequential contracts | orchestration §5 PO approval | `PHASE-U-TS1-REPORT.md` |
| `PHASES/U-TS3a-r3b-content-hello-world.md` | R3b content | TS1 `DONE` | `PHASE-U-TS3a-REPORT.md` |
| `PHASES/U-TS3b-r4-graph-hello-world.md` | R4 graph | TS1 `DONE` + TS3a locale/route contract | `PHASE-U-TS3b-REPORT.md` |
| `PHASES/U-TS3c-r5-oracle-hello-world.md` | R5 oracle | TS1 `DONE` + TS3a locale/route contract | `PHASE-U-TS3c-REPORT.md` |
| `PHASES/U-TS4a-r6-pwa-hello-world.md` | R6 PWA stub | TS1 `DONE` (parallel to TS3) | `PHASE-U-TS4a-REPORT.md` |
| `PHASES/U-TS4b-r7-testing-hello-world.md` | R7 four tests | TS1 `DONE` (continuous) | `PHASE-U-TS4b-REPORT.md` |

Each runbook carries: entry/exit, required reading, non-negotiable boundaries, domain-contract
slice, keep/cut (or add) scope, mechanical gates, rollback law, touched-path budget, cold-review
requirement, status enum (`DONE` / `PARTIAL` / `BLOCKED`), exact commands, report requirements,
and a paste-ready §12 agent prompt.

**Touched-path overlap check (generator-time):** no two TS3/TS4 lanes share a primary edit target
(wisdom pages · `GraphIsland.svelte` · `OracleTerminal.tsx` · `public/sw.js`+manifest · new tests).
Soft coordination only: TS4a may add a registration snippet in `layouts/Page.astro`; TS4b extends
TS1's `.github/workflows/ci.yml`. TS1 remains the checkpoint that re-confirms this before parallel
worktrees open.

---

## 5. Corrections applied during this verification pass

1. **Lane report filenames** — five runbooks named `PHASE-R{3b,4,5,6,7}-hello-world-REPORT.md`,
   which collides in vocabulary with the rich-reference `PHASE-R*-REPORT.md` set. Renamed targets
   to `PHASE-U-TS{3a,3b,3c,4a,4b}-REPORT.md` (TS1 already used `PHASE-U-TS1-REPORT.md`).
2. **`domain.ts` line-count claim** — orchestration said "62 lines" matching a **dirty** working
   tree; committed `HEAD` is **58 lines**. Orchestration §1 and TS1's `wc -l` expectation updated.
   TS3c's domain-contract slice was reset to the committed Oracle shapes (no `locale` /
   `themes` / `tags` until TS1 deliberately freezes an amended commit).
3. **Orchestration status line** — set to `GENERATOR DONE (documents only)`; lane execution still
   blocked on §5.

---

## 6. Judgment calls surfaced (not silently decided)

### 6.1 Dirty working tree on `main` (blocks an honest TS1 freeze)

`git status` shows uncommitted edits under `services/frontend/src/types/domain.ts`,
`components/oracle/**`, and `services/backend/**`. Week-0 lanes must not write `main`; they also
must not freeze a contract that only exists as WIP. **Before TS1 starts:** product owner either
lands the Oracle locale/themes/tags amendment on a deliberate commit, or discards it. Freezing
against an unclean tree would make every later lane's §3 slice ambiguous.

### 6.2 TS0 still `VERIFYING`

[`PHASE-TS0-REPORT.md`](PHASE-TS0-REPORT.md) remains `VERIFYING` pending independent review. The
Week-0 generator does not depend on promoting TS0, but TS1's "read the reference" work should
prefer a verified local stack. Flag only — not a generator blocker.

### 6.3 Orchestration §5 still open (lane-execution gate)

This report does **not** answer:

1. Are the six runbooks approved as written (or with named edits)?
2. What is the target date for "Week 1 green"?
3. Who executes which lane?

Until those land, TS1's own status enum says **BLOCKED**, and every other lane's entry gate fails.

---

## 7. Explicit non-claims

This report does **not** claim:

- Phase U overall is DONE (still PROPOSED at programme level; TS0 VERIFYING; TS1–TS8 blocked)
- Any `skeleton/*` branch or worktree exists
- `domain.ts` is frozen
- `.github/workflows/ci.yml` exists
- Any hello-world subtraction or `ASSIGNMENT.md` was written
- Phase V may start Week 1 (still gated on TS1+TS3+TS4 execution going green)

---

## 8. Resume rule (closed enum alignment)

| Status | Meaning for Week-0 generator | Next action |
| --- | --- | --- |
| **DONE** | Six runbooks verified + this report filed | Await §5 PO answers; then paste `PHASES/U-TS1-subtraction-and-contracts.md` §12 into a fresh session |
| **PARTIAL** | Named runbook or grounding gap remains | Finish the named gap; do not open TS1 |
| **BLOCKED** | External dependency (e.g. cannot read `services/frontend`) | Clear blocker; re-run grounding |
| **VERIFYING** | Generator claims filed; independent doc review pending | Second reader confirms keep/cut tables match Phase U §2 |

**Current:** generator **DONE**; independent verification of the docs pack may still mark the pack
`VERIFYING` until a second reader signs. Lane execution: **BLOCKED** on §5.

**READY next (only after §5):** `docs/DEV_PLAN/PHASES/U-TS1-subtraction-and-contracts.md` — alone,
on `skeleton/ts1-contracts`, never on `main`. Do not open TS3a/b/c or TS4a/b until
`PHASE-U-TS1-REPORT.md` says `DONE`.

---

## Addendum — 2026-09-09, later the same day

`PHASE-U-WEEK0-ORCHESTRATION.md` §5 has since been answered on disk: runbooks approved, Week 1
confirmed 2026-09-10 (tomorrow, as of this addendum), lane execution delegated to local Ollama
`qwen3.8:27b` where possible. A seventh runbook, `PHASES/U-TS4c-auth-hello-world.md`, was also
added after this report was filed (Phase V's cohort/module revision) — see
`PHASE-U-WEEK0-ORCHESTRATION.md` §5's own note on reading the six-runbook approval as extending to
it.

**This report's `§6.3`/`§8` "BLOCKED on §5" characterization is therefore superseded — not by
editing the original claims above (they were accurate when filed), but by this dated note.** §6.1's
judgment call (dirty working tree under `domain.ts`/`components/oracle/**`/`services/backend/**`)
has **not** been independently re-verified since this report's original grounding pass — TS1's own
first action (§10 of `PHASES/U-TS1-subtraction-and-contracts.md`) is exactly the `wc -l` check that
answers this before anything freezes.

**Straight answer to "is it relevant to run TS1 now": yes, and it is time-sensitive.** TS1 blocks
every other Week-0 lane, and Week 1 of student collaboration is dated for tomorrow. Executing TS1
is a real repo-changing action (new worktree, branch, CI workflow file, possible branch-protection
config) — not authorized by this addendum alone. It is ready to start on confirmation.

---

## Addendum — 2026-09-09, Week-0 lane execution closed

All seven isolated branches exist; none were merged to `main`. TS5 (fresh-history assembly) is
**not** opened by this addendum.

| Lane | Branch | Tip | Status |
| --- | --- | --- | --- |
| TS1 | `skeleton/ts1-contracts` | `47f15da9` | DONE — freeze + CI; draft [PR #1](https://github.com/ruvebal/ttod/pull/1) do not merge |
| TS3a | `skeleton/ts3a-r3b` | `955198fc` | DONE |
| TS3b | `skeleton/ts3b-r4` | `bfea9da7` | DONE — graph is full sample 460/665 |
| TS3c | `skeleton/ts3c-r5` | `5a16a98f` | DONE |
| TS4a | `skeleton/ts4a-r6` | `4b2db64e` | DONE |
| TS4b | `skeleton/ts4b-r7` | `bcdd5438` | DONE |
| TS4c | `skeleton/ts4c-auth` | `445f3257` | DONE — `User`/`FavoriteEntry` not on freeze branch |

**TS5 inputs (named, not decided):** (1) cherry-pick or reject TS4c's `domain.ts` types; (2) backend sample cap vs. 460-node graph; (3) drop or rewrite `OracleTerminal.test.tsx` (still expects queue/themes UI that TS3c cut); (4) merge `Page.astro` (TS4a registration) with TS4b's shell test.

Lane sessions used Cursor inherit, not local `qwen3.8:27b`.
