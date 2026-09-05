# Phase S2′ Report — TTOD bilingual content model (atomic migration)

**Status:** DONE (2026-09-04)
**Cascade:** [`PHASE-S-TTOD-BILINGUAL-CONTENT-MODEL.md`](PHASE-S-TTOD-BILINGUAL-CONTENT-MODEL.md) §S2′
**Prerequisite:** S1′ — [`PHASE-S1-REPORT.md`](PHASE-S1-REPORT.md), reverified green before this run (see Preflight).

## State

S2′ shipped: live `ttod.yml` backfilled with `lang: en` on every record, `meta.languages`
computed, `meta.version` bumped `3.0.0` → `3.1.0`, every quote's own `schema_version` bumped to
match, every record's `content_digest` recomputed, and every hardcoded `"3.0.0"` version constant
in `ttod_core/` bumped to `"3.1.0"` except two in `ttod_core/canonical.py` deliberately left
unchanged (judgment call, explained below). `cli.py validate --strict` now exits `0` against the
live file; the S1′ report's skipped guard test now runs and passes instead of being skipped.

## Preflight

- `git status`: working tree was **not clean** at the start — it carried the uncommitted S1′
  deliverable (schema/validator/read-path changes, `tests/fixtures/s1_*`, `PHASE-S1-REPORT.md`,
  etc.), exactly matching `PHASE-S1-REPORT.md`'s own artifact list. This is this studio's normal
  practice (no auto-commit; the user reviews and commits). Verified by reading `PHASE-S1-REPORT.md`
  and cross-checking the diff before proceeding — did not stop, since the dirty state is the
  declared closed S1′ prerequisite, not unrelated stray work.
- Full test suite before touching anything:
  `cd ~/src/ttod && PYTHONPATH=. .venv/bin/python -m unittest discover -s tests -p 'test_*.py'`
  → **Ran 176 tests in 2.106s — OK (skipped=1)**, matching the S1′ report's claim exactly.
- Pre-migration byte digest of live `ttod.yml`:
  `b757fe5ae11066dc315dab39a66930859a65d7dd6420be04cfc8c7e9be22c50c` (6726 lines, 229 quotes).
  Backup copied outside the repo to
  `/private/tmp/claude-501/-Users-ruvebal-src-ttod/fe5c8acc-4ff6-42b7-a702-81ce0a282130/scratchpad/ttod.yml.pre-s2-backup`
  (verified byte-identical by digest before proceeding).

  **Judgment call:** Phase Q6's own backup (`private/ttod.yml.pre-q6-backup`) is tracked *inside*
  the repo (confirmed with `git ls-files` — not gitignored; `.gitignore` only excludes `_private/`,
  not `private/`). This task's own instructions explicitly said to keep the S2′ backup **outside**
  the tracked repo instead, "never inside the repo where it could get committed by accident." I
  followed the explicit task instruction over the older Q6 precedent; flagging the inconsistency
  here rather than silently picking one.

## Version constants bumped (full inventory)

