---
title: Teaching model
eyebrow: Front-end II · first half of the semester
description: How TTOD maps to UDIT Front-end II Units 1–7, Entrega 1, and the mid-term defence of process and understanding.
permalink: /teaching/
lang: en
---

# Complete spine, shallow organs

TTOD is the teaching product for the **first half** of [Front-end II](https://ruvebal.github.io/web-atelier-udit/tracks/feii/) at UDIT: production architecture with Astro, offline browser behaviour, testing and AI-assisted review, and measured performance. The [English track index](https://ruvebal.github.io/web-atelier-udit/tracks/en/feii/) names the twelve-unit semester; TTOD owns Units 1–7 as one coherent artifact.

The proposed teaching baseline gives learners a small but complete product journey. Advanced areas are present as working hello worlds, not as finished assignment answers. The instructor can first explain how the system fits together; students then expand the same seams through assessed design and implementation.

## Course connection

| Course surface | Role of TTOD | Official weight (indicative) |
| --- | --- | --- |
| [Entrega 1 — Astro Architecture (Units 2–6)](https://ruvebal.github.io/web-atelier-udit/tracks/en/feii/how-to-pass-this-track/) | First deliverable: the student-owned Astro product with content collections, mandatory `es` + `en` routing, islands, multi-framework integration, testing suite, and AI-assisted review workflow | 25% · Week 7 |
| Mid-term (Units 1–7) | Written and practical check of **declarative use of the system**, defence of process, and understanding of the code—not a polished black-box demo | 15% · Week 7 |
| Units 1–7 together | Roughly half the semester before 3D, IoT, and the capstone | — |

Authoritative grading, calendar, and recovery rules live on the course site: [How to Pass Front-end II](https://ruvebal.github.io/web-atelier-udit/tracks/en/feii/how-to-pass-this-track/) and the [FE II track](https://ruvebal.github.io/web-atelier-udit/tracks/feii/). This documentation site describes the product and pedagogy; it does not replace the official guide.

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

This is a design rationale, not a claim that TTOD improves learning. The skeleton must first be built, rehearsed, independently reviewed, and synchronized with the localized course materials.

## Why the support must fade

The teaching pattern draws on cognitive apprenticeship: first make expert thinking visible through modeling and coaching, then fade support as learners assume responsibility. A recent semester-long qualitative study of AI-assisted programming sharpens the risk: support behaves as scaffolding when learners still modify, test, and explain outputs, but can become cognitive offloading when those meaning-making activities disappear. The study proposes a process model rather than a universal effectiveness result, so TTOD treats this as a design rationale to test—not as proof of learning (Liu, Fan, and Pan 2026).

The practical consequence is deliberate incompleteness. Students inherit a traceable system, but the valuable decisions—information architecture, interaction behavior, accessibility, recovery, performance, and test strategy—remain theirs. AI use is visible and discussable; generated output is never accepted as a substitute for explaining or changing the code.

Assessment therefore triangulates product behavior with process evidence and a short oral or written defence of understanding. Nikolić and Basta Nikolić’s four-pillar framework motivates this structure, but is itself conceptual and explicitly unvalidated; it is an assessment-design resource, not evidence that this course design works (Nikolić and Basta Nikolić 2026).

## Scope of theory

Theory covers rendering, content systems, localization, islands, state, streamed interfaces, offline browser behavior, accessibility, testing, and measured performance—the Unit 1–7 half of FE II. Containers are only a means to run the local system. Cloud operations and server administration are outside this front-end teaching scope.

Accessibility is part of the architecture and assessment from the first hello world. The shared baseline targets semantic structure, keyboard operation, visible focus, readable status, and non-color cues in line with the testable direction of WCAG 2.2; conformance remains a separate verification claim ([W3C 2024](https://www.w3.org/TR/WCAG22/)).

## Related course pages

- [FE II track (published)](https://ruvebal.github.io/web-atelier-udit/tracks/feii/)
- [English track index](https://ruvebal.github.io/web-atelier-udit/tracks/en/feii/)
- [How to Pass Front-end II](https://ruvebal.github.io/web-atelier-udit/tracks/en/feii/how-to-pass-this-track/)
- [For students]({{ '/audiences/students/' | relative_url }})
