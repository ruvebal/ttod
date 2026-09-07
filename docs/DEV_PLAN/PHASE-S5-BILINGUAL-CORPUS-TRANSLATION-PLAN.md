# Phase S5 — complete bilingual corpus translation and scholarly edition plan

**Status:** IN_PROGRESS — first bounded Ollama drafting tranche staged as proposals only
**Date:** 2026-09-06; first tranche triggered 2026-09-07
**Edition direction:** English source records → Spanish sister records  
**Execution environment:** local Ollama only  
**Canonical boundary:** model output is always a proposal; only a named human may accept it

## 1. Purpose and definition of “complete”

The goal is a complete English–Spanish edition of the active TTOD corpus, not a bulk machine-
translated copy. Every in-scope English source must have exactly one active Spanish sister record,
linked by `translation_of`, reviewed by a human, independently addressable, and reproducible from
a frozen source edition.

The denominator must always be computed, never copied into prose:

```text
eligible sources = active English originals in the chosen edition scope
complete sources = eligible sources with exactly one active Spanish translation_of sister
coverage = complete sources / eligible sources
```

The repository measured 229 English records and no accepted Spanish records on 2026-09-06. That is
a dated baseline, not an implementation constant. Deprecated, erased, unresolved-rights, and
restricted records are excluded from the public bilingual-edition denominator. Translating them
for archival study requires a separate editorial decision.

## 2. Edition principles

This programme follows a digital-scholarly-edition model:

- **Fix the source witness.** Record the source git commit, `ttod.yml` SHA-256, schema version,
  canonicalization version, and per-record content digests before drafting.
- **Preserve identity and alignment.** Originals retain their IDs. Each Spanish translation gets
  the next ordinary section ID at human acceptance and points directly to its English original;
  no locale suffixes and no translation chains.
- **Separate transcription, translation, and interpretation.** `text` translates the aphorism;
  `teaches` translates its pedagogical gloss. The gloss may explain; the aphorism may not be made
  more explicit merely because ambiguity is difficult.
- **Make intervention visible.** Machine drafting, human revision, validation, and final editorial
  responsibility remain distinguishable in provenance. A fluent output is not presumed faithful.
- **Retain variants outside the canonical edition.** Alternative drafts remain proposals or
  adjudication material. Only one Spanish sister per source may be active.
- **Never overwrite silently.** A later improved translation is a reviewed revision/deprecation
  event under TTOD governance, not an in-place textual substitution without history.
- **Keep publication and working data separate.** The public edition exposes the source/translation
  relationship and appropriate authorship/rights information; raw model responses, local paths,
  prompts, and reviewer working notes remain private editorial material.

This plan uses TEI-style scholarly-editing principles—explicit textual responsibility, language,
source/target alignment, revision history, and separable editorial statements—without forcing the
TTOD YAML model into TEI XML. TTOD's own v3.1 records remain canonical; any TEI or JSON-LD export
would be derived and separately validated.

## 3. Scope and translation unit

### 3.1 Primary scope

Translate every canonical record satisfying all of:

- original language `en`;
- active lifecycle status;
- no outgoing `translation_of` edge (it is an original, not a translation);
- public-edition rights resolved when the target edition is public; and
- no existing active `es` sister pointing to it.

Recompute this set immediately before each authorized tranche so newly accepted records and
already completed pairs are handled correctly.

### 3.2 Fields

| Field | Treatment |
| --- | --- |
| `text` | translate with literary and rhetorical fidelity |
| `teaches` | translate accurately in clear pedagogical Spanish |
| `lang` | set to `es` |
| `relation_edges` | add exactly one `translation_of` edge to the English original |
| `section`, `level`, `subsection` | inherit initially; human reviewer confirms applicability |
| `tags` | preserve canonical controlled tags; do not translate taxonomy tokens |
| technical tokens | preserve exact spelling when they are code, formats, APIs, paths, commands, or identifiers |
| `show_when` and other untranslated prose-bearing fields | inventory before the campaign; either include through an approved schema/tool extension or document them explicitly as out of edition scope—never leave mixed-language fields unnoticed |
| rights | make a fresh item-level decision; copying source rights is only a draft default, not proof that translation rights are identical |
| `origin` | `blackbox` for model-originated drafts |
| authorship/provenance | record exact Ollama model tag and immutable model ID plus human reviewer responsibility |

