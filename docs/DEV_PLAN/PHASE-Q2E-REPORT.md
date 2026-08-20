# Phase Q2E Report — canonical serialization, exports, and digests

**Execution date:** 2026-08-18
**Completion pass:** 2026-08-18 (audit close)
**State:** DONE
**Mode:** parallel lane
**Entry:** Q1 DONE (PHASE-Q1-REPORT.md)

## 1. Exact commands and exit codes

```bash
$ . .venv/bin/activate && python -m unittest discover -s tests -p 'test_canonical.py' -v
Ran 27 tests in 0.003s
OK

$ . .venv/bin/activate && python -m unittest discover -s tests -p 'test_exporter.py' -v
Ran 11 tests in 0.006s
OK
```
Exit codes: 0

Full suite: 107 tests, OK.

## 2. TTOD-C14N-v1

Implemented per contract §2.3:

1. Recursive Unicode NFC.
2. Reject non-string identifiers/tags and non-finite numbers (integer `404` is **rejected**, not coerced).
3. UTF-8 JSON, lexicographically sorted keys, preserved array order, compact separators, one terminal newline.
4. SHA-256 `content_digest` over the canonical quote projection (digest fields excluded).
5. Snapshot digest over ID-sorted quotes + schema/taxonomy/collection policy digests.
6. Manifest: algorithm, projection version, source-file digest, record count, export options, included/excluded lifecycle states.

`Canonicalizer.verify_content_digest()` recomputes and raises `CanonicalizationError` on mismatch. Tests: `test_verify_content_digest_detects_tampering`, `test_q1_negative_digest_mismatch_fixture`. Those tests would have been absent (and the integrity gate unproven) before this pass.

## 3. Determinism proof

- `test_determinism_two_exports_byte_identical` / `test_determinism_byte_diff_test` — canonicalizer raw bytes.
- `test_export_two_runs_byte_identical` — **file bytes** of two `export_json` runs are identical (`assertEqual(path1.read_bytes(), path2.read_bytes())`).
- `test_export_graph_two_runs_byte_identical` — same for graph projection.

`generated_at` is omitted from the **written** `_manifest` so the file is byte-stable. The Python `SnapshotManifest` may still carry a timestamp if a caller passes `generated_at`.

Written exports use `to_canonical_json()`, not `json.dumps(..., indent=2)`.

## 4. Atomic export mechanics

`Exporter._write_atomically()`:

1. Sibling temp file in the **same directory** as the target.
2. `flush()` + `os.fsync()`.
3. Re-read bytes and compare to the intended C14N payload.
4. `Path.replace()` atomic rename.
5. On failure, temp is unlinked; the target file is not left half-written.

Parent directories are created so the sibling temp can live on the same filesystem. The target **file** is created only at rename. Crash-between-write-and-rename injection remains a Q6 proof.

## 5. Export policy

`ExportPolicy.should_include()`:

- erased excluded unless `include_erased`
- deprecated excluded when `include_deprecated=False`
- `public_export=True` excludes `rights.access=restricted`

## 6. Graph export

`Exporter.export_graph()` writes a deterministic read-only projection:

- `projection: graph-v1`
- `nodes` sorted by id (id, section, origin, status, text)
- `edges` from `related`, `relation_edges`, ancestry, deprecation/supersession, sorted by (source, rel, target)

This is the Q2E graph binding (contract §2.3 / §4A). A writable graph backend remains a later RFC.

## 7. Files touched

**Created/updated:** `ttod_core/canonical.py`, `ttod_core/exporter.py`, `tests/test_canonical.py`, `tests/test_exporter.py`

**Forbidden (not touched):** `cli.py`, `ttod.yml`, `schema/*.json`, committed `exports/` (none)

## 8. Safe resume point for Q3

Wire `export` / `snapshot` CLI to `Exporter.export_json` and `export_graph`. Pass export-policy flags. Use `verify_content_digest` on accept/write.

## 9. Gate status

| Gate | Required proof | Status |
| --- | --- | --- |
| Determinism | Two clean JSON exports and two graph exports are byte-identical | **GREEN** |
| Integrity | Tampered `content_digest` raises; Q1 digest-mismatch fixture rejected | **GREEN** |

## 10. Completion-pass delta (audit close)

Audit: no graph export; written JSON was indented (not C14N); two-run “determinism” stripped timestamps after parse; no tamper test. This pass writes C14N, omits `generated_at` from the file, adds `export_graph`, and asserts raw byte identity plus digest tampering.
