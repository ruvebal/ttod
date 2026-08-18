# Phase Q0 readiness report — TTOD contract repair

**Audit date:** 2026-08-14

**State:** READINESS AUDIT COMPLETE · implementation NOT STARTED

**Mutation statement:** read-only inspection of live repositories; one `add` failure probe ran
against a disposable `/private/tmp` copy. No live TTOD file, corpus, database, export, dependency,
commit, or deployment was changed.

## 1. Inputs inspected

| Input | SHA-256 at audit |
| --- | --- |
| `/Users/ruvebal/src/ttod/CLAUDE.md` | `fb3bbb0a80cdc9fee29291d72df4fa396bb710cef593f352e9ecca175f57b0dc` |
| `/Users/ruvebal/src/ttod/.cursor/rules/ttod-editing.mdc` | `b95a5ce222299d73bf6d6c2f4aec57c0c9b35ee098455cd63c971650e8375db4` |
| `/Users/ruvebal/src/ttod/cli.py` | `55acf4b45c78e92d4a77cb03d913040bb3ffb016e195e049063fc3f4c71e3b47` |
| `/Users/ruvebal/src/ttod/ttod.yml` | `141e314722ae53bcd9c6101782af55ec6a3c33e70aa820afafaae912323afcb5` |
| `/Users/ruvebal/src/ttod/sources/tao-of-ai-development/README.md` | `24cbb08432c14b563c0ba5329f2807b6fd3827ae3d7725c361ca36355cbc3078` |
| DevIAC development-plan index | `b41a01d5180159c5e27eb16bfef9796be04b4398a3aaee9864fd90d09effea81` |
| Athanor Provenance Law | `43d56b16b9d9a6e79c6f832d5c11517e415622495fe33ec0a7094b5e89ceba59` |
| Athanor Phase S cascade | `567e442b0510adf710bee6258ba0fd3f95c065a25820b520deb7df31a185bb70` |
| WPL conformance profile | `1660303637225a4796442bb95de017dc3d3d3d71d7f1306dab9426d556108077` |

The TTOD directory has no `.git` directory and `git -C /Users/ruvebal/src/ttod status --short`
fails. Q0 must therefore establish a recoverable version-control or equivalent signed-snapshot
boundary before any canonical migration. This report does not infer whether TTOD is intentionally
unversioned or its repository metadata is elsewhere.

## 2. Measured baseline

The current `python cli.py validate` exits 0 and says `229 quotes validated, 0 errors`. That result
means only the current hand-written checks passed; it is not schema or contract conformance.

| Observation | Measured result | Consequence |
| --- | --- | --- |
| Documented count | `CLAUDE.md` says 221; YAML and CLI contain 229 | documentation drift is already user-visible |
| Claimed schema | `schema/quote.schema.json` is absent | “validate against schema” is not true |
| Add transaction | disposable-copy `cli.py add` reported `arch-060`, then `validate` raised a YAML `ParserError` at the appended item | canonical add path is unsafe and blocked |
| Derived statistics | YAML says architecture 43 and wisdom 14; actual values are 51 and 16 | materialized statistics are stale |
| Level statistics | YAML says 50/67/44/52; actual beginner/intermediate/advanced/master are 50/73/50/56 | dashboards cannot trust stored counters |
| Coverage | YAML says 12 of 16; there are 18 declared sections and 13 populated | denominator and numerator are stale |
| Collection counts | `daily_wisdom=12` vs 90 matching `featured`; `masters_path=12` vs 56 master quotes | collection metadata is not derived mechanically |
| Tag taxonomy | 236 used scalar values are absent from the declared taxonomy | current validator does not enforce the editing rule |
| YAML scalar typing | tag `404` loads as an integer in `img-009` and `img-024` | canonical exports do not have a stable string-only tag type |
| Human validation | no quote contains `validated_by`; no current quote has `origin=blackbox` | the conditional rule has never been mechanically exercised |
| Origin accounting | 215 records omit `origin`, but `stats` counts omissions as `human` | authorship is being inferred without evidence |
| Identity metadata | `meta.last_id_by_section` matches observed maxima | preserve this currently consistent invariant |
| Reference integrity | all current collection IDs and lesson quote IDs resolve; all `related` targets resolve | preserve these currently green invariants |
| Related graph | 435 directed edges, 229 without a reverse edge | acceptable under the current “preferred” rule; do not auto-rewrite semantics |
| Deprecation | no current record uses `deprecated` | retirement and erasure paths have no exercised fixture |
| License boundary | source chapter is CC BY-NC-SA 4.0 while the database says CC BY-SA 4.0 | source material cannot be merged under an inherited license |
| Editing instructions | the Cursor rule tells editors to read `meta.sections`; sections are at root `sections` | rule and schema disagree |

