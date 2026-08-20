# Phase Q5 Report — Policy and Provenance Sensors

**State:** DONE (2026-08-18)  
**Repository:** `/Users/ruvebal/src/ttod`  
**Entry:** Q3/Q4 contract in place  
**Exit:** nine sensors green with positive + negative fixtures each

---

## 1. Sensor summary

| # | Sensor | Module | Negative fixture | Positive fixture | Tests |
| --- | ------ | ------ | ---------------- | ---------------- | ----- |
| 1 | Sibling-process quotation | `independence.py` | `q5_sibling_negative_athanor_wpl.json` | `q5_sibling_positive_ahmes.json` | PASS |
| 2 | Evidence admissibility | `independence.py` | `q5_admissibility_negative_arch052.json` | `q5_admissibility_positive_pedagogical.json` | PASS |
| 3 | Rights / public export | `rights.py` | `q5_rights_negative_restricted.json`, `q5_rights_negative_unresolved.json` | `q5_rights_positive_public.json` | PASS |
| 4 | Observed vs declared generation | `provenance.py` | `q5_generation_negative_mismatch.json` | `q5_generation_positive_match.json` | PASS |
| 5 | Human acceptance | `lifecycle.py` | `q5_human_acceptance_negative_blackbox.json` | `q5_human_acceptance_positive_validated.json` | PASS |
| 6 | Immutable ID / deprecation | `lifecycle.py` | `q5_lifecycle_negative_duplicate_id.json` | `q5_lifecycle_positive_deprecated.json` | PASS |
| 7 | Higher-law erasure | `lifecycle.py` | `q5_erasure_negative_ordinary_delete.json` | `q5_erasure_positive_tombstone.json` + repository integration | PASS |
| 8 | Digest transfer | `provenance.py` | `q5_digest_negative_tampered.json` | `q5_digest_positive_valid.json` | PASS |
| 9 | Shared-snapshot equality | `independence.py` | `q5_snapshot_negative_different.json` | `q5_snapshot_positive_equal.json` | PASS |

---

## 2. arch-052 verdict (explicit)

Fixture `q5_admissibility_negative_arch052.json` uses arch-052's real ancestry shape:

- `source`: `athanor/docs/DEV_PLAN/PHASE-2.md`
- `lesson`: `athanor-phase-2`
- `immediate_parent_refs`: `["athanor-phase-2-plan"]`

When `claim_domain=athanor_architecture`:

```
evidence_admissible = false
independence_reason = SELF_DERIVED_NOT_EVIDENCE
code = SELF_DERIVED_NOT_EVIDENCE
```

**No quote-ID special casing** — detection uses ancestry markers only (same pattern matches arch-052).

When `claim_domain=pedagogical`: `evidence_admissible=true` (quote remains valid pedagogy).

---

## 3. Erasure vs deletion proof

| Check | Result |
| ----- | ------ |
| `reject_ordinary_deletion(operation="delete")` | FAIL with `ORDINARY_DELETION_FORBIDDEN` |
| `TTODRepository` has no `delete_quote` | Confirmed |
| Authorized erasure tombstone fixture | PASS — tombstone text, audit fields present |
| Repository `erase_quote` on disposable copy | PASS — produces valid tombstone via sensor 7 |

Erasure replaces `text` with `[REDACTED - legally erased under higher-law authority]`; audit metadata (`erasure_authority`, `erasure_decision_ref`, `reason`, `effective_at`) retained. Personal content not kept in `text`/`teaches`.

---

## 4. Verification

```bash
cd /Users/ruvebal/src/ttod && . .venv/bin/activate
python -m unittest discover -s tests -p 'test_sensors*.py'
# Ran 21 tests — OK

python -m unittest discover -s tests -p 'test_*.py'
# Ran 154 tests — OK
```

---

## 5. Files touched

| Path | Role |
| ---- | ---- |
| `ttod_core/sensors/types.py` | SensorResult, stable codes |
| `ttod_core/sensors/independence.py` | Sensors 1, 2, 9 |
| `ttod_core/sensors/rights.py` | Sensor 3 |
| `ttod_core/sensors/provenance.py` | Sensors 4, 8 |
| `ttod_core/sensors/lifecycle.py` | Sensors 5, 6, 7 |
| `ttod_core/sensors/__init__.py` | Public exports |
| `tests/fixtures/q5_*.json` | 17 fixture files |
| `tests/test_sensors.py` | 21 tests |

Live `ttod.yml` unchanged. No bypass flags on rights sensor.

---

## 6. Safe resume point

| Phase | State |
| ----- | ----- |
| **Q6** | DONE (2026-08-18) | [`PHASE-Q6-REPORT.md`](PHASE-Q6-REPORT.md) |

> **Post-Q6:** arch-052 re-verified on live migrated data — `SELF_DERIVED_NOT_EVIDENCE` for
> Athanor/WPL architecture claims; pedagogical admissibility unchanged.

---

## 7. Design notes

- Sensors consume Q2E `Canonicalizer.verify_content_digest` and `ExportPolicy` — no logic duplication.
- Sibling sensor rejects exact contract §3 edge triples plus sibling-only evidence resolution.
- Rights sensor has no override flag; unresolved/missing/restricted blocks public export.
- Test reviewer identities use `*-NOT-HUMAN` suffix per Q4 convention.
