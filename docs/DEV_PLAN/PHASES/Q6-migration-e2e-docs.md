<!--
Self-contained runbook. Derived from docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md —
that file is normative; regenerate this one if it changes.
-->

# Phase Q6 — migration, end-to-end verification, and same-patch documentation

**Mode:** sequential closeout · **Estimate:** 1–1.5 days
**Entry:** Q4 and Q5 green
**Exit:** approved migration, E2E proof, docs/comments updated in the same patch, rollback proof,
release report filed

## 0. What this phase actually is

This is the only phase that touches the **live** `ttod.yml`, and only after every gate before it
is green and a human has approved a semantic diff. It is also the phase where every documentation
string this whole programme deferred — "License: CC BY-NC-SA 4.0" in `CLAUDE.md` and the `ttod.yml`
header, the stale editing-rule cross-references, hardcoded counts — finally gets corrected,
because §8 of the master contract requires docs to move in the same patch as the behavior they
describe, and this is the last patch.

## 1. Required reading, in order

1. Every prior `docs/DEV_PLAN/PHASE-Qx-REPORT.md` (Q0 through Q5) — this phase is a closeout, not
   a fresh design; if any prior report left an item "carried forward," resolve it here or state
   explicitly why it's still open and the release cannot proceed.
2. `docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md` §6 (full gate matrix — this phase must
   pass every row, not just the ones newly introduced here), §7 (rollback law), §8 (documentation
   propagation table, in full — this is your literal checklist).
3. `docs/DEV_PLAN/DECISIONS/Q0-2026-08-18-RIGHTS-LICENSE-NC.md` — the license strings you are now
   authorized to actually rewrite in `CLAUDE.md` and the `ttod.yml` header (this decision explicitly
   deferred that rewrite to Q6; this is Q6).
4. `CLAUDE.md`, `.cursor/rules/ttod-editing.mdc`, `sources/tao-of-ai-development/README.md` — the
   full current text of everything you're about to update, not a summary.

## 2. Migration sequence

1. Re-hash the Q0 inputs and reconcile any drift since Q0's report — if `cli.py`, `ttod.yml`, or
   the editing rule changed for reasons unrelated to this programme in the meantime, note it.
2. Generate a v3 candidate **in a temporary path**, not in place. Do not invent missing
   authorship, validation, sources, or licenses during this generation — every gap becomes an
   explicit unresolved/legacy state, per contract §2.1's compatibility rules.
3. Convert numeric tag scalars (the live `404` bug) to string form **only** through an explicit,
   logged migration decision for that specific conversion — this is the one place a coercion like
   this is allowed, because it's human-approved and logged, unlike the silent-coercion anti-pattern
   forbidden in Q2E.
4. Recompute all derived metadata (totals, last IDs, taxonomy decisions, collection counts,
   coverage, statistics) mechanically from the candidate — never copy a number from a prior
   document or from memory of what it "should" be.
5. Produce a **semantic diff** between the live `ttod.yml` and the v3 candidate — field-by-field,
   human-readable, not a raw text diff of 141KB of YAML — and present it for approval.
6. **Obtain human approval before replacing `ttod.yml` atomically.** This step cannot be automated
   away; if you are an agent executing this file, your job ends at producing the diff and the
   approval request, and resumes only after an explicit human go-ahead is recorded (in the report,
   quote who approved it and when).
7. Only after approval: run the Q3 write transaction (lock, re-read, write temp, fsync, atomic
   rename, validate persisted bytes) to replace the live `ttod.yml`.

## 3. End-to-end and failure-injection proof

1. Run the full gate matrix (§6 of the master contract) against the migrated result.
2. Run a real TTOD → Athanor → proposal → TTOD review/accept round trip on fixtures (reuse Q4's
   fixtures if suitable; do not skip this because Q4 already tested it in isolation — Q6 proves it
   against the actual migrated v3 data shape).
