# S0 decision — bilingual content model: separate IDs, linked by a `translation_of` relation

**Status:** FROZEN (product-owner instruction, 2026-09-04)
**Decider:** Rubén Vega Balbás (TTOD product owner)
**Cascade:** Phase S0 — see [`../PHASE-S-TTOD-BILINGUAL-CONTENT-MODEL.md`](../PHASE-S-TTOD-BILINGUAL-CONTENT-MODEL.md)
**Does not mutate:** `ttod.yml`, `schema/*.json`, `cli.py`, `ttod_core/` — this record freezes the
decision only; S1–S4 in the cascade document implement it.
**Amended 2026-09-05:** added decision 4 below — assisted translation drafting at promotion time
(S4), corrected from the original request ("auto-promote both languages together") to
auto-*draft*-only, because auto-promoting a model-generated translation would let a model allocate
a canonical ID without human acceptance — the exact capability `AGENTS.md` denies every model tool.
**Amended 2026-09-06** after a cold review of the Phase S plan (verified against live code, not
taken on faith): added decisions 5–8 below, closing four gaps the review found real, not
cosmetic — dual-compat schema versioning was a footgun, `translation_of` had no semantic
invariants beyond "target exists," ID/naming policy was implicit, and `meta.language`'s meaning
after Spanish quotes exist was undefined. **Also corrects an error in this record's own §"What
this does not do":** `img-055` and `cc-025` were miscited elsewhere as "2 quotes already carrying
undeclared Spanish diacritics" — verified 2026-09-06, both are **English** aphorisms that merely
*mention* a diacritic character (`cc-025`: *"You put an 'ñ' in the URL..."*) or a loanword
(`img-055`: *"...a cliché"*). Neither is Spanish-language content; neither is an S4 backfill
candidate. The earlier claim came from a character-class regex without a semantic read — exactly
the kind of unverified assertion this project's own discipline exists to catch.

## Decision

A translated quote is a **separate canonical record**, not a locale-keyed field on the original:

1. Each quote record gains a `lang` field (ISO 639-1, e.g. `en`, `es`). **(Revised 2026-09-06:
   required for every record, no dual-compat window.)** S2 rewrites every live record present at
   migration time (derive the count from the file then — do not treat any number in this decision
   as live) and recomputes every digest in one atomic migration — a `schema_version >= 3.1.0` ⇒ required,
   else implicit-`en` split would add a JSON Schema `if`/`then`, a Python mirror of the same
   branch, and a standing footgun: `ttod_core/repository.py::SCHEMA_VERSION` is hardcoded
   `"3.0.0"` (confirmed live 2026-09-06 — a `grep` count is in Phase S §S2′, not restated here to
   avoid this record going stale if that count changes), and it is not the only file with `"3.0.0"`
   hardcoded — see decision 5. A dual-compat rule would let new quotes silently ship without `lang`
   until every one of those constants is separately remembered and bumped. One bump, `lang` simply
   `required`, closes that door in the same migration that already touches every record.
2. A translation is linked to its source via the **existing, already-general** `relation_edges[]`
   mechanism (`schema/quote.schema.json`'s `relation_type` is an unconstrained string — no schema
   change needed for this part): the translated record carries
   `relation_edges: [{ "target": "<source-id>", "relation_type": "translation_of" }]`. The
   direction is one-way — the translation points at the original; the original does not need a
   reverse edge, the same asymmetry already used for `deprecated_by`/`superseded_by`.
3. Each language's record keeps its own full governance: own `id`, own `content_digest`, own
   `origin`/`validation`, own `rights`. A translation is not automatically co-authored or
   co-licensed with its source — it goes through the same proposal/review path as any other new
   quote.
4. **(Added 2026-09-05; trigger clarified 2026-09-06.)** A human MAY request an **automated draft**
   of a sister-language version via the explicit `cli.py translate-draft <source-id> --to <lang>`
   command (Phase S §S4′). That draft is a `proposal` only — `origin: blackbox`, linked via
   decision 2's `translation_of` edge. It reaches `status: active` only through the ordinary
   `proposal accept --reviewer-id …` a human runs separately. **Not** a side effect of `add` /
   `proposal accept` — an auto-hook on promotion is out of scope unless a later decision reopens
   it. Auto-drafting is scoped forward-only by default; backfilling the existing corpus is a
   distinct, separately-authorized bulk operation, not a consequence of this decision.
5. **(Added 2026-09-06.) `translation_of` semantic invariants, not only reference existence.**
   Resolving a target ID is necessary but not sufficient — without more, the schema would accept a
   same-language "translation," two Spanish records both claiming to translate one English source,
   a self-edge, or an A→B→A cycle. Frozen:
   - target must exist and be `status: active` (a translation of a deprecated/erased quote is a
     data-quality question for a human, not a silent validation pass);
   - `lang(source) ≠ lang(target)` — a same-language `translation_of` edge is invalid;
   - at most one `active` translation per `(target_id, lang)` pair — no two competing Spanish
     translations of the same English original both active at once;
   - no self-target;
   - **star, not chain:** a `translation_of` edge must point at a record that itself carries no
     outgoing `translation_of` edge — i.e. at an original, not at another translation. This keeps
     "what is the canonical source" a one-hop question, never a walk.
   - **recommended, not required:** a translation's `section` matches its target's `section` —
     flag a mismatch for human review rather than rejecting it outright, since a translator may
     legitimately judge a different section fits better. Diagnostic code:
     `TRANSLATION_SECTION_MISMATCH` (warning; becomes an error under `validate --strict`, matching
     existing meta-drift warning behavior).
   Each invariant's named code and **frozen fixture filename** live in Phase S §S1′ — do not invent
   alternate names at implementation time.
