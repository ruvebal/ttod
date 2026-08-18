<!--
Self-contained runbook. Derived from docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md —
that file is normative; regenerate this one if it changes.
-->

# Phase Q2P — proposal and human-review workflow

**Mode:** parallel lane (runs alongside Q2V, Q2E in isolated worktrees) · **Estimate:** 1–1.5 days
**Entry:** Q1 green
**Exit:** proposal lifecycle and human-review gates enforced

## 0. What this phase actually is, and the parallel-lane rule

Q2V, Q2E, and Q2P run at the same time in separate worktrees, each owning disjoint files. You own
`ttod_core/proposals.py` and `tests/test_proposals.py` and nothing else. This is the phase where
the whole programme's core safety property lives — **a machine may propose but may not accept** —
so treat every shortcut temptation here as a security bug, not a convenience.

## 1. Required reading, in order

1. `docs/DEV_PLAN/PHASE-Q1-REPORT.md` and `schema/proposal.schema.json` specifically — re-confirm
   it rejects a canonical `id` field. If it doesn't, stop and escalate before writing this module;
   do not "just also check for that" in Python as a substitute for the schema being correct.
2. `docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md` §2.2 (proposal record shape) and §1
   ("Proposal in" and "Human promotion" bullets — this is the authority boundary you're encoding).

## 2. Task breakdown

Implement `ttod_core/proposals.py`:

1. **Proposal ID allocation.** A proposal gets a `proposal_id` (UUID/URN) at creation time. It
   never gets, reserves, or previews a canonical section-number ID. There is no code path in this
   module that writes to `ttod.yml` or computes what the "next" canonical ID would be — that
   computation belongs entirely to Q3's acceptance transaction, which re-reads the live snapshot
   under a lock. If you catch yourself writing an ID-allocation function here, delete it.
2. **Status machine.** `proposed → needs_revision | accepted | rejected | withdrawn`. Model this
   as an explicit enum/state machine, not free-text status strings, so invalid transitions
   (e.g. `rejected → accepted`) are a code-level impossibility, not a runtime check someone can
   forget to call.
3. **Append-only review activities.** Every review action (comment, revision request, accept
   decision) is appended to a `human review activities[]` list. Nothing in this list is ever
   mutated or deleted after being written — this is the audit trail Q5's sensors will check.
4. **Identified-human acceptance.** An "accept" review activity must carry an identified human
   reviewer (a real identity string, never a placeholder, never inferred). This module validates
   that the *shape* is correct; it does **not** itself have an `accept()` method that flips a
   proposal to canonical — that transaction, including the exclusive lock and `ttod.yml` write, is
   Q3's. This module's job ends at "this proposal is now marked accepted and carries an identified
   human reviewer and an `accepted_quote_id`-shaped placeholder for Q3 to fill atomically."
5. **Rights and provenance carry-through.** `source_refs`, `origin`, `rights`, `related`, and
   ancestry fields travel through a proposal exactly as received — this module must not fill in,
   infer, or "clean up" any of them. If a rights field is unresolved on input, it stays unresolved
   on output.
6. **Preserve WPL/evidence digests exactly.** `wpl_record_id`/`wpl_record_digest` and the shared
   `evidence_snapshot_digest` pass through byte-for-byte. Do not recompute or re-derive them here.

## 3. Touched-path budget

**Allowed:** `ttod_core/proposals.py`, `tests/test_proposals.py`, `ttod_core/__init__.py` only if
it doesn't exist yet.

**Forbidden:** `ttod_core/validation.py`, `ttod_core/canonical.py`, `ttod_core/exporter.py`,
`cli.py`, `ttod.yml`, `schema/*.json`. **Especially forbidden:** any function in this module that
writes to `ttod.yml`, computes a canonical ID, or exposes an "accept" capability usable by a model
or automated caller without a human-identity argument that the caller cannot omit or fake.

## 4. Do NOT (failure modes seen on this class of task)

- Do not implement ID pre-allocation "to make Q3 simpler later." Reserving a section-number ID
  before human acceptance is exactly the bug this whole phase exists to prevent — a half-finished
  proposal that already looks like it has a canonical ID is how silent provenance promotion
  happens.
- Do not let `accept()` (or equivalently-named method) actually mutate canonical state or write
  `ttod.yml`. This module models the proposal's own lifecycle; the atomic acceptance transaction
  against the live repository is out of scope here and belongs to Q3.
- Do not accept a free-text or optional reviewer identity on an "accept" transition. If the
  identity argument is missing, the transition must be a hard error, not a transition that
  proceeds with a null/placeholder reviewer.
- Do not "helpfully" backfill a missing `rights` or `origin` field on a proposal so that
  downstream code has less to handle. Carrying data through unmodified, including its gaps, is the
  requirement.
- Do not mutate or delete entries in the review-activities audit trail, even to "fix a typo" in a
  test fixture — model it as append-only for real, including in your own test setup code.

## 5. Applicable gates

| Gate | Required proof |
| --- | --- |
| Review | blackbox/mixed proposal without identified human acceptance cannot become active |
| Capability | model can propose but cannot accept (this phase proves it at the module level; Q3/Q4 prove it at the system level) |

## 6. Exact commands

```bash
cd /Users/ruvebal/src/ttod
python -m unittest discover -s tests -p 'test_proposals.py'
```

## 7. Report requirements

File `docs/DEV_PLAN/PHASE-Q2P-REPORT.md`: state, confirmation (with a pointer to the specific test)
that no code path in this module can write `ttod.yml` or allocate a canonical ID, confirmation
that an accept-without-identified-human transition is a hard error and is tested, confirmation
that rights/origin/provenance fields pass through unmodified (test with a fixture that has
deliberately unresolved fields and assert they remain unresolved), files touched, safe resume
point for Q3.

## 8. Agent prompt — paste this into Cascade/Devin

```text
Act as TTOD proposal-workflow engineer for Phase Q2P. Work only inside /Users/ruvebal/src/ttod, in
your own isolated worktree/branch. Two other lanes (Q2V, Q2E) run in parallel in their own
worktrees, owning different files — you own only ttod_core/proposals.py and
tests/test_proposals.py (plus ttod_core/__init__.py if the package doesn't exist yet). Do not
touch ttod_core/validation.py, ttod_core/canonical.py, ttod_core/exporter.py, cli.py, ttod.yml, or
schema/*.json.

Read docs/DEV_PLAN/PHASE-Q1-REPORT.md and schema/proposal.schema.json (confirm it rejects a
canonical id field before proceeding — if it doesn't, stop and report this instead of working
around it in Python), and docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md section 2.2 and
the "Proposal in"/"Human promotion" bullets of section 1.

Implement ttod_core/proposals.py: proposal_id (UUID/URN) allocated at creation, NEVER a canonical
section-number ID and no function anywhere in this module that computes or reserves one; an
explicit status enum/state machine (proposed, needs_revision, accepted, rejected, withdrawn) that
makes invalid transitions impossible at the type level, not just checked at runtime; an
append-only human review activities list that is never mutated or deleted, including in your own
tests; an accept-shaped transition that requires an identified human reviewer argument that cannot
be omitted, null, or a placeholder — but does NOT itself write ttod.yml or allocate a canonical ID
(that atomic transaction is Q3's, not this module's); source_refs, origin, rights, related, and
ancestry fields must pass through completely unmodified, including when they are unresolved on
input — do not backfill or infer anything; wpl_record_id/digest and evidence_snapshot_digest pass
through byte-for-byte, never recomputed here.

Write tests/test_proposals.py proving: no code path can write ttod.yml or allocate a canonical ID;
accept without an identified human reviewer is a hard error; a fixture with deliberately
unresolved rights/origin fields keeps them unresolved after passing through this module; invalid
status transitions (e.g. rejected to accepted) are impossible or hard errors.

File docs/DEV_PLAN/PHASE-Q2P-REPORT.md with state, pointers to the specific tests proving the
no-canonical-write and no-silent-accept properties, the pass-through-fidelity proof, files
touched, and the safe resume point for Q3.
```