3. Run failure injection at three points: after the lock is acquired, after the temp file is
   written, and before the rename. At each point, prove the source `ttod.yml` bytes survive
   unchanged (this is the concrete proof Q3's rollback design was meant to provide — Q6 is where
   it finally gets exercised against something that matters).
4. Verify `arch-052` is displayable as a pedagogical quote but evidence-inadmissible for Athanor/
   WPL architecture claims, against the live migrated data (not just Q5's synthetic fixture).

## 4. Same-patch documentation (the §8 checklist, applied)

In the **same** implementation patch:

- `CLAUDE.md` — update `License:` from `CC BY-NC-SA 4.0` to reflect the split (point to
  `LICENSE-CODE`/`LICENSE-CONTENT`, per the decision record), and any schema/field references that
  changed shape from v2.2 to v3.
- `.cursor/rules/ttod-editing.mdc` — align with the now-mechanically-enforced rules; remove
  guidance that's now redundant with schema validation, keep guidance the schema can't express.
- `sources/tao-of-ai-development/README.md` and the `ttod.yml` header — same license-string update,
  plus schema version bump (`Schema Version: 2.2.0` → whatever v3 lands as).
- User-facing CLI docs (`--help` text) for every command touched since Q3.
- `docs/DEV_PLAN/INDEX.md` — flip every phase's state to `DONE` only as its own report went green;
  do not batch-flip all phases to `DONE` just because Q6 completed.
- Every pertinent public docstring/invariant comment at a destructive-operation boundary (the
  transaction lock, the erasure path, the self-corroboration check) — comments explain the durable
  _why_ (atomicity, human promotion, self-corroboration, rights/erasure), not line-by-line
  mechanics. A schema or behavior change with stale docs/comments fails the docs-contract gate —
  this is not optional polish.

## 5. Touched-path budget

**Allowed:** the approved candidate `ttod.yml` (only after human approval, via the Q3 transaction),
documentation and rules files named in §4, pertinent docstrings, the release report, a generated
baseline manifest.

**Forbidden:** rewriting source chapters under `sources/` (they are immutable inputs, per contract
§7), injecting new corpus content, any deployment action, any `git commit`/`git push` unless
separately authorized by the human operator at that moment — finishing this phase's file changes
does not itself authorize committing or pushing them.

## 6. Do NOT (failure modes seen on this class of task)

- Do not replace `ttod.yml` without a recorded human approval of the semantic diff. This is the
  one hard stop in the entire programme that a fully autonomous agent run must not cross alone.
- Do not invent missing authorship, validation, source, or license facts to make the v3 candidate
  "cleaner." Gaps stay gaps, explicitly marked.
- Do not silently coerce the `404`-style tag bug anywhere except through the one logged, approved
  migration-decision step in §2.3.
- Do not flip every phase's status to `DONE` in `docs/DEV_PLAN/INDEX.md` as a batch edit — each
  phase's `DONE` state must trace to that phase's own green report.
- Do not treat "the plan document says Phase Q is complete" as evidence it's complete. Per the
  master contract's closing line: never claim Phase Q complete from planning-document checks
  alone — only from the gate matrix and reports.
- Do not skip the failure-injection tests because the happy path passed. The rollback gate exists
  specifically for the unhappy paths.

## 7. Applicable gates (all of §6, explicitly including)

| Gate          | Required proof                                                                                                                         |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Rollback      | induced failures leave ttod.yml byte-identical and no orphan canonical ID                                                              |
| Round trip    | TTOD-out and proposal-in preserve origin/license/validation/related/deprecation/ancestry and all digests                               |
| Documentation | changed contract appears in schemas, CLI help, CLAUDE, Cursor rule, source README, plan/report, and pertinent code comments/docstrings |
| No mutation   | no corpus injection, shared DB migration, deployment, commit, push, or source-chapter rewrite without separate authority               |

## 8. Exact commands

```bash
cd /Users/ruvebal/src/ttod
. .venv/bin/activate
python cli.py validate --strict --json
python cli.py stats --check
python -m unittest discover -s tests -p 'test_*.py'
python cli.py snapshot --output /private/tmp/ttod-snapshot-a.json
python cli.py snapshot --output /private/tmp/ttod-snapshot-b.json
cmp /private/tmp/ttod-snapshot-a.json /private/tmp/ttod-snapshot-b.json
python cli.py bridge-self-test --fixture tests/fixtures/q4_roundtrip.json
```

## 9. Report requirements

File `docs/DEV_PLAN/PHASE-Q6-REPORT.md`: state, the semantic diff presented for approval and who
approved it and when, full gate-matrix results (every row, pass/fail), the three failure-injection
results with proof of byte-identical rollback, the `arch-052` live-data verdict, the complete list
of documentation files updated in this patch with a one-line summary of what changed in each,
files touched, and a final statement of whether Phase Q is genuinely complete or what specifically
remains.

## 10. Agent prompt — paste this into Cascade/Devin

```text
Act as TTOD release engineer for Phase Q6, the closeout phase. Work only inside
/Users/ruvebal/src/ttod. Read every prior docs/DEV_PLAN/PHASE-Qx-REPORT.md (Q0 through Q5), docs/
DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md sections 6, 7, and 8 in full, docs/DEV_PLAN/
DECISIONS/Q0-2026-08-18-RIGHTS-LICENSE-NC.md, and the full current text of CLAUDE.md,
.cursor/rules/ttod-editing.mdc, and sources/tao-of-ai-development/README.md.

Re-hash the Q0 inputs and reconcile drift. Generate a v3 candidate in a TEMPORARY path — never
invent missing authorship, validation, sources, or licenses; every gap becomes an explicit
unresolved/legacy state. Convert numeric tag scalars like 404 to strings only through one explicit,
logged migration-decision step — this is the sole place such coercion is allowed in the whole
programme. Recompute all derived metadata mechanically, never copied from a document. Produce a
field-by-field semantic diff between the live ttod.yml and the v3 candidate.

STOP at the semantic diff and request human approval before writing anything to ttod.yml. This is
a hard stop — do not cross it autonomously. Only after an explicit recorded approval, run the Q3
write transaction (lock, re-read, temp write, fsync, atomic rename, validate persisted bytes) to
replace the live ttod.yml.

After migration: run the full gate matrix from contract section 6; run a real TTOD-Athanor-
proposal-TTOD round trip against the migrated data; run failure injection after lock, after temp
write, and before rename, proving byte-identical source survival each time; verify arch-052's
verdict (evidence_admissible=false, SELF_DERIVED_NOT_EVIDENCE for Athanor/WPL architecture claims)
against the live migrated data.

In the SAME patch, update: CLAUDE.md's License line (point to LICENSE-CODE/LICENSE-CONTENT per the
decision record) and any v2.2-to-v3 field references; .cursor/rules/ttod-editing.mdc to align with
now-mechanically-enforced rules; the ttod.yml header license string and schema version; CLI --help
text for every command touched since Q3; docs/DEV_PLAN/INDEX.md's phase-state table (flip only the
phases whose own report actually went green — never a batch flip); pertinent docstrings/invariant
comments at destructive-operation boundaries, explaining the durable why, not line-by-line
mechanics. A change without its matching doc update in this same patch fails the docs-contract
gate.

Do not commit or push without separate explicit authorization at that moment — finishing this
phase's edits does not itself authorize git operations. Do not rewrite source chapters under
sources/ or inject corpus content.

File docs/DEV_PLAN/PHASE-Q6-REPORT.md with the semantic diff and its approval record, full gate-
matrix results, the three failure-injection proofs, the arch-052 live verdict, the complete
documentation-update list, files touched, and a final honest statement of whether Phase Q is
complete or what specifically remains.
```
