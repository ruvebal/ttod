<!--
Self-contained runbook. Derived from docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md —
that file is normative; regenerate this one if it changes.
-->

# Phase Q3 — atomic repository and CLI integration

**Mode:** sequential integration · **Estimate:** 1–2 days
**Entry:** all three Q2 lanes green (Q2V, Q2E, Q2P reports filed `DONE`)
**Exit:** atomic CLI transactions and failure rollback proven

## 0. What this phase actually is

This is where the three isolated Q2 modules (`validation.py`, `canonical.py`/`exporter.py`,
`proposals.py`) get integrated behind `cli.py`, and where `ttod.yml` gets a real write path for
the first time in this programme. Everything before this phase was library code with no side
effects on canonical data. This phase is the first one where a bug can actually corrupt
`ttod.yml` — treat every write path with that seriousness.

## 1. Required reading, in order

1. `docs/DEV_PLAN/PHASE-Q2V-REPORT.md`, `PHASE-Q2E-REPORT.md`, `PHASE-Q2P-REPORT.md` — the three
   modules you're integrating. Read their actual public interfaces (not just the reports) before
   writing integration code.
2. `docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md` §6 (Transaction, Rollback, Concurrency
   gate rows) and §7 (rollback and mutation law, in full — this is binding, not aspirational).
3. Current `cli.py` — understand the existing (unsafe) `add` command's behavior. The 2026-08-14
   readiness audit found it appends a YAML list item after the root `templates` mapping rather
   than into `quotes`, with no post-write validation or rollback. You are replacing this, not
   patching it.

## 2. The write transaction — implement exactly this sequence

```
parse input
  -> construct candidate (in memory, not yet written)
  -> validate complete candidate (via Q2V's validator, --strict semantics)
  -> acquire exclusive lock on ttod.yml
  -> re-read live ttod.yml under the lock and rebase the candidate onto it
     (another process may have written since you read; do not trust a stale read)
  -> allocate canonical ID (only now, only under the lock, only for an accept transaction —
     never during generation or proposal import, per contract section 7)
  -> write to a same-directory temp file
  -> flush + fsync
  -> atomic rename over ttod.yml
  -> validate the persisted bytes (re-read what's now on disk, not the in-memory candidate)
  -> release lock
```

On failure at **any** step, `ttod.yml` must remain byte-identical to its pre-transaction state,
and the proposal (if this was a proposal-accept path) must remain resumable — not corrupted, not
half-accepted.

## 3. CLI commands to add/change

- `validate --strict --json` — wires Q2V.
- `stats --check` — recomputes all derived metadata (totals, last IDs, taxonomy decisions,
  collection counts, coverage) from the canonical snapshot in the same pass; reports drift with
  snapshot digest and generation time; **never hand-patches a number**. If it cannot recompute
  atomically, it must stop and report a contract blocker rather than writing a partial fix.
- `snapshot`, `export` — wire Q2E.
- `proposal create/import/review/accept` — wire Q2P plus the write transaction above for `accept`
  specifically. `create`/`import`/`review` never touch `ttod.yml`.
- `deprecate` — ordinary retirement path (sets `status=deprecated`, never deletes).
- guarded `erase` — the higher-law exceptional path; full sensor enforcement is Q5, but the CLI
  command itself must require an explicit authority/decision-reference argument, not proceed on
  defaults.
- `add` — becomes either a human-authored proposal+accept convenience wrapper around the same
  transaction above, or is deprecated outright. It must never bypass review/transaction rules as a
  shortcut, even for "quick" edits.
- Reject unknown tags by default everywhere; taxonomy extension is its own explicit, reviewed
  operation, not a side effect of adding a quote with a new tag.

## 4. Touched-path budget

**Allowed:** `cli.py`, `ttod_core/repository.py` (new — this is where the transaction/locking
logic lives, distinct from the three Q2 modules), `pyproject.toml` (only if a new dependency, e.g.
a file-locking library, is genuinely required — note it explicitly in the report), CLI integration
tests, a migration script skeleton (not executed against live data yet).

**Forbidden:** migrating the **live** `ttod.yml` — all transaction testing in this phase runs
against disposable copies or fixtures, exactly like the original `add` failure probe did. Do not
run an accept/add transaction against the real repository root `ttod.yml` in this phase.

## 5. Do NOT (failure modes seen on this class of task)

- Do not allocate a canonical ID anywhere except inside the locked, re-read, about-to-write step
  of the accept transaction. Not in `proposals.py` (forbidden there by Q2P), not speculatively in
  the CLI before the lock is held.
- Do not skip the "re-read/rebase under lock" step because "nothing else writes to this file right
  now" — the concurrency gate (§6) requires two simultaneous acceptors to serialize correctly, and
  that only works if every acceptor re-reads under the lock rather than trusting an earlier read.
