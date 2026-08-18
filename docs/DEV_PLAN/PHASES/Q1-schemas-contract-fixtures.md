<!--
Self-contained runbook. Derived from docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md —
that file is normative; regenerate this one if it changes.
-->

# Phase Q1 — schemas and contract fixtures

**Mode:** sequential · **Estimate:** 1–1.5 days
**Entry:** Q0 green (`docs/DEV_PLAN/PHASE-Q0-REPORT.md` files `DONE` or all Q1-relevant blockers
explicitly resolved)
**Exit:** schemas and golden fixtures validate/fail exactly as specified — no informal judgment
calls left for Q2

## 0. What this phase actually is

Turn the frozen data contract (master contract §2.1–2.3) into three executable JSON Schemas plus
a fixture suite that proves each invariant fires. This phase produces **schemas and tests only**.
It does not touch `cli.py`, `ttod_core/` (Q2's job), or `ttod.yml` (Q6's job). If your fixture
needs a validator to pass, write the fixture as a `.json`/`.yaml` file under `tests/fixtures/`, not
as inline logic in `cli.py`.

## 1. Required reading, in order

1. `docs/DEV_PLAN/PHASE-Q0-REPORT.md` — confirms what was frozen; treat every field name/enum
   named there as fixed. If it disagrees with what you're about to implement, the report wins;
   stop and reconcile before writing schema.
2. `docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md` §2 (target data contract, in full —
   this is your schema spec) and §3 (independence protocol — this is where the sibling-output
   rejection edges and `arch-052` fixture requirement come from).
3. Current `.cursor/rules/ttod-editing.mdc` — the schema must not silently contradict the
   hand-maintained editing discipline still governing `ttod.yml` today.
4. `ttod.yml` (skim structure, not full content) — your schema must be able to describe the
   *shape* of existing records even where content is legacy/unresolved, per the "existing values
   remain byte-preserved" compatibility rule in contract §2.1.

## 2. The three schemas

Build against **JSON Schema Draft 2020-12**.

1. `schema/quote.schema.json` — validates a single quote record against every axis in contract
   §2.1's table (Identity, Content, Authorship, Review, Source, Evidence, Rights, Relations,
   Lifecycle, Ancestry). Each axis's "Rule" column in that table is a schema constraint, not prose
   — encode it (e.g. `origin` enum is exactly `human | studio | blackbox | mixed | legacy-unknown`,
   with no default; a missing/absent origin must fail differently than an explicit
   `legacy-unknown`, per "no silent provenance promotion" in contract §1).
2. `schema/ttod.schema.json` — validates the document root: `meta`, `sections`, `tag_taxonomy`,
   `collections`, `lessons`, and a `quotes` array whose items `$ref` `quote.schema.json`.
3. `schema/proposal.schema.json` — validates the pre-canonical proposal shape from contract §2.2.
   **A proposal schema must reject a canonical `id` field being present at all** — that is the
   mechanical enforcement of "no proposal reserves a section-number ID."

## 3. Fixtures — one directory, explicit pass/fail split

Under `tests/fixtures/q1_*`:

**Positive** (must validate clean): legacy-read record (old shape, missing fields present as
`legacy-unknown`/unresolved rather than defaulted), v3 human-authored record, v3 reviewed-blackbox
record (has `validated_by`-equivalent human acceptance), deprecated record, protected
erasure-tombstone record.

**Negative** — one fixture per invariant, and the test must assert an **exact error code**, not a
substring of a prose message:
- missing review on blackbox/mixed content
- unknown or non-string tag (this is the `404`-as-integer bug the Q0 readiness audit found live in
  `ttod.yml` — your fixture should be exactly that shape)
