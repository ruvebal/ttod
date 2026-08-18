<!--
Self-contained runbook. Written so a coding agent (Cascade, Devin, or equivalent) can execute
this phase from this file alone, without reliably reading four other documents mid-task.
Derived from docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md — that file is normative;
if this runbook and the master contract ever disagree, the master contract wins and this file
is stale and must be regenerated.
-->

# Phase Q0 — schema and authority freeze

**Mode:** sequential blocker · **Estimate:** 0.5–1 day
**Entry:** the master contract (`../PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md`) + the existing
readiness audit (`../PHASE-Q0-READINESS-REPORT.md`)
**Exit:** signed decisions and baseline recorded; a recoverable pre-mutation boundary exists
**State as of 2026-08-18:** partially satisfied already — see §1a before doing anything.

## 0. What this phase actually is

Q0 does not write code. It is a **freeze**: confirm, in writing, every semantic decision that Q1
onward will build on, and prove the repository has a recoverable rollback point before any file
that matters gets touched. If you find yourself editing `ttod.yml`, `cli.py`, `schema/`, or
anything under `sources/`, **stop** — that is not this phase.

## 1. Required reading, in order

1. `/Users/ruvebal/src/ttod/CLAUDE.md` — data model, author, current (stale) license line.
2. `/Users/ruvebal/src/ttod/.cursor/rules/ttod-editing.mdc` — the current hand-maintained editing
   discipline; Q1+ formalizes this into schema, it does not contradict it.
3. `docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md` §1–4 (outcome/boundaries, target data
   contract, independence protocol, DAG) — this is the content you are confirming/freezing, not
   drafting from scratch. It already exists; your job is to verify it's internally consistent and
   record that it's frozen.
4. `docs/DEV_PLAN/PHASE-Q0-READINESS-REPORT.md` — the 2026-08-14 read-only audit. Treat every
   number in it as a claim to re-verify, not a fact to trust — it says so itself in §2A.
5. `docs/DEV_PLAN/DECISIONS/Q0-2026-08-18-RIGHTS-LICENSE-NC.md` — the rights/license decision,
   already frozen. Do not reopen it; only reference it.
6. `cli.py`, `ttod.yml` header (first ~60 lines) and root-level keys (not the full 141KB file).
7. `sources/tao-of-ai-development/README.md` — the source chapter's own license/provenance notes.
8. DevIAC knowledge flywheel doc, Athanor Provenance Law/Phase S, and the frozen WPL contract —
   these live outside this repository (Athanor/WPL/DevIAC are sibling systems). If you cannot
   locate them from this working directory, record that as a gap in the Q0 report rather than
   inventing their content. Do not freeze a version pin you cannot actually verify.

## 2. What is already true (do not redo this work)

- **Recoverable baseline:** the 2026-08-14 readiness report flagged that `/Users/ruvebal/src/ttod`
  had no `.git` directory — a blocking gap. As of 2026-08-18, `git init` has been run and there is
  a clean initial commit (`git log` shows one commit, `git status` is clean). **Re-verify this**
  (`git status`, `git log --oneline`) rather than assuming it still holds, but do not re-run
  `git init` or touch history.
- **Rights/license decision:** frozen in `DECISIONS/Q0-2026-08-18-RIGHTS-LICENSE-NC.md` — code is
  MIT (`LICENSE-CODE`), content is CC BY-NC-SA 4.0 (`LICENSE-CONTENT`), default `rights.license`
  for new/unresolved-and-rights-holder-authored quotes is `CC-BY-NC-SA-4.0`. This is done. Do not
  re-decide it; only cite it in the Q0 report.
- **v3 field names/enums, compatibility period, `TTOD-C14N-v1` projection, proposal lifecycle,
  human reviewer identity shape, higher-law erasure authority, shared `EvidenceSnapshot` fields,
  sibling-output prohibition, `arch-052` expected verdict** are already specified in the master
  contract §2.1–2.3 and §3. Your job is to (a) read them critically for internal contradiction,
  (b) confirm none of them silently contradicts `.cursor/rules/ttod-editing.mdc` or the current
  `ttod.yml` header in a way that blocks migration, and (c) declare them frozen in the Q0 report
  by reference — do not retype them into a new decision doc; that would create a third source of
  truth.

## 3. What is still open

- **Athanor/WPL version pins.** The master contract says to freeze these but does not state a
  version. If the Athanor/WPL repositories are not reachable from this environment, record this
  explicitly as an **open item carried into Q1 as a blocker**, not as a silently-skipped freeze.
  Do not invent a version number.
- **Current input hashes.** The 2026-08-14 report has hashes for that date. You must compute
  fresh SHA-256 hashes for `CLAUDE.md`, `.cursor/rules/ttod-editing.mdc`, `cli.py`, and `ttod.yml`
  as they stand today, and note whether they match the 2026-08-15 post-audit-correction hashes
  recorded in `PHASE-Q0-READINESS-REPORT.md` §2A. If they differ and you don't know why, stop and
  ask — do not guess a reason.
- **Confirm this restructuring session's edits are consistent.** `INDEX.md` (repo root) was
  rewritten, the duplicate root `PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md` was deleted, and
  `LICENSE-CODE`/`LICENSE-CONTENT` were added. Verify these are committed or staged, not left as
  uncommitted drift, before declaring the baseline "recoverable."