6. **(Added 2026-09-06.) ID and naming policy — no locale suffixes.** A Spanish twin of
   `arch-001` is the next free `arch-NNN` allocated the same way any new quote is (via
   `meta.last_id_by_section`, at `proposal accept` time) — never `arch-001-es` or any other
   locale-suffixed ID scheme. `lang` and `relation_edges` already carry the language/lineage
   information; the ID stays a plain section-number identity, exactly as today. State this
   explicitly in S1′/S3′ so an implementing agent does not invent a suffix convention.
7. **(Added 2026-09-06.) `meta.language` is redefined, not silently left false.** Once any
   Spanish quote exists, the current `meta.language: en` (a single collection-wide flag) becomes
   false. Chosen: `meta.language` is **deprecated in favor of `meta.languages: [en, es, ...]`** —
   a derived list of every `lang` value actually present in the collection, recomputed the same
   way `meta.total_quotes` already is (never hand-edited, drift-checked by `stats --check`). S2
   writes `meta.languages`; `meta.language` may be kept one more cycle as a read-compatible mirror
   equal to the first entry of `meta.languages`, purely for tooling that has not migrated, and
   removed in a later major version — it is never authoritative after S2.
8. **(Added 2026-09-06.) Corrected count claim.** No existing quote is Spanish-language content.
   `img-055` and `cc-025` — previously miscited as "2 quotes already carrying undeclared Spanish
   diacritics" — are English aphorisms that merely mention a diacritic character or a loanword
   (verified by reading, not by character-class regex). S2 backfills `lang: en` on every live
   record uniformly (count derived at migration report time); there is no partial-Spanish subset
   to reconcile. Historical note: the corpus measured **229** quotes when this decision was
   amended (2026-09-06) — that figure is a dated snapshot, not an implementation constant.

## Why (over the alternative considered)

The alternative — one canonical `id` per aphorism-concept, with `text`/`teaches` becoming
locale-keyed sub-objects (e.g. `translations.es.text`) — was rejected because it would have
changed what `content_digest` means. `ttod_core/canonical.py:compute_content_digest()` hashes
*every* field on the record except the digest fields themselves (verified 2026-09-04, not a
curated subset) — so a locale-keyed `text` would make a record's identity depend on which
locale's prose last changed, undermining Phase Q's TTOD-C14N-v1 guarantee that two clean exports
of the same canonical state are byte-identical, and would have required rewriting the
canonicalizer, validator, and exporter's assumption that `text` is a plain string. The
separate-ID model needs **no such change**: every record stays single-language, `content_digest`
keeps its current meaning untouched, and the linking mechanism (`relation_edges` with an
open-ended `relation_type`) already exists and is already rendered by
`ttod_core/exporter.py`'s `_graph_edges()` and consumed by Phase R's graph island (§4.1 of
`PHASE-R-TTOD-ORACLE-PLATFORM-CASCADE-PROMPT.md`).

## What this does not do

- It does **not** add `lang` to `schema/quote.schema.json` or migrate `ttod.yml` in this session —
  that is Phase S1/S2, gated on this decision, not performed by it.
- ~~It does not decide whether `lang` becomes `required`...~~ **Decided 2026-09-06 (decision 1,
  revised): required for all records, one migrated bump, no dual-compat window.**
- It does **not** authorize distilling `sources/tao-of-ai-development/` or
  `sources/tao-of-human-centered-design/` into quotes. Those chapters stay parked; their own
  READMEs' "do not merge in the same session as a lesson forge" instruction still applies. Phase
  S only prepares the schema/relation mechanism a future, separately-authorized merge session
  would use.
- It does **not** change any existing quote's `id`, `content_digest`, or `rights` before Phase S2
  runs a recorded, atomic, reported migration — exactly like Phase Q6's v2→v3 migration.
- It does **not** let a model-generated translation reach `status: active` without a separate
  human `proposal accept` (decision 4). A request for "promote both languages together" was
  received and corrected to "auto-draft both, auto-accept neither" — the literal ask would have
  given a model tool an accept capability, which `AGENTS.md` denies unconditionally.

## Consequences for Phase R

`domain.ts`'s `WisdomEntry` (§4 of the Phase R cascade doc) and `GraphLink['rel']` (§4.1) must
carry `lang` and `'translation_of'` respectively **before** R1's `/api/v1/*` contract is treated
as frozen — patched directly into that document as part of this decision, not deferred to a
separate PR, since Phase R's own discipline (§10) says the contract is frozen "by construction"
once the cohort start gate opens. **Added 2026-09-06:** `domain.ts`'s `GraphNode` (§4) must also
carry `lang` — `Exporter._graph_nodes()` does not project it today, and without it Phase R's R4
graph island cannot filter or color by language once Spanish quotes exist. The read-path API
surface (`wisdom/sample`, `graph`, and §3.1's retrieval-confidence search) should accept a `lang`
filter once S1′ ships it — otherwise Phase R's `/es/` routes render an all-English corpus with a
Spanish shell around it, which is the exact failure mode Phase S exists to prevent.
