<!--
TTOD research overview — entry point for department/research-group review.
Author: Rubén Vega Balbás, PhD · ruvebal@crea-comm.net · Drafted 2026-09-04.
This is a proposal under review, not an approved protocol. No data collection,
consent process, or research use of student work begins until §5's approvals
are in place. It gates research USE of Phase R's process evidence only — the
engineering build (docs/DEV_PLAN/PHASE-R-TTOD-ORACLE-PLATFORM-CASCADE-PROMPT.md)
needs no research approval and proceeds as ordinary FE II coursework regardless.

This document, and everything it links to, is independent of and makes no
reference to any other internal case-study proposal in the author's teaching
practice. Nothing here should be read as describing, replacing, or relating to
any such document.
-->

# TTOD Research Initiative — overview

> **Planning note (2026-09-05, audited and amended):** the research initiative remains pre-pitch
> and the audience guides have not been generated. Their proposed evidence, governance, audience
> separation, and cold-review workflow are specified in [`GUIDE-FORGE-PLAN.md`](GUIDE-FORGE-PLAN.md);
> the paste-ready generator is [`PROMPT-FORGE-TTOD-GUIDES.md`](PROMPT-FORGE-TTOD-GUIDES.md). The
> generator must first reconcile this older proposal narrative with the current Phase R
> cohort-starter/R6 student-ownership decision, now recorded in
> [`../DEV_PLAN/DECISIONS/R6-DEFERRED-STUDENT-OWNED.md`](../DEV_PLAN/DECISIONS/R6-DEFERRED-STUDENT-OWNED.md)
> and [`../DEV_PLAN/PHASE-R-CLOSURE-AND-COHORT-HANDOFF-REPORT.md`](../DEV_PLAN/PHASE-R-CLOSURE-AND-COHORT-HANDOFF-REPORT.md)
> (filed 2026-09-05, was missing when this section was first drafted). This pass's audit also
> found that no mechanism yet guarantees the reference build stays out of student hands — see
> "What this is not" below and `GUIDE-FORGE-PLAN.md` §2 for the exact finding.

**Subject:** Project Launch: TTOD Research Initiative & Advanced Front-End Pedagogy

Dear Colleagues,

I am writing to announce the formal kick-off of a research initiative built on this semester's
Front-End II capstone: the **TTOD Oracle Platform** — a governed pedagogical wisdom database
(`ttod.yml`, MIT/CC BY-NC-SA 4.0, already public) extended into a live, multi-framework web
platform by a 7-student cohort, under a documented, phased, cold-review-gated development plan.

Rather than assigning traditional, isolated coursework, the cohort collaborates on a single
production-grade "walking-skeleton" architecture — contributing components across Astro, React,
Svelte, FastMCP, and containerized Python services — while I retain sole responsibility for the
backend and the initial scaffold, so the cohort starts from a verified, working foundation rather
than debugging infrastructure on day one. To validate that this architecture is buildable at all
before committing a cohort's grade to it, I have already built a complete reference
implementation myself; it stays instructor-side and is never distributed to students, who receive
only the walking-skeleton foundation and build the remaining components independently against the
same task specification, not against my implementation of it.

The complete research design, ethical participation framework, and system architecture are fully
documented in this repository:

- [`docs/research/RESEARCH-LINE.md`](RESEARCH-LINE.md) — the research question, episteme,
  methodology, risk register, and venue ladder.
- [`docs/research/COHORT-CASE-PROPOSAL.md`](COHORT-CASE-PROPOSAL.md) — the request to the
  co-investigator and department/degree coordination: the gap, why this cohort, consent taxonomy,
  and calendar.
- [`docs/DEV_PLAN/PHASE-R-TTOD-ORACLE-PLATFORM-CASCADE-PROMPT.md`](../DEV_PLAN/PHASE-R-TTOD-ORACLE-PLATFORM-CASCADE-PROMPT.md)
  — the engineering side: what is actually being built, by whom, and the §6.1 cold-review
  protocol and §13 research-design track referenced above.
- [`docs/DEV_PLAN/DECISIONS/R6-DEFERRED-STUDENT-OWNED.md`](../DEV_PLAN/DECISIONS/R6-DEFERRED-STUDENT-OWNED.md)
  and [`docs/DEV_PLAN/PHASE-R-CLOSURE-AND-COHORT-HANDOFF-REPORT.md`](../DEV_PLAN/PHASE-R-CLOSURE-AND-COHORT-HANDOFF-REPORT.md)
  — what the cohort actually receives (the `cohort-starter` handoff) versus what stays an
  instructor-side reference build, and the open question of how that separation is technically
  enforced once repository access is shared with the cohort.

I welcome your review of the documentation. Please let me know if you would like to schedule a
brief discussion regarding data collection and research outputs for this semester.

Best regards,
Rubén Vega Balbás, PhD
Prof. Desarrollo Web Front-End I/II · UDIT

---

## What this is, in one paragraph

Front-End II's 2026-27 Entrega 1 ("Astro Architectural Project," 25% of the grade, due Week 7 /
October 2026) is, by course requirement, an Astro project with content collections, i18n routing,
islands architecture, a Vitest+RTL+Playwright test suite, CI/CD, and an AI-assisted code-review
workflow. This cohort's Entrega 1 **is** the TTOD Oracle Platform. The research question layered
on top asks whether an instructor-forged walking skeleton, cascade-orchestrated parallel work,
and a mandatory cold-review gate after every phase — the actual development method this cohort is
using, documented in real time — produces observable differences in engineering discipline and in
how students narrate authorship under ambient AI, relative to an unscaffolded team project. See
[`RESEARCH-LINE.md`](RESEARCH-LINE.md) §3 for the full research-question set.

## What this is not

- Not a change to what would be taught anyway. The cascade plan, the cold-review gate, and the
  Astro/i18n/testing requirements exist because FE II's own syllabus requires them (see the
  cascade doc's §0.1.6), not because a study needed them invented.
- Not a claim of effect sizes or a validated framework. With a single 7-student cohort, this is a
  documented case study, not an experiment — see `RESEARCH-LINE.md` §7 for what will and will not
  be claimed.
- Not live yet. No process evidence (commits, AI-use declarations, cold-review reports) is used
  as research data until the consents in `COHORT-CASE-PROPOSAL.md` §6 are administered
  independently of the instructor, and grades for the term are filed.
- Not proof that the reference build stays out of student hands. The intent is firm — the cohort
  builds R3b onward independently, never from a copy of my own implementation — but the technical
  enforcement of that separation is not yet verified, because this repository is public with a
  single shared remote. Publishing a student-facing branch to that same remote does not, by
  itself, achieve the isolation this proposal depends on; the actual distribution mechanism will
  be verified (git-history check against the real artifact a student clones) before any cohort
  receives repository access, and that verification will be recorded, not assumed.

## Status

**Proposal stage — pre-pitch.** Nothing in `docs/research/` has been reviewed by a co-investigator,
department coordination, or a data-protection officer. Treat every claim in `RESEARCH-LINE.md`
and `COHORT-CASE-PROPOSAL.md` as a draft position, not an approved protocol.
