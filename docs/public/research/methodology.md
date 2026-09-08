---
title: Method and safeguards
eyebrow: Research design boundary
description: A cautious methodology outline for a possible future TTOD educational study.
permalink: /research/methodology/
---

# Method before data

The current work prepares an investigable teaching system. It does not authorize a study. Future empirical work would require explicit questions, participant information, ethics and data-protection review, defined access and retention, and a clear separation between teaching, assessment, and voluntary research participation.

## Methodological stance

The engineering work follows a design-enquiry logic: articulate a pedagogical problem, build a traceable intervention, expose its assumptions, and preserve evidence of iteration. That supports disciplined design decisions but does not convert product development into educational research.

A future study could use a bounded case-study design to examine the artifact in context. If the focus is how students negotiate AI support, a constructivist grounded-theory approach with constant comparison may be appropriate; [Liu, Fan, and Pan 2026](#ref-liu-fan-pan-2026) provide a recent programming-education example, not a protocol to copy unchanged. The researcher must state positionality, sampling, coding, negative-case treatment, and the boundary between inductive findings and prior sensitizing concepts.

Self-regulation under AI assistance is itself an empirical object. [López-Pernas et al. 2025](#ref-lopez-pernas-et-al-2025) coded thousands of undergraduate ChatGPT interactions in a web programming course to study collaboration, dependence, and delegation over time—evidence that process logs and interaction coding can be research instruments when authorized, not that TTOD’s logs already are.

## Possible empirical design

A bounded educational case could combine technical artifact audit with qualitative analysis of versioned decision records and a short oral explanation. Questions, inclusion criteria, codebook, and analysis plan should be registered or versioned before analysis. Any comparison should focus on observable reasoning and traceability unless the design supports stronger inference.

Potential artifacts include a student repository, decision notes, declared AI use, automated checks, and a defense of selected changes. Triangulation can compare what the product does, what the record says, and what the learner can explain; disagreement between those sources is evidence to analyze, not noise to erase. None should be collected for research without the required authorization and communication.

Assessment-facing designs in computing education already treat student-built web products as authentic evidence. [Garcia 2025](#ref-garcia-2025) studies self-coded digital portfolios in a web design and development course under a project-based frame, which motivates keeping technical ownership and reflection together—without claiming the same outcomes for TTOD. Brownfield process studies such as [Shihab et al. 2025](#ref-shihab-et-al-2025) motivate questions about how learners accept, reject, and debug AI suggestions inside an inherited codebase—the situation the teaching spine creates by design.

## Safeguards

- Course access and grading must not depend on research participation.
- The teaching repository and any research dataset must have different identities and access rules.
- Data minimization, retention, pseudonymization, withdrawal, and reviewer access must be settled in advance.
- The rich instructor reference must be isolated from the student artifact by evidence, not assertion.
- Results must distinguish feasibility, teaching observation, assessment evidence, and research evidence.
- Negative, mixed, or inconclusive findings remain valid outcomes.

## Evidence anchors

The following sources motivate, but do not validate, the proposed design. In-text author–date forms link to the Chicago list below.

- [Shihab et al. 2025](#ref-shihab-et-al-2025) on Copilot effects and processes in brownfield coding tasks.
- [Nikolić and Basta Nikolić 2026](#ref-nikolic-basta-nikolic-2026) on a four-pillar AI-resilient assessment framework (conceptual; no validation data reported).
- [Liu, Fan, and Pan 2026](#ref-liu-fan-pan-2026) on scaffolding versus cognitive offloading in AI-assisted programming education.
- [López-Pernas et al. 2025](#ref-lopez-pernas-et-al-2025) on self-regulation dynamics in student–AI programming problem solving.
- [Garcia 2025](#ref-garcia-2025) on self-coded portfolios as authentic assessment in web design and development.
- [Davalos and Zhang 2026](#ref-davalos-zhang-2026) on learning visibility when AI enters the assessment loop.
- [*Computer Science Curricula 2023*](#ref-cs2023) on curriculum-wide generative AI, ethics, and professional responsibility.

These sources support studying process and assessment design. They do not establish effectiveness for this platform, course, or cohort. The AI-resilient assessment framework is explicitly conceptual; its indicators and instruments require empirical validation. The qualitative programming study is theory-building and context-bound. Those limits are carried into TTOD’s claim language.

## Analysis and quality controls

- Version the research questions, artifact definitions, interview or defense prompts, and analysis plan before examining outcomes.
- Keep engineering telemetry, assessed coursework, and consented research records as distinct datasets with distinct access rules.
- Use at least two evidence forms for claims about reasoning; do not infer understanding from repository activity alone. [Davalos and Zhang 2026](#ref-davalos-zhang-2026) argue that retaining final outputs while losing process visibility is a measurement failure mode—not a detection problem alone.
- Record disconfirming cases, coding changes, researcher memos, and unresolved interpretations.
- Report the learning setting, AI policy, tool access, prior experience, language context, and starter-code depth so readers can judge transferability.
- Treat accessibility, workload, and differential participation as research questions and possible harms—not merely implementation details.

<figure class="diagram-teaser">
  <a class="diagram-teaser-link" href="{{ '/assets/diagrams/ttod-research-safeguards.html' | relative_url }}">
    <img src="{{ '/assets/diagrams/ttod-research-safeguards.png' | relative_url }}" alt="Data-flow diagram showing candidate evidence — logs, grades, and defence — gated by consent and ethics/data review, authorized into distinct teaching and research datasets, and triangulated into either validated findings or equally valid negative/mixed findings." loading="lazy">
  </a>
  <figcaption><a href="{{ '/assets/diagrams/ttod-research-safeguards.html' | relative_url }}">Open the interactive safeguards diagram ↗</a> — how evidence would be gated, kept in distinct-access datasets, and triangulated once authorized.</figcaption>
</figure>

## Evidence still needed

The research preparation must deepen its evidence on worked-example fading, system tracing, cognitive load, studio learning, front-end conceptual transfer, student–AI self-regulation beyond single-course cases, and the dual teacher–researcher role. Primary classics on cognitive load while learning software and on cognitive apprenticeship are present incompletely or without verified bibliographic metadata for public citation; claim language therefore keeps them as open evidence needs rather than cited warrants. Current legal or institutional requirements must be verified against authoritative sources when a protocol is drafted.

## References

- <span id="ref-cs2023"></span>*Computer Science Curricula 2023*. Association for Computing Machinery, IEEE Computer Society, and AAAI. [https://doi.org/10.1145/3664191](https://doi.org/10.1145/3664191).
- <span id="ref-davalos-zhang-2026"></span>Davalos, Eduardo, and Yike Zhang. 2026. “AI Misuse in Education Is a Measurement Problem: Toward a Learning Visibility Framework.” arXiv. [https://doi.org/10.48550/arxiv.2603.07834](https://doi.org/10.48550/arxiv.2603.07834).
- <span id="ref-garcia-2025"></span>Garcia, Manuel B. 2025. “Self-Coded Digital Portfolios as an Authentic Project-Based Learning Assessment in Computing Education: Evidence from a Web Design and Development Course.” *Education Sciences* 15 (9): 1150. [https://doi.org/10.3390/educsci15091150](https://doi.org/10.3390/educsci15091150).
- <span id="ref-liu-fan-pan-2026"></span>Liu, Dandan, Guangrui Fan, and Lihu Pan. 2026. “Tool, Tutor, or Crutch?: A Grounded Theory of Cognitive Scaffolding and Offloading in AI-Assisted Programming Education.” *International Journal of STEM Education* 13: 10. [https://doi.org/10.1186/s40594-025-00592-w](https://doi.org/10.1186/s40594-025-00592-w).
- <span id="ref-lopez-pernas-et-al-2025"></span>López-Pernas, Sonsoles, Kamila Misiejuk, Eduardo Oliveira, and Mohammed Saqr. 2025. “The Dynamics of the Self-Regulation Process in Student-AI Interactions: The Case of Problem-Solving in Programming Education.” In *Proceedings of the 25th Koli Calling International Conference on Computing Education Research*. [https://doi.org/10.1145/3769994.3770043](https://doi.org/10.1145/3769994.3770043).
- <span id="ref-nikolic-basta-nikolic-2026"></span>Nikolić, Dragan, and Marijana Basta Nikolić. 2026. “Designing AI-Resilient Assessment in Higher Education: A Four-Pillar Conceptual Framework.” *Frontiers in Artificial Intelligence* 9. [https://doi.org/10.3389/frai.2026.1841682](https://doi.org/10.3389/frai.2026.1841682).
- <span id="ref-shihab-et-al-2025"></span>Shihab, Md Istiak Hossain, Christopher Hundhausen, Ahsun Tariq, Summit Haque, Yunhan Qiao, and Brian Wise Mulanda. 2025. “The Effects of GitHub Copilot on Computing Students’ Programming Effectiveness, Efficiency, and Processes in Brownfield Coding Tasks.” In *Proceedings of the 2025 ACM Conference on International Computing Education Research V.1*. [https://doi.org/10.1145/3702652.3744219](https://doi.org/10.1145/3702652.3744219).
