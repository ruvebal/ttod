# TTOD development plan index

**Repository:** `/Users/ruvebal/src/ttod`

**Programme status:** READY at Q0 contract freeze · rights/split-license decision frozen ·
recoverable git baseline established · per-phase agent runbooks published under `PHASES/` ·
implementation has not started

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

| Phase | Purpose | Mode | State | Runbook |
| --- | --- | --- | --- | --- |
| Q0 | Freeze the measured baseline and v3 contract decisions | sequential blocker | READY (rights/NC frozen 2026-08-18; split-license + git baseline added 2026-08-18) | [`PHASES/Q0-schema-authority-freeze.md`](PHASES/Q0-schema-authority-freeze.md) |
| Q1 | Schema, compatibility model, and golden fixtures | sequential | BLOCKED by Q0 | [`PHASES/Q1-schemas-contract-fixtures.md`](PHASES/Q1-schemas-contract-fixtures.md) |
| Q2V | Strict validation and invariant engine | parallel lane | BLOCKED by Q1 | [`PHASES/Q2V-validation-core.md`](PHASES/Q2V-validation-core.md) |
| Q2E | Canonical serialization, exports, and digests | parallel lane | BLOCKED by Q1 | [`PHASES/Q2E-canonical-export-digests.md`](PHASES/Q2E-canonical-export-digests.md) |
| Q2P | Proposal and human-review workflow | parallel lane | BLOCKED by Q1 | [`PHASES/Q2P-proposals-review.md`](PHASES/Q2P-proposals-review.md) |
| Q3 | Atomic repository and CLI integration | sequential integration | BLOCKED by Q2V/Q2E/Q2P | [`PHASES/Q3-atomic-repository-cli.md`](PHASES/Q3-atomic-repository-cli.md) |
| Q4 | Athanor-mediated quote-out / proposal-in bridge | cross-repo integration | BLOCKED by Q3 and Athanor S0-WPL freeze | [`PHASES/Q4-athanor-bridge.md`](PHASES/Q4-athanor-bridge.md) |
| Q5 | Independence, provenance, rights, and erasure sensors | parallel by sensor | BLOCKED by Q3/Q4 contract | [`PHASES/Q5-policy-provenance-sensors.md`](PHASES/Q5-policy-provenance-sensors.md) |
| Q6 | Migration, end-to-end verification, documentation, and release | sequential closeout | BLOCKED by Q4/Q5 | [`PHASES/Q6-migration-e2e-docs.md`](PHASES/Q6-migration-e2e-docs.md) |

## Evidence and status

- [`PHASE-Q0-READINESS-REPORT.md`](PHASE-Q0-READINESS-REPORT.md) records the read-only
  2026-08-14 audit, exact input hashes, observed failures, and the safe resume point.
- [`DECISIONS/Q0-2026-08-18-RIGHTS-LICENSE-NC.md`](DECISIONS/Q0-2026-08-18-RIGHTS-LICENSE-NC.md)
  freezes the repository split license (code MIT, content CC BY-NC-SA 4.0) and the default
  `rights.license` for new/unresolved TTOD quotes as **CC BY-NC-SA 4.0**. `ttod.yml` and
  `AGENTS.md` (and legacy `CLAUDE.md` redirect) are not rewritten until Q6; `../LICENSE-CODE` and
  `../LICENSE-CONTENT` are the
  authoritative repository-level statement until then.
- A phase is not `DONE` because this plan exists. Each phase must file a verified report at
  `docs/DEV_PLAN/PHASE-Qx-REPORT.md` with commands, exits, artifacts, negative tests, and a
  provenance transfer matrix, per its runbook's "Report requirements" section.
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
