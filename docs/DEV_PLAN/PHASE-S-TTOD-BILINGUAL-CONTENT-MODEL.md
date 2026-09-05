<!--
TTOD Phase S — bilingual content model (lang field + translation_of relation).
Planning baseline: 2026-09-04. Revised 2026-09-06 after a cold review verified against live code
closed eight real gaps (not cosmetic ones) — see DECISIONS/S0-...md's 2026-09-06 amendment for the
decisions this revision implements. No live implementation performed by this document.
Prerequisite gate for Phase R's R1 domain-contract freeze — see
PHASE-R-TTOD-ORACLE-PLATFORM-CASCADE-PROMPT.md §0.1.
-->

# Phase S — TTOD bilingual content model

**Status:** S0 decision FROZEN (2026-09-04), amended 2026-09-05 (S4) and 2026-09-06 (invariants,
ID policy, `meta.language` redefinition, a corrected count claim — see
[`DECISIONS/S0-2026-09-04-BILINGUAL-CONTENT-MODEL.md`](DECISIONS/S0-2026-09-04-BILINGUAL-CONTENT-MODEL.md)).
S1′ DONE 2026-09-04 (see PHASE-S1-REPORT.md); S2′ DONE 2026-09-04 (see PHASE-S2-REPORT.md) — live
ttod.yml migrated (`lang: en` on all 229 records, `meta.languages`, `meta.version: 3.1.0`, every
version constant bumped, `validate --strict` exits 0). S3′ DONE (see PHASE-S3-REPORT.md) —
documentation propagation (editing walkthrough, source-README addenda, INDEX.md refresh,
migration-backup convention). S4′ DONE 2026-09-04 (see PHASE-S4-REPORT.md) — `cli.py translate-draft`
ships, writes proposals only (never a canonical quote); pilot rubric run on 10 live quotes against
the primary model (9/10 clean, 1/10 — `img-071` — flagged FAIL on semantic fidelity, human
revision required before that one proposal is accepted) plus a full 10-quote comparison run against
the pilot alternate, which fared worse on the same set.

**Owner:** TTOD product owner (Rubén Vega Balbás)

**Why this exists:** the v3 schema has no per-quote locale field — only a single collection-wide
`meta.language: en` flag — while two parked source chapters are bilingual or Spanish-only
(`sources/tao-of-ai-development/` has `en.md` + `es.md`; `sources/tao-of-human-centered-design/`
has only `es.md`), and Phase R's Astro frontend is being required (FE II Deliverable 1) to route
`en`/`es`. Without this phase, Phase R's i18n routing dresses the shell in Spanish while the
underlying quote *content* stays whatever language each record happens to be in. This phase makes
the data model actually bilingual-capable before Phase R's `R1` freezes a contract on top of it.
It does **not** distill the two parked chapters into quotes — that stays human-curated, later,
per their own READMEs.

**Blocks:** Phase R's R1 (backend `domain.ts`/`WisdomEntry` contract freeze) must not be treated
as final until S1′ (schema) is at least decided; R0 should read this document before generating
R1's runbook.

---

## Why this document was revised 2026-09-06

A cold review of the original S1–S4 plan — checked against live code, not taken on faith — found
the design decision sound but the implementation plan under-specified in ways that would have
caused real bugs, not just documentation gaps:

- `translation_of` had a reference-existence check but no semantic invariants — same-language
  "translations," duplicate active translations, self-edges, and chains would all have validated
  as clean.
- The proposed 3.0/3.1 dual-compat window was a footgun: `SCHEMA_VERSION = "3.0.0"` is hardcoded
  in `ttod_core/repository.py`, and five more files carry the same literal — a dual-compat rule
  would have let new quotes silently ship without `lang` indefinitely.
- `lang` propagation stopped at the quote schema and Phase R's `domain.ts` — it never reached
  `schema/proposal.schema.json`'s `candidate_content`, `ttod_core/bridge.py`'s
  `field_mapping_coverage()` (a tested, exhaustive allow-list — an unlisted field is silently
  dropped on export, confirmed by reading the code, not inferred), or `Exporter._graph_nodes()`.
- `meta.language`'s meaning after Spanish quotes exist was left undefined.
- ID/naming policy (locale-suffixed IDs vs. a fresh section-number ID) was never stated, inviting
  an implementing agent to invent one.
