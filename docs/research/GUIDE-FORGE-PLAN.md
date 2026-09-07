# TTOD research and guide-forge plan

**Status:** PROPOSED — planning artifact only; no guides generated  
**Date:** 2026-09-05 (audited 2026-09-05; enriched against verified Athanor evidence 2026-09-06)  
**Owner:** Rubén Vega Balbás, PhD  
**Engineering baseline:** Phase R reference build exists; the student handoff is R1/R2/R3a and
R6 remains student-owned.

## Launch readiness, as of 2026-09-07

**T0–T3 and the T5 institutional pitch lane are DONE; T4 is PARTIAL.** T0 froze commit `8e73116299d29dd78b59f1717283f39eaca5fcea`
and produced the claim registry, contradiction register, and cold-audited report under
`docs/research/guides/`. T1's evidence base is real and already substantial (see §4's
verified vault check below) — this is no longer a plan that assumes literature discovery will
work; it has been checked. **T3 is closed as documentation; T4 has a drafted guide but remains
partial until the final distribution artifact passes the history-isolation test.** T5 was launched
only for decision-facing drafts, after T0/T2 supplied their contracts.
**T6 stays correctly `BLOCKED`** — no institutional inputs have been supplied. **The full
`PROMPT-FORGE-TTOD-GUIDES.md` generator is not yet launched** — launching it is Rubén's decision,
this section only reports what would and would not go smoothly if it were.

## 1. Honest maturity verdict

TTOD is mature as an **engineering object and documented teaching design**, but not yet mature as
an approved research study.

| Layer | Current maturity | Evidence | Next gate |
| --- | --- | --- | --- |
| Governed TTOD data/tooling | operational | Phase Q reports and repository tests | maintain invariants |
| Oracle reference architecture | validated reference implementation | Phase R R1–R5 reports and cold reviews | finish only work authorized by the R6 decision |
| Student development task | planned as implementable from a walking skeleton | R6 decision, generator script, R3a onboarding, and `PHASE-R-CLOSURE-AND-COHORT-HANDOFF-REPORT.md` (filed 2026-09-05 — the index no longer references a missing artifact) | the closure report's own distribution advice is unverified against §2's isolation requirement below — cold-read a clean clone of whatever artifact students actually receive, not the local `cohort-starter` branch, before treating this row as closed |
| Research design | substantial pre-protocol | `RESEARCH-LINE.md`, `COHORT-CASE-PROPOSAL.md`, Phase R §13; **verified 2026-09-06:** 46 docs / 23,798 nodes already injected in `profield-frontend-pedagogy` (§4 T1 readiness) | co-investigator, ethics/data-protection review, and one targeted literature gap (teacher-researcher-conflict/ethics cluster, confirmed empty — see T1) |
| Research operation | not authorized | no approved consent or data-management protocol | approvals before any student artifact becomes research data |
| Audience guides | not yet designed as a coherent set | technical and research documents exist, but not an audience-separated guide family | run this plan |

So this is more than a sketch: it has research questions, a methodology, an asset inventory, an
ethics risk register, a consent taxonomy, and a venue ladder. It remains **pre-pitch and
pre-collection**. No effect, novelty, institutional approval, or participant-data claim is mature.

## 2. One project, two explicitly separated phases

Every generated introduction must describe the same project in this order:

1. **The development as a research object.** TTOD studies a documented, AI-assisted,
   cold-review-gated front-end development process. This layer explains the research gap,
   questions, theoretical framing, process evidence, limits, ethics, and approval state. It does
   not turn ordinary coursework into research data by declaration.
2. **The front-end build as the immediate teaching task.** Students receive a working local
   walking skeleton and build the remaining application through the course deliverable. They run
   it on their own laptop or university-lab machine. Tanit and Lilith are Rubén's private studio
   infrastructure and are never presented as student services.

The phases are linked but not mutually gating: teaching and software development may proceed
without research approval; research use of student-produced evidence may not.

**A third boundary, distinct from both and easy to miss:** GitHub reports `ruvebal/ttod` as a
**private** repository with `main` as its default branch (verified with `gh repo view` on
2026-09-05), and the local clone has one shared `origin`. The reference build
(R3b/R4/R5/R7, `main`) and the student handoff (`cohort-starter`) currently live as two branches
of that same remote-to-be. Pushing `cohort-starter` to that `origin` — the exact command the
closure report proposes — does **not** isolate it: any student with clone/fetch access to the
same repository can run `git log --all` or `git fetch origin main` and read the finished reference
implementation the cohort is meant to build themselves. This is not a hypothetical; it is true the
moment students receive access to a repository containing both branches. Treat "students never see the
reference build" as unmet until the actual distribution artifact is verified to carry no
`main`-reachable commits — see T4's gate below.

