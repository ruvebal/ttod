---
title: Research
eyebrow: Evidence before effect claims
description: TTOD's research questions, current maturity, safeguards, and evidence boundaries.
permalink: /research/
---

# A research programme in preparation

TTOD currently supports a technical and pedagogical design enquiry: how can a complete but deliberately shallow front-end system make architectural boundaries, process evidence, and student design responsibility easier to examine in an AI-assisted learning environment?

This is a proposal, not an approved empirical protocol. No claim is made that TTOD improves learning, no participant recruitment is authorized, and no student work becomes research data merely because it was produced in a course.

## Four artifacts that must not be confused

1. **Rich instructor reference:** feasibility evidence that the architecture can run end to end.
2. **Teaching baseline:** a future hello-world product used for explanation and tracing.
3. **Student products:** independently expanded, assessed work demonstrating learner decisions.
4. **Research records:** only material collected under a separately approved and communicated protocol.

## Candidate questions

- Which traces help a learner correctly locate rendering, state, trust, data, and test ownership?
- How much starter implementation supports system understanding without collapsing authentic design work?
- Which process artifacts make AI-assisted contributions explainable and reviewable?
- How can oral explanation, repository evidence, accessibility checks, and product behavior complement one another in assessment?

## What existing literature can and cannot do

Research on AI-assisted programming, authentic assessment, process documentation, and explanation motivates the design. [Liu, Fan, and Pan 2026](#ref-liu-fan-pan-2026) describe a tension between domain mastery and tool mastery and distinguish scaffolding from cognitive offloading; their grounded-theory study does not adjudicate efficacy or predict outcomes in this course. [Nikolić and Basta Nikolić 2026](#ref-nikolic-basta-nikolic-2026) propose process documentation, oral defense, authentic tasks, and transparent AI-use policies, while explicitly reporting no validation data.

Complementary STEM and computing-education work sharpens the same boundary without proving a TTOD effect. [Shihab et al. 2025](#ref-shihab-et-al-2025) study how Copilot changes effectiveness, efficiency, and process in brownfield programming tasks—useful for questions about integrating suggestions into an existing codebase, not as a transfer claim for this scaffold. [López-Pernas et al. 2025](#ref-lopez-pernas-et-al-2025) examine self-regulation in student–AI interactions during web-programming problem solving, which motivates attention to dependence, delegation, and regulation over time. [Garcia 2025](#ref-garcia-2025) reports on self-coded digital portfolios as authentic project-based assessment in a web design and development course, supporting product-plus-process assessment designs. [Davalos and Zhang 2026](#ref-davalos-zhang-2026) reframe “AI misuse” as a learning-visibility and measurement problem when educators retain products but lose process insight—an analogy for why TTOD treats traces and oral defence as design requirements rather than detection theatre.

Curriculum guidance in [*Computer Science Curricula 2023*](#ref-cs2023) treats generative AI, society, ethics, and professional responsibility as curriculum-wide concerns rather than a detached tool lesson; that is a standards-facing warrant for scope, not classroom evidence.

These sources justify questions and safeguards, not a TTOD effect. More longitudinal classroom evidence is needed, and local implementation observations are engineering evidence rather than educational outcomes. Classic instructional-design primaries on cognitive load and cognitive apprenticeship remain on the evidence-needed list until their bibliographic metadata can be verified for public citation.

## Critical perspective

The central risk is confusing a polished product with learning. Faster completion can coexist with weaker explanation, debugging, or independent problem decomposition. TTOD therefore treats generated code as an object for critique: learners must locate its assumptions, test it, modify it, and explain responsibility for the result. The intended contrast is not “AI or no AI,” but support that is deliberately faded versus dependency that remains invisible.

That critical lens also applies to the platform itself. A governed corpus can still encode omissions; a graph can make editorial relations appear natural; an Oracle can project authority; process logs can be staged; and an oral defense can create workload or equity costs. Research must examine those power and validity questions rather than using traceability as a synonym for truth.

Read the [method and safeguards]({{ '/research/methodology/' | relative_url }}) or the [teaching model]({{ '/teaching/' | relative_url }}).

## Current status

| Layer | Status | Next gate |
| --- | --- | --- |
| Engineering feasibility | locally observed; independent verification open | close the evidence report |
| Teaching skeleton | planned | freeze subtraction and assignment contracts |
| Curriculum alignment | scheduled later | bilingual semantic-parity review |
| Empirical research | pre-protocol, pre-collection | ethics, data, consent or legal-basis review |

## References

- <a id="ref-cs2023"></a>*Computer Science Curricula 2023*. Association for Computing Machinery, IEEE Computer Society, and AAAI. [https://doi.org/10.1145/3664191](https://doi.org/10.1145/3664191).
- <a id="ref-davalos-zhang-2026"></a>Davalos, Eduardo, and Yike Zhang. 2026. “AI Misuse in Education Is a Measurement Problem: Toward a Learning Visibility Framework.” arXiv. [https://doi.org/10.48550/arxiv.2603.07834](https://doi.org/10.48550/arxiv.2603.07834).
- <a id="ref-garcia-2025"></a>Garcia, Manuel B. 2025. “Self-Coded Digital Portfolios as an Authentic Project-Based Learning Assessment in Computing Education: Evidence from a Web Design and Development Course.” *Education Sciences* 15 (9): 1150. [https://doi.org/10.3390/educsci15091150](https://doi.org/10.3390/educsci15091150).
- <a id="ref-liu-fan-pan-2026"></a>Liu, Dandan, Guangrui Fan, and Lihu Pan. 2026. “Tool, Tutor, or Crutch?: A Grounded Theory of Cognitive Scaffolding and Offloading in AI-Assisted Programming Education.” *International Journal of STEM Education* 13: 10. [https://doi.org/10.1186/s40594-025-00592-w](https://doi.org/10.1186/s40594-025-00592-w).
- <a id="ref-lopez-pernas-et-al-2025"></a>López-Pernas, Sonsoles, Kamila Misiejuk, Eduardo Oliveira, and Mohammed Saqr. 2025. “The Dynamics of the Self-Regulation Process in Student-AI Interactions: The Case of Problem-Solving in Programming Education.” In *Proceedings of the 25th Koli Calling International Conference on Computing Education Research*. [https://doi.org/10.1145/3769994.3770043](https://doi.org/10.1145/3769994.3770043).
- <a id="ref-nikolic-basta-nikolic-2026"></a>Nikolić, Dragan, and Marijana Basta Nikolić. 2026. “Designing AI-Resilient Assessment in Higher Education: A Four-Pillar Conceptual Framework.” *Frontiers in Artificial Intelligence* 9. [https://doi.org/10.3389/frai.2026.1841682](https://doi.org/10.3389/frai.2026.1841682).
- <a id="ref-shihab-et-al-2025"></a>Shihab, Md Istiak Hossain, Christopher Hundhausen, Ahsun Tariq, Summit Haque, Yunhan Qiao, and Brian Wise Mulanda. 2025. “The Effects of GitHub Copilot on Computing Students’ Programming Effectiveness, Efficiency, and Processes in Brownfield Coding Tasks.” In *Proceedings of the 2025 ACM Conference on International Computing Education Research V.1*. [https://doi.org/10.1145/3702652.3744219](https://doi.org/10.1145/3702652.3744219).
