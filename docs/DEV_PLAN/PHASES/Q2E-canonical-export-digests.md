<!--
Self-contained runbook. Derived from docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md —
that file is normative; regenerate this one if it changes.
-->

# Phase Q2E — canonical serialization, exports, and digests

**Mode:** parallel lane (runs alongside Q2V, Q2P in isolated worktrees) · **Estimate:** 1 day
**Entry:** Q1 green
**Exit:** byte-stable exports and manifests

## 0. What this phase actually is, and the parallel-lane rule

Q2V, Q2E, and Q2P run at the same time in separate worktrees, each owning disjoint files. You own
`ttod_core/canonical.py` and `ttod_core/exporter.py` (plus their tests) and nothing else. Do not
touch `ttod_core/validation.py` or `ttod_core/proposals.py` even if you need something from them —
if you need a shared interface that doesn't exist yet, that gap was supposed to be closed in Q1;
record it in the report as a Q1-interface concern rather than defining your own local version of it.

## 1. Required reading, in order

1. `docs/DEV_PLAN/PHASE-Q1-REPORT.md` and its schemas — the shape you are canonicalizing.
2. `docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md` §2.3 (deterministic identity — this
   is your literal spec for `TTOD-C14N-v1`) and §6 (Determinism, Integrity gate rows).

## 2. `TTOD-C14N-v1` — implement exactly this, no substitutions

From contract §2.3, in order:

1. Recursively normalize every string to Unicode NFC.
2. Reject non-string identifiers/tags and non-finite numbers (this is where the `404`-loads-as-
   integer bug gets a permanent home to die — a tag scalar must be a string, full stop; a
   canonicalization pass that silently coerces `404` to `"404"` is not acceptable here, because
   Q1's negative fixture expects this to be a **rejection**, not a silent fix. Silent coercion at
   this layer would make that fixture fail for the wrong reason.)
3. Emit UTF-8 JSON with lexicographically sorted object keys, preserved array order, fixed compact
   separators, and exactly one terminal newline.
4. Compute SHA-256 over the canonical quote projection → `content_digest`.
5. Compute the snapshot digest over quotes sorted by canonical ID, plus schema/taxonomy/collection
   policy versions.
6. Record algorithm name, projection version, source-file digest, record count, export options,
   and included/excluded lifecycle states in a signed-or-hashed snapshot manifest.

**Determinism is the whole point:** two exports from the same canonical state and options must be
byte-identical. Write a test that runs the exporter twice on the same fixture input and diffs the
bytes — not just the parsed structure.

## 3. Atomic export mechanics

JSON and graph exports must:
1. Write to a sibling temporary file in the same directory as the target (not `/tmp` — same
   filesystem, so the final rename is atomic).
