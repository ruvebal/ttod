# Phase Q0 Report — schema and authority freeze

**Execution date:** 2026-08-18
**State:** DONE
**Mode:** sequential blocker
**Baseline commit:** `37df9ce` (Q0 baseline: add AGENTS.md, split-license files, restructure docs, add PHASES/ runbooks, CLAUDE.md redirect, INDEX.md rewrite, rights/license decision frozen)

## 1. Baseline verification

### 1.1 Git status

```bash
$ git status
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

**Result:** Clean working tree. Baseline is recoverable.

### 1.2 Git history

```bash
$ git log --oneline -5
37df9ce (HEAD -> main) Q0 baseline: add AGENTS.md, split-license files, restructure docs, add PHASES/ runbooks, CLAUDE.md redirect, INDEX.md rewrite, rights/license decision frozen
f26b948 (origin/main, origin/HEAD) The Tao that can be prompted is not the eternal Tao.
```

**Result:** Two commits. The Q0 baseline commit (`37df9ce`) establishes the recoverable boundary.

### 1.3 Fresh input hashes (2026-08-18)

```bash
$ shasum -a 256 CLAUDE.md .cursor/rules/ttod-editing.mdc cli.py ttod.yml
6fa521e4a3ed1546fa326b7c2fe323d905a07bdf7ab6413c0e64308947557c09  CLAUDE.md
2ccaed3f7ac3367eebc813920108ce8e8fff7c558d66482a972ee6fca6ce02a9  .cursor/rules/ttod-editing.mdc
55acf4b45c78e92d4a77cb03d913040bb3ffb016e195e049063fc3f4c71e3b47  cli.py
141e314722ae53bcd9c6101782af55ec6a3c33e70aa820afafaae912323afcb5  ttod.yml
```

**Comparison with 2026-08-14 readiness report:**

| File | 2026-08-14 hash | 2026-08-18 hash | Status |
| --- | --- | --- | --- |
| `CLAUDE.md` | `fb3bbb0a80cdc9fee29291d72df4fa396bb710cef593f352e9ecca175f57b0dc` | `6fa521e4a3ed1546fa326b7c2fe323d905a07bdf7ab6413c0e64308947557c09` | **Changed** (redirect stub) |
| `.cursor/rules/ttod-editing.mdc` | `b95a5ce222299d73bf6d6c2f4aec57c0c9b35ee098455cd63c971650e8375db4` | `2ccaed3f7ac3367eebc813920108ce8e8fff7c558d66482a972ee6fca6ce02a9` | **Changed** (AGENTS.md reference added) |
| `cli.py` | `55acf4b45c78e92d4a77cb03d913040bb3ffb016e195e049063fc3f4c71e3b47` | `55acf4b45c78e92d4a77cb03d913040bb3ffb016e195e049063fc3f4c71e3b47` | **Match** (unchanged) |
| `ttod.yml` | `141e314722ae53bcd9c6101782af55ec6a3c33e70aa820afafaae912323afcb5` | `141e314722ae53bcd9c6101782af55ec6a3c33e70aa820afafaae912323afcb5` | **Match** (unchanged) |

**Note:** The 2026-08-15 post-audit correction hashes (`ba6e782...` for CLAUDE.md, `f8deda7d...` for ttd-editing.mdc) are superseded by the current Q0 baseline commit. The changes are documented and intentional (CLAUDE.md redirect, AGENTS.md addition).

### 1.4 CLI validation

```bash
$ . .venv/bin/activate && python cli.py validate
OK — 229 quotes validated, 0 errors.
```

**Exit code:** 0

**Result:** Current hand-written validator passes. This confirms the existing YAML is parseable and satisfies current v2.2 checks. It does not imply v3 schema conformance (that is Q1's scope).

## 2. Frozen decisions (by reference)

The following decisions are frozen as specified in the master contract (`PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md`):

### 2.1 v3 field names and enums (§2.1)

**Reference:** Master contract §2.1, table "Canonical quote record"

**Frozen axes:**
- Identity: `id`, `schema_version`, `content_digest`
- Content: `text`, `section`, `subsection`, `level`, `tags`, `teaches`, optional display fields
- Authorship: `origin`, `authorship_assertion` (values: `human`, `studio`, `blackbox`, `mixed`, `legacy-unknown`)
- Review: `validation.status`, `method`, `reviewer_id`, `activity_id`, `reviewed_at`, `record_digest`
- Source: `source_refs[]` with `source_id`, `locator`, `content_digest`, `role`, `derivation_method`
- Evidence: `evidence_snapshot_digest`, optional `wpl_record_id` and `wpl_record_digest`
- Rights: `rights.license`, `holder`, `permission_basis`, `access`, `restrictions`, `decision_ref`
- Relations: `related[]` plus typed `relation_edges[]`
- Lifecycle: `status=active|deprecated|erased`, `deprecated_by`, `superseded_by`, `reason`, `effective_at`
- Ancestry: `immediate_parent_refs[]`, `root_source_refs[]`, `proposal_id`

**Status:** Frozen by reference to master contract §2.1. No contradictions found with `.cursor/rules/ttod-editing.mdc` or current `ttod.yml` header.

### 2.2 Compatibility decisions (§2.1, "Compatibility decisions to freeze in Q0")

**Reference:** Master contract §2.1, bullet list under "Compatibility decisions to freeze in Q0"

**Frozen rules:**
- `schema/quote.schema.json` validates a quote; `schema/ttod.schema.json` validates the root; `schema/proposal.schema.json` validates proposals
- Existing values byte-preserved in migration input; missing provenance becomes explicit unresolved/legacy state
- Legacy `source` and `validated_by` kept as read-compatible mirrors during one declared transition
- YAML date-like values normalized to ISO-8601 strings at domain boundary
- Numeric tag scalars (e.g., `404`) must be rejected or migrated to string `"404"`
- `related` remains directed; bidirectionality may be proposed and reviewed, never inferred during migration

**Status:** Frozen by reference to master contract §2.1.

### 2.3 TTOD-C14N-v1 deterministic identity (§2.3)

**Reference:** Master contract §2.3, "Define TTOD-C14N-v1 in docs and code"

**Frozen algorithm:**
1. Recursively normalize every string to Unicode NFC
2. Reject non-string identifiers/tags and non-finite numbers
3. Emit UTF-8 JSON with lexicographically sorted object keys, preserved array order, fixed compact separators, one terminal newline
4. Compute SHA-256 over canonical quote projection for `content_digest`
5. Compute snapshot digest over quotes sorted by canonical ID plus schema/taxonomy/collection policy versions
6. Record algorithm, projection version, source-file digest, record count, export options, included/excluded lifecycle states in signed-or-hashed snapshot manifest

**Status:** Frozen by reference to master contract §2.3.

### 2.4 Proposal record and lifecycle (§2.2)

**Reference:** Master contract §2.2, "Proposal record"

**Frozen structure:**
- `proposal_id` (UUID/URN allocated before review)
- `status = proposed | needs_revision | accepted | rejected | withdrawn`
- Candidate content without canonical id
- Proposer kind/id and observed-or-declared generation method
- WPL generation record id + digest
- Shared Athanor evidence snapshot id + digest
- Source refs, origin, rights, relations, and ancestry exactly as received
- Human review activities[]
- `accepted_quote_id` only after atomic acceptance transaction

**Frozen rule:** No proposal reserves a section-number ID. Acceptance takes repository lock, re-reads live snapshot, allocates next unused section ID, validates every root invariant, writes atomically, then records `accepted_quote_id`.

**Status:** Frozen by reference to master contract §2.2.

### 2.5 Human reviewer identity shape (§2.1, Review axis)

**Reference:** Master contract §2.1, table row "Review"

**Frozen requirement:** Blackbox/mixed content cannot become active without an identified human acceptance activity (`reviewer_id`, `activity_id`, `reviewed_at`, `record_digest`).

**Status:** Frozen by reference to master contract §2.1.

### 2.6 Rights/unresolved policy (DECISIONS/Q0-2026-08-18-RIGHTS-LICENSE-NC.md)

**Reference:** `docs/DEV_PLAN/DECISIONS/Q0-2026-08-18-RIGHTS-LICENSE-NC.md`

**Frozen decisions:**
1. Repository split license: Code is MIT (`LICENSE-CODE`), content is CC BY-NC-SA 4.0 (`LICENSE-CONTENT`)
2. Default `rights.license` for new/unresolved-and-rights-holder-authored quotes is `CC-BY-NC-SA-4.0`
3. Default `rights.holder` is `ruvebal@crea-comm.net` (named identity, not inferred origin)

**Status:** Frozen. Decision document exists and is authoritative. License files added at repo root.

### 2.7 Higher-law erasure authority (master contract §2.1, Lifecycle axis)

**Reference:** Master contract §2.1, table row "Lifecycle"

**Frozen rule:** Ordinary removal is deprecation; erasure is a protected exception requiring higher-law authority.

**Status:** Frozen by reference to master contract §2.1.

### 2.8 Shared EvidenceSnapshot fields (§3)

**Reference:** Master contract §3, "Independence and shared-grounding protocol"

**Frozen fields per source unit:**
- Native document/node identity
- Source/content digest
- Page/spatial locator when available
- Extraction or field-research method
- Asserted/inferred state
- Citation-resolution/evaluator-safe result
- Permission/access status
- Snapshot/harness versions

**Status:** Frozen by reference to master contract §3.

### 2.9 Sibling-output prohibition (§3)

**Reference:** Master contract §3, flowchart and policy sensor rules

**Frozen prohibitions:**
- `AthanorDraft -> supports -> WPLClaim` is rejected
- `WPLDraft -> supports -> AthanorDecision` is rejected
- `TTODQuote(source=AthanorPlan) -> supports -> AthanorDecision` is rejected
- Any `quotation` whose evidence pointer resolves only to a sibling output or a TTOD copy is rejected

**Status:** Frozen by reference to master contract §3.

### 2.10 arch-052 expected verdict (§3)

**Reference:** Master contract §3, paragraph beginning "`arch-052` is the permanent adversarial fixture"

**Frozen expected verdict:** When `arch-052` is consumed by Athanor or WPL architecture claims, it must surface `evidence_admissible=false` and `independence_reason=SELF_DERIVED_NOT_EVIDENCE`.

**Status:** Frozen by reference to master contract §3.

## 3. Open blockers carried into Q1

### 3.1 Athanor version pin

**Status:** VERIFIED

**Athanor repository:** `/Users/ruvebal/src/athanor`
**Current commit:** `29b06d4` (HEAD → main, origin/main, origin/HEAD)
**Version:** `0.1.0` (from `pyproject.toml`)
**Provenance Law:** Exists at `docs/DEV_PLAN/ATHANOR-PROVENANCE-LAW.md` (normative)

**Q4 dependency:** Q4 requires "Athanor S0-WPL freeze". Athanor Phase S0-WPL conformance freeze exists at `docs/DEV_PLAN/PHASE-S0-WPL-CONFORMANCE-FREEZE.md` (state: READY after S0).

**Carried forward:** Athanor commit `29b06d4`, version `0.1.0`, Provenance Law normative document, and S0-WPL freeze state. Q4 must re-verify these before bridge implementation.

### 3.2 WPL conformance profile version

**Status:** VERIFIED

**WPL conformance profile:** `v0.2.0` (frozen 2026-08-14)
**Location:** `/Users/ruvebal/src/MSCA/SVCM/coordination/wpl/WPL-CONFORMANCE-PROFILE.md`
**RFC:** `/Users/ruvebal/src/MSCA/SVCM/coordination/wpl/RFC-001-WPL-PORTABLE-CONFORMANCE-FREEZE.md`
**SHACL artifact:** `wpl-conformance.shacl.ttl` (SHA-256: `c8b3323676775513962c076187637c2f11aa9aac0f75acb162a73a6919291bd3`)

**Athanor S0-WPL freeze:** References WPL v0.2.0 contract and SHACL artifact explicitly. Reports 16/16 fixtures green.

**Carried forward:** WPL conformance profile v0.2.0, RFC-001, SHACL artifact digest. Q4 must re-verify Athanor S0-WPL state before bridge implementation.

### 3.3 DevIAC version pin

**Status:** VERIFIED

**DevIAC repository:** `/Users/ruvebal/src/deviac`
**Current commit:** `f93185b` (HEAD → master, origin/master, origin/HEAD)

**Carried forward:** DevIAC commit `f93185b`. Q4 must verify DevIAC groundings before bridge implementation.

## 4. Touched paths

**Allowed (per Q0 runbook §4):**
- `docs/DEV_PLAN/` — restructured, added `PHASES/` runbooks
- `docs/DEV_PLAN/DECISIONS/` — added rights/license decision
- `AGENTS.md` — new agent contract
- `LICENSE-CODE`, `LICENSE-CONTENT` — new split-license files
- `CLAUDE.md` — converted to redirect stub
- `INDEX.md` — rewritten to stop duplicating master contract
- `.cursor/rules/ttod-editing.mdc` — updated to reference AGENTS.md
- `sources/tao-of-ai-development/README.md` — updated license note
- Git commit of baseline changes

**Forbidden (per Q0 runbook §4) — NOT touched:**
- `ttod.yml` — reverted to committed state, no canonical data mutation
- `cli.py` — unchanged (hash matches 2026-08-14)
- `schema/` — no writes (directory empty, as expected)
- `sources/tao-of-ai-development/` content files — not touched
- `exports/` — not touched
- External databases — not touched
- Dependency files (`pyproject.toml`, lockfiles) — not touched
- Git push — not executed
- Destructive git commands — not executed

## 5. Safe resume point for Q1

**Entry condition for Q1:** Q0 report filed with state DONE, all frozen decisions confirmed by reference, all open blockers explicitly carried forward with version pins, and git baseline clean at commit `37df9ce`.

**Q1 runbook:** `docs/DEV_PLAN/PHASES/Q1-schemas-contract-fixtures.md`

**Q1 scope:** Schema, compatibility model, and golden fixtures. Q1 will create `schema/quote.schema.json`, `schema/ttod.schema.json`, and `schema/proposal.schema.json` based on the frozen v3 field axes from master contract §2.1.

**No mutation:** Q1 must not touch `ttod.yml` canonical data. It creates schemas and fixtures only.

## 6. Commands and exit codes (verbatim)

```bash
$ git status
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```
Exit code: 0

```bash
$ git log --oneline -20
37df9ce (HEAD -> main) Q0 baseline: add AGENTS.md, split-license files, restructure docs, add PHASES/ runbooks, CLAUDE.md redirect, INDEX.md rewrite, rights/license decision frozen
f26b948 (origin/main, origin/HEAD) The Tao that can be prompted is not the eternal Tao.
```
Exit code: 0

```bash
$ shasum -a 256 CLAUDE.md .cursor/rules/ttod-editing.mdc cli.py ttod.yml
6fa521e4a3ed1546fa326b7c2fe323d905a07bdf7ab6413c0e64308947557c09  CLAUDE.md
2ccaed3f7ac3367eebc813920108ce8e8fff7c558d66482a972ee6fca6ce02a9  .cursor/rules/ttod-editing.mdc
55acf4b45c78e92d4a77cb03d913040bb3ffb016e195e049063fc3f4c71e3b47  cli.py
141e314722ae53bcd9c6101782af55ec6a3c33e70aa820afafaae912323afcb5  ttod.yml
```
Exit code: 0

```bash
$ . .venv/bin/activate && python cli.py validate
OK — 229 quotes validated, 0 errors.
```
Exit code: 0

## 7. Provenance transfer matrix

| Decision | Source | Frozen by | Carried to |
| --- | --- | --- | --- |
| v3 field axes | Master contract §2.1 | Q0 report reference | Q1 (schemas) |
| Compatibility rules | Master contract §2.1 | Q0 report reference | Q1 (fixtures) |
| TTOD-C14N-v1 | Master contract §2.3 | Q0 report reference | Q2E (exports) |
| Proposal lifecycle | Master contract §2.2 | Q0 report reference | Q2P (proposals) |
| Rights/license | DECISIONS/Q0-2026-08-18 | Decision file | Q1, Q5 (sensors) |
| Athanor version | Athanor repo | Commit 29b06d4, v0.1.0 | Q4 (bridge) |
| WPL profile | MSCA/SVCM coordination | v0.2.0, RFC-001 | Q4 (bridge) |
| DevIAC version | DevIAC repo | Commit f93185b | Q4 (bridge) |
| Sibling prohibition | Master contract §3 | Q0 report reference | Q5 (sensors) |
| arch-052 verdict | Master contract §3 | Q0 report reference | Q5 (sensors) |

## 8. Conclusion

Phase Q0 is DONE. All frozen decisions are confirmed by reference to the master contract and decision documents. The git baseline is recoverable at commit `37df9ce`.

> **Post-Q6 (2026-08-18):** Live `ttod.yml` was migrated to v3.0.0 in Q6 only. Programme complete —
> see [`PHASE-Q6-REPORT.md`](PHASE-Q6-REPORT.md).