## 3. Guide family: one primary audience per document

Do not make one omnibus manual. Generate a shared claim registry first, then these documents:

| Document | Primary audience | Required job | Research content |
| --- | --- | --- | --- |
| `MAINTAINER-GUIDE.md` | Rubén / future maintainer | operate, verify, release, recover, and maintain the teaching/reference split | full internal status and decision gates |
| `STUDENT-DEVELOPER-GUIDE.md` | FE II student developer | clone the cohort starter, run locally, understand R1/R2/R3a, implement assigned work, test, review, and defend it | brief project rationale; no implication that participation in research is required |
| `END-USER-GUIDE.md` | person using TTOD Oracle | navigate quotes, languages, graph, docs, and oracle safely | no methodology dump; concise AI/rights limitations |
| `DEPARTMENT-DECISION-BRIEF.md` | head/degree coordination | decide educational fit, workload, resources, and authorization path | bounded case-study proposal and risk/benefit summary |
| `PI-RESEARCH-BRIEF.md` | principal investigator / co-investigator | assess contribution, design validity, evidence, roles, ethics, and publication path | full research design with claim-strength labels |
| `PITCH-INVESTIGACION-TTOD-ES.md` | Spanish-speaking research evaluators, department leadership, and research-group PI | evaluate the project through an Excellence–Impact–Implementation argument and decide whether to sponsor protocol development | Spanish evaluator-facing synthesis; no call, funding, or eligibility claim |
| `PARTICIPANT-INFORMATION-SHEET.md` | potential student participant | understand voluntary participation and data use | **HOLD:** generate only after institutional and data-protection requirements are supplied and independently reviewed |

“Student developer” and “research participant” are different roles. Course access, assessment,
grading, repository access, and software use must never depend on research consent.

## 4. Studio technology to plug in

Use the tools in this order:

1. **Athanor discovery + Ahmes verification** — search only the
   `profield-frontend-pedagogy` project first. Read the full Ahmes page for every retained result,
   resolve its citation key, and admit it as an ordinary citation only when
   `evaluator_safe=yes`. Otherwise emit `[BIBLIO-GAP]`; do not repair metadata by intuition.
   **T0 correction (2026-09-06):** both relevant skills exist and their responsibilities differ.
   Use the shared `~/.codex/skills/ground-with-athanor-ahmes/SKILL.md` for claim grounding,
   page-level verification, evaluator-safe citation resolution, and `[BIBLIO-GAP]` discipline.
   Consult `~/src/ahmes/.cursor/skills/profield-ahmes-athanor/SKILL.md` only when operating the
   Profield→Ahmes→Athanor ingestion pipeline. Do not substitute the ingestion skill for the
   grounding skill. Also:
   `athanor project list` / `athanor search` fail in a fresh shell with
   `fe_sendauth: no password supplied` — the CLI's `.env` (`DATABASE_URL=…${PG_PASSWORD}…`) is not
   auto-loaded and `PG_PASSWORD` is not set anywhere in this environment. Until that's fixed
   upstream, verify/discover directly against the running `deviac-postgres` container instead
   (same pattern `scripts/phase_p4_preflight.sh` already uses):
   ```bash
   docker exec deviac-postgres psql -U deviac -d athanor -tAc \
     "SELECT file_name, node_count FROM injections i JOIN projects p ON p.project_id = i.project_id
      WHERE p.slug = 'profield-frontend-pedagogy' ORDER BY file_name;"
   ```
   This lists titles only (discovery-grade) — it is **not** a citation source; still resolve each
   candidate through `ahmes query --cite` before treating it as evaluator-safe, per this section's
   own rule above.
2. **`documentation-forger`** — define one primary audience, document class, claim ownership,
   maintenance triggers, and runnable acceptance tests per document.
3. **`user-guide-forger`** — forge maintainer, student-developer, and end-user guides from
   verified repository behavior. Apply the CPSC comprehension axis as an editorial aid only; its
   current studio-library citation is a `[BIBLIO-GAP]` until evaluator-safe resolution exists.
4. **`student-ai-guide-forger`** — contribute the AI-use, authorship, disclosure, process-log,
   and oral-defense sections of the student guide. It does not own the entire guide.
5. **`pitch-forger`** — borrow only its accuracy, disclosure, venue-currentness, and
   non-invention discipline for institutional briefs. It is not itself a department-approval
   template.
