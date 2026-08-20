# Phase Q3 Report — Atomic Repository and CLI Integration

**State:** DONE (2026-08-18)  
**Repository:** `/Users/ruvebal/src/ttod`  
**Entry:** Q2V, Q2E, Q2P reports DONE  
**Exit:** atomic write transaction, rollback, concurrency, and CLI wiring proven on disposable copies only

---

## 1. Write-transaction sequence (as implemented)

Matches runbook §2 step-for-step:

| Step | Implementation |
| ---- | -------------- |
| parse input | `yaml.safe_load` / proposal `candidate_content` |
| construct in-memory candidate | `_build_quote_from_candidate` (ID allocated only under lock) |
| validate strict (pre-write) | `TTODValidator(strict=True).validate_root(root)` after mutate |
| acquire exclusive lock | `fcntl.flock` on `{path}.lock` via `FileLock` |
| re-read under lock | `current_bytes = self.read_bytes()` **after** lock (not stale pre-lock bytes) |
| allocate canonical ID | `_allocate_canonical_id` inside `mutate()`, only on accept/deprecate/erase paths |
| temp write + fsync | `_write_yaml_atomic` → `{path}.tmp` |
| atomic rename | `os.replace(tmp, path)` |
| validate persisted bytes | re-read disk + `validate_root(strict=True)`; restore on failure |
| release lock | `FileLock.release()` in `finally` |

On failure: `_ensure_bytes_unchanged(original_bytes)` restores pre-transaction bytes if the file was touched.

**Dependency note:** no new packages — locking uses stdlib `fcntl` only.

---

## 2. Gate proofs

### Transaction

`tests/test_repository.py::TestRepositoryAccept::test_accept_updates_quote_and_meta`

- Disposable copy of `tests/fixtures/q3_minimal_ttod.yml`
- Accept adds `arch-002`, sets `meta.total_quotes=2`, `meta.last_id_by_section.arch=2`

### Rollback (byte-identical after induced failure)

| Test | Hook | Result |
| ---- | ---- | ------ |
| `test_rollback_after_lock_injection` | `fail_after_lock` | bytes unchanged |
| `test_rollback_after_temp_write_injection` | `fail_after_temp_write` | bytes unchanged |
| `test_rollback_before_rename_injection` | `fail_before_rename` | bytes unchanged |
| `test_no_orphan_id_on_rollback` | `fail_before_rename` | still 1 quote, total_quotes=1 |

Pre-Q3 these tests would fail — no repository module, no hooks, legacy `add` appended raw YAML.

### Concurrency

`tests/test_repository.py::TestRepositoryConcurrency::test_two_acceptors_distinct_ids`

- Two threads, `threading.Barrier(2)`, same disposable file
- Results: `arch-002` and `arch-003` (distinct); `meta.total_quotes=3`
- Pre-Q3: would duplicate IDs (no lock/re-read)

### CLI wiring

`tests/test_cli_integration.py` — 8 tests covering:

- `validate --json`, `validate --strict --json`
- `stats --check` (clean fixture)
- `add` requires `--reviewer-id`; successful add via transaction
- `snapshot` determinism (`cmp` byte-identical)
- `erase` requires authority
- `stats` reports `<missing>` origin (no default-to-human)

### Snapshot determinism (runbook command)

```bash
cp tests/fixtures/q3_minimal_ttod.yml /tmp/ttod-q3-test.yml
python cli.py snapshot --output /tmp/ttod-snapshot-a.json --file /tmp/ttod-q3-test.yml
python cli.py snapshot --output /tmp/ttod-snapshot-b.json --file /tmp/ttod-q3-test.yml
cmp /tmp/ttod-snapshot-a.json /tmp/ttod-snapshot-b.json  # identical
```

---

## 3. CLI commands (legacy paths replaced)

| Command | Module | Notes |
| ------- | ------ | ----- |
| `validate [--strict] [--json] [--file]` | Q2V | replaces hand-rolled validator |
| `stats [--check] [--file]` | repository | `--check` read-only drift; never hand-patches |
| `snapshot`, `export` | Q2E | C14N JSON / graph-v1 |
| `proposal create/import/review/accept` | Q2P + repository | only `accept` writes YAML |
| `deprecate`, `erase` | repository | erase requires `--authority` + `--decision-ref` |
| `add` | proposal+accept wrapper | requires `--reviewer-id`; same transaction as accept |

Unknown tags rejected by default (`--allow-unknown-tags` to override on accept/add).

Legacy unsafe `add` (append-after-root, no validation) **removed**.

---

## 4. Meta prefix alignment

`meta.last_id_by_section` uses **prefix keys** (`arch`, `wis`) matching live `ttod.yml`.

- `ttod_core/repository.py`: `compute_last_id_by_prefix`, stats `--check`, ID allocation
- `ttod_core/validation.py`: `_validate_meta_counts` updated to compare prefix keys (accepts section-id keys via `section_to_prefix` map)

Live `stats --check` on repository-root `ttod.yml`: **OK** — stored meta matches recomputed snapshot.

---

## 5. Verification commands

```bash
cd /Users/ruvebal/src/ttod
. .venv/bin/activate
python -m unittest discover -s tests -p 'test_*.py'
# Ran 125 tests — OK

python cli.py validate --strict --json
# exit 1 — expected until Q6 (live v2 quotes lack schema_version, origins, etc.)

python cli.py stats --check
# OK — stored meta matches recomputed snapshot (229 quotes)
```

**Not claimed:** live `ttod.yml` passes strict validate — that is Q6 scope.

---

## 6. Files touched

| File | Change |
| ---- | ------ |
| `ttod_core/repository.py` | **new** — lock, transaction, stats check, accept/deprecate/erase |
| `ttod_core/validation.py` | prefix-aware `_validate_meta_counts` |
| `ttod_core/__init__.py` | export `TTODRepository` |
| `cli.py` | full rewrite — Q2V/Q2E/Q2P/repository wiring |
| `tests/fixtures/q3_minimal_ttod.yml` | **new** — v3 disposable fixture |
| `tests/test_repository.py` | **new** — rollback, concurrency, accept |
| `tests/test_cli_integration.py` | **new** — CLI integration |

No changes to live `ttod.yml`, `schema/`, or `sources/`.

---

## 7. Safe resume point

| Phase | State | Entry |
| ----- | ----- | ----- |
| **Q4** | READY | Athanor transport + proposal-in bridge; verify S0-WPL freeze |
| **Q5** | DONE (2026-08-18) | [`PHASE-Q5-REPORT.md`](PHASE-Q5-REPORT.md) |
| **Q6** | DONE (2026-08-18) | live migration — see [`PHASE-Q6-REPORT.md`](PHASE-Q6-REPORT.md) |

> **Post-Q6:** Live strict validate passes; `python cli.py validate --strict --json` → 0 errors.

**ttod-bridge:** nine pending proposals in `~/src/.cursor/skills/ttod-bridge/pending/` — use `proposal import` → human review → `proposal accept` after Q3 (never hand-merge `ttod.yml`).

---

## 8. Tests that would fail pre-Q3

- All `TestRepositoryRollback`, `TestRepositoryConcurrency`, `TestRepositoryAccept`
- `test_cli_integration` add/snapshot/stats paths
- Prefix-aware meta count validation on fixtures using `arch:` keys