- **A factual error in this plan's own earlier draft:** `img-055` and `cc-025` were cited as "2
  quotes already carrying undeclared Spanish diacritics." Verified by reading (2026-09-06): both
  are English aphorisms that merely *mention* a diacritic character or a loanword — `cc-025` is
  *about* someone putting an `ñ` in a URL; `img-055` uses the English word "cliché." Neither is
  Spanish-language content. This revision removes that claim everywhere it appeared.

Every fix below traces to one of these findings. Nothing here is invented caution — each item was
verified against the live repository before being written down.

---

## Programme

| Step | Deliverable | Depends on | Gate |
| --- | --- | --- | --- |
| **S0** | Content-model decision frozen (incl. 2026-09-06 invariants) | — | [`DECISIONS/S0-...md`](DECISIONS/S0-2026-09-04-BILINGUAL-CONTENT-MODEL.md) exists |
| **S1′** | Schema + validator (with `translation_of` semantic invariants) + full read-path propagation (proposal, transport, bridge, exporter graph nodes) + fixtures | S0 | DONE — [`PHASE-S1-REPORT.md`](PHASE-S1-REPORT.md) |
| **S2′** | Atomic migration: `lang: en` + `meta.languages` on all live records, every version constant bumped together, no dual-compat window | S1′ | DONE — [`PHASE-S2-REPORT.md`](PHASE-S2-REPORT.md) |
| **S3′** | Documentation propagation — remaining scope only (the R1-blocking half already shipped with S1′) | S1′, S2′ | DONE — [`PHASE-S3-REPORT.md`](PHASE-S3-REPORT.md) |
| **S4′** | Assisted translation drafting: explicit `cli.py translate-draft` only, writes a `proposal`, never a canonical quote | S1′ | DONE — [`PHASE-S4-REPORT.md`](PHASE-S4-REPORT.md) |

No parallel lanes — this is small enough to run sequentially in one sitting per step, unlike
Phase Q's multi-lane programme. Per the studio's `cascade-forge` skill's own threshold ("two or
more" of: sequential dependency, long-running job, human gate, delegable operator work) — this
phase has a sequential dependency and a human decision gate (S0, closed), but no long-running job
and no repeatable operator loop, so it stays a single orchestrator document rather than spawning a
`PHASES/` folder of per-step runbooks the way Phase Q or Phase R did.

---

## S1′ — Schema, validator, and full read-path propagation

### Schema

1. **`lang`, required, no dual-compat.** `schema/quote.schema.json` gains
   `{"type": "string", "pattern": "^[a-z]{2}$"}` (ISO 639-1; a bare pattern, not a closed enum —
   `en`/`es` today, extensible later with no schema-version bump for a third language), added to
   `required`. Per S0's 2026-09-06 revision, there is **no** `schema_version >= 3.1.0`-only branch
   — S2′ migrates every live record to `3.1.0` in the same atomic step that adds `lang`, so by the
   time this validator rule matters, nothing in the live file predates it.
2. **No new schema for the relation itself, but new validator invariants.**
   `relation_type` stays an unconstrained string (verified against the live schema) — no schema
   change for `translation_of` as a value. But `ttod_core/validation.py` gains real checks, because
   "target resolves to a live quote" is necessary and **not sufficient**:

   | Invariant | Diagnostic code | Frozen fixture filename |
   | --- | --- | --- |
   | target exists | `TRANSLATION_TARGET_UNRESOLVED` | `tests/fixtures/s1_negative_translation_target_unresolved.json` |
   | target is `status: active` | `TRANSLATION_TARGET_INACTIVE` | `tests/fixtures/s1_negative_translation_target_inactive.json` |
   | `lang(source) ≠ lang(target)` | `TRANSLATION_SAME_LANGUAGE` | `tests/fixtures/s1_negative_translation_same_language.json` |
   | no self-target | `TRANSLATION_SELF_TARGET` | `tests/fixtures/s1_negative_translation_self_target.json` |
   | star, not chain — target carries no outgoing `translation_of` | `TRANSLATION_CHAIN` | `tests/fixtures/s1_negative_translation_chain.json` |
   | at most one `active` translation per `(target_id, lang)` | `TRANSLATION_DUPLICATE_ACTIVE` | `tests/fixtures/s1_negative_translation_duplicate_active.json` |
   | `section` matches target's `section` | `TRANSLATION_SECTION_MISMATCH` *(warning; hard error only under `--strict`, same as existing meta-drift warnings)* | `tests/fixtures/s1_warning_translation_section_mismatch.json` |

   Confirm today's reference-integrity pass (`related`, `deprecated_by`, `superseded_by`,
   `immediate_parent_refs`, `root_source_refs`) does **not** already walk `relation_edges[].target`
   — verified absent 2026-09-06 — and add it as part of this same set of checks, not a separate
   pass. Do **not** invent alternate filenames or codes; the inventory in §S1′ fixtures below is
   authoritative.
