<!--
Phase R0 report — TTOD Oracle Platform, Stage 1 (generate). No live implementation performed.
-->

# Phase R0 Report — generate R1–R7 runbooks (Stage 1: mold, not forge)

**Status:** DONE

**Scope executed:** exactly R0's Stage-1 job per
[`PHASE-R-TTOD-ORACLE-PLATFORM-CASCADE-PROMPT.md`](PHASE-R-TTOD-ORACLE-PLATFORM-CASCADE-PROMPT.md)
§0 and §11 — read the master document in full, verified Phase S's gate, verified the Ollama tag
assumptions, generated seven self-contained runbooks under `PHASES/`, updated `INDEX.md`. **No
container, dependency, `services/` directory, Dockerfile, or line of application code was
scaffolded.** No `ttod.yml`, `schema/*.json`, or `ttod_core/*.py` file was touched. No §13
research-track content was generated or referenced. Nothing was committed.

---

## 1. Documents read, in full, before generating anything

1. `docs/DEV_PLAN/PHASE-R-TTOD-ORACLE-PLATFORM-CASCADE-PROMPT.md` (1044 lines) — all 13 sections.
2. `docs/DEV_PLAN/PHASE-S-TTOD-BILINGUAL-CONTENT-MODEL.md` (its full "why revised" section, S1′–S4′
   programme, and master paste).
3. `docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md` (section headings) and
   `PHASES/Q3-atomic-repository-cli.md` in full, as the structural template.
4. `AGENTS.md` in full.
5. `docs/DEV_PLAN/INDEX.md` in full (before and after editing).

Also spot-checked (not in the mandatory reading list, but load-bearing for verifying claims rather
than trusting prose): `PHASE-S2-REPORT.md`, `PHASE-S4-REPORT.md`, `ttod_core/exporter.py`
(`_graph_nodes`/`_graph_edges`), `ttod_core/repository.py` (the blackbox-accept blocker), root
`.gitignore`, `pyproject.toml`, repo root listing.

## 2. §0.1 frozen decisions — confirmed still current, item by item

Verified against the live 2026-09-06-revision text (not re-litigated, per the master document's own
instruction) and, where a decision made a factual claim, verified against the live repository
rather than trusted from prose:

| Item | Status confirmed |
| --- | --- |
| 1. Audience/scale, instructor-first gate | RESOLVED — text unchanged, still internally consistent (7 students, R1/R2/R3a instructor-owned, R4/R5 two-owner split). |
| 2. Ollama placement, three tiers | RESOLVED in shape; the specific tag-availability sub-claims were re-verified live — see §3 below, one claim needed updating. |
| 3. Public deployment target (Scaleway, single `stg`) | RESOLVED — no contradicting evidence found. |
| 4. Testing strategy (R7, Testing Trophy stack) | RESOLVED — reused verbatim in R7's runbook. |
| 5. FE II Deliverable 1 alignment | RESOLVED — the "Phase R is a superset of Deliverable 1" framing is carried into every student-lane runbook's entry section. |
| 6. Bilingual content model prerequisite for R1 | RESOLVED, **and independently verified green** — see §4 below. This was the one item R0 was explicitly told to re-verify rather than trust (§0.1.6's own text, and the task's own instruction), so it got the most scrutiny. |
| 7. Repo placement | **See the judgment call below (§6.1) — the master document contains an internal contradiction on this exact item that is worth surfacing, not silently resolving.** |

No item required re-litigation of a settled decision. Item 6 required active re-verification
(commands run, not assumed) rather than passive re-reading, per the master document's own emphasis.

## 3. Ollama tag verification — actual `ollama list` output, and what changed

Command run during this R0 pass:

```
$ ollama list
NAME                           ID              SIZE      MODIFIED
qwen3.8:27b                    22130167c4c2    17 GB     5 days ago
nomic-embed-text:latest        0a109f422b47    274 MB    3 weeks ago
thessia-scholar-v3:latest      7ebfdd4a5149    34 GB     6 weeks ago
thessia-coder-v3:latest        c9d3e8a967ed    15 GB     6 weeks ago
thessia-sentinel-v3:latest     81729aeef23a    15 GB     6 weeks ago
qwen2.5:72b-instruct-q4_K_M    424bad2cc13f    47 GB     5 months ago
qwen2.5:32b-instruct           9f13ba1299af    19 GB     5 months ago
qwen2.5:3b                     357c53fb659c    1.9 GB    5 months ago
qwen2.5:7b                     845dbda0ea48    4.7 GB    6 months ago
llama3.2-vision:latest         6f2f9757ae97    7.8 GB    6 months ago
```