## 4. Touched-path budget

**Allowed:** `docs/DEV_PLAN/` (this file's own directory tree), `docs/DEV_PLAN/DECISIONS/`, a
new read-only baseline/hash artifact (e.g. `docs/DEV_PLAN/PHASE-Q0-REPORT.md`), `git add`/`git
commit` of already-existing untracked files (README, LICENSE files) if not yet committed.

**Forbidden:** any write to `ttod.yml`, `cli.py`, `schema/`, `sources/`, `exports/`, any external
database, or any dependency file (`pyproject.toml`, lockfiles). No `git push`. No destructive git
command (`reset --hard`, `checkout --`, `clean -f`) without stopping to ask first.

## 5. Do NOT (failure modes seen on this class of task)

- Do not "helpfully" start writing `schema/quote.schema.json` because you've read the target
  contract and it seems obvious — that is Q1, gated on this phase's report being filed first.
- Do not invent a reviewer identity, an Athanor/WPL version pin, or a source hash you have not
  actually computed. An unresolved item stays unresolved and gets carried forward explicitly.
- Do not treat the numbers in `PHASE-Q0-READINESS-REPORT.md` (e.g. "229 quotes") as still true
  without recomputing — the report itself warns these are point-in-time measurements.
- Do not relicense anything beyond what `DECISIONS/Q0-2026-08-18-RIGHTS-LICENSE-NC.md` already
  decided. If you think the decision is wrong, flag it in the report; do not silently override it.
- Do not run `git init` again, rewrite git history, or force-push. The baseline already exists.

## 6. Applicable gate

| Gate | Required proof |
| --- | --- |
| Baseline | input hashes/status recorded; no secrets in tracked files; recoverable pre-migration state confirmed (git clean, one commit, no stray uncommitted mutations to canonical files) |

## 7. Exact commands

```bash
cd /Users/ruvebal/src/ttod
git status
git log --oneline -20
shasum -a 256 CLAUDE.md .cursor/rules/ttod-editing.mdc cli.py ttod.yml
. .venv/bin/activate 2>/dev/null && python cli.py validate || echo "cli.py validate: record exit code and output verbatim in the report"
```

## 8. Report requirements

File `docs/DEV_PLAN/PHASE-Q0-REPORT.md` (do not overwrite `PHASE-Q0-READINESS-REPORT.md`; that is
the prior audit, kept as history). Include:

- State (`READY` → `DONE` only if every item in §2/§3 above is resolved or explicitly carried
  forward as a named blocker into Q1).
- Fresh input hashes with today's date, and a diff against the 2026-08-15 hashes in the prior
  report.
- Exact commands run and their exit codes (§7), verbatim output for `cli.py validate`.
- Explicit confirmation of the git baseline (commit hash, clean status).
- A list of every decision frozen (by reference to contract section or decision file — do not
  duplicate their text) and every decision still open, with an owner and target phase.
- Safe resume point for Q1.

## 9. Agent prompt — paste this into Cascade/Devin

```text
Act as TTOD contract steward for Phase Q0. Work only inside /Users/ruvebal/src/ttod. Read, in
order: CLAUDE.md; .cursor/rules/ttod-editing.mdc; docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-
CASCADE.md sections 1 through 4; docs/DEV_PLAN/PHASE-Q0-READINESS-REPORT.md;
docs/DEV_PLAN/DECISIONS/Q0-2026-08-18-RIGHTS-LICENSE-NC.md; cli.py; the first 60 lines of
ttod.yml. Do not edit ttod.yml, cli.py, schema/, sources/, or exports/ — this phase is read-only
except for docs/DEV_PLAN/** and git add/commit of already-created files.

Run: git status; git log --oneline -20; shasum -a 256 on CLAUDE.md, .cursor/rules/ttod-editing.mdc,
cli.py, and ttod.yml; and `python cli.py validate` (activate .venv first if present). Record every
command and its exact output.

Confirm in writing whether each of the following is frozen and consistent, citing the contract
section that freezes it, or mark it an explicit open blocker if you cannot verify it from this
repository: v3 field names/enums; compatibility period; TTOD-C14N-v1 projection; proposal
lifecycle; human reviewer identity shape; rights/unresolved policy (already frozen — cite the
decision file, do not redecide); higher-law erasure authority; shared EvidenceSnapshot fields;
sibling-output prohibition; arch-052 expected verdict (SELF_DERIVED_NOT_EVIDENCE for Athanor/WPL
architecture claims); Athanor/WPL version pins (likely NOT verifiable from this repo alone — say
so explicitly rather than guessing a version).

Do not invent any fact you cannot verify: no fabricated reviewer identity, source hash, or version
pin. Do not start Q1 work (no schema/*.json files). Do not touch git history, do not force-push,
do not run git init again (it has already been run).

File docs/DEV_PLAN/PHASE-Q0-REPORT.md with: state, fresh hashes and their diff against the prior
report's hashes, exact commands/exit codes, confirmation of the recoverable git baseline, the
frozen-vs-open decision list with owners, and the exact safe resume point for Q1. Do not claim
DONE while any decision needed by Q1 remains unresolved and uncarried-forward.
```