3. **ID/naming policy — no locale suffixes** (S0 decision 6). A Spanish twin of `arch-001` is the
   next free `arch-NNN`, allocated via `meta.last_id_by_section` at `proposal accept` time exactly
   as today — never `arch-001-es`. Covered by
   `tests/fixtures/s1_negative_locale_suffix_id.json` (must fail the existing ID pattern —
   assert the **exact** live schema/validator code, do not invent a new `LOCALE_SUFFIX` code) and
   stated in S3′'s doc updates so an implementing agent does not invent a suffix scheme.

### Full read-path propagation (confirmed gaps, not "verify later")

`lang` reaching `quote.schema.json` and Phase R's `domain.ts` is necessary but does **not** by
itself solve Phase R's i18n content problem. Every one of these was checked against the live file,
not assumed:

| Surface | Confirmed state (2026-09-06) | Required change |
| --- | --- | --- |
| `schema/proposal.schema.json` `candidate_content` | curated property list; no `lang`, no `relation_edges` (schema-permissive by unset `additionalProperties`, not by design) | add both explicitly |
| `schema/transport_quote_out_v1.json` | curated property list; has `relation_edges`, **no `lang`** | add `lang` |
| `ttod_core/bridge.py::field_mapping_coverage()` | explicit, tested (docstring: "prove no silent drops") `schema_field → transport_field` map; **no `lang` entry** — confirmed this means `to_transport()` silently omits `lang` today, by reading the loop, not inferring it | add `"lang": "lang"` entry |
| `ttod_core/exporter.py::Exporter._graph_nodes()` | returns `{id, section, origin, status, text}` — **no `lang`** | add `lang` to the projection; Phase R `domain.ts` `GraphNode` gains `lang` (patch that document in the same S3′ patch) |
| `GET /api/v1/wisdom/sample`, `GET /api/v1/graph`, §3.1's retrieval-confidence search (Phase R) | not yet built | accept a `lang` filter param once S1′ ships the field — otherwise Phase R's `/es/` routes render an all-English corpus regardless of shell language |

### `meta.language` → `meta.languages`

Per S0 decision 7: `meta.language: en` (a single flag) becomes false the moment any Spanish quote
exists. S1′ specifies (S2′ writes) `meta.languages: [en, es, ...]` as a **derived** field — computed
from the actual `lang` values present, the same non-hand-edited discipline `meta.total_quotes`
already has, drift-checked by `stats --check`. `meta.language` may be kept one cycle as a
read-compatible mirror (first entry of `meta.languages`) for unmigrated tooling, never authoritative
after S2′.

### `stats` gains a language breakdown

One line, `cli.py stats`: `languages: {en: N, es: M}` (values derived from the live file, never
hardcoded in code or docs — see the AGENTS.md rule this project already holds itself to). Without
this, Phase R could ship `/es/` locale routes over an effectively all-English corpus and nobody
would notice until a user did.

### S1′ fixtures — frozen inventory (do not invent names)

Follow Q1's golden-fixture convention (`PHASES/Q1-schemas-contract-fixtures.md`): files under
`tests/fixtures/s1_*`, tests assert **exact** `DiagnosticCode` values (never a prose substring).
Multi-quote cases use a root-shaped `{ "quotes": [ ... ] }` object (same pattern as
`q5_lifecycle_negative_duplicate_id.json`); single-quote schema cases may be a bare quote object
(same pattern as `q1_negative_dangling_related.json`). IDs inside fixtures are disposable
(`arch-9xx` range) — never collide with live `ttod.yml` IDs, and never use a locale-suffixed ID
except in the one negative that proves the pattern rejects it.