The existing `translate-draft` command covers `text` and `teaches`, copies several structural
fields, and creates a proposal. S5 must audit all other prose-bearing fields before calling the
edition complete.

## 4. Language and editorial policy

Create and freeze an `EDITORIAL-TRANSLATION-POLICY.md` before drafting. It must decide:

- target variety: contemporary international Spanish, with Spain usage preferred only where it
  does not reduce wider intelligibility;
- address and voice: preserve the source's impersonal, imperative, or dialogical stance;
- developer terminology: a bilingual controlled glossary with preferred term, allowed variant,
  forbidden false friend, rationale, and examples;
- loanwords: retain established technical English only when normal Spanish professional usage
  warrants it; never leave ordinary prose untranslated;
- code and identifiers: never translate literal syntax, filenames, commands, URLs, IDs, CSS
  properties, library names, or standards identifiers;
- punctuation and typography: Spanish punctuation and quotation conventions, while preserving
  meaningful lineation;
- wordplay, Taoist language, koans, and haiku: preserve semantic tension and rhetorical economy;
  do not claim syllabic equivalence unless the reviewer has scanned it;
- gender and inclusivity: prefer natural non-marked formulations; avoid mechanically expanding
  concise aphorisms;
- ambiguity: record an editorial note when two readings materially affect the translation rather
  than letting the model choose invisibly;
- untranslatable terms: retain, gloss, or transpose only according to an explicit recorded choice;
  and
- proper names, citations, and attributed text: do not translate quotations whose rights or
  attribution do not authorize adaptation without a separate rights decision.

The glossary is versioned editorial authority. A model may consult it; it may not add preferred
terms to it autonomously.

## 5. Model-selection protocol

### 5.1 What is known now

Local inventory on 2026-09-06 includes:

- `qwen3.8:27b` — validated by the Phase S4 ten-item pilot: 9/10 accepted by its rubric, with one
  clear lexical error (`Coda` for imperative “Code”);
- `qwen2.5:72b-instruct-q4_K_M` — largest general instruction model installed, but not calibrated
  for TTOD translation;
- `qwen2.5:32b-instruct` — comparison pilot scored below `qwen3.8:27b` overall but corrected one
  item the primary missed; and
- scholar/coder/sentinel models — specialized models, not presumed suitable translators without
  evidence.

Therefore “best model” means best on a frozen TTOD translation benchmark, not largest parameter
count. `qwen3.8:27b` is the proven baseline, not automatically the final winner.

### 5.2 Calibration before corpus work

Build a frozen, stratified benchmark of at least 30 records or 10% of the eligible corpus,
whichever is larger. Include every section and level, plus deliberate stress cases:

- haiku/lineated form;
- Taoist or Buddhist ambiguity;
- humor and wordplay;
- developer jargon and code literals;
- accessibility/ethics language;
- imperatives and parallel constructions;
- culturally marked metaphors;
- long or syntactically unusual `teaches`; and
- the known `img-071` adversary.

Run at least `qwen3.8:27b` and `qwen2.5:72b-instruct-q4_K_M` with identical prompts and frozen
generation settings. Blind model identity during human scoring. Score each field separately on a
0–3 scale for semantic fidelity, non-invention, Spanish idiomaticity, register, rhetorical/formal
fidelity, terminology, and pedagogical fidelity. Any contradiction, reversed prescription,
corrupted code token, invented claim, or unmarked omission is a critical failure regardless of
the average.

Promote a model to primary only if it has:

- no higher critical-error rate than the baseline;
- higher median total quality or a clearly documented equal-quality efficiency advantage;
- stable structured-output parsing; and
- acceptable latency on the actual local machine.

If the 72B model does not meet that gate, use `qwen3.8:27b`. Use the best-performing alternate as
an adjudication model for difficult records. Never accept a translation merely because two models
agree; shared error is possible.

Record the model tag, Ollama model ID, prompt version, glossary version, decoding settings, and
source digest in the edition statement. This is editorial provenance, not behavioral monitoring.

## 6. Drafting protocol

### 6.1 Preflight gate

Before bulk drafting:

1. Strict validation and metadata checks pass on the source corpus.
2. A byte-identical tracked backup/source snapshot exists under the established migration
   convention.
