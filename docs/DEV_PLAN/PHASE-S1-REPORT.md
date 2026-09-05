# Phase S1′ Report — TTOD bilingual content model (schema + validator + read-path)

**Status:** DONE (2026-09-04)
**Cascade:** [`PHASE-S-TTOD-BILINGUAL-CONTENT-MODEL.md`](PHASE-S-TTOD-BILINGUAL-CONTENT-MODEL.md) §S1′
**Does not mutate live `ttod.yml`:** S2′ owns the atomic `lang: en` backfill and version-constant bump.

## State

S1′ shipped: required `lang`, `translation_of` semantic invariants with named codes, frozen
`tests/fixtures/s1_*` inventory, and full read-path propagation (proposal/transport/bridge/exporter
graph nodes + stats language breakdown). Live `ttod.yml` is **intentionally invalid** under
`validate --strict` until S2′ (missing `lang` on every record) — gated by skipped
`test_live_file_is_strict_valid`.

## Confirmed diagnostic codes (first-write probe)

| Fixture | Exact code |
| --- | --- |
| `s1_negative_missing_lang.json` | `TYPE_ERROR` (jsonschema `required` → mapper) |
| `s1_negative_locale_suffix_id.json` | `TYPE_ERROR` (id pattern fail → mapper) |
| translation invariants | `TRANSLATION_TARGET_UNRESOLVED`, `TRANSLATION_TARGET_INACTIVE`, `TRANSLATION_SAME_LANGUAGE`, `TRANSLATION_SELF_TARGET`, `TRANSLATION_CHAIN`, `TRANSLATION_DUPLICATE_ACTIVE`, `TRANSLATION_SECTION_MISMATCH` |

## Artifacts

| Path | Change |
| --- | --- |
| `schema/quote.schema.json` | `lang` property + `required` |
| `schema/ttod.schema.json` | `meta.languages`; `meta.language` deprecated note |
| `schema/proposal.schema.json` | `candidate_content.lang`, `relation_edges` |
| `schema/transport_quote_out_v1.json` | `lang` |
| `schema/transport_proposal_in_v1.json` | `lang`, `relation_edges` |
| `ttod_core/validation.py` | translation_of invariants + DiagnosticCodes |
| `ttod_core/bridge.py` | `field_mapping_coverage` + `TRANSPORT_FIELDS` include `lang` |
| `ttod_core/exporter.py` | `_graph_nodes` projects `lang` |
| `ttod_core/repository.py` | derived `languages` / `language_counts`; candidate requires `lang` |
| `ttod_core/migration.py` | `_apply_default_lang` so Q6 migrate path stays schema-valid |
| `cli.py` | `add --lang`; `stats` language breakdown |
| `tests/fixtures/s1_*.json` | frozen inventory (10 files) |
| `tests/test_s1_bilingual.py` | exact-code assertions + read-path tests |
| `AGENTS.md` | quote shape + ID/language policy |
| Phase R cascade §4 | GraphNode/WisdomEntry lang notes aligned |

## Commands / exits

```bash
cd ~/src/ttod && PYTHONPATH=. .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
# Ran 176 tests in ~2s — OK (skipped=1: live strict validate pending S2′)

PYTHONPATH=. .venv/bin/python -m unittest tests.test_s1_bilingual -v
# all S1′ fixtures green
```

Live validate (expected fail until S2′):

```bash
PYTHONPATH=. .venv/bin/python cli.py validate --strict
# exits non-zero: 'lang' is a required property on live quotes
```

## Negative tests

All frozen S1′ negatives assert exact `DiagnosticCode` values (never prose substrings).
Section-mismatch is a warning non-strict and an error under `--strict`.

## Resume point

**Next:** S2′ — atomic migration of live `ttod.yml` (`lang: en`, `meta.languages`, bump every
hardcoded `3.0.0` constant, digest recompute, rollback proof). Do not treat R1 contract freeze as
final until S1′ remains green and S2′ restores live `validate --strict` exit 0.
