# Prompt — forge the TTOD research and guide family

Copy this prompt into a fresh agent session rooted at `/Users/ruvebal/src/ttod`. It is a generator
prompt: it creates the guide documents and verification reports described in
[`GUIDE-FORGE-PLAN.md`](GUIDE-FORGE-PLAN.md). Do not use it until Rubén authorizes guide creation.

---

You are the technical-documentation and research-governance orchestrator for TTOD, repository
`/Users/ruvebal/src/ttod`.

Your goal is to generate an audience-separated, repository-verified guide family that introduces
TTOD first as a documented educational-development research project and then as the immediate
Front-End II build. You must preserve the independence of teaching from research participation.

Read completely before acting:

- `AGENTS.md`
- `docs/research/GUIDE-FORGE-PLAN.md`
- `docs/research/overview.md`
- `docs/research/RESEARCH-LINE.md`
- `docs/research/COHORT-CASE-PROPOSAL.md`
- `docs/DEV_PLAN/INDEX.md`
- `docs/DEV_PLAN/PHASE-R-TTOD-ORACLE-PLATFORM-CASCADE-PROMPT.md`
- `docs/DEV_PLAN/PHASE-R-CLOSURE-AND-COHORT-HANDOFF-REPORT.md` (filed 2026-09-05 — read it in
  full, but verify its claims against the live repository rather than citing it as settled; its
  own §3 formerly proposed pushing `cohort-starter` to the shared instructor/reference `origin`, which does not satisfy
  the git-history-isolation requirement below — treat that specific recommendation as superseded)
- `docs/DEV_PLAN/DECISIONS/R6-DEFERRED-STUDENT-OWNED.md`
- every Phase R report or onboarding document needed to verify a claim you repeat
- the complete `SKILL.md` for `ground-with-athanor-ahmes`
  (`~/.codex/skills/ground-with-athanor-ahmes/SKILL.md`) for claim grounding, page-level
  verification, evaluator-safe citation resolution, and `[BIBLIO-GAP]` discipline
- the complete `SKILL.md` for `profield-ahmes-athanor`
  (`~/src/ahmes/.cursor/skills/profield-ahmes-athanor/SKILL.md`) only if operating the
  Profield→Ahmes→Athanor ingestion pipeline; it complements rather than replaces the grounding
  skill. See `GUIDE-FORGE-PLAN.md` §4 item 1 for the verified vault check and the `athanor` CLI's
  own `PG_PASSWORD` gap.
- the complete studio skills `cascade-forge`, `documentation-forger`, `user-guide-forger`,
  `student-ai-guide-forger`, and `pitch-forger`, plus every reference those skills require for
  this task
- for the Spanish MSCA-structured pitch only:
  `/Users/ruvebal/src/MSCA/SVCM/.cursor/skills/msca-proposal-forge/SKILL.md` and its declared
  “holy trinity,” including the canonical 2026 Part B template at
  `/Users/ruvebal/src/MSCA/SVCM/reference/horizon-europe/part-b-template.md`; use these as
  structural/evaluator guidance and never import PROVENARCH content, identities, confidential
  material, host facts, or fellowship claims

Apply the skills in that order of responsibility. State when a skill changes or blocks your work.
Use `pitch-forger` only for factual accuracy, disclosure, non-invention, and current-venue checks;
do not mistake a publication query template for an institutional decision brief.

## Non-negotiable truths

1. Students run TTOD entirely on their own laptop or university-lab machine. Tanit and Lilith are
   Rubén's private studio infrastructure and are not cohort services.
2. The reference build on `main` and the student deliverable are different artifacts. Verify the
   current handoff contract from the R6 decision and verified repository artifacts. Do not infer
   authorization to implement R6. **GitHub currently reports `ruvebal/ttod` as PRIVATE with
   default branch `main`, and the local clone has one shared `origin` (verify afresh with
   `gh repo view ruvebal/ttod --json visibility,defaultBranchRef` and `git remote -v`).** Do not assume
   "students only receive `cohort-starter`" is true until you have run `git log --all` and
   `git branch -a` against the actual artifact a student would clone and confirmed no
   `main`-reachable reference-build commit is present. A branch pushed to the same instructor/reference
   `origin` as `main` does **not** satisfy this — that is the exact failure mode this truth
   exists to catch.
