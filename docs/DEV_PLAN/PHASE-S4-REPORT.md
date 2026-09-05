# Phase S4′ Report — TTOD assisted translation drafting

**Status:** DONE (2026-09-04), with one explicit, unsoftened pilot failure recorded below
**Cascade:** [`PHASE-S-TTOD-BILINGUAL-CONTENT-MODEL.md`](PHASE-S-TTOD-BILINGUAL-CONTENT-MODEL.md) §S4′
**Prerequisite:** S1′ — [`PHASE-S1-REPORT.md`](PHASE-S1-REPORT.md), reverified green before this run.
**Does not mutate live `ttod.yml`:** confirmed byte-identical throughout this session (see Preflight
and Post-run verification). Writes only to the gitignored `proposals/` store.
**Out of scope, not touched:** S3′ (`.cursor/rules/ttod-editing.mdc`, `sources/*/README.md`,
`docs/DEV_PLAN/INDEX.md`) — owned by a parallel effort, confirmed disjoint file set throughout.

---

## Status verdict, stated plainly before the detail

`cli.py translate-draft` works exactly as specified: it fails fast on both named invariants before
calling any model, it writes a `status: proposed` proposal and structurally cannot write a
canonical `id` or `status: active` anywhere, and it records whichever model tag actually ran in the
proposal's own provenance fields (verified against the saved JSON, not just claimed — see
"Provenance verification").

The primary-model pilot (`qwen3.8:27b`, the model that gates DONE per the task brief) scored **9/10
clean** on the four-criterion rubric and **1/10 clear FAIL** on semantic fidelity
(`img-071` — the model mistranslated the imperative "Code with wisdom" as "**Coda** con sabiduría,"
a real Spanish word that does not mean "to code"; the correct rendering, which the comparison model
actually produced, is "**Codifica** con sabiduría"). This is called DONE, not PARTIAL, because:

- the failure is caught, documented, and structurally cannot reach the corpus unreviewed — S4′'s
  entire design point is that a human runs `proposal review` / `proposal accept` before anything
  becomes canonical, and that gate is exactly what would catch this one;