**Dev-tier (`qwen3.8:27b`) — CONFIRMED, matches the master document's claim exactly.** Present,
17 GB, matches the document's own description ("27.3B params... `Q4_K_M` quant"). No action needed;
R1/R2's runbooks hardcode nothing here anyway (env-var driven), but the tag is real and pullable
from this host if it ever needs re-pulling elsewhere.

**Embedding model (`nomic-embed-text`) — CONFIRMED present.** 274 MB, matches R2's runbook's
assumption. Good for R2's retrieval-confidence pipeline.

**Light-tier model — STILL NOT CONFIRMED, exactly as the master document already flagged, with one
new detail worth recording.** Neither `llama3.2:1b` nor `qwen2.5:1.5b` appears in the list above.
**New detail this R0 pass adds:** `llama3.2-vision:latest` is present — this is a **different**
model (a vision-capable variant, ~7.8 GB) from the required `llama3.2:1b` text model, and must not
be mistaken for it by a future session skimming `ollama list` output quickly. This is exactly the
kind of near-miss the master document's own §0.1.2 warns about ("do not treat 'the tag is named in
this document' as equivalent to 'the tag is available'") — worth naming explicitly since
`llama3.2-vision` and `llama3.2:1b` share a family prefix and could be conflated at a glance.

**Consequence carried into the generated runbooks:** R2's, R3a's, and R6's runbooks all restate,
explicitly, that the light-tier tag must be pulled as part of compose bring-up
(`ollama pull llama3.2:1b` or `qwen2.5:1.5b`, one chosen as default) — none of them assume it is
already present. This was already the master document's instruction; R0 changes nothing here
except re-confirming the gap is still real as of this pass and adding the `llama3.2-vision`
near-miss note above.

## 4. Phase S gate (§0.1.6) — independently verified, not trusted from prose

Commands run during this R0 pass, against the live repository:

```
$ python cli.py validate --strict --json
{"is_valid": true, "errors": [], "warnings": []}   # exit 0

$ python cli.py stats
Total quotes: 229
...
By language (derived from quote lang; never hardcoded):
  en: 229
```

**Both S1′ and S2′ are confirmed green.** `validate --strict` exits 0 with zero errors/warnings;
`stats` shows a real, non-null per-language breakdown (`en: 229`, matching `PHASE-S2-REPORT.md`'s
own migration-completion count). This satisfies R1's precondition gate (§0.1.6) as of this pass.

Also spot-checked and confirmed still live in code (relevant to R1's `oracle/propose` scope,
§3.1 of the master document): `ttod_core/repository.py` lines 266–267 still raise
`RepositoryError("blackbox origin requires validation.reviewer_id before accept")` for every
`origin: blackbox` proposal, and `Exporter._graph_nodes()` (lines 137–150) now includes `lang` in
its projection, exactly as `PHASE-S1-REPORT.md` claims. Both facts are carried into R1's, R4's, and
R5's generated runbooks accurately (the accept-blocker as an explicit, honestly-stated known gap;
the graph-node `lang` field as a confirmed-real contract field).

Full test suite: `python -m unittest discover -s tests -p 'test_*.py'` → **204 tests, OK**. (Note
for future sessions: `AGENTS.md` still says "161 tests (Phase Q closeout)" — that count is stale,
grown by Phase S's own added fixtures/tests; not fixed here, out of R0's scope, but worth a
housekeeping note since a stale count in a rules file is exactly the kind of drift this project
otherwise disciplines itself against.)

**Conclusion: R1's precondition gate is genuinely satisfied, with live evidence, not a stale
claim carried forward.** R1's runbook states this plainly and tells the next session to re-verify
it again themselves before starting (§2 of `R1-backend-bridge.md`) rather than trusting this
report indefinitely.

## 5. Generated runbooks

All seven, under `docs/DEV_PLAN/PHASES/`, one per row of the master document's §6 table:

| File | Owner | Mode |
| --- | --- | --- |
| `PHASES/R1-backend-bridge.md` | **Rubén (instructor)** | sequential, walking-skeleton triad |
| `PHASES/R2-fastmcp-server.md` | **Rubén (instructor)** | sequential, walking-skeleton triad |
| `PHASES/R3a-walking-skeleton.md` | **Rubén (instructor)** | sequential, walking-skeleton triad — this phase's own exit **is** the cohort-start gate |
| `PHASES/R3b-astro-content-engine.md` | student, 1 owner | depends on cohort-start gate, not R3b→R4/R5 |
| `PHASES/R4-svelte-graph-island.md` | student, 2 owners | depends on cohort-start gate (R1+R3a), not R3b |
| `PHASES/R5-react-oracle-terminal.md` | student, 2 owners | depends on cohort-start gate (R1+R2+R3a), not R3b |
| `PHASES/R6-pwa-cicd-audit.md` | student, 1 owner | depends on R3b **and** R4 **and** R5 all DONE |
| `PHASES/R7-testing-strategy.md` | student, 1 owner | **continuous** from cohort-start gate onward; closing report only after R3b/R4/R5 DONE |

Each runbook restates inline (verified by construction while writing, not just claimed): its
entry/exit gates (§6/§7 of the master document), its slice of §2's non-negotiable boundaries
including the full §2.4 secrets-discipline section, its slice of §4's domain contract, §8's
rollback law, §6.1's cold-review requirement, §12.1's status enum, and a paste-ready standalone
agent prompt. Confirmed via `grep` that none of the seven reference `docs/research/`, Ahmes,
Athanor, Profield, or ADK — one near-miss was caught and fixed during this pass (§6.2 below).