| File | Constant | Old → New |
| --- | --- | --- |
| `ttod_core/repository.py` | `TTODRepository.SCHEMA_VERSION` | `"3.0.0"` → `"3.1.0"` |
| `ttod_core/__init__.py` | `__version__` | `"3.0.0"` → `"3.1.0"` |
| `ttod_core/migration.py` | `SCHEMA_VERSION` (drives `meta.version` and every quote's `schema_version` via `migrate_root`) | `"3.0.0"` → `"3.1.0"` |
| `ttod_core/migration.py` | `update_header_comment_block()`'s `# Schema Version:` line | was hardcoded literal `"3.0.0"`; now emits `f"# Schema Version: {SCHEMA_VERSION}"` (dynamic, `3.1.0`) — closes a drift risk the plan didn't name explicitly but is the same class of bug it warns about |
| `ttod_core/bridge.py` | `QuoteOutAdapter.to_transport()`'s `transfer_metadata.exporter_version` | `"3.0.0"` → `"3.1.0"` |
| `ttod_core/exporter.py` | `Exporter._build_json_export()`, fallback passed to `compute_snapshot_digest()` | `"3.0.0"` → `"3.1.0"` |
| `ttod_core/exporter.py` | `Exporter._build_json_export()`, fallback passed to `create_manifest(schema_version=...)` | `"3.0.0"` → `"3.1.0"` |

**Left unchanged (judgment call — flagged per the plan's own instruction to report rather than
guess):**

| File | Constant | Reasoning |
| --- | --- | --- |
| `ttod_core/canonical.py:64` | `SnapshotManifest.projection_version` default | Interpreted as the **TTOD-C14N-v1 canonicalization/projection-scheme version** — a distinct axis from the data schema version. The projection logic itself (which fields are excluded from a digest, key sorting, NFC normalization, compact-JSON serialization) is byte-for-byte unchanged by S2′. Confirmed empirically after the real migration: `cli.py graph`'s `_manifest.projection_version` still correctly reads `"3.0.0"` while the same file's `meta.version` reads `"3.1.0"` — the two numbers now visibly diverge in every export, which is the intended signal that they track different things. |
| `ttod_core/canonical.py:233` | `Canonicalizer.create_manifest()`'s `schema_version` default parameter | Discovered this parameter is **dead code**: it is accepted but never assigned to `SnapshotManifest` (that dataclass has no `schema_version` field, only `projection_version`, which `create_manifest()` never sets from this parameter either — it just uses the dataclass default). Every real call site (`exporter.py`) already passes an explicit value, so the default is never observed in any current test or output. Changing it has zero behavioral effect; leaving it as `"3.0.0"` avoids implying a fix to the apparent dead-parameter wiring, which would be a code-correctness change beyond this migration's scope. Flagging as a pre-existing anomaly worth a separate, later ticket — not fixed here. |

Also checked per the plan's instruction: no fixture or test asserts `exporter_version` or
`projection_version` literally as `"3.0.0"` (`grep` across `tests/test_bridge.py` and
`tests/test_canonical.py` confirmed). `tests/fixtures/q4_roundtrip.json` contains
`"schema_version": "3.0.0"` but only as arbitrary sample input data fed into
`export_quote_out()` — no test asserts it as an *output* version, so it was left as-is (it is
testing field-preservation, not version equality). Same reasoning applied to the many `"3.0.0"`
literals in `tests/test_validation.py`, `tests/test_canonical.py`, `tests/test_exporter.py`,
`tests/test_schema_contract.py`, `tests/test_cli_integration.py` — all are synthetic input fixtures
for schema-pattern tests (`^[0-9]+\.[0-9]+\.[0-9]+$` / `^3\.`), not live-version assertions; the
full suite stayed green through every step below, confirming none of them broke.

## Migration run

```bash
cd ~/src/ttod

# 1. Candidate (never touches live file)
PYTHONPATH=. .venv/bin/python cli.py migrate prepare \
  --output <scratchpad>/ttod-s2-candidate.yml --json
# exit 0 — quotes_total: 229, schema_version_added: 229, content_digests_computed: 229,
# meta_version: "3.1.0", decision_count: 229 (all lang_default_en), strict_valid: true, error_count: 0

# confirmed live ttod.yml untouched: sha256 unchanged, still b757fe5a...22c50c

# 2. Apply atomically
PYTHONPATH=. .venv/bin/python cli.py migrate apply --approve
# exit 0 — same summary as above; "OK — live ttod.yml migrated to v3"
```

`migrate apply` reuses the existing Q3/Q6 atomic-write transaction
(`TTODRepository.apply_v3_migration()`): validate the migrated candidate strict pre-lock → acquire
exclusive `fcntl` lock → write to a sibling `.tmp` file → fsync → `os.replace()` rename → re-read
disk bytes and re-validate strict → release lock; any exception at any step restores the original
bytes byte-for-byte. This is the same mechanism already exercised by
`tests/test_q6_migration.py::TestMigrationRollback` and is what the rollback proof below re-ran.

## Record count and digest verification (before → after, live file)

| Check | Result |
| --- | --- |
| Record count before | 229 |
| Record count after | 229 |
| `count_in == count_out` | confirmed equal |
| Records whose `content_digest` changed | **229 / 229** (every record) |
| Records whose `content_digest` did not change | 0 |
| `meta.version` | `"3.0.0"` → `"3.1.0"` |
| `meta.languages` | absent → `["en"]` |
| `meta.language` (deprecated mirror) | `"en"` → `"en"` (unchanged; still first entry of `meta.languages`) |
| Quotes missing `lang` after migration | 0 |
| Post-migration live file byte digest | `b663860b0b6ab4ca7e88c90661848993ae12401be69c74b801c46aa7cf957e97` |

Verified independently with a Python script comparing `{id: content_digest}` maps between the
scratchpad pre-migration backup and the post-migration live file: `count_in: 229 count_out: 229`,
`digests changed: 229 of 229`.

## Post-migration verification

```bash
PYTHONPATH=. .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
# Ran 176 tests in 2.153s — OK (skipped=1)   [before un-skipping the guard test, see below]

PYTHONPATH=. .venv/bin/python cli.py validate --strict
# OK — 0 errors, 0 warnings   (exit 0 — this is the signal S2′ succeeded)

PYTHONPATH=. .venv/bin/python cli.py stats
# ...
# By language (derived from quote lang; never hardcoded):
#   en: 229

PYTHONPATH=. .venv/bin/python cli.py stats --check
# Recomputed total_quotes: 229
# Recomputed last_id_by_section: {...}
# OK — stored meta matches recomputed snapshot.   (exit 0, no drift)
```

`en: 229` is the live count as read from the migrated file at report time, not a hardcoded value —
it happens to equal S0's dated 2026-09-06 snapshot figure because, per S0 decision 8, there was no
partial-Spanish subset to reconcile; every record was uniformly backfilled.

### Guard-test un-skip

`tests/test_q6_migration.py::TestLiveMigrated::test_live_file_is_strict_valid` carried a skip
decorator added during S1′ ("live ttod.yml is intentionally red until S2′ backfills lang: en and
bumps meta.version"). That condition is now false, so the skip was removed. Re-running the full
suite:

```bash
PYTHONPATH=. .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
# Ran 176 tests in 2.311s — OK   (0 skipped)
```

Sanity note: after removing the skip decorator, `git diff -- tests/test_q6_migration.py` shows
**zero diff against `HEAD`** — the last real commit's version of this file already lacked the skip
(it predates S1′, when the live file needed no `lang` backfill to validate strict). Un-skipping
after S2′ exactly restores that committed baseline; this is a consistency confirmation, not a
coincidence to worry about.

## Two-clean-export determinism check

```bash
PYTHONPATH=. .venv/bin/python cli.py export --output <scratch>/export1.json
PYTHONPATH=. .venv/bin/python cli.py export --output <scratch>/export2.json
shasum -a 256 <scratch>/export1.json <scratch>/export2.json
# 65b69fa304d627298924c9432f935bda24f7cb27bbf44048748c37db2922e105  export1.json
# 65b69fa304d627298924c9432f935bda24f7cb27bbf44048748c37db2922e105  export2.json
```

Byte-identical (`diff` confirmed empty). As a bonus check, `cli.py graph` was also run twice
(not required by the plan but cheap and directly exercises the newly-projected `lang` field on
graph nodes):

```bash
PYTHONPATH=. .venv/bin/python cli.py graph --output <scratch>/graph1.json
PYTHONPATH=. .venv/bin/python cli.py graph --output <scratch>/graph2.json
shasum -a 256 <scratch>/graph1.json <scratch>/graph2.json
# bdd0193cd0552829360b7357f4ebe99edba920299e5c6385ba6b6befb42574b3  graph1.json
# bdd0193cd0552829360b7357f4ebe99edba920299e5c6385ba6b6befb42574b3  graph2.json
```

Byte-identical. Sample node: `{"id": "a11y-001", "lang": "en", "origin": "legacy-unknown",
"section": "accessibility", "status": "active", "text": "..."}` — confirms `_graph_nodes()`
projects `lang` end-to-end on the real migrated file, and `_manifest.projection_version` in that
same output correctly still reads `"3.0.0"` per the canonical.py judgment call above.

## Rollback proof (disposable copy, never the live file)

Per `AGENTS.md`'s "use disposable copies (`--file`) for bridge self-tests and experiments" and the
task's explicit instruction not to induce failure against the real live file: three fresh
byte-for-byte copies of **today's actual live `ttod.yml`** (pre-migration, 229 quotes) were made in
the scratchpad directory, then `TTODRepository.apply_v3_migration()` was invoked against each with
an injected `TransactionHooks` failure — the same mechanism `tests/test_q6_migration.py` already
exercises, re-run here explicitly against current content and current (post-version-bump) code:

| Injected failure | `RepositoryError` raised | Disposable copy byte-identical to its own pre-write state |
| --- | --- | --- |
| `fail_after_lock=True` | yes ("injected failure after lock (migrate-v3)") | **yes** |
| `fail_after_temp_write=True` | yes ("injected failure after temp write") | **yes** |
| `fail_before_rename=True` | yes ("injected failure before rename") | **yes** |

A fourth, separate disposable copy was then migrated cleanly (no injected failure) to confirm the
mechanism actually completes successfully end-to-end before trusting it against the live file:
`quotes_total=229`, bytes changed, `meta.version: 3.1.0`, `meta.languages: ['en']`,
`meta.language: en`, sample quote `lang: en` / `schema_version: 3.1.0`, `validate --strict` on the
migrated candidate → `strict valid: True, errors: 0`. Only after this did the real migration run
against the actual live file (see "Migration run" above).

`tests/test_q6_migration.py::TestMigrationRollback` (pre-existing, part of the 176-test suite,
green throughout) exercises the identical `apply_v3_migration()` + `TransactionHooks` mechanism on
its own disposable copy (`private/ttod.yml.pre-q6-backup` if present, else live), so this manual
rollback run is corroborating evidence on today's actual content, not the only proof.

## Files touched

| Path | Change |
| --- | --- |
| `ttod.yml` | live migration: `lang: en` on all 229 records, `meta.languages: [en]`, `meta.version: 3.1.0`, every `content_digest` recomputed, header comment `# Schema Version: 3.1.0` |
| `ttod_core/repository.py` | `SCHEMA_VERSION` bump |
| `ttod_core/__init__.py` | `__version__` bump |
| `ttod_core/migration.py` | `SCHEMA_VERSION` bump; header-comment line now derived from the constant instead of a second hardcoded literal |
| `ttod_core/bridge.py` | `exporter_version` bump |
| `ttod_core/exporter.py` | two fallback-default bumps |
| `tests/test_q6_migration.py` | removed the S1′-introduced skip on `test_live_file_is_strict_valid` (now passes; content is identical to the last committed version of this file) |

`ttod_core/canonical.py` deliberately **not** touched — see judgment-call table above.

Not touched (out of scope, confirmed): `schema/*.json` (no `"3.0.0"` literal exists in any schema
file — `meta.version`'s pattern is `^3\.`, not a pinned literal), S3′ documentation propagation,
S4′ translation drafting, `sources/tao-of-ai-development/` and
`sources/tao-of-human-centered-design/` (untouched, not distilled).

## Ambiguities / judgment calls (explicit, per task instruction)

1. **Backup location** — kept outside the repo per this task's explicit instruction, diverging from
   Q6's own precedent of a tracked `private/` backup. Noted above; not resolved either way beyond
   following the instruction given.
2. **`canonical.py`'s two `"3.0.0"` literals** — left unchanged; reasoned as a distinct
   canonicalization-scheme version, not the data schema version, with the dead-parameter finding
   flagged for a future, separate cleanup. Not resolved by product-owner input in this session —
   flagged rather than guessed, per the task's own instruction.
3. **Un-skipping `test_live_file_is_strict_valid`** — not explicitly requested by the task's step
   list, but its skip reason named S2′ landing as the exact condition to remove it; leaving a
   stale, permanently-skipped guard test that exists specifically to catch this class of regression
   seemed like the wrong default, so it was un-skipped and reconfirmed green. Flagging this as a
   judgment call in case the product owner wanted the skip removal handled separately.
4. **`ttod_core/migration.py`'s header-comment literal (line ~310)** — the plan's named list did not
   explicitly call out this second hardcoded `"3.0.0"` (distinct from the `SCHEMA_VERSION`
   constant a few lines away), but it writes directly into the live file's header banner and would
   have left `ttod.yml`'s own comment header claiming `Schema Version: 3.0.0` while `meta.version`
   said `3.1.0` — an internal inconsistency of exactly the kind this phase exists to close. Bumped
   it (now derived from the `SCHEMA_VERSION` constant instead of a second separate literal) rather
   than leaving it stale.

## Resume point

S2′ is DONE. Live `ttod.yml` is `lang`-complete, strict-valid, and every named version constant is
internally consistent at `3.1.0` (with the two `canonical.py` exceptions reasoned above). **Next:**
S3′ (documentation propagation — `.cursor/rules/ttod-editing.mdc` walkthrough, source-chapter
README addenda, `docs/DEV_PLAN/INDEX.md` refresh) and S4′ (`cli.py translate-draft`) are both
explicitly out of scope for this report and were not started.
