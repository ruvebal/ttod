<!--
Self-contained runbook. Derived from docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md —
that file is normative; regenerate this one if it changes.
-->

# Phase Q2V — strict validation and invariant engine

**Mode:** parallel lane (runs alongside Q2E, Q2P in isolated worktrees) · **Estimate:** 1–1.5 days
**Entry:** Q1 green
**Exit:** strict root/record/reference/derived-state gates all enforced

## 0. What this phase actually is, and the parallel-lane rule

Q2V, Q2E, and Q2P run at the same time, each in its **own isolated worktree/branch**, and each
owns a disjoint set of files. **This is the single most common way a free-tier agent introduces a
severe bug in this phase**: it "helpfully" edits a file another lane owns, or edits `cli.py`
directly (which belongs to Q3), because from inside one worktree it's not obvious another lane
exists. If you are an agent executing this file: you own `ttod_core/validation.py` and
`tests/test_validation.py` and nothing else. If a gate seems to require touching a file outside
that scope, **stop and say so in the report** — do not fork an incompatible local interpretation
of the Q1 schema/interface to work around it.

## 1. Required reading, in order

1. `docs/DEV_PLAN/PHASE-Q1-REPORT.md` and the schemas it produced (`schema/quote.schema.json`,
   `schema/ttod.schema.json`, `schema/proposal.schema.json`) — these are frozen interfaces for
   this phase. If one is wrong, that is a Q1 amendment, not something to patch around here.
2. `docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md` §2.1 (the invariant table) and §6
   (mechanical gate matrix) — this phase implements the "Schema", "Current-data strictness", and
   "Reference" rows.
3. `docs/DEV_PLAN/PHASE-Q0-READINESS-REPORT.md` §2 — this is your acceptance test list in
   disguise: every "measured result" row in that table (stale statistics, tag-taxonomy drift,
   origin-omission-counted-as-human, etc.) is a bug your validator must be able to detect and
   report, not silently tolerate.

## 2. Task breakdown

1. Create `ttod_core/` as a package if it doesn't exist yet (check first — another lane's file
   creation may have already made the directory; do not overwrite `__init__.py` if Q2E or Q2P got
   there first in a shared review, though in isolated worktrees this should not occur).
2. `ttod_core/validation.py`: implement validation using the Q1 JSON Schemas as the first pass,
   then layer the invariants JSON Schema cannot express alone:
   - global identity uniqueness (no duplicate canonical `id` across the whole document)
   - prefix/section match (`arch-*` must live under `architecture`, etc. — this is currently only
     documented in `.cursor/rules/ttod-editing.mdc`, not mechanically enforced; enforce it here)
   - root `meta` counts vs actual max-ID per section
   - `tag_taxonomy` closure: every tag used by any quote must exist in the declared taxonomy
     (the Q0 readiness audit found 236 used tags absent from the taxonomy live in `ttod.yml` —
     your validator must flag every one of those, not just structurally-valid-looking ones)
   - collection and lesson reference integrity (`collections.*.ids`, lesson `quote_ids` resolve)
   - `related` target resolution
   - lifecycle consistency (`deprecated_by`/`superseded_by` targets resolve; a `status=erased`
     record satisfies the tombstone shape, not the full content shape)
   - rights completeness for records flagged public-export-eligible
   - review completeness: **never count a missing/absent `origin` as `human`** — this is the exact
     bug the current `stats` command has (215 records omit `origin`; current code counts the
     omission as human). Your validator must emit a distinct "origin unresolved" diagnostic, not
     silently pass it through.
   - ancestry resolution (`immediate_parent_refs`, `root_source_refs`)
3. Implement `--strict` semantics: in strict mode, every drift row above is a hard failure. In
   non-strict/compatibility mode, some are warnings — but the **count of compatibility warnings
   must itself be nonzero and visible** in the report/JSON output whenever any exist; a
   compatibility mode that silently swallows warnings defeats its own purpose.
4. Diagnostics format: stable, enumerable error/warning **codes** (e.g. `TAG_NOT_IN_TAXONOMY`,
   `ORIGIN_UNRESOLVED`, `PREFIX_SECTION_MISMATCH`), plus a JSON output mode. Q1's negative
   fixtures already assert exact codes against the schema layer — this phase's codes must be
   equally stable, since Q3's CLI and Q5's sensors will both depend on them not silently changing.
5. `tests/test_validation.py`: run every Q1 fixture through this validator (not just the raw JSON
   Schema) and assert the same exact-code behavior, plus additional fixtures for the invariants
   this phase adds beyond what JSON Schema alone expresses (tag taxonomy closure, prefix/section
   match, origin-omission handling, derived-count drift).