- Do not validate the in-memory candidate and call it done — validate what actually landed on disk
  after the atomic rename. A bug in the write path itself (encoding, truncation) would otherwise
  go undetected.
- Do not test the write transaction against the real `/Users/ruvebal/src/ttod/ttod.yml`. Use a
  disposable copy, exactly as the original 2026-08-14 audit's `add` probe did.
- Do not let `stats --check` silently hand-edit `meta.total_quotes` or any derived count. If exact
  atomic recomputation isn't possible in some case, it must fail loudly with a contract-blocker
  message, not write an approximate number.
- Do not let `add` (or its replacement) skip the validate-under-lock step "for simple quotes."
  There is no simple-quote exception to the transaction.

## 6. Applicable gates

| Gate | Required proof |
| --- | --- |
| Transaction | successful add/accept updates quote, totals, max ID, taxonomy decision, collections, statistics together |
| Rollback | induced failures leave ttod.yml byte-identical and no orphan canonical ID |
| Concurrency | two acceptors serialize and receive distinct IDs or one clean retry; never duplicate |

## 7. Exact commands

```bash
cd /Users/ruvebal/src/ttod
. .venv/bin/activate
python cli.py validate --strict --json
python cli.py stats --check
python -m unittest discover -s tests -p 'test_*.py'
python cli.py snapshot --output /private/tmp/ttod-snapshot-a.json
python cli.py snapshot --output /private/tmp/ttod-snapshot-b.json
cmp /private/tmp/ttod-snapshot-a.json /private/tmp/ttod-snapshot-b.json
```

Run rollback/concurrency tests against a disposable copy, e.g.:
```bash
cp ttod.yml /private/tmp/ttod-q3-test.yml
```
and point the transaction under test at that copy, not the live file.

## 8. Report requirements

File `docs/DEV_PLAN/PHASE-Q3-REPORT.md`: state, the exact write-transaction sequence as
implemented (confirm it matches §2 above step for step, or explain and justify any deviation),
proof of at least one induced-failure rollback test (byte-identical `ttod.yml` after, no orphan
ID), proof of a two-acceptor concurrency test, exact commands/outputs, files touched, safe resume
point for Q4/Q5.

## 9. Agent prompt — paste this into Cascade/Devin

```text
Act as TTOD repository/CLI integration engineer for Phase Q3. Work only inside
/Users/ruvebal/src/ttod. Read docs/DEV_PLAN/PHASE-Q2V-REPORT.md, PHASE-Q2E-REPORT.md, and
PHASE-Q2P-REPORT.md plus the actual public interfaces of ttod_core/validation.py,
ttod_core/canonical.py, ttod_core/exporter.py, and ttod_core/proposals.py. Read docs/DEV_PLAN/
PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md sections 6 and 7 in full — section 7 is binding mutation
law, not a suggestion.

Implement ttod_core/repository.py with this exact write-transaction sequence and no shortcuts:
parse input -> construct in-memory candidate -> validate complete candidate via the Q2V validator
in --strict mode -> acquire an exclusive lock on ttod.yml -> re-read the live file under the lock
and rebase the candidate onto it (never trust an earlier read) -> allocate a canonical ID only now,
only under the lock, only for an accept transaction (never during generation or proposal import)
-> write a same-directory temp file -> flush and fsync -> atomically rename over ttod.yml ->
re-read and validate the bytes now actually on disk -> release the lock. On failure at any step,
ttod.yml must stay byte-identical to before, and any in-flight proposal must remain resumable, not
corrupted.

Wire cli.py commands: validate --strict/--json, stats --check (recomputes all derived metadata
atomically from the canonical snapshot in the same pass; never hand-patches a number; stops with
an explicit contract-blocker message if atomic recomputation isn't possible), snapshot, export,
proposal create/import/review/accept (only accept touches ttod.yml, via the transaction above),
deprecate, guarded erase (requires an explicit authority/decision-reference argument, no default
path), and add (becomes a human-authored proposal+accept convenience wrapper using the same
transaction, or is deprecated — it must never bypass review/transaction rules). Reject unknown
tags by default everywhere.

Test the write transaction ONLY against disposable copies (e.g. cp ttod.yml
/private/tmp/ttod-q3-test.yml) — never against the live repository-root ttod.yml in this phase.
Prove: an induced failure at each major step (after lock, after temp write, before rename) leaves
the target byte-identical to before with no orphan canonical ID; two simultaneous acceptors either
serialize to distinct IDs or one gets a clean retry, never a duplicate; two clean snapshot exports
are byte-identical (cmp them).

File docs/DEV_PLAN/PHASE-Q3-REPORT.md with state, the transaction sequence as implemented, the
rollback and concurrency proofs, exact commands/outputs, files touched, and the safe resume point
for Q4/Q5.
```