- the other 9 outputs are genuinely strong, not merely "not obviously wrong" — several show real
  translation judgment (e.g. `img-007`'s "apego"/"pérdida" preserving the Buddhist double meaning
  of "attachment"/"loss" that the English plays on; `img-063`'s correct plural-adjective agreement
  on "imágenes... tiranas"; `rrp-015`'s elided-copula aphoristic economy), not template output;
- a 1-in-10 clear defect rate for a small (27B) local model, under a workflow that mandates human
  review before acceptance, is evidence the human gate is doing its job — not evidence the tool is
  "not usable at scale." A pilot with zero defects across creative/idiomatic content would be the
  more suspicious result.

This is a judgment call, not a formality — see "Honest assessment" below for the full reasoning,
including where I considered PARTIAL and rejected it.

---

## Preflight

- `git status`: working tree dirty with uncommitted S1′/S2′/S3′-in-progress work, exactly as
  expected per the task brief. Touched only `cli.py`, `ttod_core/repository.py` (one line),
  `ttod_core/translation.py` (new), `tests/test_s4_translate_draft.py` (new), and this cascade
  document's status line / S4′ Programme row (both explicitly authorized by the task).
- `PYTHONPATH=. .venv/bin/python cli.py validate --strict` → `OK — 0 errors, 0 warnings` (exit 0).
- `PYTHONPATH=. .venv/bin/python cli.py stats` → `Total quotes: 229`, `By language: en: 229` —
  live count read at report time, not assumed from the S0 snapshot figure.
- `ollama list` confirmed both named candidates already pulled, no substitution needed:
  `qwen3.8:27b` (17 GB) and `qwen2.5:32b-instruct` (19 GB). Also present but not used as a
  translator per the plan's own reasoning: `thessia-scholar-v3:latest`, `thessia-coder-v3:latest`;
  `thessia-sentinel-v3:latest` correctly left untouched (reserved role per DevIAC's cascade).
- Confirmed Ollama reachable at `http://localhost:11434` via `/api/tags` before writing any code
  against it.

## Mechanism discovery notes (read before the rubric)

- `qwen3.8:27b` is a hybrid-reasoning ("thinking") model. A first attempt using Ollama's
  `format: "json"` structured-output mode returned an **empty** `response` field — the model's
  `thinking` trace consumed the call's implicit budget before any JSON was emitted. Switching to
  `think: false` plus a plain `TEXT: ...` / `TEACHES: ...` delimited format fixed this (7–20s per
  call instead of failing) and is what `ttod_core/translation.py::call_ollama_generate()` sends.
  `think: false` is harmless on `qwen2.5:32b-instruct` (a non-thinking model) — confirmed by testing
  both with and without the flag before committing to it as unconditional.
- No new Python dependency: the Ollama call uses `urllib.request` (stdlib) — `requests` is not
  installed in `.venv` and none was added.

## Implementation — `cli.py translate-draft <source-id> --to <lang>`

```
$ PYTHONPATH=. .venv/bin/python cli.py translate-draft --help
Usage: cli.py translate-draft [OPTIONS] SOURCE_ID
  --to TEXT        Target ISO 639-1 language (e.g. es)  [required]
  --model TEXT      Ollama model tag to run  [default: qwen3.8:27b]
  --host TEXT       Ollama API host  [default: http://localhost:11434]
  --timeout FLOAT   Ollama call timeout (seconds)  [default: 180.0]
  --proposer-id TEXT
  --file PATH       TTOD YAML source (default: live ttod.yml, read-only)
  --output PATH     Write proposal JSON here in addition to the store
```

Explicit command only, exactly as required — not wired as a side effect of `add` or
`proposal accept`; neither of those commands was touched.

**Fail-fast order (before any model call):**

1. `--to` equals the source quote's own `lang` → `typer.Exit(2)`, message names
   `TRANSLATION_SAME_LANGUAGE` explicitly, model never called (verified: mocked `translate_quote`
   asserted `not_called()` in `test_same_language_refused_before_model_call`).
2. An `active` translation of `(source_id, --to)` already exists (scanned via
   `find_active_translations()` — reads `relation_edges[].relation_type == "translation_of"` +
   `status` defaulting to `active` when absent, matching the validator's own `_quote_status()`
   convention in `ttod_core/validation.py`) → prints a `WARNING` naming
   `TRANSLATION_DUPLICATE_ACTIVE`, **does not block** — model is still called
   (verified: `test_duplicate_active_warns_but_still_calls_model`).

Real runs against disposable copies confirmed both paths (see commands below); live `ttod.yml`'s
sha256 was identical before and after every fail-fast test.

**Proposal payload** (`ttod_core/translation.py::build_translation_candidate()`), confirmed against
a real saved proposal (`proposals/2fa8db44-bac0-49d8-a3cb-411f087201d5.json`, `cc-022 → es`):

```json
{
  "text": "Vacía la olla, Debe llenarse sin derrame, Respalda, luego vierte lento.",
  "section": "code-craft",
  "level": "beginner",
  "lang": "es",
  "origin": "blackbox",
  "relation_edges": [{"target": "cc-022", "relation_type": "translation_of"}],
  "authorship_assertion": "machine-translated from 'cc-022' (lang=en) via ollama:qwen3.8:27b — human review required before acceptance",
  "teaches": "La migración exige cuidado. ...",
  "tags": ["codecraft", "migration", "backup", "haiku", "poetry", "safety", "patterns"],
  "subsection": "patterns",
  "rights": {"access": "public", "license": "CC-BY-NC-SA-4.0", "holder": "ruvebal@crea-comm.net", "permission_basis": "rights-holder-relicense-2026-08-18"}
}
```

`section`/`level`/`tags`/`subsection`/`rights` are copies of the source's own fields (editable
defaults, per §S4′); `teaches` is translated, not left in English; `origin: blackbox` always;
`authorship_assertion`/`generation_method` record the actual model dynamically (verified next).

## Provenance verification (dynamic, not claimed)

```
$ jq '.generation_method, .candidate_content.authorship_assertion' proposals/21e4cc66-...json   # qwen3 run
"ollama:qwen3.8:27b:translate-draft-v1"
"machine-translated from 'img-071' (lang=en) via ollama:qwen3.8:27b — human review required before acceptance"

$ jq '.generation_method, .candidate_content.authorship_assertion' proposals/e0f56eef-...json   # qwen2.5 run
"ollama:qwen2.5:32b-instruct:translate-draft-v1"
"machine-translated from 'img-071' (lang=en) via ollama:qwen2.5:32b-instruct — human review required before acceptance"
```

Confirmed: the two identically-shaped calls, differing only in `--model`, produced provenance
fields that name the model that actually ran, matching the CLI's own printed output for each run
— not a hardcoded string.

## Negative proof — never a canonical write path

Per the task's single load-bearing constraint, `tests/test_s4_translate_draft.py` includes a
dedicated `TestStructuralNoCanonicalWritePath` class that:

- inspects `inspect.getsource()` of `ttod_core/translation.py` and of `cli.translate_draft` and
  asserts the literal absence of `accept_proposal`, `accept_quote_direct`,
  `_allocate_canonical_id`, `.accept(`, `TTODRepository(`, and both `"status": "active"` /
  `'status': 'active'` spellings — a grep-on-source proof, not just a runtime assertion that could
  itself be wrong;
- confirms via `hasattr()` that `ttod_core/translation.py` never even imports `ProposalStore`,
  `TTODRepository`, or `create_proposal` into its own namespace (it has zero import of
  `ttod_core.repository` at all — only `cli.py` wires the read-only `_repo(file).load()` and the
  write-only `_proposal_store().save()`);
- confirms `build_translation_candidate()`'s own source contains its two `assert` guards
  (`assert "id" not in candidate`, `assert "status" not in candidate`) — belt-and-suspenders: even
  if every other guard were bypassed, this function raises `AssertionError` rather than emit a
  candidate carrying either key;
- functionally proves it for varied inputs (`test_never_contains_id_or_status`) and end-to-end via
  the CLI (`test_happy_path_writes_proposal_not_quote`): loads the saved JSON and asserts
  `"id" not in candidate_content`, `"status" not in candidate_content`, `status == "proposed"`,
  `accepted_quote_id is None`, `human_review_activities == []`, and that the target `ttod.yml`'s
  bytes are unchanged after the run.

## Commands / exits

```bash
cd ~/src/ttod

# Fail-fast #1 — same language, no model call, live file untouched
PYTHONPATH=. .venv/bin/python cli.py translate-draft cc-022 --to en
# REFUSED: --to 'en' equals source quote 'cc-022's own lang 'en' ... — exit 2

# Fail-fast #2 — duplicate active, warns, still drafts (disposable fixture with a synthetic
# es twin of cc-022 injected)
PYTHONPATH=. .venv/bin/python cli.py translate-draft cc-022 --to es --file <disposable>
# WARNING: an active translation of 'cc-022' into 'es' already exists: ['cc-901'] ... — exit 0

# Real end-to-end draft against a disposable copy
PYTHONPATH=. .venv/bin/python cli.py translate-draft cc-022 --to es \
  --file <disposable> --output <scratch>/cc-022-es-draft.json
# Drafted translation proposal: b974d8ec-... ; model: qwen3.8:27b (18.1s) ; exit 0

# Full automated suite (26 new S4′ tests, mocked model — deterministic, no live Ollama dependency)
PYTHONPATH=. .venv/bin/python -m unittest tests.test_s4_translate_draft -v
# Ran 26 tests in 0.03s — OK

# Full repository suite
PYTHONPATH=. .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
# Ran 202 tests in 2.35s — OK   (176 pre-existing + 26 new S4′; 0 regressions)

# Live corpus untouched throughout
PYTHONPATH=. .venv/bin/python cli.py validate --strict   # OK — 0 errors, 0 warnings (exit 0)
shasum -a 256 ttod.yml
# b663860b0b6ab4ca7e88c90661848993ae12401be69c74b801c46aa7cf957e97   (identical at session start and end)
```

---

## Pilot rubric — 10 live quotes, primary model `qwen3.8:27b` (gates DONE)

Selection: random sample (seed 42) across sections/levels from the live 229-quote corpus,
deliberately including haiku-shaped forms (`cc-022`, `dop-003`'s embedded haiku), wordplay/humor
(`cc-032`), a Buddhist-inflected technical pun (`img-007`), an ethical-register piece (`img-058`),
and a nested-quotation piece (`img-063`) — not cherry-picked for ease.

Criteria: **fidelity** (no meaning drift), **register** (aphoristic, not expanded/explained),
**form** (line breaks/syllabic economy where haiku-shaped), **no invented content**.

| ID | Source `text` | `qwen3.8:27b` translation | Fidelity | Register | Form | No invention | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `cc-022` | "The pot once emptied, Must be filled without a spill, Backup, then pour slow." | "Vacía la olla, Debe llenarse sin derrame, Respalda, luego vierte lento." | pass | pass | pass (3-part rhythm kept; participial→imperative shift is a defensible register choice, not drift) | pass | **PASS** |
| `dop-003` | "...GPU and CPU drink from the same pool. 128GB unified is not a compromise..." + haiku teaches | "...la GPU y la CPU beben del mismo pozo..." + "pozo de memoria compartido / setenta y dos mil millones de pesos / caben donde nadie soñó" | pass ("weights"→"pesos" is the correct ML-jargon term, not a guess) | pass | pass (3-line haiku form kept) | pass (minor tense shift "could dream"→"soñó," poetic economy, not new content) | **PASS** |
| `img-029` | "The heaviest image weighs nothing when never loaded. The lightest image crushes the user when poorly placed." | "La imagen más pesada no pesa nada si nunca se carga. La más ligera aplasta al usuario si está mal colocada." | pass | pass | pass (parallel structure kept) | pass | **PASS** |
| `img-007` | "WebP is the middle way: neither the attachment of PNG nor the loss of JPG." | "WebP es el camino medio: ni el apego de PNG ni la pérdida de JPG." | pass | pass — "apego"/"pérdida" preserve the Buddhist double meaning ("attachment"/"loss") the English plays on; a genuinely good translation choice, not a lucky cognate | pass | pass | **PASS** |
| `img-071` | "Seek the middle path. Optimize with compassion. **Code** with wisdom. Test with humility." | "Busca el camino medio. Optimiza con compasión. **Coda** con sabiduría. Prueba con humildad." | **FAIL** — "Coda" is a real Spanish noun (musical coda / rhetorical closing passage); it is not a verb and does not mean "to code." The imperative parallel to "Busca/Optimiza/Prueba" needed "Codifica" or the tech-register "Codea" (which the comparison model produced correctly, see below) | fail (a native reader parses "Coda con sabiduría" as nonsensical in this imperative series) | pass (4-clause form kept) | borderline — a wrong word, not added content, but it is a hallucinated lexical substitution | **FAIL — flagged for mandatory human revision, do not accept as drafted** |
| `img-063` | "The ancient masters said: 'Content is king.' ... Images have become the tyrant..." | "Los antiguos maestros decían: 'El contenido es el rey.' ... Las imágenes se han vuelto tiranas..." | pass | pass | pass (embedded quote preserved) | pass | **PASS** |
| `arch-034` | "A protocol is a promise. An adapter is a translator. A port is a doorway. The domain does not know who knocks..." | "Un protocolo es una promesa. Un adaptador es un traductor. Un puerto es una puerta. El dominio no sabe quién llama..." | pass | pass | pass (triadic parallel structure kept) | pass | **PASS** |
| `cc-032` | "'Final_Final_v2' implies you have looked into the future and were wrong. Twice." | "'Final_Final_v2' implica que miraste al futuro y te equivocaste. Dos veces." | pass | pass (comic beat of the standalone "Dos veces." preserved) | pass | pass | **PASS** (note: `teaches`'s "acumulador" for "hoarder" is a mild lexical imprecision — "acaparador" is more idiomatic — not severe enough to fail fidelity) |
| `rrp-015` | "The repo is temporary; the grade is permanent." | "El repositorio es temporal; la calificación, permanente." | pass | pass — elided copula in the second clause is classic Spanish aphoristic economy, arguably improves register fit | pass | pass | **PASS** |
| `img-058` | "Autoplay video is not engagement—it is assault. The user who does not choose to hear does not consent to hear." | "El vídeo que se reproduce solo no es interacción, es asalto. Quien no elige oír no consiente oír." | pass | pass (assertive ethical register kept) | pass | pass | **PASS** |

**Primary-model score: 9/10 PASS, 1/10 FAIL (`img-071`, semantic fidelity).**

## Comparison run — `qwen2.5:32b-instruct`, same 10 quotes, same prompt

Not required to gate DONE, run anyway per the task's "if you have time" instruction — full 10, not
a subset.

| ID | `qwen2.5:32b-instruct` translation | Notable defect vs. `qwen3.8:27b` |
| --- | --- | --- |
| `cc-022` | "La olla vaciada, Debe llenarse sin derramar, Respalda, luego lento." | **Dropped the verb** — "then pour slow" became just "luego lento" ("then slow"), losing the pouring action entirely. Real meaning loss; `qwen3.8:27b` kept "vierte" correctly. |
| `dop-003` | "En Silicon de Apple, la GPU y la CPU beben del mismo estanque..." | "Silicon de Apple" is an awkward calque of the proper noun "Apple Silicon" (should stay "Apple Silicon" or "el Apple Silicon"); `qwen3.8:27b`'s phrasing was more natural. Otherwise equivalent. |
| `img-029` | "La imagen más pesada pesa nada cuando nunca se carga. La imagen más ligera aplasta al usuario cuando mal colocada." | **Two grammar errors**: "pesa nada" needs the negative-concord "no" ("no pesa nada"); "cuando mal colocada" is missing its copula ("cuando **está** mal colocada"). Reads as broken Spanish, not aphoristic economy. |
| `img-007` | Identical to `qwen3.8:27b`'s output. | none |
| `img-071` | "Busca el camino medio. Optimiza con compasión. **Codifica** con sabiduría. Prueba con humildad." | **Correct** — this is the one quote where `qwen2.5:32b-instruct` outperformed the primary model. |
| `img-063` | "Los antiguos maestros dijeron: 'El contenido es rey.' ... el contenido sirve a su gusto." | Minor stylistic variants only ("dijeron" vs "decían," article-less "es rey," "gusto" vs "antojo") — both are defensible, not a defect. |
| `arch-034` | "...El dominio no **conoce** quién llama..." | "conoce" is a slightly less natural choice than "sabe" here (Spanish idiom for "doesn't know who's calling" favors "saber"), minor style note, not a hard error. |
| `cc-032` | Equivalent to `qwen3.8:27b` (tense variant "has mirado" vs "miraste," both valid). | none of substance |
| `rrp-015` | Identical `text`; `teaches` reworded equivalently. | none |
| `img-058` | "La reproducción automática no es **engagement**—es asalto..." | **Left "engagement" untranslated** — an incomplete translation into the target language, the one thing the task instruction explicitly asked for. `qwen3.8:27b` correctly rendered it as "interacción." |

**Comparison-model score: 7/10 clean, 3/10 with a concrete defect** (`cc-022` meaning loss,
`img-029` grammar errors, `img-058` untranslated anglicism) **and 1/10 where it corrected the
primary model's error** (`img-071`).

**Conclusion: `qwen3.8:27b` remains the better default** on this pilot set — fewer and less severe
defects overall — which validates rather than merely assumes the plan's original choice of primary
candidate. `img-071` is the one case where a human reviewer drafting via the primary model should
consider re-running with `--model qwen2.5:32b-instruct` for a second candidate to compare, exactly
the workflow the duplicate-active warning (not hard-block) was designed to support.

---

## Honest assessment — why DONE and not PARTIAL

I considered PARTIAL seriously given the explicit instruction to call it out if failures mean the
model "isn't usable at scale yet," and I want the reasoning on record rather than asserted:

- **Against DONE:** `img-071` is a real, unambiguous semantic-fidelity failure, not a nitpick — a
  native Spanish reader would find "Coda con sabiduría" nonsensical in context. If this proposal
  were accepted without a human catching it, a wrong quote would enter the corpus.
- **For DONE:** S4′'s entire design (S0 decision 4, `AGENTS.md`'s non-negotiable rule) makes
  acceptance a separate, deliberate human act — nothing in this deliverable can put `img-071`'s
  draft into `ttod.yml` un-reviewed, and I confirmed this structurally, not just by policy. Judging
  "usable at scale" by whether *every single pilot output is flawless* would set a bar that would
  fail almost any small local model on genuinely idiomatic content, and would misjudge what this
  tool is for: reducing a human translator's from-scratch effort, not replacing their review. 9 of
  10 outputs were not merely acceptable but showed real translation judgment (the `img-007`
  Buddhist-pun preservation in particular would be a strong result even from a larger model).

**Verdict: DONE**, with `img-071`'s specific proposal (`21e4cc66-6c2a-4b10-b0dd-b764bff3f82e`)
explicitly flagged here as **not to be accepted as drafted** — a human reviewer should either
correct "Coda"→"Codifica" by hand before accepting, or prefer the `qwen2.5:32b-instruct` draft
(`e0f56eef-9a8e-440a-83e8-983075c199f1`) for that one quote instead.

---

## Discovered pre-existing gaps (not caused by S4′, flagged not fixed unless noted)

1. **Fixed (in scope, one line):** `cli.py`'s `proposal create` command called `create_proposal()`
   without importing it — a pre-existing `NameError` that made the *existing* `proposal create` CLI
   command crash on every invocation (confirmed by running it before my change). `ttod_core/
   repository.py` imports `create_proposal` privately; `cli.py`'s `from ttod_core.repository import
   ProposalStore, RepositoryError, TTODRepository` never re-exported it. Fixed by adding
   `from ttod_core.proposals import create_proposal` to `cli.py`'s imports — needed for
   `translate-draft` to use the same pattern correctly, and it happens to fix the pre-existing
   command too. Verified both commands work post-fix.
2. **Fixed (in scope, one line):** `ttod_core/repository.py::_build_quote_from_candidate()`'s
   curated optional-field pass-through tuple did not include `authorship_assertion` — meaning even
   though `quote.schema.json` has always had this field, a proposal's `candidate_content
   .authorship_assertion` was silently dropped at `proposal accept` time (the exact "unlisted field
   is silently dropped" class of bug S1′'s report already flagged for `bridge.py`). Added
   `"authorship_assertion"` to that tuple so the provenance S4′ is required to record actually
   survives into the canonical quote if/when a human accepts the draft. Confirmed via the full test
   suite (202/202 green) that this does not change behavior for any existing candidate that omits
   the field.
3. **Flagged, not fixed — confirmed live, blocks a real workflow step:**
   `TTODRepository.accept_proposal()` → `validate_candidate_content()` requires
   `candidate_content.validation.reviewer_id` to be truthy whenever `origin == "blackbox"` — but
   neither `cli.py proposal accept` nor `translate-draft` ever populates that field. Reproduced
   live: `PYTHONPATH=. .venv/bin/python cli.py proposal accept <a real translate-draft proposal_id>
   --reviewer-id test-human-reviewer --file <disposable>` → `ACCEPT FAILED: blackbox origin
   requires validation.reviewer_id before accept` (exit 1). This is **pre-existing**, not introduced
   by S4′ — the check is in code S4′ doesn't touch — but it was very likely never hit in practice
   before now because no other live CLI path produces `origin: blackbox` proposals by default
   (`proposal create` defaults to `studio`; `add` defaults to `human`). `translate-draft` is the
   first real producer of `blackbox` proposals through the CLI, so this is the first time the gap
   surfaces concretely. **This means a human cannot currently run `proposal accept
   --reviewer-id ...` on any S4′-drafted proposal without first hand-editing its JSON to add a
   `candidate_content.validation.reviewer_id` field** (or equivalent). I did not fix this: it touches
   the accept-transaction's human-gating logic directly, which I judged too consequential to change
   as a side effect of this task — the "right" fix (e.g. `proposal accept` auto-populating
   `candidate_content.validation` from its own `--reviewer-id` argument before calling
   `accept_proposal`) is a real design decision about the review contract, not a one-line pass-
   through fix like #1/#2 above. Recommending this as an immediate, small, separately-scoped
   follow-up — it currently blocks the very "next step" `translate-draft`'s own output tells the
   reviewer to take.
4. **Flagged, not fixed — does not block anything live:** `TTODValidator.validate_proposal()`
   rejects *every* freshly-created proposal (mine included, but also pre-existing ones from
   `proposal create`) because `Proposal.to_dict()` always emits `null` for unset optional fields
   (`wpl_record_id`, `wpl_record_digest`, `evidence_snapshot_id`, `evidence_snapshot_digest`) while
   `proposal.schema.json` types them as plain `"string"` with no `null` allowed. Confirmed this is
   pre-existing (reproduced with a minimal `create_proposal()` call carrying no S4′ code at all) and
   confirmed it does not block any live write path — `accept_proposal()` validates
   `candidate_content` via the separate Python-level `validate_candidate_content()`, never calls
   `TTODValidator.validate_proposal()` on the whole proposal object. Only exercised today by direct
   test-suite calls to `validate_proposal()`. Not fixed — a schema-vs-serialization decision (loosen
   the schema to allow `null`, or have `to_dict()` omit unset optional keys) belongs to whoever owns
   `proposal.schema.json`, not to this task.

---

## Files touched

| Path | Change |
| --- | --- |
| `ttod_core/translation.py` | **New.** Prompt building, Ollama call (`urllib`, stdlib only), response parsing, `find_active_translations()`, `build_translation_candidate()`. Zero import of `ttod_core.repository` — verified by test. |
| `cli.py` | Added `translate-draft` command (122 lines incl. help text); added the missing `from ttod_core.proposals import create_proposal` import (fixes pre-existing `proposal create` crash, see gap #1); added `translation` module imports. `add`, `proposal accept`, `proposal create`'s own body unchanged. |
| `ttod_core/repository.py` | One line: added `"authorship_assertion"` to `_build_quote_from_candidate()`'s pass-through tuple (see gap #2). No other change. |
| `tests/test_s4_translate_draft.py` | **New.** 26 tests: prompt/response parsing (7), `find_active_translations` (5), `build_translation_candidate` shape + structural id/status guarantees (3), source-level structural no-write-path proof (3), full CLI integration incl. fail-fast/duplicate-warn/happy-path/error-surfacing (8). |
| `docs/DEV_PLAN/PHASE-S-TTOD-BILINGUAL-CONTENT-MODEL.md` | Status line and Programme table's S4′ row only, updated to DONE with this report linked — did not touch the S3′ row or any other section (owned by the parallel effort). |
| `proposals/*.json` (gitignored, not committed) | 20 real pilot proposals (10 quotes × 2 models) plus fail-fast test artifacts, cleaned up before the final pilot run so the directory reflects exactly the pilot output. |

Not touched, confirmed: `.cursor/rules/ttod-editing.mdc`, `sources/*/README.md`,
`docs/DEV_PLAN/INDEX.md` (S3′ scope), `ttod.yml` (byte-identical sha256 throughout), any parked
source chapter, any bulk/backfill operation.

## Full test suite

```
PYTHONPATH=. .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
# Ran 202 tests in 2.346s — OK   (176 pre-S4′ + 26 new; 0 regressions, 0 skips)
```

## Resume point

S4′ is DONE. `cli.py translate-draft` is usable today for forward drafting (S0 decision 4's
forward-only scope — no bulk backfill was run or authorized). Before a human can actually complete
the `proposal accept` half of the workflow on a drafted `blackbox` proposal, gap #3 above needs a
small, separate fix (`proposal accept` should populate `candidate_content.validation` from its own
`--reviewer-id`, or an equivalent). `img-071`'s draft (`21e4cc66-6c2a-4b10-b0dd-b764bff3f82e`)
should not be accepted as-is. S3′ status is out of this report's scope — see
`PHASE-S3-REPORT.md` if filed. No bulk backfill of the 229-quote corpus was performed or
authorized; that remains a separate, explicitly-gated future decision per the phase document.
