# Phase Q4 Report — Athanor-Mediated Two-Way Bridge

**State:** DONE (2026-08-18)  
**Repository:** `/Users/ruvebal/src/ttod` (+ Athanor adapter in `/Users/ruvebal/src/athanor`)  
**Entry:** Q3 DONE; Athanor S0-WPL freeze verified at `athanor/docs/DEV_PLAN/PHASE-S0-WPL-CONFORMANCE-FREEZE.md` (READY after S0)  
**Exit:** transport schema frozen, round-trip proven on fixtures, zero canonical-write capability on bridge paths

---

## 1. Sub-lane status

| Sub-lane | State | Proof |
| -------- | ----- | ----- |
| **TTOD transport** | DONE | `schema/transport_*.json`, `ttod_core/bridge.py`, 8 tests, CLI wiring |
| **Athanor adapter** | DONE | `athanor_api/application/ttod_bridge.py`, 6 pytest tests |
| **Live data** | Not touched | All round-trips on fixtures / disposable copies |

---

## 2. Transport schema (v1.0.0)

| Message | Schema file | Purpose |
| ------- | ----------- | ------- |
| Quote-out | `schema/transport_quote_out_v1.json` | TTOD → Athanor; `usage_role=pedagogical` mandatory |
| Proposal-in | `schema/transport_proposal_in_v1.json` | Athanor → TTOD inbox; UUID `proposal_id` only |

Field mapping: `field_mapping_coverage()` documents every `quote.schema.json` property — no silent drops (`tests/test_bridge.py::TestFieldMapping`).

Documented exclusions (v1): `schema_version` (contract_version in transfer_metadata), `authorship_assertion`, legacy `lesson`/`source`.

---

## 3. Capability gate (Athanor cannot write canonical TTOD)

**TTOD transport layer** (`ttod_core/bridge.py`):

- AST import check: no `ttod_core.repository` imports (`assert_no_canonical_write_imports`)
- No accept/deprecate/erase in bridge module
- `run_bridge_self_test` isolated in `ttod_core/bridge_self_test.py` (CLI/test runner only)

**Athanor adapter** (`athanor_api/application/ttod_bridge.py`):

- `TTODSnapshotReader` refuses `.yml`/`.yaml` paths — Q2E JSON only
- `TTODProposalOutbox` writes to outbox directory only
- AST import check: no `ttod` package imports (`assert_no_ttod_write_capability`)
- No `TTODRepository`, no accept path, no canonical ID allocation

Human accept remains exclusively via `python cli.py proposal accept --reviewer-id …` or `add --reviewer-id …` (Q3 transaction).

---

## 4. Round-trip proof (fixtures)

Fixture: `tests/fixtures/q4_roundtrip.json`

| Step | Action | Verified |
| ---- | ------ | -------- |
| 1 | Quote-out from `source_quote` | `usage_role=pedagogical`, digests preserved |
| 2 | Proposal-in import | WPL/evidence digests byte-identical |
| 3 | Human accept (`test-fixture-reviewer-q4-NOT-HUMAN`) | `arch-002` on disposable copy |
| 4 | Accepted record | candidate fields + `wpl_record_digest` + `proposal_id` on quote |

```bash
cd /Users/ruvebal/src/ttod && . .venv/bin/activate
python -m unittest discover -s tests -p 'test_bridge*.py'   # 8 tests OK
cp tests/fixtures/q3_minimal_ttod.yml /tmp/ttod-q4-selftest.yml
python cli.py bridge-self-test --fixture tests/fixtures/q4_roundtrip.json --file /tmp/ttod-q4-selftest.yml
# wpl_record_digest_preserved: true
```

**Athanor side** (snapshot → quote-out → proposal-in → outbox):

```bash
cd /Users/ruvebal/src/athanor && . .venv/bin/activate
pytest tests/test_ttod_bridge.py -q   # 6 passed
```

---

## 5. CLI commands (additive — Q3 semantics unchanged)

| Command | Writes ttod.yml? |
| ------- | ---------------- |
| `bridge quote-out QUOTE_ID --snapshot FILE.json` | No |
| `bridge proposal-in FILE.json` | No (proposals store only) |
| `bridge-self-test --fixture … --file DISPOSABLE.yml` | Yes (disposable copy only; refuses live path) |

---

## 6. Repository change for provenance at accept

`ttod_core/repository.py`: `_apply_proposal_provenance()` copies `proposal_id`, `wpl_record_id`, `wpl_record_digest`, `evidence_snapshot_digest` from Proposal onto accepted quote and recomputes `content_digest`. Required for bridge round-trip integrity.

---

## 7. Verification commands

```bash
# TTOD full suite
cd /Users/ruvebal/src/ttod && . .venv/bin/activate
python -m unittest discover -s tests -p 'test_*.py'
# Ran 133 tests — OK

# Athanor bridge suite
cd /Users/ruvebal/src/athanor && . .venv/bin/activate
pytest tests/test_ttod_bridge.py -q
# 6 passed
```

---

## 8. Files touched

**TTOD**

| File | Change |
| ---- | ------ |
| `ttod_core/bridge.py` | Completed/fixed transport adapters |
| `ttod_core/bridge_self_test.py` | Round-trip runner (isolated from transport) |
| `ttod_core/repository.py` | Proposal provenance on accept |
| `schema/transport_quote_out_v1.json` | (pre-existing) frozen |
| `schema/transport_proposal_in_v1.json` | (pre-existing) frozen |
| `tests/fixtures/q4_roundtrip.json` | Round-trip fixture |
| `tests/test_bridge.py` | Field mapping, capability, round-trip |
| `cli.py` | `bridge` subcommands + `bridge-self-test` |

**Athanor**

| File | Change |
| ---- | ------ |
| `athanor_api/application/ttod_bridge.py` | Read-only snapshot reader + proposal outbox |
| `tests/test_ttod_bridge.py` | Adapter tests |

Live `ttod.yml` unchanged.

---

## 9. Safe resume point

| Phase | State |
| ----- | ----- |
| **Q5** | DONE (2026-08-18) | [`PHASE-Q5-REPORT.md`](PHASE-Q5-REPORT.md) |
| **Q6** | DONE (2026-08-18) | [`PHASE-Q6-REPORT.md`](PHASE-Q6-REPORT.md) |

> **Post-Q6:** Pending proposals may use `proposal accept --reviewer-id …` on live `ttod.yml` via Q3
> transactions. arch-052 adversary verified on migrated live data in Q6.

---

## 10. Not claimed

- Live Athanor HTTP REST binding (studio contract defines resources; implementation is future)
- Live `ttod.yml` migration or production accept
- Q5 independence sensors (e.g. arch-052 adversary) — Q5 scope