| File | Expect | Exact code / assertion |
| --- | --- | --- |
| `tests/fixtures/s1_positive_translation_pair.json` | clean (0 errors, 0 warnings) | `en` original `arch-901` + `es` twin `arch-902` with `translation_of` → `arch-901`; both `section: architecture`; proves separate IDs, not `arch-901-es` |
| `tests/fixtures/s1_negative_missing_lang.json` | error | `TYPE_ERROR` (confirmed 2026-09-04: jsonschema `required` → `_map_schema_error_to_code` → `TYPE_ERROR`; do not invent `MISSING_LANG`) |
| `tests/fixtures/s1_negative_translation_target_unresolved.json` | error | `TRANSLATION_TARGET_UNRESOLVED` |
| `tests/fixtures/s1_negative_translation_target_inactive.json` | error | `TRANSLATION_TARGET_INACTIVE` |
| `tests/fixtures/s1_negative_translation_same_language.json` | error | `TRANSLATION_SAME_LANGUAGE` |
| `tests/fixtures/s1_negative_translation_self_target.json` | error | `TRANSLATION_SELF_TARGET` |
| `tests/fixtures/s1_negative_translation_chain.json` | error | `TRANSLATION_CHAIN` — three records where an intermediate itself has `translation_of` |
| `tests/fixtures/s1_negative_translation_duplicate_active.json` | error | `TRANSLATION_DUPLICATE_ACTIVE` |
| `tests/fixtures/s1_warning_translation_section_mismatch.json` | warning (non-strict); error under `--strict` | `TRANSLATION_SECTION_MISMATCH` |
| `tests/fixtures/s1_negative_locale_suffix_id.json` | error | `TYPE_ERROR` (confirmed: `arch-901-es` fails quote `id` pattern → same mapper; do not invent `LOCALE_SUFFIX`) |

**Out of fixture files (unit assertions in `tests/`, still S1′):**

| Assertion | Where |
| --- | --- |
| `field_mapping_coverage()` includes `"lang": "lang"` and `to_transport()` emits `lang` | extend `tests/test_bridge.py` |
| `Exporter._graph_nodes()` projects `lang` | add/extend exporter test |
| `cli.py stats` language-breakdown shape | extend stats test; do not hardcode corpus counts |

**S1′ gate:** every file in the inventory above passes/fails with the exact code listed; bridge and
exporter unit assertions green; `stats` reports a language-breakdown shape; no alternate fixture
names or diagnostic codes introduced by the implementer. Fixture filenames in this section are
authoritative — do not invent `s1_*` aliases.

---

## S2′ — Migration (single bump, full version-constant surface)

1. `cli.py migrate prepare` (extended, or a new `migrate-s2` command mirroring its shape) reads
   live `ttod.yml`, adds `lang: en` to **every** current record, computes and writes
   `meta.languages`, bumps `meta.version: 3.1.0`, and writes a **candidate** file — never in place.
2. Because `ttod_core/canonical.py:compute_content_digest()` hashes every field except the digest
   fields themselves (verified, not a curated subset), adding `lang` to every record **changes
   every `content_digest`**. Expected, not a bug — the report states it plainly. Gate on
   **`count_in == count_out`** and **every migrated record's digest changed** — derived from the
   file under migration at the time the report is written, never a hardcoded number in this
   document or the report template (a live count belongs in the report, not in a plan that outlives
   any particular corpus size).
3. **Bump every hardcoded `"3.0.0"` in the same migration, not just `ttod.yml`.** Confirmed live
   2026-09-06 in: `ttod_core/repository.py::SCHEMA_VERSION`, `ttod_core/__init__.py::__version__`,
   `ttod_core/canonical.py` (`projection_version` default and a `schema_version` default param),
   `ttod_core/bridge.py` (`exporter_version` in transfer metadata), `ttod_core/migration.py::
   SCHEMA_VERSION`, `ttod_core/exporter.py` (two `"3.0.0"` fallback defaults). Also update any
   bridge round-trip fixture that asserts `3.0.0` literally. Missing any of these leaves the
   codebase internally inconsistent about its own version even after `ttod.yml` itself is correct.
4. `cli.py migrate apply --approve` takes the repository lock, re-validates the candidate
   `--strict`, and atomically replaces `ttod.yml` — exact rollback law as Phase Q §7: record the
   original byte digest first, keep a recoverable backup outside the target filename, never write
   a partially validated result.
5. **Report requirement** (`PHASE-S2-REPORT.md`, same fields as any Phase Q report): record count
   before/after (must match — no quote gained or lost), digest-count-changed (must equal the
   record count), the six-plus version-constant touch points from step 3 confirmed bumped,
   `validate --strict` exit code, full test-suite result, two clean re-exports compared
   byte-for-byte, and an induced-failure rollback proof (kill the process mid-write, confirm
   `ttod.yml` is byte-identical to the pre-migration backup).