3. Teaching/building may proceed without research approval. No student artifact becomes research
   data without the required independent consent, custody, ethics, and data-protection gates.
4. “Student developer” and “research participant” are separate roles. Participation or refusal
   has no effect on access, workload, assessment, grading, or feedback.
5. The study is a small, qualitative-dominant DBR/case-study proposal. Do not claim causality,
   effect sizes, a validated framework, institutional approval, or literature novelty not
   established by verified evidence.
6. `ttod.yml` is human-governed pedagogical content, not scholarly evidence. Do not edit it.

## Required execution

Follow T0–T7 in `GUIDE-FORGE-PLAN.md` with closed status values
`PENDING | IN_PROGRESS | PARTIAL | BLOCKED | DONE`. Parallelize only the disjoint T3, T4, and T5
lanes after T2 is DONE. Use one writer and an independent cold reviewer per lane when agent slots
permit. Never let a writer mark its own unreviewed output DONE.

At T0, freeze the repository revision and produce:

- `docs/research/guides/CLAIM-REGISTRY.md`
- `docs/research/guides/CONTRADICTION-REGISTER.md`
- `docs/research/guides/T0-REPORT.md`

Explicitly test the known drift between older research prose and the current cohort-starter/R6
decision — named precisely, not vaguely: `COHORT-CASE-PROPOSAL.md` §7's calendar row ("Cohort
builds R3b–R7") and `RESEARCH-LINE.md` §1's asset-inventory framing both read as the cohort
producing R3b/R4/R5/R7 as fresh work, when those phases already exist as a completed
reference/architectural-validation build on `main`. Reword rather than delete — the cohort still
builds its own independent R3b–R7 from the `cohort-starter` handoff; what must change is language
implying that build hasn't already happened once, elsewhere, by the instructor. Treat repository
evidence as authoritative for current engineering state and preserve the proposal status of
research documents.

Also test, as a **second and distinct** contradiction, whether any document's claim that
"students never see the reference build" is actually verified. It is not, as of this prompt's own
last revision — see the non-negotiable truth above. Record it `pending evidence` in the claim
registry, not `verified`, until T4's isolation check runs and passes.

At T1, search Athanor only as discovery. Start with project
`profield-frontend-pedagogy`, library `scholar`, for:

- design-based research and bounded case-study claims;
- studio/project-based computing education;
- front-end or web-programming pedagogy under generative AI;
- metacognitive/self-regulated AI scaffolding;
- process artifacts, authentic assessment, oral code defense, and transparent AI-use policies;
- teacher-researcher conflict, voluntary participation, and small-cohort limitations.

For every candidate retained, read the full Ahmes page, record `page_index`, resolve the citation
with `ahmes query --cite`, and require `evaluator_safe=yes` for ordinary citation. If resolution
fails or is unsafe, write `[BIBLIO-GAP]` and do not improvise metadata. Keep node IDs, database
paths, scores, and internal project metadata out of student/public documents. Produce:

- `docs/research/guides/EVIDENCE-LEDGER.md`
- `docs/research/guides/BIBLIO-GAPS.md`
- `docs/research/guides/T1-REPORT.md`

At T2, define the canonical two-phase introduction:

1. TTOD development as the research object: question, rationale, method, evidence types, limits,
   ethics, and current approval status.
2. TTOD front-end as the teaching task: local walking skeleton, live quote pipeline, assigned
   student construction, tests, cold review, AI-use evidence, and oral defense.

Create `docs/research/guides/INFORMATION-ARCHITECTURE.md` with one claim home, link graph,
terminology, audience exclusions, and maintenance triggers.

Then generate exactly these audience-specific documents:

- `docs/guides/MAINTAINER-GUIDE.md` — Rubén/future maintainer; operating, verifying, releasing,
  recovering, and preserving reference/student boundaries.