R1, R2, and R3a are explicitly marked instructor-owned in their own headers and bodies, not just in
`INDEX.md`. R3b/R4/R5 explicitly state they depend on the cohort-start gate and **not** on R3b
finishing first for R4/R5 (the master document's own dependency-graph nuance, restated so a runbook
reader doesn't have to re-derive it from the mermaid diagram). R7's runbook opens with an explicit
"this is continuous, not terminal" framing before any other content, per the task's own emphasis.

## 6. Judgment calls and open questions — surfaced explicitly, not silently decided

Per the master document's own closing instruction ("this document has already been cold-reviewed
once today specifically to close ambiguities before R0 runs, so a genuinely new one you find is
worth surfacing clearly, not guessing past"), four items below required a call this report is
flagging rather than treating as self-evidently settled.

### 6.1 A real contradiction in the master document: §0.1.7 vs. §11's prompt text

`§0.1` item 7 is headed **"Repo placement — closed"** and states the decision content plainly
(platform lives inside `ttod/`, `services/`/`caddy/`/root `docker-compose.yml`, no satellite repo).
`§3`'s system-architecture section separately resolves the one sub-ambiguity that item's own text
left open (in-process import vs. subprocess shell-out — resolved: in-process). By the time a reader
reaches §11, item 7 reads as fully closed on every axis.

**But §11's own paste-ready generator prompt text says:** *"Item 7 (repo placement) is still open;
ask the product owner rather than guessing if it matters for the runbook you are about to write."*

This is a direct contradiction between two parts of the same document, most plausibly a leftover
from before the 2026-09-06 revision that updated §0.1.7 to "closed" without also updating §11's
prompt text to match. **This R0 pass resolved it by treating §0.1.7's explicit "closed" status —
and §3's entire system-architecture section, which is built directly on top of that decision as
settled fact — as authoritative**, since §0.1.7 is more specific, more recently revised in
substance, and is what every other section of the document (including the mermaid diagram in §3
and the entire endpoint/domain-contract design in §3–§4) already assumes without qualification.
Treating item 7 as still-open would have meant not generating any runbook at all, which
contradicts the document's own §6 table and mermaid dependency graph existing and being fully
fleshed out.

**Recommendation, not silently acted on:** the master document's §11 prompt text should be edited
to drop the "item 7 is still open" sentence, or updated to note it was resolved in §0.1.7/§3. This
report flags it; it does not edit the master document itself (out of R0's scope — R0 generates
runbooks and this report, it does not amend the master document).

### 6.2 §13 near-miss, caught and fixed during generation

R2's runbook initially cited `ahmes/.cursor/skills/profield-ahmes-athanor/SKILL.md` as precedent
for choosing `nomic-embed-text` — a citation the master document's own §3 item 4 makes for a
legitimate, non-§13 engineering reason (establishing that this embedding model is already the
studio standard). But the task's constraint against referencing Ahmes/Athanor/Profield in any of
the seven runbooks is unqualified, so this citation was removed from `R2-fastmcp-server.md` during
this pass, keeping the substantive point (nomic-embed-text is the studio-standard embedding model,
confirmed pulled locally) without the specific path reference. Verified via `grep` afterward — zero
matches for `ahmes|athanor|profield|google.adk|docs/research|research-designer` across all seven
runbooks.

### 6.3 Embedding-model env var — a genuine gap in the master document's own rule, resolved one way, flagged

§2.2 of the master document states "no runbook may hardcode a model tag" in the context of the
three-tier chat model, but §3 item 4 names `nomic-embed-text` directly in prose rather than through
an env var. R2's runbook resolves this the same direction as the rest of the document — a new
`OLLAMA_EMBED_MODEL` env var, defaulting to `nomic-embed-text` in `.env.example` — and states this
explicitly as an interpretation choice in R2's own §2.2, not a silent decision. If the product owner
intended `nomic-embed-text` to be a genuinely fixed, non-configurable choice, reverting this is a
one-line change to `.env.example`'s default, not a design change to R2's runbook.

### 6.4 Two decisions explicitly deferred to whoever executes R3a/R6, not resolved by R0

Two points the master document itself says must be "confirmed before generating R6's runbook" /
decided at build time were **not** resolved by R0 (R0 is documentation-only and has no standing to
make an architecture call the product owner reserved for implementation time):

- **Local/Lilith Caddy TLS profile** (bare `8080`/`8443` no-TLS vs. sitting behind the studio's
  existing `*.crea-comm.loc` mkcert pattern) — the master document's §3 explicitly says "confirm
  which before generating R6's runbook, don't assume." R0 could not get real-time product-owner
  confirmation during a documentation-only generation pass, so `R3a-walking-skeleton.md` (§2.2)
  states this as an open decision R3a's own executor makes and records, defaulting to the simpler
  bare-port profile absent a stated reason otherwise, and `R6-pwa-cicd-audit.md` reads R3a's
  recorded choice rather than re-deciding it.
- **Which light-tier model tag (`llama3.2:1b` vs. `qwen2.5:1.5b`) is the actual default** — the
  master document says "pick one... document the choice," without picking on its own behalf. R0
  left this to R2/R3a's actual build session (both runbooks say so explicitly) rather than guessing
  a default that this documentation-only pass has no way to test.

Neither of these blocks R0 from being complete — both are legitimate implementation-time decisions,
not planning gaps — but naming them here means the next session doesn't have to re-discover that
they're open.

## 7. INDEX.md update

`docs/DEV_PLAN/INDEX.md`'s Phase R row updated: state changed from "PROPOSED — no runbooks
generated yet, no code written" to reflect R0 DONE (seven runbooks listed, links added), while
explicitly preserving **"Phase R status remains PROPOSED at the platform level"** — no container
built, no `docker-compose up` run, R1/R2/R3a not yet executed. This distinction (R0 sub-phase DONE
vs. Phase R overall still PROPOSED) is stated as its own sentence in `INDEX.md` so a future reader
skimming only the status column cannot misread "R0 DONE" as "Phase R DONE."

## 8. Explicit non-claims (per the task's own hard constraint)

This report does **not** claim: Phase R has "started" in the implementation sense: no container,
service, or line of application code exists. Any of R1–R7 is DONE — all seven are freshly generated
runbooks with no execution yet. The cohort-start gate is open. Any Scaleway deploy decision record
exists (it doesn't — checked, absent from `docs/DEV_PLAN/DECISIONS/`, which currently holds only
the Q0 rights/license and S0 bilingual-content decision files).

## 9. Resume point

**R0 is DONE.** Per the master document's own §12.2 resume rule: resume at R1/R2/R3a — the
instructor-owned walking skeleton — before any student lane, regardless of what else looks READY.
All three are logically independent of each other (each depends only on R0) and may be worked in
any order or in parallel by the same owner (Rubén), but the cohort-start gate needs all three
`DONE` together before R3b/R4/R5/R7 may begin, and R6 additionally needs R3b+R4+R5 all `DONE`.

**Concretely, READY next:** `docs/DEV_PLAN/PHASES/R1-backend-bridge.md`,
`R2-fastmcp-server.md`, and `R3a-walking-skeleton.md` — each is self-contained and independently
paste-ready (§13 of each runbook — actually §13 in R1, §12 in R2, §12 in R3a; the closing
"Agent prompt" section of each file). R1's precondition gate (Phase S S1′+S2′) is confirmed
satisfied as of this report (§4 above) — the next session executing R1 should still re-verify it
personally per that runbook's own §2, not trust this report indefinitely, since time may have
passed and `ttod.yml`/`schema/` could have changed.

No student lane (R3b, R4, R5, R6, R7) should be started until `PHASE-R1-REPORT.md`,
`PHASE-R2-REPORT.md`, and `PHASE-R3a-REPORT.md` all exist and say `DONE`.