- missing rights decision on a record flagged for public export
- dangling `related` target
- a canonical `id` present inside a proposal record
- broken ancestry (an `immediate_parent_refs` entry that doesn't resolve)
- digest mismatch (`content_digest` that doesn't match a `TTOD-C14N-v1` recomputation)
- sibling-output evidence (an `evidence_snapshot_digest` that resolves only to a TTOD copy or a
  sibling process's own draft — the exact edges contract §3 lists as rejected)
- `arch-052` self-corroboration: a fixture shaped exactly like `arch-052` (ancestry pointing to an
  Athanor Phase 2 plan) used as evidence for an Athanor/WPL architecture claim — must fail with
  `SELF_DERIVED_NOT_EVIDENCE`, not a generic validation error.

Write `tests/test_schema_contract.py` (or the project's existing test framework/runner if
different — check `pyproject.toml` before assuming `pytest`) asserting each fixture's expected
error **code**, and that every positive fixture is clean with zero errors.

## 4. Touched-path budget

**Allowed:** `schema/*.json` (new files), `tests/fixtures/q1_*` (new files), a new
`tests/test_schema_contract.py`, and contract docs under `docs/DEV_PLAN/` if you discover and need
to record an ambiguity (do not silently resolve an ambiguity yourself — record it and pick the
stricter reading, per contract §1 "an implementation may be stricter than WPL Core; it may not
weaken portable meaning").

**Forbidden:** `cli.py`, `ttod.yml`, anything under `ttod_core/` (doesn't exist yet — Q2 creates
it), `exports/`.

## 5. Do NOT (failure modes seen on this class of task)

- Do not implement validation logic in Python and call it "the schema." The schema is the JSON
  Schema document; Q2V later writes the Python validator that *uses* it plus the invariants JSON
  Schema alone cannot express (cross-record uniqueness, digest recomputation).
- Do not make error assertions substring-match prose ("contains 'missing'"). Assert an exact,
  stable code. Free-tier agents left unconstrained here tend to write brittle tests that pass
  today and silently stop testing anything the moment the prose wording changes.
- Do not default `origin` to `human` anywhere, including in a fixture meant to represent "typical"
  data — that is the exact anti-pattern contract §1 forbids ("no default-to-human").
- Do not let the proposal schema accept a canonical `id`. This is the single most safety-critical
  constraint in this phase — it is what makes "human promotion" possible to enforce later in Q3.
- Do not touch `cli.py` even to "just wire up the schema for a quick check." That coupling belongs
  to Q2E/Q3.

## 6. Applicable gates

| Gate | Required proof |
| --- | --- |
| Schema | quote/root/proposal positive fixtures pass; each negative fails with expected code |

## 7. Exact commands

```bash
cd /Users/ruvebal/src/ttod
python -m unittest discover -s tests -p 'test_schema_contract.py'
# or, if the project uses pytest (check pyproject.toml first):
# pytest tests/test_schema_contract.py -v
```

## 8. Report requirements

File `docs/DEV_PLAN/PHASE-Q1-REPORT.md`: state, list of fixtures created (positive/negative) with
one line each on what invariant it proves, exact test command and output, any ambiguity found in
the contract and how it was resolved (stricter reading + citation), files touched, and the safe
resume point for Q2V/Q2E/Q2P (which may now run in parallel worktrees).

## 9. Agent prompt — paste this into Cascade/Devin

```text
Act as TTOD schema engineer for Phase Q1. Work only inside /Users/ruvebal/src/ttod. Before writing
anything, read docs/DEV_PLAN/PHASE-Q0-REPORT.md, docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-
CASCADE.md sections 2 and 3 in full, .cursor/rules/ttod-editing.mdc, and skim the structure (not
full content) of ttod.yml.

Implement three Draft 2020-12 JSON Schemas: schema/quote.schema.json (every axis in contract
section 2.1's table — Identity, Content, Authorship, Review, Source, Evidence, Rights, Relations,
Lifecycle, Ancestry — each with the exact enum/constraint the table specifies; origin has no
default and legacy-unknown is an explicit value, never inferred), schema/ttod.schema.json (root:
meta, sections, tag_taxonomy, collections, lessons, quotes[] referencing quote.schema.json), and
schema/proposal.schema.json (contract section 2.2's shape; MUST reject any canonical id field
being present at all).

Create fixtures under tests/fixtures/q1_*: five positive (legacy-read, v3 human, v3
reviewed-blackbox, deprecated, protected erasure-tombstone) and one negative fixture per invariant:
missing review on blackbox/mixed, unknown/non-string tag (mirror the live 404-as-integer bug found
in ttod.yml img-009/img-024), missing rights decision on public-export-flagged record, dangling
related target, canonical id inside a proposal, broken ancestry, digest mismatch against a
TTOD-C14N-v1 recomputation, sibling-output evidence, and an arch-052-shaped self-corroboration
fixture that must fail with exactly SELF_DERIVED_NOT_EVIDENCE.

Write tests/test_schema_contract.py asserting exact error codes per negative fixture (never a
prose substring) and zero errors on every positive fixture. Check pyproject.toml for the actual
test runner before assuming pytest vs unittest.

Touch only schema/*.json, tests/fixtures/q1_*, tests/test_schema_contract.py, and docs/DEV_PLAN/
if you must record a resolved ambiguity. Do not touch cli.py, ttod.yml, ttod_core/, or exports/.
Do not implement validator logic in Python and call it done — that's Q2V's job; this phase is the
schema documents plus fixtures proving them.

File docs/DEV_PLAN/PHASE-Q1-REPORT.md with state, the fixture list and what each proves, exact
test command/output, any ambiguity found and its stricter-reading resolution with citation, files
touched, and the safe resume point for Q2V/Q2E/Q2P.
```