6. **MSCA structural source** — for the Spanish research pitch, read the local
   `/Users/ruvebal/src/MSCA/SVCM/.cursor/skills/msca-proposal-forge/SKILL.md`, its “holy trinity,”
   and the canonical 2026 Part B template at
   `/Users/ruvebal/src/MSCA/SVCM/reference/horizon-europe/part-b-template.md`. Reuse its
   evaluator logic, not PROVENARCH content, identities, confidential material, host facts, or
   fellowship claims. Preserve the official weighting as an editorial allocation guide:
   Excellence 50%, Impact 30%, Implementation 20%. Record the template version and access date.
7. **`cascade-forge`** — orchestrate the work as gated, resumable lanes with reports and cold
   review. It generates documents; it does not change research status by writing `DONE` in prose.

No guide may expose Athanor/Ahmes database paths, node identifiers, internal project metadata, or
studio credentials. Public and student outputs contain resolved citations only.

## 5. Cascade

Use the closed states `PENDING | IN_PROGRESS | PARTIAL | BLOCKED | DONE`.

### T0 — Baseline and contradiction register — `DONE` (2026-09-06)

Outputs: [`guides/CLAIM-REGISTRY.md`](guides/CLAIM-REGISTRY.md),
[`guides/CONTRADICTION-REGISTER.md`](guides/CONTRADICTION-REGISTER.md), and
[`guides/T0-REPORT.md`](guides/T0-REPORT.md).

- Freeze git revision and read Phase Q, Phase R, the R6 decision,
  `PHASE-R-CLOSURE-AND-COHORT-HANDOFF-REPORT.md` (now filed), and all `docs/research/` files.
  Record a referenced-but-missing report as a gap; never silently treat its link text as evidence.
- Reconcile current facts before drafting. **Resolved by T0, retained here as audit history:**
  `COHORT-CASE-PROPOSAL.md` §7's calendar row — "Sep–Oct 2026 | Cohort builds R3b–R7" — reads as
  the cohort producing R3b/R4/R5/R7 as fresh work, but those phases already exist as a
  reference/architectural-validation build on `main`, completed before any cohort start. The
  cohort's own graded R3b–R7 is a separate, independent build from the `cohort-starter` handoff,
  not a continuation of the reference build — reword, don't just cross-reference, everywhere this
  ambiguity recurs (`RESEARCH-LINE.md` §1's "asset inventory" row and `overview.md`'s kickoff
  letter carry the same phrasing).
- **Second contradiction, wording resolved but evidence gate still open:** research
  document asserts students never see the reference build, but no verified mechanism currently
  guarantees that — see the shared-`origin` finding in §2 above. Record this as
  `pending evidence`, not `verified`, until T4 tests it.
- Produce a claim registry with `verified | interpretive | pending evidence | obsolete` labels.
- Gate: no unresolved contradiction may enter two documents with different wording.

### T1 — Evidence and protocol maturity audit — `DONE` (2026-09-07)

Outputs: [`guides/EVIDENCE-LEDGER.md`](guides/EVIDENCE-LEDGER.md),
[`guides/BIBLIO-GAPS.md`](guides/BIBLIO-GAPS.md), and
[`guides/T1-REPORT.md`](guides/T1-REPORT.md).

- Refresh the Athanor literature discovery for DBR, studio/project-based computing education,
  metacognitive AI scaffolding, process artifacts, oral defense, authorship, and small-cohort case
  study limits.
- Verify retained evidence through Ahmes page text and citation resolution.
- Separate literature claims from TTOD repository observations and proposed design principles.
- Produce an evidence ledger and `[BIBLIO-GAP]` register.
- Gate: no submission-facing claim rests on vector-search snippets alone.

**T1 discovery baseline, verified 2026-09-06 (titles only — discovery-grade, not yet
evaluator-safe citations):**
`profield-frontend-pedagogy` already holds **46 documents, 23,798 nodes, 31,251 entities**, all
`status: completed`. This is not a cold start — a real, thematically strong candidate pool exists
per §3's research episteme:

| RESEARCH-LINE.md topic | Candidate title(s) already in the vault |
| --- | --- |
| Design-based research | "Applying the design-based learning model to foster undergrad…" (`10.1186/s41239-021-00308-4`) |
| Studio/project-based computing education | Nelson & Ponciano, "Experiences and insights from using GitHub Classroom to support Project-Based Courses" (2021); Garcia, "Self-Coded Digital Portfolios as an Authentic Project-Based Learning Assessment in Computing" |
| Front-end/web pedagogy under generative AI | "The Effects of GitHub Copilot on Computing Students' Programm…" (`10.1145/3702652.3744219`); Kazemitabaar et al., "CodeAid classroom deployment" (CHI 2024) |
| Metacognitive/deferred AI scaffolding | Singh et al., "Hint-Writing with Deferred AI Assistance" (arXiv 2604.19931, 2026) — names RQ1's "deferred assistance" mechanism directly; Liu, Fan & Pan, "Tool, tutor, or crutch? A grounded theory of cognitive scaffolding and offloading" + its published correction; Phung et al., "Plan More, Debug Less" (AIED 2025) |
| Process artifacts / AI-use disclosure / academic integrity | González-Videgaray et al., "GenAI academic integrity" (2026); Digital Education Council, "AI in Higher Education LATAM Survey" (2026) |
| AI-resilient assessment (relevant to RQ4/oral defense) | "Designing AI-resilient assessment in higher education" (`10.3389/frai.2026.1841682`) |
| Web-architecture framing for the platform itself (not RQ evidence, but citable context for "islands"/resumability language) | "Resumability: A New Primitive for Developing Web Applications" (`10.1109/ACCESS.2024.3352891`); "Potential of Serverless Edge-powered Islands for Web Development" (`10.13052/jwe1540-9589.2411`) |
| Accessibility-in-teaching (ASSETS venue fit, §6 of `RESEARCH-LINE.md`) | "Teaching Digital Accessibility in Computing Education"; "Digital Accessibility Literacy: A Conceptual Framework" |

**Honest gap, checked and confirmed empty, not assumed:** no injected title matches
teacher-researcher conflict, consent, or research-ethics literature (`file_name ILIKE
'%conflict%'/'%consent%'/'%ethic%'` against the vault returns zero rows). This is the risk register's
own 🔴 top item (`RESEARCH-LINE.md` §5) — T1 needs either a fresh, targeted Athanor injection for
this cluster specifically, or an explicit human literature contribution; do not let the vault's
general richness elsewhere paper over this one real absence. T1 retained only sources that later
passed `ahmes query --cite --require-evaluator-safe`; see the evidence ledger and gap register.

### T2 — Shared information architecture — `DONE` (2026-09-07)

Output: [`guides/INFORMATION-ARCHITECTURE.md`](guides/INFORMATION-ARCHITECTURE.md).

- Define the canonical two-phase introduction, vocabulary, audience matrix, link graph, claim
  homes, and maintenance triggers.
- Specify what each audience needs, what it must not receive, and the reading order.
- Gate: every claim has one canonical home; all other occurrences link or summarize consistently.

### T3 — Operational guide lane — `DONE` (2026-09-07)

- Outputs: [`MAINTAINER-GUIDE.md`](MAINTAINER-GUIDE.md), [`END-USER-GUIDE.md`](END-USER-GUIDE.md), and [`guides/T3-T4-REPORT.md`](guides/T3-T4-REPORT.md).
- Forge `MAINTAINER-GUIDE.md` and `END-USER-GUIDE.md`.
- Verify every command, route, port, environment variable, failure mode, and recovery instruction
  against the checked-out repository or a clearly labelled fixture.
- Gate: a cold reader can complete the guide goal without hidden studio knowledge.

### T4 — Student developer lane — `PARTIAL` (2026-09-07)

- Output: [`STUDENT-DEVELOPER-GUIDE.md`](STUDENT-DEVELOPER-GUIDE.md), with the state report in [`guides/T3-T4-REPORT.md`](guides/T3-T4-REPORT.md).
- Forge `STUDENT-DEVELOPER-GUIDE.md` from a clean generated cohort-starter checkout, not `main`.
- Explain the hello-world-to-live-quote path before assigning later work.
- Add explicit AI-use declarations, decision/process evidence, review protocol, and oral defense.
- **Verify git-history isolation before writing anything that claims it.** From whatever artifact
  a student will actually clone (not the local `cohort-starter` branch inside this working
  repository), run `git log --all --oneline` and `git branch -a` and confirm no commit reachable
  from `main`'s reference build (R3b/R4/R5/R7 content) appears. If the distribution plan is "push
  `cohort-starter` to the same instructor/reference `origin`," this check **fails** — that plan needs an orphan
  export or a separate repository/template instead. Do not write "students cannot see the
  reference build" in any guide until this command has actually been run against the real
  artifact and produced a clean result.
- Gate: local-only setup is verified; Tanit/Lilith are absent except in a “not part of your path”
  clarification; research participation is never a condition of coursework; git-history isolation
  is verified, not assumed.

### T5 — Institutional lane — `DONE` for initial briefs and Spanish pitch (2026-09-07)