The `add` probe used only copies in a newly created temporary directory. It established a real
failure mode: `cli.py` appends a YAML list item after the root `templates` mapping rather than
inserting into `quotes`, and performs no post-write validation or rollback.

## 2A. Post-audit instruction correction (2026-08-15)

The stale hardcoded quote-count language was removed from the live `CLAUDE.md` and Cursor editing
rule. Their current hashes are `ba6e78265c4c6fd3396f40850714f1fc840c7e7933fd59cd8defaac83a299ac6`
and `f8deda7d4a0b1fc1ea47d34c9ed93cec969b8aaa53f27e0436636c1021cf325a`. The canonical data and
CLI remain byte-identical to the audit (`ttod.yml` `141e314...`, `cli.py` `55acf4...`).
Instructions now require dynamic metadata derivation and an explicit blocker when the acceptance
path cannot recompute projections atomically. The missing schema, unsafe add path, and stale stored
statistics remain Q0/Q3 implementation findings; no canonical data was repaired by this document
change.

## 3. Architecture finding

TTOD is canonical pedagogical content, not an evidence authority. Athanor is the single mediation
surface for retrieval and generation provenance, while Ahmes extraction pages and governed field
research remain the evidence boundary. This yields three distinct objects:

1. an immutable **evidence snapshot**, shared by Athanor and WPL without sharing their prose;
2. a TTOD **canonical quote snapshot**, served outward by Athanor for pedagogical use; and
3. a **quote proposal**, generated inward through Athanor but held outside `ttod.yml` until an
   identified human accepts it under TTOD rules.

These objects must not be collapsed. In particular, `arch-052` was distilled from an Athanor Phase
2 plan. It may be shown as a pedagogical quote with that ancestry, but it cannot corroborate
Athanor's architecture or a WPL claim. The applicable sensor must classify that use as
`SELF_DERIVED_NOT_EVIDENCE` and fail any attempted `supports_claim` edge.

## 4. Grounding boundary

This planning audit did not perform new vector discovery, inject a corpus, or treat a vector hit as
evidence. The target design reuses Athanor/Ahmes page-level, citation-resolution discipline. A
shared snapshot may include ingested sources and governed field-research units, but each unit must
carry its own identity, access/permission state, content digest, and validation status.

No claims from the Athanor plan or WPL draft are quoted here as scholarly evidence. They are
versioned contract inputs only. The two processes may independently derive conclusions from the
same snapshot digest; they may not use each other's generated text as a source.

## 5. Readiness decision

Phase Q is implementation-ready only at the Q0 blocker. Q0 must freeze the v3 compatibility and
authority decisions before code changes. The following are explicitly not complete:

- JSON Schemas and golden fixtures;
- strict validation and deterministic digests;
- an atomic add/accept path;
- a proposal-before-canonical-ID workflow;
- the Athanor quote-out / proposal-in adapter;
- sibling-independence, rights, deprecation, and erasure sensors;
- migration of `ttod.yml` and correction of instructions/statistics.

**Safe resume point:** execute Q0 from the cascade, prove a recoverable baseline, approve the
v2.2→v3 compatibility decisions, and only then open Q1.