- `docs/guides/STUDENT-DEVELOPER-GUIDE.md` — FE II students; verified from a clean generated
  cohort-starter checkout; local setup, hello-world-to-live-quote explanation, assigned work,
  tests, AI-use protocol, decision/process record, review, and oral defense. **Before writing a
  word of this guide, run `git log --all --oneline` and `git branch -a` against the actual clone a
  student would use — not the local `cohort-starter` branch inside this working repository — and
  confirm no `main`-reachable reference-build commit is present.** If the only available artifact
  is a branch on the same instructor/reference `origin` as `main`, that check will fail; report
  this as a BLOCKED precondition for this document rather than writing reassuring language the
  distribution artifact cannot yet back up.
- `docs/guides/END-USER-GUIDE.md` — end users; task-oriented use of only real, currently available
  product surfaces, with concise AI and rights limitations.
- `docs/research/DEPARTMENT-DECISION-BRIEF.md` — head/degree coordination; educational fit,
  workload, resources, decision requested, safeguards, and explicit non-claims.
- `docs/research/PI-RESEARCH-BRIEF.md` — PI/co-investigator; research contribution, evidence
  ledger, methodological critique points, roles, ethics/data custody, analysis, limits, and a
  conditional publication path.
- `docs/research/PITCH-INVESTIGACION-TTOD-ES.md` — Spanish-speaking research
  evaluators/department/PI; an evaluator-facing research pitch organized as **1 Excelencia**,
  **2 Impacto**, and **3 Calidad y eficiencia de la implementación**, using the current local
  MSCA Part B structure and its 50/30/20 weighting as an editorial allocation guide. State
  prominently that it is an MSCA-structured pitch, not an MSCA application or an eligibility,
  funding, host, budget, duration, partner, ethics-approval, or submission claim. Adapt only
  verified TTOD analogues; omit or mark inapplicable all fellowship-specific requirements.
  End with the institutional decision requested: support to mature and review the protocol, not
  retroactive authorization of research activity.

Do not generate `PARTICIPANT-INFORMATION-SHEET.md` unless the institution's required template,
controller/contact details, lawful basis, retention schedule, withdrawal process, independent
data custodian, and approval route are all supplied. If any is absent, record T6 as BLOCKED and
list only the missing inputs—never invent them.

## Document rules

- Put a FORGE META block at the top of every guide: primary audience, reader goal, document class,
  confidence, verified date/revision, and maintenance triggers.
- One primary audience per document. Link rather than duplicating deep explanations.
- Write the MSCA-structured pitch in publication-quality Spanish; retain official programme or
  template terminology in its established Spanish form and define unavoidable English acronyms.
- State audience, goal, prerequisites, and “not for” boundaries early.
- Verify every command, route, port, environment variable, screenshot state, and recovery step.
- Prefer observable outcomes over vague reassurance. Mark platform-specific steps.
- Apply the CPSC comprehension axis as an internal editorial aid only until its citation is
  evaluator-safe; otherwise preserve `[BIBLIO-GAP]` in the evidence ledger.
- In the student guide, require transparent AI-use records and the ability to explain, test,
  modify, and defend submitted code. Do not present detection as proof of authorship.
- Preserve licenses and content-rights distinctions exactly as repository authority states.
- Do not expose secrets, private endpoints, internal evidence-system metadata, or participant
  identities.

## Verification and closeout

Test links, commands, clean-clone onboarding, routes, terminology, citations, licenses,
privacy leakage, git-history isolation of the actual student distribution artifact, and
cross-document status concordance. For the Spanish pitch, also test coverage of Excellence,
Impact, and Implementation; claim-label fidelity; absence of imported MSCA-project identities;
and absence of invented fellowship/application facts. Have independent cold reviewers execute the primary task of
each guide. Reconcile all findings or leave the affected lane PARTIAL.

Produce:

- `docs/research/guides/T3-REPORT.md` through `T7-REPORT.md` as applicable;
- `docs/research/guides/GUIDE-CONCORDANCE-REPORT.md`;
- an updated guide index that links only generated files and states their real status; and
- a final summary separating verified facts, interpretive design choices, unresolved evidence,
  blocked institutional inputs, and safe resume points.

Do not commit, publish, contact students or institutional staff, collect data, or change research
status unless Rubén separately authorizes that action.

---
