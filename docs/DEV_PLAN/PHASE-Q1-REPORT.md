# Phase Q1 Report — schemas and contract fixtures

**Execution date:** 2026-08-18
**Completion pass:** 2026-08-18 (audit close)
**State:** DONE
**Mode:** sequential
**Entry:** Q0 DONE (PHASE-Q0-REPORT.md filed 2026-08-18)

## 1. Exact commands and exit codes

```bash
$ . .venv/bin/activate && python -m unittest discover -s tests -p 'test_schema_contract.py' -v
...
Ran 16 tests in 0.103s
OK
```
Exit code: 0

Full suite (Q1–Q2P together):

```bash
$ . .venv/bin/activate && python -m unittest discover -s tests -p 'test_*.py'
Ran 107 tests in 0.403s
OK
```
Exit code: 0

## 2. Schemas

### 2.1 schema/quote.schema.json
Validates a single quote against v3 axes from master contract §2.1.

**Key constraints:**
- `origin` enum: `human | studio | blackbox | mixed | legacy-unknown` (no default)
- `id` pattern: `^[a-z]+-[0-9]+$`
- `allOf` conditional 1: `if` requires `origin` **and** `origin ∈ {blackbox, mixed}` before demanding `validation` with `reviewer_id`, `activity_id`, `status=validated`. A missing origin does **not** match this branch.
- `allOf` conditional 2: `rights.access=public` requires `rights.license` and `rights.holder`
- Digest fields: SHA-256 pattern `^[a-f0-9]{64}$`

### 2.2 schema/ttod.schema.json
Root: `meta`, `sections`, `tag_taxonomy`, `collections`, `lessons`, `quotes[]` `$ref` quote schema.

### 2.3 schema/proposal.schema.json
`not` required on `id` — rejects any canonical id presence.

## 3. Fixtures

### 3.1 Positive (5) — schema-clean

| Fixture | Proves |
| --- | --- |
| `q1_positive_legacy_read.json` | `origin=legacy-unknown` and missing v3 fields allowed |
| `q1_positive_v3_human.json` | Full v3 human record |
| `q1_positive_v3_reviewed_blackbox.json` | Blackbox with identified human validation |
| `q1_positive_deprecated.json` | Lifecycle deprecation metadata |
| `q1_positive_erasure_tombstone.json` | `status=erased` tombstone shape |

Positive v3 fixtures that carry `content_digest` now store a real TTOD-C14N-v1 digest (format-valid at Q1; recomputation checked in Q2V/Q2E).

### 3.2 Negative — schema-enforced (exact code asserted)

| Fixture | Code |
| --- | --- |
| `q1_negative_missing_review_blackbox.json` | `MISSING_REVIEW` |
| `q1_negative_missing_origin.json` | `ORIGIN_UNRESOLVED` |
| `q1_negative_non_string_tag.json` | `NON_STRING_TAG` |
| `q1_negative_missing_rights_public_export.json` | `RIGHTS_INCOMPLETE_FOR_PUBLIC` |
| `q1_negative_canonical_id_in_proposal.json` | `CANONICAL_ID_FORBIDDEN` |

Tests call `schema_error_code(ValidationError)` and assert the **exact code string**. They do not substring-match prose.

### 3.3 Negative — schema-pass, deferred (honest, not fake-fail)

JSON Schema cannot express these. Tests assert schema **passes** and name the downstream code:

| Fixture | Deferred to | Expected code |
| --- | --- | --- |
| `q1_negative_dangling_related.json` | Q2V | `RELATED_TARGET_NOT_FOUND` |
| `q1_negative_broken_ancestry.json` | Q2V | `ANCESTRY_TARGET_NOT_FOUND` |
| `q1_negative_digest_mismatch.json` | Q2V/Q2E | `DIGEST_MISMATCH` |
| `q1_negative_sibling_output_evidence.json` | Q5 | `SELF_DERIVED_NOT_EVIDENCE` |
| `q1_negative_arch_052_self_corroboration.json` | Q5 | `SELF_DERIVED_NOT_EVIDENCE` |

## 4. Ambiguities resolved

### 4.1 Schema version pattern
Allow `^[0-9]+\.[0-9]+\.[0-9]+$` so legacy v2.2.0 records remain byte-preserved. Citation: contract §2.1 compatibility.

### 4.2 Erasure tombstone ID
Erased records keep standard IDs (`arch-100`); `status=erased` is the marker.

### 4.3 Missing origin vs blackbox `if/then` (completion pass)
Draft 2020-12 `if` without `required: ["origin"]` treats an absent property as matching `origin ∈ {blackbox, mixed}`. That made omitted origin fail as `'validation' is a required property` (`MISSING_REVIEW`) instead of `ORIGIN_UNRESOLVED`. Fixed: `if.required = ["origin"]`. Fixture `q1_negative_missing_origin.json` locks it. This test would have failed against the pre-fix schema.

### 4.4 Public-export rights
Schema now encodes `access=public` → `license` + `holder`. Completeness beyond schema (cross-record) remains Q2V.

## 5. Files touched

**Created / updated this phase (including completion pass):**
- `schema/quote.schema.json`, `schema/ttod.schema.json`, `schema/proposal.schema.json`
- `tests/fixtures/q1_*` (5 positive, 10 negative)
- `tests/test_schema_contract.py`

**Forbidden (not touched):** `cli.py`, `ttod.yml`, `exports/`

## 6. Safe resume point

Q1 is DONE. Q2V consumes exact codes and deferred fixtures. Q2E uses C14N against digest fixtures. Q2P uses the proposal `not id` constraint.

## 7. Gate status

| Gate | Required proof | Status |
| --- | --- | --- |
| Schema | Positive fixtures pass; each **schema-expressible** negative fails with expected code; inexpressible negatives are deferred with named codes | **GREEN** — 16/16 Q1 tests |

## 8. Completion-pass delta (audit close)

Independent audit found Q1 overstated: error codes were comments, missing-origin matched the blackbox branch, and six “negative” tests actually passed. This pass closed those defects without reopening Q0 or touching `ttod.yml`.
