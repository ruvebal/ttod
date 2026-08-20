# TTOD development plan index

**Repository:** `/Users/ruvebal/src/ttod`

**Programme status:** Q0–Q6 DONE (Phase Q complete — 2026-08-18)

**Canonical entry point:**
[`PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md`](PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md)

**Shared studio protocol:**
[`deviac/docs/DEV_PLAN/TTOD-BRIDGE-INTEROPERABILITY-CONTRACT.md`](../../../deviac/docs/DEV_PLAN/TTOD-BRIDGE-INTEROPERABILITY-CONTRACT.md)

TTOD owns canonical quote identity; the studio protocol supplies reusable REST, offline-bundle,
and graph/RDF bindings. Counts, coverage, and collection totals are generated dynamically from a
snapshot rather than hardcoded in instructions.

TTOD is the studio-owned pedagogical quotation system. `ttod.yml` remains its canonical
human-governed database. Athanor may serve a versioned TTOD snapshot and may return proposed
quotes to a review inbox, but no model, Athanor adapter, WPL process, or sibling repository may
write canonical quote records directly.

## Active programme

Each row's runbook is a self-contained agent prompt — see
[`PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md`](PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md) §5 for how
they relate to the master contract. Hand one runbook to one agent session; do not hand the whole
cascade document and ask it to "do Q3."

| Phase | Purpose                                                        | Mode                   | State                                                  | Runbook                                                                            |
| ----- | -------------------------------------------------------------- | ---------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| Q0    | Freeze the measured baseline and v3 contract decisions         | sequential blocker     | DONE (2026-08-18; report filed at PHASE-Q0-REPORT.md)  | [`PHASES/Q0-schema-authority-freeze.md`](PHASES/Q0-schema-authority-freeze.md)     |
| Q1    | Schema, compatibility model, and golden fixtures               | sequential             | DONE (2026-08-18; completion pass closed exact-code + origin if/then; PHASE-Q1-REPORT.md) | [`PHASES/Q1-schemas-contract-fixtures.md`](PHASES/Q1-schemas-contract-fixtures.md) |
| Q2V   | Strict validation and invariant engine                         | parallel lane          | DONE (2026-08-18; completion pass: origin+digest on validate_root; PHASE-Q2V-REPORT.md) | [`PHASES/Q2V-validation-core.md`](PHASES/Q2V-validation-core.md)                   |
| Q2E   | Canonical serialization, exports, and digests                  | parallel lane          | DONE (2026-08-18; completion pass: C14N writes, graph export, tamper tests; PHASE-Q2E-REPORT.md) | [`PHASES/Q2E-canonical-export-digests.md`](PHASES/Q2E-canonical-export-digests.md) |
| Q2P   | Proposal and human-review workflow                             | parallel lane          | DONE (2026-08-18; report filed at PHASE-Q2P-REPORT.md) | [`PHASES/Q2P-proposals-review.md`](PHASES/Q2P-proposals-review.md)                 |
| Q3    | Atomic repository and CLI integration                          | sequential integration | DONE (2026-08-18; PHASE-Q3-REPORT.md)               | [`PHASES/Q3-atomic-repository-cli.md`](PHASES/Q3-atomic-repository-cli.md)         |
| Q4    | Athanor-mediated quote-out / proposal-in bridge                | cross-repo integration | DONE (2026-08-18; PHASE-Q4-REPORT.md; TTOD + Athanor sub-lanes) | [`PHASES/Q4-athanor-bridge.md`](PHASES/Q4-athanor-bridge.md)                       |
| Q5    | Independence, provenance, rights, and erasure sensors          | parallel by sensor     | DONE (2026-08-18; PHASE-Q5-REPORT.md; 9 sensors, 21 tests) | [`PHASES/Q5-policy-provenance-sensors.md`](PHASES/Q5-policy-provenance-sensors.md) |
| Q6    | Migration, end-to-end verification, documentation, and release | sequential closeout    | DONE (2026-08-18; PHASE-Q6-REPORT.md; live ttod.yml v3) | [`PHASES/Q6-migration-e2e-docs.md`](PHASES/Q6-migration-e2e-docs.md)               |

## Evidence and status

