<!--
Strand B programme map — one research line, three cases.
Author: Rubén Vega Balbás, PhD · drafted 2026-11-24 with AI assistance (Claude, Anthropic;
declared per DECLARACION-AUTORIA-ASISTIDA-POR-IA-ES.md). Owner review pending.
-->

# Strand B — programme map (TTOD · Neoplastix · ATELIER-IA)

**One line, three bounded cases.** Strand B asks whether taking part as a developer in a real
product built with agentic AI assistance, inside a cohort of peers, works as a learning activity
with observable outcomes. Each case keeps its own boundary, consent and corpus. None imports
another case's data as evidence. Strand A stays parked and is never evidence.

| | **Case 1 — TTOD** | **Case 2 — Neoplastix (Mondrian Project)** | **Case 3 — ATELIER-IA** (proposed) |
| --- | --- | --- | --- |
| Course | Front-End II, 2026–27, semester 1 | Front-End I, 2026–27, semester 1 | Front-End I, 2026–27, **semester 2** (React capstone) |
| Product | TTOD Oracle Platform (Astro + Svelte/React islands, FastAPI, FastMCP, Ollama, Redis) | Neoplastix — measured neoplastic studies (Astro 7, one Svelte island, SVG, Python analyzer) | React cohort product built on the transferable kit distilled from cases 1–2 |
| Cohort | 8 students, 5 teams/seams | 7 seats, 2 bachelors (FE I + AI & Data Science) | Same FE I students, semester 2 (n ≈ 7, to confirm) |
| Repo | `ruvebal/ttod` | `ruvebal/mondrian-project` | to create from the kit (no student data before resolution) |
| Live | Compose stack, classroom host pending (Phase AA) | `https://neoplastix.crea-comm.net` (static, 200) | preview environments during the pilot |
| Teaching state | Sprint + oral defence done (15 Oct 2026); post-defence merge train done (#88–#92) | Active: M0–M3 DONE; M4/M6/M8 open; M9 blocked | Not started (the call forbids starting before resolution) |
| Research state | Process traces exist; **analysis blocked** until grades closed + custody | M9 owns notice, custody, pseudonymisation, abstract | Innova EDU UDIT 2026-27 proposal: [`innova-edu-2026-27/`](innova-edu-2026-27/) |
| Case-specific RQ | RQ-B1–B4 ([`STRAND-B-PEDAGOGICAL-DESIGN.md`](STRAND-B-PEDAGOGICAL-DESIGN.md) §1) | "When the artefact is a measured study and the tempting failure is an AI-drawn Mondrian, which traces make authorship explainable?" (Mondrian `PITCH.md` §3) | RQ-C1–C3 below |

## Ethics position (applies to all three cases)

On **22 October 2026** the instructor reported the UDIT Research Ethics Committee's position on
Strand B: the committee **does not need to issue a dictamen**; the research goes ahead and the
committee is kept informed, under four conditions:

1. The department has accepted the practice as a teaching activity.
2. The students have accepted.
3. Students are anonymised in the research (`P01…Pn`).
4. Students are present as co-authors (opt-in byline, never linked to a pseudonym).

**The conditions are per cohort.** Acceptances given by case 1 do not carry over to case 2 or 3.

**Case 3 changes the instrument set.** Cases 1–2 use only ordinary coursework traces. Case 3 adds
pre/post questionnaires and an explain-the-code task. The committee's position covered no surveys,
so case 3 is **submitted to the committee again before recruitment** (the Innova call, §13.1, also
requires it and forbids retrospective ethics review). Planned for January 2027, after resolution.

> `INDEX.md` and `STRAND-B-PEDAGOGICAL-DESIGN.md` §10 said "review in progress" until 2026-11-24;
> both now point here.

## Shared instruments (the programme's spine)

| Instrument | C1 | C2 | C3 | Kind |
| --- | :-: | :-: | :-: | --- |
| PR with plan + AI Review Log (accept/reject/verify) | ✓ | ✓ | ✓ | coursework trace |
| Cold review before merge; human-only approve/merge | ✓ | ✓ | ✓ | coursework trace |
| Oral defence on one decision / one number | ✓ | ✓ | ✓ | coursework trace |
| AI-critical rubric: Defer · Narrate · Critique · Verify (8 signs, 0–2) | ✓ (draft) | ✓ (planned) | ✓ (two raters) | assessment aid |
| Explain-the-code task (code produced ≠ learning demonstrated) | — | — | ✓ pre/post | research instrument |
| Questionnaire: self-efficacy with AI + critical AI use | — | — | ✓ pre/post | research instrument |
| Pseudonymisation script (`git log` + PR export + declarations → `P01…Pn`) | to port | M9 | reuse | tooling |

## Case 3 research questions (ATELIER-IA)

- **RQ-C1** Does packaging the cohort method as a transferable kit reproduce, in a third course
  and level, the process traces seen in cases 1–2 (complete AI Review Logs, defended rejections,
  named verifications)?
- **RQ-C2** How does students' ability to explain and modify their own merged code change between
  the start and the end of the semester, and where does it diverge from what they shipped?
- **RQ-C3** Which parts of the kit (walking skeleton, lane assignment, cold review, AI Review Log,
  defence) do students and a second instructor rate as necessary, and which as overhead?

Claim ceiling: design principles and transferability limits. No causal "AI improves learning"
claim; small n, qualitative-dominant, pre/post as description, not inference.

## What "complete" means for each case (gap list)

| Gap | C1 TTOD | C2 Neoplastix | Owner |
| --- | --- | --- | --- |
| Grades closed and recorded in custody | Moodle entry pending (`AI-CRITICAL-USAGE-CONCLUSIONS` §5 checklist unticked) | at semester close | instructor |
| Signed acceptances in private custody | exists (custody log) | M0 draft → deliver | instructor |
| Department + ECSIT informed in writing | done for C1 | M0 private email | instructor |
| Committee informed the study is underway | C1 reply 22 Oct | inform when ready | instructor |
| Pseudonymisation tooling | port from C2 | M9 `scripts/pseudonymise.py` | M9 |
| Versioned codebook before analysis | to open `ethics/analysis/` (no PII) | M9 | instructor |
| Public deployment | AA7 + AA4 merge → AA6 → classroom host | live; kiosk device (M7) pending | instructor + department |
| Congress product | JENUI/ITiCSE drafts (`CONGRESS-ABSTRACTS-DRAFT.md`) | M9 abstract | instructor |

Resources for deployment, communication and congress presentation are requested from the
department separately: [`innova-edu-2026-27/SOLICITUD-RECURSOS-DEPARTAMENTO-ES.md`](innova-edu-2026-27/SOLICITUD-RECURSOS-DEPARTAMENTO-ES.md).

## Grounding state (2026-11-24)

A full neural-vector + Athanor + Ahmes cite-gate pass ran over AI × education × real projects ×
GitHub × curriculum. Eleven page-addressed, evaluator-safe sources now ground the ATELIER-IA memoria;
six cited works have no Ahmes vault yet, nineteen vaults fail the gate on metadata, and nine topics
have no source in the studio corpus (communities of practice, peer code review, studio-based
computing, GitHub in SE courses, DBR, validated pre/post scales, code-explanation tasks, vivas,
experiential learning). Ledger and enrichment list:
[`innova-edu-2026-27/GROUNDING-LEDGER.md`](innova-edu-2026-27/GROUNDING-LEDGER.md).

