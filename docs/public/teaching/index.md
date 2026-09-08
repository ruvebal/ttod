---
title: Teaching model
eyebrow: Front-end II · first half of the semester
description: How TTOD maps to UDIT Front-end II Units 1–7, Entrega 1, and the mid-term defence of process and understanding.
permalink: /teaching/
lang: en
---

# Complete spine at hello-world depth

TTOD is the teaching product for the **first half** of [Front-end II](https://ruvebal.github.io/web-atelier-udit/tracks/feii/) at UDIT: production architecture with Astro, offline browser behaviour, testing and AI-assisted review, and measured performance. The [English track index](https://ruvebal.github.io/web-atelier-udit/tracks/en/feii/) names the twelve-unit semester; TTOD owns Units 1–7 as one coherent artifact.

The proposed teaching baseline gives learners a small but complete product journey—every major seam is present, but none is finished as an assignment answer. Advanced areas appear as working hello-world examples. The instructor can first explain how the system fits together; students then expand the same seams through assessed design and implementation.

## Course connection

| Course surface | Role of TTOD | Official weight (indicative) |
| --- | --- | --- |
| [Entrega 1 — Astro Architecture (Units 2–6)](https://ruvebal.github.io/web-atelier-udit/tracks/en/feii/how-to-pass-this-track/) | First deliverable: the student-owned Astro product with content collections, mandatory `es` + `en` routing, islands, multi-framework integration, testing suite, and AI-assisted review workflow | 25% · Week 7 |
| Mid-term (Units 1–7) | Written and practical check of **declarative use of the system**, defence of process, and understanding of the code—not a polished black-box demo | 15% · Week 7 |
| Units 1–7 together | Roughly half the semester before 3D, IoT, and the capstone | — |

Authoritative grading, calendar, and recovery rules live on the course site: [How to Pass Front-end II](https://ruvebal.github.io/web-atelier-udit/tracks/en/feii/how-to-pass-this-track/) and the [FE II track](https://ruvebal.github.io/web-atelier-udit/tracks/feii/). This documentation site describes the product and pedagogy; it does not replace the official guide.

<figure class="diagram-teaser">
  <a class="diagram-teaser-link" href="{{ '/assets/diagrams/ttod-feii-architecture.html' | relative_url }}">
    <img src="{{ '/assets/diagrams/ttod-feii-architecture.png' | relative_url }}" alt="Front-end architecture diagram in FE II vocabulary: browser to Astro document to page shell to a Svelte or React island, HTTP/SSE to the Oracle API and governed quote snapshot, with document, island, and service-boundary ownership marked, plus Ollama shown as infrastructure the app owns in its own container." loading="lazy">
  </a>
  <figcaption><a href="{{ '/assets/diagrams/ttod-feii-architecture.html' | relative_url }}">Open the interactive Units 1–7 diagram ↗</a> — the same request path in course vocabulary: document vs. island ownership, the Unit 4 offline design, and the seams Entrega 1 and the mid-term ask you to defend.</figcaption>
</figure>

## Units 1–7 on the TTOD spine

| Units | Course focus | What TTOD makes observable |
| --- | --- | --- |
| 1–3 | Production architecture with Astro (SSR, islands, micro-frontends) | Localized routes, content contracts, Astro document ownership, bounded Svelte/React islands |
| 4 | PWA and offline capabilities | One observable local/offline boundary students must design and defend |
| 5–6 | Testing strategy and AI-assisted code review | Representative assertions at useful layers; disclosed AI use with human accept/reject/escalate evidence |
| 7 | Performance engineering | Measured budgets and bundle or runtime cost before claiming an optimization |

Units 8–12 (3D, IoT/Python, capstone defence) remain later course work. They are outside this TTOD teaching baseline.

## The five expansion areas

| Area | Provided hello world | Student-owned depth (Entrega 1) |
| --- | --- | --- |
| Astro content | one localized collection and index/detail journey | taxonomy, editorial breadth, fallback policy, and information architecture |
| Svelte graph | one small real neighborhood and accessible selection | exploration, filters, layout, URL state, and corpus-scale performance |
| React Oracle | one prompt, streamed response mode, and cited quote | robust state, sessions, recovery, disclosure, offline proposals, and interaction design |
| Browser operations and offline behavior | one observable local/offline boundary | caching, installability, queues, budgets, and operational evidence |
| Testing | one representative assertion at each useful layer | risk strategy, interaction E2E, contract breadth, accessibility, performance, and flake control |

## Pedagogical sequence

1. Run and trace the complete request path before collaboration opens.
2. Name where rendering, state, trust, content governance, and testing live.
3. Examine one minimal implementation at each framework boundary.
4. Convert deliberately absent behaviors into explicit Entrega 1 criteria.
5. Require students to explain design choices and evidence—product behaviour, process record, and mid-term defence of understanding—not merely present a finished interface.

This is a design rationale, not a claim that TTOD improves learning. The baseline must first be built, rehearsed, independently reviewed, and synchronized with the localized course materials.

## Why the support must fade

The teaching pattern draws on cognitive apprenticeship: first make expert thinking visible through modeling and coaching, then fade support as learners assume responsibility. A recent semester-long qualitative study of AI-assisted programming sharpens the risk: support behaves as scaffolding when learners still modify, test, and explain outputs, but can become cognitive offloading when those meaning-making activities disappear. The study proposes a process model rather than a universal effectiveness result, so TTOD treats this as a design rationale to test—not as proof of learning ([Liu, Fan, and Pan 2026](#ref-liu-fan-pan-2026)).

The practical consequence is deliberate incompleteness. Students inherit a traceable system, but the valuable decisions—information architecture, interaction behavior, accessibility, recovery, performance, and test strategy—remain theirs. AI use is visible and discussable; generated output is never accepted as a substitute for explaining or changing the code. Self-regulation studies of student–AI interaction in web programming further motivate watching dependence and delegation over time, not only final commits ([López-Pernas et al. 2025](#ref-lopez-pernas-et-al-2025)).

Assessment therefore triangulates product behavior with process evidence and a short oral or written defence of understanding. [Nikolić and Basta Nikolić 2026](#ref-nikolic-basta-nikolic-2026)’s four-pillar framework motivates this structure, but is itself conceptual and explicitly unvalidated; it is an assessment-design resource, not evidence that this course design works. Keeping process visible also answers a measurement concern: when AI enters the loop, educators may retain products while losing how work was produced ([Davalos and Zhang 2026](#ref-davalos-zhang-2026)). Authentic web-course portfolio assessment that requires students to code the artifact themselves likewise supports product-plus-process ownership without claiming identical outcomes here ([Garcia 2025](#ref-garcia-2025)).

## Scope of theory

Theory covers rendering, content systems, localization, islands, state, streamed interfaces, offline browser behavior, accessibility, testing, and measured performance—the Unit 1–7 half of FE II. Containers are only a means to run the local system. Cloud operations and server administration are outside this front-end teaching scope.

Accessibility is part of the architecture and assessment from the first hello world. The shared baseline targets semantic structure, keyboard operation, visible focus, readable status, and non-color cues in line with the testable direction of WCAG 2.2; conformance remains a separate verification claim ([W3C 2024](https://www.w3.org/TR/WCAG22/)).

## Related course pages

- [FE II track (published)](https://ruvebal.github.io/web-atelier-udit/tracks/feii/)
- [English track index](https://ruvebal.github.io/web-atelier-udit/tracks/en/feii/)
- [How to Pass Front-end II](https://ruvebal.github.io/web-atelier-udit/tracks/en/feii/how-to-pass-this-track/)
- [For students]({{ '/audiences/students/' | relative_url }})

## References

- <span id="ref-davalos-zhang-2026"></span>Davalos, Eduardo, and Yike Zhang. 2026. “AI Misuse in Education Is a Measurement Problem: Toward a Learning Visibility Framework.” arXiv. [https://doi.org/10.48550/arxiv.2603.07834](https://doi.org/10.48550/arxiv.2603.07834).
- <span id="ref-garcia-2025"></span>Garcia, Manuel B. 2025. “Self-Coded Digital Portfolios as an Authentic Project-Based Learning Assessment in Computing Education: Evidence from a Web Design and Development Course.” *Education Sciences* 15 (9): 1150. [https://doi.org/10.3390/educsci15091150](https://doi.org/10.3390/educsci15091150).
- <span id="ref-liu-fan-pan-2026"></span>Liu, Dandan, Guangrui Fan, and Lihu Pan. 2026. “Tool, Tutor, or Crutch?: A Grounded Theory of Cognitive Scaffolding and Offloading in AI-Assisted Programming Education.” *International Journal of STEM Education* 13: 10. [https://doi.org/10.1186/s40594-025-00592-w](https://doi.org/10.1186/s40594-025-00592-w).
- <span id="ref-lopez-pernas-et-al-2025"></span>López-Pernas, Sonsoles, Kamila Misiejuk, Eduardo Oliveira, and Mohammed Saqr. 2025. “The Dynamics of the Self-Regulation Process in Student-AI Interactions: The Case of Problem-Solving in Programming Education.” In *Proceedings of the 25th Koli Calling International Conference on Computing Education Research*. [https://doi.org/10.1145/3769994.3770043](https://doi.org/10.1145/3769994.3770043).
- <span id="ref-nikolic-basta-nikolic-2026"></span>Nikolić, Dragan, and Marijana Basta Nikolić. 2026. “Designing AI-Resilient Assessment in Higher Education: A Four-Pillar Conceptual Framework.” *Frontiers in Artificial Intelligence* 9. [https://doi.org/10.3389/frai.2026.1841682](https://doi.org/10.3389/frai.2026.1841682).
