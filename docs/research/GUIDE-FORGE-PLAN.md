# TTOD research and guide-forge plan

**Status:** PROPOSED — planning artifact only; no guides generated  
**Date:** 2026-09-05  
**Owner:** Rubén Vega Balbás, PhD  
**Engineering baseline:** Phase R reference build exists; the student handoff is R1/R2/R3a and
R6 remains student-owned.

## 1. Honest maturity verdict

TTOD is mature as an **engineering object and documented teaching design**, but not yet mature as
an approved research study.

| Layer | Current maturity | Evidence | Next gate |
| --- | --- | --- | --- |
| Governed TTOD data/tooling | operational | Phase Q reports and repository tests | maintain invariants |
| Oracle reference architecture | validated reference implementation | Phase R R1–R5 reports and cold reviews | finish only work authorized by the R6 decision |
| Student development task | planned as implementable from a walking skeleton | R6 decision, generator script, R3a onboarding, and `PHASE-R-CLOSURE-AND-COHORT-HANDOFF-REPORT.md` (filed 2026-09-05 — the index no longer references a missing artifact) | the closure report's own distribution advice is unverified against §2's isolation requirement below — cold-read a clean clone of whatever artifact students actually receive, not the local `cohort-starter` branch, before treating this row as closed |
| Research design | substantial pre-protocol | `RESEARCH-LINE.md`, `COHORT-CASE-PROPOSAL.md`, Phase R §13 | evidence refresh, co-investigator, ethics/data-protection review |
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
| `PARTICIPANT-INFORMATION-SHEET.md` | potential student participant | understand voluntary participation and data use | **HOLD:** generate only after institutional and data-protection requirements are supplied and independently reviewed |

“Student developer” and “research participant” are different roles. Course access, assessment,
grading, repository access, and software use must never depend on research consent.

## 4. Studio technology to plug in

Use the tools in this order:

1. **Athanor discovery + Ahmes verification** — search only the
   `profield-frontend-pedagogy` project first. Read the full Ahmes page for every retained result,
   resolve its citation key, and admit it as an ordinary citation only when
   `evaluator_safe=yes`. Otherwise emit `[BIBLIO-GAP]`; do not repair metadata by intuition.
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
6. **`cascade-forge`** — orchestrate the work as gated, resumable lanes with reports and cold
   review. It generates documents; it does not change research status by writing `DONE` in prose.

No guide may expose Athanor/Ahmes database paths, node identifiers, internal project metadata, or
studio credentials. Public and student outputs contain resolved citations only.

## 5. Cascade

Use the closed states `PENDING | IN_PROGRESS | PARTIAL | BLOCKED | DONE`.

### T0 — Baseline and contradiction register (sequential blocker)

- Freeze git revision and read Phase Q, Phase R, the R6 decision,
  `PHASE-R-CLOSURE-AND-COHORT-HANDOFF-REPORT.md` (now filed), and all `docs/research/` files.
  Record a referenced-but-missing report as a gap; never silently treat its link text as evidence.
- Reconcile current facts before drafting. **Known contradiction, exact location:**
  `COHORT-CASE-PROPOSAL.md` §7's calendar row — "Sep–Oct 2026 | Cohort builds R3b–R7" — reads as
  the cohort producing R3b/R4/R5/R7 as fresh work, but those phases already exist as a
  reference/architectural-validation build on `main`, completed before any cohort start. The
  cohort's own graded R3b–R7 is a separate, independent build from the `cohort-starter` handoff,
  not a continuation of the reference build — reword, don't just cross-reference, everywhere this
  ambiguity recurs (`RESEARCH-LINE.md` §1's "asset inventory" row and `overview.md`'s kickoff
  letter carry the same phrasing).
- **Second contradiction to register, not yet resolved anywhere in this tree:** every research
  document asserts students never see the reference build, but no verified mechanism currently
  guarantees that — see the shared-`origin` finding in §2 above. Record this as
  `pending evidence`, not `verified`, until T4 tests it.
- Produce a claim registry with `verified | interpretive | pending evidence | obsolete` labels.
- Gate: no unresolved contradiction may enter two documents with different wording.

### T1 — Evidence and protocol maturity audit (after T0)

- Refresh the Athanor literature discovery for DBR, studio/project-based computing education,
  metacognitive AI scaffolding, process artifacts, oral defense, authorship, and small-cohort case
  study limits.
- Verify retained evidence through Ahmes page text and citation resolution.
- Separate literature claims from TTOD repository observations and proposed design principles.
- Produce an evidence ledger and `[BIBLIO-GAP]` register.
- Gate: no submission-facing claim rests on vector-search snippets alone.

### T2 — Shared information architecture (after T0 and T1)

- Define the canonical two-phase introduction, vocabulary, audience matrix, link graph, claim
  homes, and maintenance triggers.
- Specify what each audience needs, what it must not receive, and the reading order.
- Gate: every claim has one canonical home; all other occurrences link or summarize consistently.

### T3 — Operational guide lane (parallel after T2)

- Forge `MAINTAINER-GUIDE.md` and `END-USER-GUIDE.md`.
- Verify every command, route, port, environment variable, failure mode, and recovery instruction
  against the checked-out repository or a clearly labelled fixture.
- Gate: a cold reader can complete the guide goal without hidden studio knowledge.

### T4 — Student developer lane (parallel after T2)

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

### T5 — Institutional lane (parallel after T2)

- Forge separate department and PI briefs; never collapse their decision needs into one pitch.
- The department brief asks for an educational/operational decision. The PI brief asks for
  methodological critique, co-investigator roles, evidence refinement, and ethics/data custody.
- Gate: documents say “proposal” until real approvals exist and include explicit non-claims.

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
- no private studio endpoint is offered to students;
- no guide invents approval, consent, evidence, commands, routes, or capabilities; and
- reports preserve `PARTIAL` or `BLOCKED` honestly when a gate is unmet.

## 7. What this plan does not authorize

- It does not generate or publish the guides.
- It does not collect, classify, or analyze student data.
- It does not request consent or imply institutional approval.
- It does not implement R6.
- It does not mutate `ttod.yml` or treat TTOD quotations as scholarly evidence.
- It does not turn a promising n=7 case into a causal or validated-framework claim.
- It does not create the isolated student-distribution artifact itself (§2's git-history
  finding) — it only tests whatever artifact already exists and reports the result. Creating or
  pushing that artifact is a separate action requiring Rubén's explicit authorization.
