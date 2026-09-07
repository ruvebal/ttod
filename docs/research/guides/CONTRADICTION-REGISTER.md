# T0 contradiction register

**State:** DONE — wording reconciled where T0 had authority; unresolved evidence stays explicit.

| ID | Conflicting statements | Finding | Resolution / canonical wording | State |
| --- | --- | --- | --- | --- |
| X-001 | `COHORT-CASE-PROPOSAL.md` §7 said “Cohort builds R3b–R7” without distinguishing it from the already-built reference lanes; `RESEARCH-LINE.md` §1 similarly described one undifferentiated phase trail. | Readers could infer that R3b/R4/R5/R7 had not already been implemented by the instructor. | “The instructor reference build contains R3b/R4/R5 and partial R7 work. From an isolated walking skeleton, students independently implement their assessed R3b–R7 scope; R6 remains student-owned.” Both files were amended. | resolved |
| X-002 | `overview.md` said the reference “is never distributed” while its own “What this is not” section says technical separation is unverified. | Intention was presented as accomplished fact. | “The reference is intended to remain instructor-side; non-distribution is pending until the actual student artifact passes T4's git-history-isolation test.” | pending evidence; wording resolved |
| X-003 | `overview.md` called the reference implementation “complete”; the R6 decision says R6 is unimplemented and the closure report says R7 is PARTIAL. | “Complete” is false for the full Phase R scope. | “An R3b/R4/R5 reference implementation exists; R6 is absent and R7 is PARTIAL.” | resolved |
| X-004 | `overview.md` announced a “formal kick-off” but later says “Proposal stage — pre-pitch” and no approval exists. | Proposal and launch are distinct institutional states. | “Proposal for institutional and research-group review.” | resolved |
| X-005 | Older research prose said every phase/report closes with independent cold review; R6 has no implementation and R7 remains PARTIAL. | A design rule was written as a completed universal fact. | Separate existing instructor evidence from the future cohort protocol; do not claim closed evidence for absent/partial lanes. | resolved |
| X-006 | Current privacy is sometimes rhetorically coupled to future student isolation. | A private repository can still expose all branches to authorized collaborators, and future public release changes visibility again. | Privacy is a current repository state, not a pedagogical isolation mechanism. Use a separate/orphan student artifact and verify it; record future publication as intention until released. | open implementation gate for T4 |
| X-007 | The audited forge plan and prompt said `ground-with-athanor-ahmes` did not exist and replaced it with `profield-ahmes-athanor`. | Both files exist: the shared skill governs evidence grounding and citation safety; the Ahmes-project skill governs ingestion operations. | Name both and route work by responsibility. T1 uses the grounding skill; ingestion work may additionally use the project skill. | resolved |

## Gate decision

No unresolved contradiction now has competing canonical wording. X-002 and X-006 remain open as
evidence/implementation gates, but all T0 documents must describe them as pending rather than
asserting isolation.