2. Flush and `fsync` the temp file.
3. Validate the written bytes (re-read and re-validate, don't trust the in-memory object).
4. Atomically rename the temp file over the target.
5. **Never create `exports/` before validation succeeds** — if validation fails partway, the
   `exports/` directory (or the target file inside it) must not exist in a half-written state.

Implement export policy for `deprecated`/`erased`/`restricted` records: a public export excludes
or redacts them per their lifecycle/rights state (the exact redaction rule is a Q5 sensor concern
for erasure specifically, but the exporter must at minimum have a policy hook here, not bake in
"always include everything").

## 4. Touched-path budget

**Allowed:** `ttod_core/canonical.py`, `ttod_core/exporter.py`, `tests/test_canonical.py` (or
combined `tests/test_exporter.py` — match whatever test-file convention Q2V's report establishes,
if it lands first; otherwise pick one and note it), `ttod_core/__init__.py` only if it doesn't
exist yet.

**Forbidden:** `ttod_core/validation.py`, `ttod_core/proposals.py`, `cli.py`, `ttod.yml`,
`schema/*.json`, anything actually inside `exports/` (that directory is generated output, not
source — do not commit generated exports).

## 5. Do NOT (failure modes seen on this class of task)

- Do not silently coerce a bad tag scalar (e.g. integer `404`) into a valid string during
  canonicalization "to be helpful." Reject it. Coercion belongs to an explicit, human-reviewed
  migration decision (Q6), not to the canonicalization function used everywhere else.
- Do not skip the fsync-then-atomic-rename sequence because "it works without it in testing." The
  failure mode this guards against (partial write on crash/interrupt) won't show up in a normal
  test run; it is a requirement regardless of whether your test suite happens to exercise it.
- Do not create `exports/<file>` and then validate — validate the temp file, then rename. Order
  matters: the target path must never observably exist in a broken state.
- Do not treat "the two exports look the same when I eyeball the JSON" as proof of determinism —
  diff the raw bytes in a test.
- Do not touch `cli.py`. Wiring `export`/`snapshot` commands to this module is Q3's job.

## 6. Applicable gates

| Gate | Required proof |
| --- | --- |
| Determinism | two clean exports/snapshots are byte-identical and share digests |
| Integrity | content/snapshot/WPL/evidence digest tampering fails |

## 7. Exact commands

```bash
cd /Users/ruvebal/src/ttod
python -m unittest discover -s tests -p 'test_canonical.py'
python -m unittest discover -s tests -p 'test_exporter.py'
```

## 8. Report requirements

File `docs/DEV_PLAN/PHASE-Q2E-REPORT.md`: state, confirmation that a two-export byte-diff test
exists and passes, confirmation of the fsync/temp-file/atomic-rename sequence with a description
of how it was tested (e.g. failure injection between temp-write and rename, if attempted — full
failure-injection proof is Q6's job, but note here if you validated the happy path only), export
policy for deprecated/erased/restricted records, files touched, safe resume point for Q3.

## 9. Agent prompt — paste this into Cascade/Devin

```text
Act as TTOD canonicalization/export engineer for Phase Q2E. Work only inside
/Users/ruvebal/src/ttod, in your own isolated worktree/branch. Two other lanes (Q2V, Q2P) run in
parallel in their own worktrees, owning different files — you own only ttod_core/canonical.py and
ttod_core/exporter.py (plus their tests, plus ttod_core/__init__.py if the package doesn't exist
yet). Do not touch ttod_core/validation.py, ttod_core/proposals.py, cli.py, ttod.yml, or
schema/*.json.

Read docs/DEV_PLAN/PHASE-Q1-REPORT.md and its schemas, and docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-
REPAIR-CASCADE.md section 2.3 verbatim — it is your exact spec for TTOD-C14N-v1.

Implement TTOD-C14N-v1 in ttod_core/canonical.py: recursive Unicode NFC normalization; reject (do
not silently coerce) non-string identifiers/tags and non-finite numbers — a tag scalar like
integer 404 must be REJECTED, not auto-converted to "404", because Q1's negative fixture expects a
rejection; emit UTF-8 JSON with lexicographically sorted keys, preserved array order, compact
separators, one terminal newline; compute SHA-256 content_digest over the canonical quote
projection; compute a snapshot digest over ID-sorted quotes plus schema/taxonomy/collection policy
versions; record algorithm, projection version, source-file digest, record count, export options,
and included/excluded lifecycle states in a manifest.

Implement ttod_core/exporter.py: JSON and graph export writing to a same-directory sibling temp
file, flush+fsync, re-read-and-validate the written bytes, atomic rename over the target, and
NEVER create the target path (inside exports/) before validation succeeds. Implement an export
policy hook for deprecated/erased/restricted records rather than always including everything.

Write tests proving two exports of the same fixture input are byte-identical (diff raw bytes, not
parsed structure) and that digest tampering is detected.

File docs/DEV_PLAN/PHASE-Q2E-REPORT.md with state, the byte-diff determinism proof, the
fsync/atomic-rename sequence and how far you tested it, export policy description, files touched,
and the safe resume point for Q3.
```
