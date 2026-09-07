# T0 baseline and contradiction report

**State:** DONE  
**Date:** 2026-09-06  
**Frozen committed revision:** `8e73116299d29dd78b59f1717283f39eaca5fcea`

## Scope and method

T0 read the Phase Q/Phase R programme index, filed Phase Q reports, Phase R decision and closure
evidence, and every file under `docs/research/`. Repository and decision evidence outranked
proposal prose. The working tree was not clean at freeze time: pre-existing uncommitted Phase S5,
R7, and frontend changes were recorded as working state but were not represented as evidence in
the frozen commit.

Local `qwen3.8:27b` received the principal research, decision, closure, and index documents as a
skeptical drafting pass. Its useful findings were checked manually against exact source text.
The model had no authority to label a claim verified or to edit files; its overlong intermediate
enumeration was stopped after it had surfaced the relevant contradictions.

## Outputs

- [`CLAIM-REGISTRY.md`](CLAIM-REGISTRY.md): 27 atomic claims using the mandated four labels
  (C-027 added 2026-09-07 from the owner's MSCA-structured Spanish-pitch decision).
- [`CONTRADICTION-REGISTER.md`](CONTRADICTION-REGISTER.md): seven reconciled contradictions/gates.
- Source wording corrected in `COHORT-CASE-PROPOSAL.md`, `RESEARCH-LINE.md`, and `overview.md`.

## Cold audit

The post-draft cold read checked each correction against the R6 decision, Phase R closure table,
research-status disclaimer, current branch/remote topology, and the T0 prompt contract.

Findings:

1. The required cohort/reference-build contradiction is corrected in all three named research
   locations without erasing the student's independent R3b–R7 task.
2. The distribution-isolation statement remains `pending evidence`; no branch or private-repo
   property is treated as proof.
3. Three additional genuine contradictions are closed: “complete reference,” “formal kick-off,”
   and the mistaken replacement of the grounding skill with the ingestion/operator skill.
4. Cohort size, course assessment details, degree composition, literature-gap claims, and future
   public release are not promoted beyond available evidence.
5. Research remains explicitly pre-pitch, unapproved, and pre-collection.
6. T1 may begin from this registry. T2–T5 remain downstream; T6 remains BLOCKED.

## Safe resume point

Begin T1 by resolving scholarly evidence into its ledger and `[BIBLIO-GAP]` register. Preserve
C-008 as pending until T4 tests a real isolated distribution artifact. Recheck repository
visibility immediately before student access or public release.