3. Ollama identifies the frozen primary model and sufficient disk/memory is available.
4. A disposable-copy rehearsal proves the full path:
   `translate-draft` → human review metadata → `proposal accept` → valid Spanish sister.
5. **Resolved and proven, 2026-09-06 — record kept here rather than silently dropped, so no
   future session re-discovers this from scratch.** The gap was deeper than first characterized:
   `schema/quote.schema.json`'s own conditional (`if origin in [blackbox, mixed] → then
   validation.required = [reviewer_id, activity_id]`, with `status` constrained to `"validated"`
   when present) demands a *complete* validation block, not `reviewer_id` alone — and nothing in
   the object model (`ReviewActivity` has no `activity_id` field at all) previously produced an
   `activity_id`. Fixed in `ttod_core/repository.py::accept_proposal()`: for `origin in
   ("blackbox", "mixed")`, it now injects `reviewer_id` (from its own required argument),
   `activity_id` (a freshly generated `accept-<uuid4>`), `status: "validated"`, and `reviewed_at`
   — each only via `setdefault`, so an already-present value from an earlier step is never
   overwritten. Proven end-to-end on a disposable copy, never touching live `ttod.yml` (sha256
   `b663860b…` identical before/after): `translate-draft cc-022 --to es` → a real
   `qwen3.8:27b` draft → `proposal accept <id> --reviewer-id ruvebal-test-reviewer` (previously
   failed with `blackbox origin requires validation.reviewer_id before accept`; now succeeds) →
   `cc-039` written with a correct `translation_of: cc-022` edge, full `validation` block, and
   `validate --strict` passing 0 errors. Three regression tests added in
   `tests/test_repository.py` (`test_blackbox_accept_injects_reviewer_id_when_absent`,
   `test_blackbox_accept_never_overwrites_explicit_reviewer_id`,
   `test_blackbox_accept_still_requires_reviewer_id_argument`); full suite 211/211 green. This
   closes item 5's own gate — it does **not** authorize bulk drafting, which still needs items
   3, 4 (as an actual rehearsal run, now trivially repeatable), 6, and §4/§5/§14's own
   authorizations.
6. **Resolved for bounded drafting, 2026-09-07.** `cli.py translate-batch` now provides the
   minimum fail-closed wrapper required before any tranche larger than one record: it recomputes
   eligible English originals, skips active `translation_of` sisters, skips already-pending
   Spanish translation proposals, refuses unbounded operation unless `--all` is explicit, never
   accepts proposals, writes a JSON run manifest, and verifies that `ttod.yml` remains
   byte-identical to the source hash recorded at run start. This is a drafting wrapper only, not a
   human-review tracker or release workflow.

### 6.2 Prompt packet

Each call receives only:

- frozen source `text` and `teaches`;
- source and target language;
- relevant approved glossary entries;
- form/register classification;
- protected literal tokens extracted from the record; and
- the exact response schema.

Do not feed prior model translations as authority. Few-shot examples must be human-approved and
must not encourage phrase homogenization across distinct aphorisms.

### 6.3 Tranches

Draft in editorial tranches, recommended 12–20 records, grouped by section/form rather than one
unattended whole-corpus run. A tranche is not accepted until the previous tranche's recurrent
errors have been incorporated into the human-owned glossary or prompt revision. Changing the
prompt, model, or glossary starts a new named drafting stratum; it never silently alters earlier
provenance.

The process need not collect interaction telemetry, keystrokes, or reviewer timing. Retain only
the minimum scholarly record: source snapshot/digest, candidate, model/prompt/glossary versions,
human decision, final text, and reason for substantive intervention.

## 7. Human review and adjudication

Every candidate receives two conceptually separate passes; one qualified person may perform both
only if the edition statement discloses that limitation.

### Pass A — bilingual fidelity review

Compare source and target side by side. Check meaning, negation, agency, modality, technical
literals, omissions, additions, metaphor, ambiguity, lineation, and `teaches` alignment. Read the
source before reading the model's rationale; preferably do not generate a rationale at all.

### Pass B — Spanish editorial review

Read the Spanish independently for idiom, rhythm, punctuation, concision, register, consistency,
and pedagogical clarity. A translation may be faithful yet unusable Spanish, or elegant yet
unfaithful; both dimensions must pass.

### Decision states

- `accept`: no substantive change needed;
- `accept-after-edit`: human supplies the final target and records the intervention category;
- `second-opinion`: run the adjudication model or consult another translator;
- `retranslate`: primary draft unusable;
- `hold`: ambiguity, rights, source defect, or terminology decision unresolved; or
- `reject`: no translation enters the edition.

High-risk items—poetry/haiku, wordplay, culturally specific metaphors, legal/ethical claims,
attributed material, and any candidate with a critical error—require a second human reading before
acceptance where feasible.

## 8. Quality model and automated checks

Use an MQM-inspired error taxonomy adapted to aphorisms:

- accuracy: mistranslation, omission, addition, untranslated content;
- terminology: inconsistent or forbidden term, corrupted protected token;
- linguistic quality: grammar, agreement, punctuation, spelling, unnatural phrasing;
- style/register: verbosity, lost aphoristic force, altered voice, flattened ambiguity;
- locale convention: inappropriate Spanish form;
- form: lost line break, parallelism, rhythm, or deliberate repetition;
- pedagogy: `teaches` contradicts or exceeds the aphorism; and
- governance: wrong language, relation, section, rights, provenance, or reviewer metadata.

Severity is `critical | major | minor | preference`. Critical and major errors block acceptance;
preferences never masquerade as defects.

Automated gates should test:

- protected tokens preserved exactly;
- no blank `text`/`teaches` and no stray prompt labels/fences;
- target language detection as a warning, never sole adjudicator;
- punctuation/line-break anomalies;
- glossary forbidden terms;
- source/target relation invariants and uniqueness;
- item rights and validation blocks;
- content digest recomputation;
- `meta.languages` and counts derived correctly; and
- strict schema/repository/bridge/export/frontend tests after every accepted tranche.

Back-translation and embedding similarity may identify candidates for review, but neither may pass
or reject a literary translation automatically.

## 9. Canonical acceptance and release

Acceptance remains one deliberate human transaction per reviewed proposal or an explicitly
authorized transactional batch whose every item already bears its own human decision. The batch
mechanism may reduce mechanics; it may not collapse review into one blanket approval.

Before each commit:

- validate strict invariants and metadata;
- ensure one and only one active Spanish sister per eligible English original;
- verify no IDs were model-generated or locale-suffixed;
- verify the English records are byte/semantically unchanged except derived metadata where
  formally required;
- verify rollback on an induced failure against a disposable copy; and
- export a bilingual coverage report computed from canonical relationships.

Release only when coverage is 100% for the frozen edition denominator, all holds are either
resolved or explicitly removed from scope by a signed editorial decision, every accepted
translation has human validation, and the frontend/API can select the sister record by language
without presenting fallback English as Spanish.

The release package should include:

- bilingual canonical snapshot and digest manifest;
- machine-readable source↔translation alignment table;
- public edition statement naming source edition, editorial policy, model assistance, human
  responsibility, known limitations, and licenses;
- glossary version;
- validation/test report; and
- preservation export in the repository's existing JSON/graph formats. A TEI/PROV export is an
  optional derived research artifact, not a release blocker.

## 10. Failure and rollback policy

- Ollama timeout, malformed response, or resource exhaustion: proposal not created; source
  unchanged; retry is explicit.
- Duplicate proposal: retain variants but do not activate more than one sister.
- Source changes after drafting: mark candidate stale by digest and redraft/review against the new
  witness.
- Model/prompt/glossary change: new provenance stratum, never retroactively relabel old drafts.
- Acceptance validation failure: canonical bytes remain unchanged and proposal stays resumable.
- Critical error discovered after release: deprecate/supersede through governance; never erase
  ordinary editorial history.
- Coverage mismatch: release blocks; do not repair counts by hand.

## 11. Roles and responsibility

| Role | Authority |
| --- | --- |
| Product owner / general editor | freezes scope, policy, model choice, edition statement, and release |
| Local Ollama model | drafts only; no ID allocation, review, acceptance, or canonical write |
| Bilingual reviewer | establishes semantic fidelity and supplies corrections |
| Spanish copy editor | establishes target-language quality and consistency |
| Technical editor | maintains glossary tooling, invariants, exports, and reproducibility |
| Cold reviewer | samples accepted pairs and verifies claims against canonical records |

If Rubén fills several roles, the edition statement names that concentration of responsibility
rather than implying independent review that did not occur.

## 12. Sampling and final audit

Human review is exhaustive; sampling is an additional audit, not a substitute. After all items are
accepted:

- re-review 100% of critical/high-risk items;
- cold-review a stratified random sample of at least 15% of ordinary items, covering every
  section, level, drafting stratum, and reviewer;
- inspect every source/target pair changed after initial acceptance;
- verify every glossary term across the full Spanish corpus; and
- run a monolingual Spanish read for voice drift and repetitive model mannerisms.

Any critical error in the cold sample reopens the affected stratum and expands review; do not
average it away.

## 13. Grounding and standards note

The plan was informed by read-only discovery in the local Athanor projects
`scholarly-editing`, `computational-authorship`, and `profield-frontend-pedagogy`. Candidate pages
supported the relevance of relational digital editions, explicit editorial intervention,
collation, and human evaluation. Their extracted bibliographic metadata was not resolved to
evaluator-safe citations in this planning pass, so they remain **[BIBLIO-GAP] discovery context**
and are not presented here as clean scholarly citations.

Before publishing the edition statement or a research article, resolve page-level citations in
Ahmes and ground the public methodology against the current official specifications most relevant
to the adopted profile: TEI P5 for language/alignment/revision concepts, W3C PROV for derived
provenance exports, and MQM for translation-error classification. These are design references;
TTOD's canonical YAML schema and human-governed repository remain authoritative.

## 14. Authorization boundary

This document authorizes nothing by itself. It does not call Ollama, stage proposals, alter
`ttod.yml`, accept translations, allocate IDs, create progress tracking, or publish an edition.
Execution begins only after the product owner freezes the editorial policy, selects the calibrated
model, fixes and proves the acceptance path, and explicitly authorizes the bulk drafting scope.

## 15. Execution log

### 2026-09-07 — first bounded drafting tranche

Rubén explicitly authorized triggering Ollama translation. A conservative first tranche was run
through the new `translate-batch` wrapper, using local `qwen3.8:27b`, target `es`, and
`--limit 12`.

The first sandboxed attempt could not reach local Ollama and created no proposals; its failure
manifest is retained at `proposals/manifests/s5-20260907T092057Z.json`.

The authorized local-Ollama run completed with 12 proposals and 0 failures. Manifest:
`proposals/manifests/s5-20260907T092117Z.json`.

Selected source IDs:

```text
img-001, img-002, img-003, img-004, img-005, img-006,
img-008, img-009, img-010, img-011, img-012, img-013
```

Verification after the run:

- `ttod.yml` SHA-256 remained `b663860b0b6ab4ca7e88c90661848993ae12401be69c74b801c46aa7cf957e97`,
  matching the manifest hash exactly.
- `python cli.py validate --strict --json` returned valid with zero errors and zero warnings.
- `python cli.py stats --check` reported clean derived metadata: `total_quotes` remains 229.
- Each created proposal is `status: proposed`, `lang: es`, `origin: blackbox`, and contains exactly
  one `translation_of` edge to its English source.

No proposal was accepted, no canonical ID was allocated, and no publication/release claim follows
from this drafting tranche.

### 2026-09-07 — remaining corpus drafting tranche

Rubén then explicitly authorized translating all remaining eligible records with no dry run. The
same `translate-batch` wrapper was run with `--all`, local `qwen3.8:27b`, and target `es`.

The run selected the 207 English originals that still had neither an active Spanish sister nor a
pending Spanish translation proposal. It completed with 207 proposals and 0 failures. Manifest:
`proposals/manifests/s5-20260907T092656Z.json`.

Verification after the run:

- `ttod.yml` SHA-256 remained `b663860b0b6ab4ca7e88c90661848993ae12401be69c74b801c46aa7cf957e97`,
  matching the manifest hash exactly.
- `python cli.py validate --strict --json` returned valid with zero errors and zero warnings.
- `python cli.py stats --check` reported clean derived metadata: `total_quotes` remains 229.
- `python cli.py translate-batch --limit 1 --dry-run` reported 0 eligible remaining sources.
- The generated material is still only draft proposal material: no proposal was accepted, no
  canonical ID was allocated, and the bilingual edition is not complete until human review and
  acceptance have been performed.