**Do not** run S2′ against the live `ttod.yml` without a recoverable backup and a green S1′ first —
same discipline as every prior TTOD migration.

---

## S3′ — Documentation propagation (revised 2026-09-06 post-S2′: scope narrowed to what's actually left)

**The "blocks R1" half of the original S3′ split is already shipped — do not redo it.** Verified
against `PHASE-S1-REPORT.md`'s own artifact list: `schema/*.json`, `ttod_core/{bridge,validation,
exporter}.py`, `PHASE-R-TTOD-ORACLE-PLATFORM-CASCADE-PROMPT.md` §4 (`WisdomEntry.lang`,
`GraphNode.lang`, `GraphLink['rel']`'s `'translation_of'`), and `AGENTS.md`'s quote-record-shape
table were all delivered as part of S1′ itself, not deferred. S3′'s real remaining scope is only
the informational half below — the original two-table split correctly anticipated a boundary that
S1′'s own implementer then folded into one delivery, which is fine and is not a deviation to
correct.

**Remaining scope:**

| Surface | Change |
| --- | --- |
| `.cursor/rules/ttod-editing.mdc` | full editing-checklist walkthrough for choosing `lang` and adding a `translation_of` edge. **Write it against the current live shape (post-S2′: `lang` present, `schema_version: "3.1.0"`), not a pre-migration hypothetical** — the corpus this doc describes now actually looks like this. |
| `sources/tao-of-ai-development/README.md`, `sources/tao-of-human-centered-design/README.md` | addendum on pairing distillations via `lang` + `translation_of` — **does not authorize the merge itself** |
| `docs/DEV_PLAN/INDEX.md` | Phase S row refreshed: S1′ DONE, S2′ DONE, S3′/S4′ status as of this run |
| `AGENTS.md` or `.cursor/rules/ttod-editing.mdc` | **new, resolves S2′'s flagged ambiguity #1:** state the migration-backup convention explicitly — future live-database migrations follow Q6's own precedent, a byte-identical pre-migration backup tracked under `private/` (not gitignored, not outside the repo), so the backup is part of the same auditable git history as everything else this project reports. S2′'s scratchpad-outside-repo backup was a reasonable one-off given that session's explicit instruction; this closes the inconsistency for the next migration rather than leaving it to be re-flagged each time. |

**Known follow-up, not blocking, not forgotten:** S2′'s report flagged `ttod_core/canonical.py::
Canonicalizer.create_manifest()`'s `schema_version` parameter as dead code (accepted, never
assigned to `SnapshotManifest`, no call site relies on it). Not fixed by S2′ (out of scope for a
migration), not fixed here (out of scope for a documentation phase) — noted so it doesn't quietly
disappear. Worth a small, separate, later cleanup: either wire it to a real field or remove the
parameter.

---

## S4′ — Assisted translation drafting (local model, human-gated, forward-only)

**Origin of this step:** requested 2026-09-05 — when a quote is promoted, auto-draft its
sister-language version instead of requiring the reviewer to write the translation from scratch.
Revised 2026-09-06 to resolve two internal contradictions the cold review caught.

**Contradiction 1, resolved: trigger is an explicit command only, never a side effect.** The
original text said promotion "may trigger" a draft (S0 decision 4) while also specifying a
separate `translate-draft` CLI command "not a side effect of `add`/`proposal accept`" (S4's
mechanism). **Resolved: explicit CLI only.** `cli.py translate-draft <source-id> --to <lang>` is
the one entry point. A hook that auto-invokes it from `proposal accept` is a legitimate later
idea, but it is out of scope for S4′ and must not be implied as already decided.

**Contradiction 2, resolved: model name is not hardcoded in the spec.** The original text named
`thessia-scholar-v3` as *the* model while a later conversation (this session) settled on
`qwen3.8:27b` as primary. **Resolved:** this document does not hardcode a model name. Whichever
model tag actually runs the call is recorded in the drafted proposal's own `authorship_assertion`/
`generation_method` field — the spec names candidates to pilot, not a fixed dependency.

**The one rule this must never break.** `AGENTS.md` and Phase Q are unambiguous: *"No model tool
has an `accept`, `deprecate`, or `erase` capability"* and *"Every `origin: blackbox` entry needs
`validated_by: human` before it counts as accepted."* **S4′ auto-drafts; it never auto-accepts.**

**Mechanism:**

1. `cli.py translate-draft <source-id> --to <lang>` — reads the source quote's `text`/`teaches`,
   calls local Ollama (offline/batch, dev-tier bare-metal host per Phase R §0.1.2, not the
   containerized app-tier model). **Candidates, checked against the actually-pulled local
   inventory (`ollama list`, 2026-09-06) rather than a hypothetical pull:** primary `qwen3.8:27b`
   (already Phase R's dev-tier tag — zero new model dependency); pilot comparison
   `qwen2.5:32b-instruct`; `thessia-scholar-v3` as an optional register-polish second pass, not the
   default translator (its documented uses are voice-rewriting and citation-checked essay
   generation, always within one language — no evidence it was fine-tuned for translation).
   `thessia-sentinel-v3` is off-limits — its name is already load-bearing for a reserved role per
   DevIAC's own `PHASE-T-CASCADE-PROMPT.md` constraint.
2. **Full drafted-proposal payload**, not just `lang` and the translated text:
   - `lang`: target language;
   - `section`, `level`, `tags`: copied from the source as a starting default — human-editable at
     review, never assumed final (a translator's judgment about fit belongs to the human accepting
     it, not to the draft);
   - `teaches`: translated alongside `text`, not left in the source language;
   - `rights`: copied from the source's `rights` block as a default, explicitly **not** assumed
     automatically correct — the reviewer confirms or corrects it at accept time, same as `section`;
   - `relation_edges: [{"target": "<source-id>", "relation_type": "translation_of"}]`;
   - `origin: blackbox`; `authorship_assertion` and `generation_method` record the actual model
     tag that ran, dynamically, never hardcoded in this document.
3. Writes the result as a **`proposal`** (`ttod_core/proposals.py`/`ProposalStore`, the same path
   every other blackbox candidate uses). A human runs `proposal review` then
   `proposal accept --reviewer-id …` as a **separate, deliberate action** — judging translation
   *accuracy* against the source, not only voice/tone. Nothing in S4′ shortens or bypasses this.

**Fail fast against S1′'s own invariants, revised 2026-09-06 — these are real code now, not just
spec.** Before calling the model at all, `translate-draft` should check locally and refuse with a
clear message rather than waste a generation call on a proposal that could never validate:
- `--to <lang>` equal to the source quote's own `lang` → refuse immediately (`TRANSLATION_SAME_LANGUAGE`
  would reject it at accept time regardless);
- an `active` translation already exists for `(source_id, --to)` → warn (not necessarily hard-refuse
  — a human may deliberately want a second candidate to compare before accepting either) that
  accepting a second one would trip `TRANSLATION_DUPLICATE_ACTIVE`.
`proposal.schema.json`'s `candidate_content` already accepts `lang`/`relation_edges` (shipped in
S1′) — S4′ does not need to touch schema files again.

**Pilot acceptance rubric — replaces "owner judges accuracy" as a DONE gate.** Run 5–10 quotes
through each candidate model with the same prompt (draft below) and score each output against.
**Pilot-quote selection, resolved 2026-09-06:** the live corpus is confirmed 100% English
(`meta.languages: ["en"]`, verified post-S2′) — any of the 229 live quotes is a valid pilot
candidate; there is no special-cased subset to avoid (the earlier "2 undeclared Spanish quotes"
concern was corrected in S0 decision 8 — `img-055`/`cc-025` are ordinary English quotes).

- **semantic fidelity** — no meaning drift from the source, checked line by line;
- **register preserved** — reads as a pedagogical aphorism, not technical prose, and not expanded
  or explained beyond what the source states;
- **form preserved** — line breaks and syllabic economy intact where the source is haiku-shaped;
- **no invented content** — nothing added that is not present in (or a direct implication of) the
  source text.

A model that fails any of these on manual review is not "usable at scale" regardless of how fluent
it reads — try the other candidate, or fall back to a human-drafted translation. S4′ is not DONE
until this rubric has been run and recorded, not merely until the CLI command executes without
error.

**Draft system-prompt** (needs the product owner's voice/judgment before use, not final):
*"Translate the following [haiku/koan/máxima] from [en/es] to [es/en]. Preserve ambiguity,
silence, and rhetorical structure — do not resolve or explain what the original leaves open.
Match the register of a pedagogical aphorism, not technical prose. Preserve line breaks and
syllabic economy where the form is haiku."*

**Scope: forward-only by default.** Backfilling the existing English corpus into Spanish is a
separate, explicitly authorized bulk operation — S4′ applies to quotes promoted **after** it ships;
retroactive backfill gets its own decision record if and when authorized, mirroring how Q6's
migration was itself a separately-scoped, reported event. There is no partial-Spanish subset in
the existing corpus to reconcile (S0 decision 8) — the backfill, if authorized, is every live
record at authorization time (derive the count then; do not hardcode it here).

**Future languages beyond en/es:** no schema change needed — `lang`'s ISO 639-1 pattern is already
open, not a closed enum. The constraint is per-language model/translation-quality availability,
decided per language when it comes up.

---

## Master paste (start/resume)

```text
Implement or resume TTOD Phase S per docs/DEV_PLAN/PHASE-S-TTOD-BILINGUAL-CONTENT-MODEL.md
(revised 2026-09-06 after a cold review, revised again same-day post-S2′ — read the "Why this
document was revised" section first; it is not optional context).

Current state as of this revision: S0 CLOSED (incl. 2026-09-06 amendment). S1′ DONE — see
PHASE-S1-REPORT.md; do not redo it, do not re-litigate its design. S2′ DONE — see
PHASE-S2-REPORT.md; live ttod.yml is lang-complete, validate --strict exits 0, meta.version is
3.1.0. Do not run S2′ again. S3′ and S4′ remain, and are independent of each other — both depend
only on S1′ (already green), not on each other. Read the S0 decision file
(docs/DEV_PLAN/DECISIONS/S0-2026-09-04-BILINGUAL-CONTENT-MODEL.md) in full before touching
anything, and AGENTS.md and .cursor/rules/ttod-editing.mdc before touching docs or schema/.

If you were asked to work on S1′ or S2′ specifically: stop, both are done — read
PHASE-S1-REPORT.md and PHASE-S2-REPORT.md instead of implementing either.

**S3′ (documentation only, no code, no live-data touch).** Its blocking half already shipped as
part of S1′ (verify against PHASE-S1-REPORT.md's own artifact list before assuming otherwise) —
S3′'s real scope is: (1) .cursor/rules/ttod-editing.mdc's full editing walkthrough, written against
the CURRENT live shape (lang present, schema_version 3.1.0), not a pre-migration hypothetical;
(2) short addenda to both parked source-chapter READMEs on pairing distillations via lang +
translation_of, without authorizing the merge itself; (3) docs/DEV_PLAN/INDEX.md's Phase S row
refreshed to reflect S1′/S2′ DONE and this run's own status; (4) document the migration-backup
convention (Q6's precedent — a tracked backup under private/, resolving S2′'s flagged ambiguity)
in AGENTS.md or ttod-editing.mdc. Do not distill sources/tao-of-ai-development/ or
sources/tao-of-human-centered-design/ into quotes — stays a separate, human-curated, later
session. File PHASE-S3-REPORT.md.

**S4′ (translate-draft command — real code, real local-model calls, no live ttod.yml touch).**
Writes a proposal, never a canonical quote: no code path may allocate a canonical ID or set
status: active — verify with a negative test. Explicit CLI command only, never a side effect of
proposal accept. Fail fast against S1′'s real validator invariants before calling any model:
refuse immediately if --to equals the source quote's own lang (would trip
TRANSLATION_SAME_LANGUAGE at accept time); warn if an active translation for (source_id, --to)
already exists (would trip TRANSLATION_DUPLICATE_ACTIVE) but don't hard-block — a human may want
a second candidate to compare. Do not hardcode a model name beyond "primary candidate, subject to
the pilot rubric" — record whichever model tag actually ran in the proposal's own provenance
fields. Any of the 229 live quotes is a valid pilot candidate (corpus confirmed 100% English
post-S2′; no special-cased subset). Run the pilot rubric (semantic fidelity, register, form, no
invented content) on 5-10 quotes before treating S4′ as usable at scale; do not call it DONE on
"the command runs without error" alone. Do not backfill the existing corpus under S4′ without a
separate, explicit authorization and its own decision record. File PHASE-S4-REPORT.md.

S3′ and S4′ touch disjoint files and may run in either order or in parallel.
```