## 3. Touched-path budget

**Allowed:** `ttod_core/validation.py`, `ttod_core/__init__.py` (if creating the package for the
first time), `tests/test_validation.py`, new fixtures under `tests/fixtures/q2v_*` if a Q1 fixture
doesn't cover an invariant this phase adds.

**Forbidden:** `ttod_core/canonical.py`, `ttod_core/exporter.py` (Q2E's files), `ttod_core/
proposals.py` (Q2P's file), `cli.py`, `ttod.yml`, `schema/*.json` (frozen by Q1 — if wrong, escalate,
don't silently patch).

## 4. Do NOT (failure modes seen on this class of task)

- Do not count a missing `origin` field as `human`. This is called out explicitly because it is
  the exact live bug in the current `cli.py stats` command — reproducing it in the new validator
  would be a regression, not a fix.
- Do not touch `cli.py`. Q2V produces a library module; wiring it into the CLI is Q3.
- Do not edit `schema/*.json` from inside this lane even if you spot what looks like a bug in it.
  Record it in the report as a Q1-interface concern instead — two lanes independently patching the
  shared schema is exactly the "fork incompatible local interpretations" failure the parallel-lane
  rule in §0 exists to prevent.
- Do not silently accept the current `ttod.yml`'s drift (stale counts, taxonomy gaps) as evidence
  your validator is "too strict." The whole point of Q2V is that this drift currently goes
  undetected; detecting it is success, not a bug in your code.

## 5. Applicable gates

| Gate | Required proof |
| --- | --- |
| Schema | quote/root/proposal positive fixtures pass through the full validator; each negative still fails with expected code |
| Current-data strictness | baseline inconsistencies are reported; `--strict` is the switch that turns them into hard failures |
| Reference | related, collection, lesson, ancestry, deprecation/supersession targets resolve |

## 6. Exact commands

```bash
cd /Users/ruvebal/src/ttod
python -m unittest discover -s tests -p 'test_validation.py'
```

## 7. Report requirements

File `docs/DEV_PLAN/PHASE-Q2V-REPORT.md`: state, every invariant implemented with its error code,
which Q0-readiness-audit findings this validator now mechanically detects (map each finding row
to a code), test command/output, any Q1-interface concern raised rather than silently patched,
files touched, safe resume point for Q3.

## 8. Agent prompt — paste this into Cascade/Devin

```text
Act as TTOD validation engineer for Phase Q2V. Work only inside /Users/ruvebal/src/ttod, in your
own isolated worktree/branch. Two other lanes (Q2E, Q2P) are running in parallel in their own
worktrees, each owning different files — you own only ttod_core/validation.py and
tests/test_validation.py (plus ttod_core/__init__.py if the package doesn't exist yet). Do not
touch ttod_core/canonical.py, ttod_core/exporter.py, ttod_core/proposals.py, cli.py, ttod.yml, or
schema/*.json under any circumstance in this phase — if you believe one of those needs to change,
stop and record it in the report instead of editing it.

Read docs/DEV_PLAN/PHASE-Q1-REPORT.md and the three schemas it produced, docs/DEV_PLAN/PHASE-Q-
TTOD-CONTRACT-REPAIR-CASCADE.md sections 2.1 and 6, and docs/DEV_PLAN/PHASE-Q0-READINESS-REPORT.md
section 2 (treat every row there as a bug your validator must be able to detect).

Implement ttod_core/validation.py: JSON-Schema pass plus global identity uniqueness, prefix/section
match, meta-count-vs-actual-max-ID, tag_taxonomy closure (must flag the 236 currently-undeclared
tags live in ttod.yml), collection/lesson reference integrity, related-target resolution, lifecycle
consistency, rights completeness for public-export-eligible records, review completeness, and
ancestry resolution. Origin omission must never be silently counted as human — emit a distinct
ORIGIN_UNRESOLVED-style code instead; this is fixing a live bug in the current stats command, not
introducing one. Implement --strict (all drift is a hard failure) vs compatibility mode (drift is
a nonzero, visible warning count, never silently swallowed). Emit stable, enumerable diagnostic
codes plus a JSON output mode.

Write tests/test_validation.py running every Q1 fixture through this full validator with the same
exact-code assertions, plus new fixtures for invariants this phase adds beyond raw JSON Schema.

File docs/DEV_PLAN/PHASE-Q2V-REPORT.md mapping each Q0-readiness-audit finding to the diagnostic
code that now catches it, with exact test command/output, any Q1-interface concern you escalated
instead of patching, files touched, and the safe resume point for Q3.
```