Outputs: [`DEPARTMENT-DECISION-BRIEF.md`](DEPARTMENT-DECISION-BRIEF.md),
[`PI-RESEARCH-BRIEF.md`](PI-RESEARCH-BRIEF.md),
[`PITCH-INVESTIGACION-TTOD-ES.md`](PITCH-INVESTIGACION-TTOD-ES.md), and
[`guides/T5-REPORT.md`](guides/T5-REPORT.md). This is a draft-and-audit state only; no
institutional approval is implied.

- Forge separate department and PI briefs; never collapse their decision needs into one pitch.
- The department brief asks for an educational/operational decision. The PI brief asks for
  methodological critique, co-investigator roles, evidence refinement, and ethics/data custody.
- Forge `PITCH-INVESTIGACION-TTOD-ES.md` in Spanish as a third, distinct artifact.
  It must begin with a short evaluator-oriented synopsis and follow this adapted structure:
  **1 Excelencia** (problem, objectives, state of the art, ambition, methodology,
  interdisciplinarity, diversity relevance, open science); **2 Impacto** (scientific,
  educational/institutional and societal outcomes; target groups; dissemination, exploitation,
  communication and intellectual-property/rights posture); **3 Calidad y eficiencia de la
  implementación** (work packages, tasks, deliverables, milestones, dependencies, effort, risks,
  governance, ethics/data custody, and institutional capacity still to be confirmed).
- Translate the evaluation logic, not the MSCA application fiction. Sections specific to a
  Postdoctoral Fellowship—fellow eligibility, researcher career development, two-way knowledge
  transfer, named host capacity, supervisor track record, secondments and placements—must be
  omitted, explicitly marked not applicable, or reframed only where TTOD has verified analogous
  facts. Never invent a host, call, budget, duration, TRL, partner, approval, or funding status.
- Use the T0 claim IDs and T1 evidence ledger. Spanish prose may translate a verified claim but
  may not strengthen it. Keep `[BIBLIO-GAP]` material out of evaluator-facing assertions.
- Include a final **decisión solicitada**: authorization/support to mature the protocol and its
  institutional safeguards, not retroactive approval of research already conducted.
- Gate: all three documents say “proposal” until real approvals exist, include explicit
  non-claims, serve distinct reader decisions, and pass an MSCA-structure compliance check plus
  native-quality Spanish editorial review.

### T6 — Participant-information hold (downstream, conditional)

- Remain `BLOCKED` until the institution's required template, controller/contact, lawful basis,
  retention schedule, withdrawal procedure, co-investigator custody, and approval route are known.
- Then draft for independent human/legal review; never let an agent self-approve it.

### T7 — Concordance and cold review (after T3–T5; T6 optional)

- Run link, command, route, terminology, privacy, citation, and audience-leak checks.
- Cold-read each document with a reviewer who did not draft it.
- Check that research status, R6 ownership, local student deployment, dates, licenses, and AI
  disclosure agree everywhere.
- Gate: issue a report with evidence and safe resume points; only verified documents become DONE.

## 6. Acceptance criteria

The guide programme is ready to execute when:

- the T0 claim registry names the current engineering and research truth;
- all ordinary scholarly citations have passed Ahmes evaluator-safe resolution;
- each guide has exactly one primary audience and a measurable reader goal;
- student development and research participation are visibly independent;
- course instructions are verified against the generated cohort-starter artifact;
- the actual student-facing distribution artifact has been checked for reference-build git
  history (§2, T4) and found clean — not merely planned to be clean;
- institutional documents contain requests, risks, responsible roles, and non-claims;
- the Spanish MSCA-structured pitch covers Excellence, Impact, and Implementation without
  presenting TTOD as an MSCA submission or inventing fellowship-specific facts;
- no private studio endpoint is offered to students;
- no guide invents approval, consent, evidence, commands, routes, or capabilities; and
- reports preserve `PARTIAL` or `BLOCKED` honestly when a gate is unmet.

## 7. What this plan does not authorize

- It does not generate or publish the guides.
- It does not create an MSCA application, assert MSCA eligibility, or transfer content or
  confidential facts from `/Users/ruvebal/src/MSCA`; that repository supplies structure only.
- It does not collect, classify, or analyze student data.
- It does not request consent or imply institutional approval.
- It does not implement R6.
- It does not mutate `ttod.yml` or treat TTOD quotations as scholarly evidence.
- It does not turn a promising n=7 case into a causal or validated-framework claim.
- It does not create the isolated student-distribution artifact itself (§2's git-history
  finding) — it only tests whatever artifact already exists and reports the result. Creating or
  pushing that artifact is a separate action requiring Rubén's explicit authorization.
