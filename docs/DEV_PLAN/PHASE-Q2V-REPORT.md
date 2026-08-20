# Phase Q2V Report — strict validation and invariant engine

**Execution date:** 2026-08-18
**Completion pass:** 2026-08-18 (audit close)
**State:** DONE
**Mode:** parallel lane (library complete; Q2E digest recompute now wired)
**Entry:** Q1 DONE (PHASE-Q1-REPORT.md)

> **Post-Q6 closure (2026-08-18):** Live `ttod.yml` now passes `validate --strict` (0 errors).
> Historical baseline below (215 missing origins) reflects pre-migration state; see
> [`PHASE-Q6-REPORT.md`](PHASE-Q6-REPORT.md).

## 1. Exact commands and exit codes

```bash
$ . .venv/bin/activate && python -m unittest discover -s tests -p 'test_validation.py' -v
...
Ran 33 tests in 0.300s
OK
```
Exit code: 0

Full suite: `python -m unittest discover -s tests -p 'test_*.py'` → **107 tests, OK**, exit 0.

Live baseline (must remain red until Q6; detecting drift is success):

```text
quotes missing origin: 215
validate_root (compat): valid=False errors=216 warnings=439
  errors: TYPE_ERROR=1, ORIGIN_UNRESOLVED=215
  warnings: META_COUNT_MISMATCH=12, TAG_NOT_IN_TAXONOMY=427
validate_root (strict): valid=False errors=655
```

`ORIGIN_UNRESOLVED` is now emitted by `validate_root()`, not only `validate_quote()`. The pre-fix root path would have reported 215 origin omissions as 0. `test_missing_origin_visible_on_validate_root` would have failed against that code.

## 2. Diagnostic codes

| Invariant | Code |
| --- | --- |
| Schema | `TYPE_ERROR`, `NON_STRING_TAG`, `MISSING_REVIEW`, `CANONICAL_ID_FORBIDDEN` |
| Identity uniqueness | `DUPLICATE_ID` |
| Prefix/section match | `PREFIX_SECTION_MISMATCH` |
| Meta max-ID | `META_COUNT_MISMATCH` |
| Tag taxonomy closure | `TAG_NOT_IN_TAXONOMY` |
| Collection / lesson refs | `COLLECTION_TARGET_NOT_FOUND`, `LESSON_TARGET_NOT_FOUND` |
| Related | `RELATED_TARGET_NOT_FOUND` |
| Lifecycle | `DEPRECATED_BY_NOT_FOUND`, `SUPERSEDED_BY_NOT_FOUND` |
| Rights (public) | `RIGHTS_INCOMPLETE_FOR_PUBLIC` |
| Origin | `ORIGIN_UNRESOLVED` |
| Ancestry | `ANCESTRY_TARGET_NOT_FOUND`, `ROOT_SOURCE_TARGET_NOT_FOUND` |
| Digest recompute | `DIGEST_MISMATCH` |

Schema-error mapping uses `validator` + path + missing-property name. A missing `origin` is no longer mapped to `MISSING_REVIEW`.

## 3. Q0 readiness findings → codes

| Q0 finding | Code | Status |
| --- | --- | --- |
| 236 used tags absent from taxonomy | `TAG_NOT_IN_TAXONOMY` | **DETECTED** (427 tag warnings on live YAML — one per use) |
| 215 records omit `origin`, counted as human | `ORIGIN_UNRESOLVED` | **DETECTED on validate_root** (215 errors) |
| Stale YAML counts | `META_COUNT_MISMATCH` | **DETECTED** (12 warnings) |
| Tag `404` loads as integer | `NON_STRING_TAG` / `TYPE_ERROR` | **DETECTED** (1 live TYPE_ERROR at schema layer on current YAML) |
| Collection/lesson/related resolve | matching `*_NOT_FOUND` | **ENFORCED** |

## 4. Strict vs compatibility

- `strict=True`: warnings become errors.
- `strict=False`: drift is a **nonzero visible warning list**. Live YAML currently yields 439 warnings.

## 5. Q1 fixtures through the full validator

`TestQ1FixturesThroughValidator` replays Q1 fixtures with exact codes:

- five positives → zero errors (including real C14N digests)
- missing review → `MISSING_REVIEW`
- missing origin → `ORIGIN_UNRESOLVED`
- integer tag → `NON_STRING_TAG`
- digest mismatch fixture → `DIGEST_MISMATCH`
- dangling related / broken ancestry / public rights → corresponding codes via a minimal root
- canonical id in proposal → `CANONICAL_ID_FORBIDDEN`

Sibling-output and `arch-052` remain Q5 (`SELF_DERIVED_NOT_EVIDENCE`).

## 6. Files touched

**Created/updated:** `ttod_core/validation.py`, `tests/test_validation.py`

**Forbidden (not touched):** `cli.py`, `ttod.yml`, `schema/*.json` (Q1 completion pass edited schemas separately)

## 7. Q1-interface concerns (closed)

The Q1 `if/then` origin bug is fixed in Q1 completion; Q2V mapping no longer treats “required validation” as a catch-all.

Lesson lists are now walked (`quote_ids` / `ids`); an empty-list early-return no longer skipped populated lists.

## 8. Safe resume point for Q3

Import `TTODValidator` from `ttod_core.validation`. Wire `validate --strict` and JSON diagnostics. Do **not** expect live `ttod.yml` to pass `--strict` until Q6 migration.

## 9. Gate status

| Gate | Required proof | Status |
| --- | --- | --- |
| Schema | Q1 positives pass full validator; schema-expressible negatives fail with expected code | **GREEN** |
| Current-data strictness | Baseline inconsistencies reported; `--strict` promotes warnings | **GREEN** (live YAML fails; that is the gate) |
| Reference | related, collection, lesson (dict **and** list), ancestry, deprecation targets | **GREEN** |
| Integrity (digest) | `q1_negative_digest_mismatch.json` → `DIGEST_MISMATCH` | **GREEN** |

## 10. Completion-pass delta (audit close)

Audit: `validate_root()` skipped per-quote origin/digest; Q1 fixtures were not replayed with exact codes; digest check was format-only. This pass wires origin+digest on the root, recomputes TTOD-C14N-v1, and adds the fixture replay class. Tests that would have failed pre-fix: `test_missing_origin_visible_on_validate_root`, `test_q1_negative_digest_mismatch_code`.