- [`PHASE-Q0-READINESS-REPORT.md`](PHASE-Q0-READINESS-REPORT.md) records the read-only
  2026-08-14 audit, exact input hashes, observed failures, and the safe resume point.
- [`DECISIONS/Q0-2026-08-18-RIGHTS-LICENSE-NC.md`](DECISIONS/Q0-2026-08-18-RIGHTS-LICENSE-NC.md)
  freezes the repository split license (code MIT, content CC BY-NC-SA 4.0) and the default
  `rights.license` for new/unresolved TTOD quotes as **CC BY-NC-SA 4.0**. Q6 rewrote
  `ttod.yml` header and `AGENTS.md`; `../LICENSE-CODE` and `../LICENSE-CONTENT` remain
  authoritative.
- A phase is not `DONE` because this plan exists. Each phase must file a verified report at
  `docs/DEV_PLAN/PHASE-Qx-REPORT.md` with commands, exits, artifacts, negative tests, and a
  provenance transfer matrix, per its runbook's "Report requirements" section.
- **2026-08-18 Q1/Q2 completion pass:** independent audit found Q1/Q2V/Q2E overstated as DONE
  (exact error codes not asserted, missing `origin` matched the blackbox `if/then`,
  `validate_root()` skipped origin/digest, exports were not C14N, no graph export, no digest
  tamper test). Those gaps are closed in the amended Q1/Q2V/Q2E reports. Full suite: 107 tests
  OK. Live `ttod.yml` was strictly invalid until Q6 migration (215 `ORIGIN_UNRESOLVED`) —
  detecting that drift was success; Q6 closed it.
- **2026-08-18 Q6:** migration closeout DONE — live `ttod.yml` v3.0.0, strict validate 0
  errors, **161 tests** OK, bridge round-trip + rollback injection on pre-migration backup,
  arch-052 live adversary confirmed. Report: [`PHASE-Q6-REPORT.md`](PHASE-Q6-REPORT.md).

## Verification (current)

```bash
cd ~/src/ttod && . .venv/bin/activate
python cli.py validate --strict --json   # exit 0
python cli.py stats --check              # exit 0
python -m unittest discover -s tests -p 'test_*.py'   # 161 tests, exit 0
```
- **2026-08-18 Q3:** atomic repository + CLI integration DONE — `ttod_core/repository.py`,
  full CLI rewrite, rollback/concurrency tests on disposable copies; 125 tests OK at Q3 close.
  Report: [`PHASE-Q3-REPORT.md`](PHASE-Q3-REPORT.md).
- **2026-08-18 Q4:** Athanor bridge DONE — transport schemas, `ttod_core/bridge.py`, Athanor
  read-only adapter, round-trip fixture + 133 TTOD / 6 Athanor tests. Report:
  [`PHASE-Q4-REPORT.md`](PHASE-Q4-REPORT.md).
- **2026-08-18 Q5:** policy sensors DONE — nine deterministic sensors in `ttod_core/sensors/`,
  17 fixtures under `tests/fixtures/q5_*`, 21 sensor tests + 154 total suite OK. arch-052
  adversary confirmed (`SELF_DERIVED_NOT_EVIDENCE`). Report: [`PHASE-Q5-REPORT.md`](PHASE-Q5-REPORT.md).
- **2026-08-18 planning-repair session:** this plan-document tree was restructured (not the
  canonical data) — the redundant root-level copy of the cascade document was removed (the
  `docs/DEV_PLAN/` copy is canonical), the root `INDEX.md` was rewritten to stop duplicating this
  file's status table, and this file's phase table gained the `PHASES/` runbook links. No
  `ttod.yml`, `cli.py`, `schema/`, or `sources/` content was touched. `git init` was completed
  separately, closing the "no recoverable baseline" gap the 2026-08-14 readiness report flagged.

## Constitutional boundary

The Athanor and WPL development processes may reference the same immutable Athanor evidence
snapshot, including ingested research and governed field-research records. They must not quote,
cite, or summarize each other's draft output as evidence. TTOD quotes are pedagogical material,
not independent corroboration. A quote derived from an Athanor plan, including `arch-052`, must
never be fed back to Athanor or WPL as support for that plan.
