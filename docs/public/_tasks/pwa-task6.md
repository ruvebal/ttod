---
title: "Measured performance budget before/after one optimization (Core Web Vitals)"
seam: pwa
team_number: 4
team_name: "PWA & Local Operations"
task_number: 6
area: "PWA/Offline"
verb: keep
layout: default
lang: en
---

# Assignment — Team 4, Task 6: Measured performance budget before/after one optimization (Core Web Vitals)

**Seam:** pwa · **Team:** 4 · **Task:** 6 of ~10
**Area(s):** PWA/Offline · **Verb served:** keep

## 1. Curriculum map

This task exercises the measurement and optimization principles found in **Unit 5 — Testing strategy** ([https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/)), specifically the discipline of establishing a baseline before changing behavior. While the primary focus is performance, the methodological requirement to "measure first, then fix, then measure again" aligns with the verification and evidence-based practices emphasized in Unit 5.

## 2. Worked example, from the real TTOD app

The starter code at `services/frontend/public/sw.js` currently implements a Cache-First strategy for exactly one asset: `/visual-system/tokens.css`. This file is a critical rendering dependency. By measuring the load time of this specific asset (or the total page load time dominated by it) before and after an optimization (such as minification, compression, or preloading), you can isolate a single, measurable bottleneck. The existing `services/frontend/src/layouts/Page.astro` renders the `#ttod-network-boundary` banner, which provides a visible state change that can be used to verify that the optimization did not break the offline detection logic.

## 3. What "done" looks like

**Visible result:** A specific, named optimization with a measured before/after number (Core Web Vitals or equivalent) — never a claimed improvement without a measurement.

**What it includes:** Designing your own budget is explicitly part of this assignment. The starter deliberately ships with no Lighthouse CI gate yet, so you are not inheriting someone else's numbers.

**What has to be done:** Measure first, pick one real bottleneck, fix it, measure again, and keep both numbers for the defense.

## 4. Success criteria (functional)

1. **Measured Baseline:** A recorded performance metric (e.g., LCP, FCP, or TTI) from the unoptimized starter code is documented.
2. **Optimization Implemented:** One specific, real bottleneck is identified and fixed. The fix must be grounded in the module's constraints (e.g., extending `sw.js` or optimizing assets, not replacing the stack).
3. **Measured Improvement:** A second performance metric is recorded after the optimization, showing a measurable improvement over the baseline.
4. **Budget Design:** A performance budget is explicitly defined by the student, justifying the chosen threshold. This is required by the module's Prohibited shortcuts section, which forbids a Lighthouse CI gate that fails on budgets the student hasn't designed themselves.

## 5. Quality criteria (the part that's new)

**Code Organization:** The optimization must be isolated and documented. If the optimization involves changes to `services/frontend/public/sw.js`, the changes must be clearly commented and justified in the context of the module's "Keep the stub honest" constraint.

**AI-Use/Process Documentation:** The process of measuring, identifying the bottleneck, and applying the fix must be documented. This includes the tools used for measurement (e.g., Lighthouse, Chrome DevTools) and the rationale for choosing the specific bottleneck.

**Test Shape:** Per [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/)'s own Trophy-not-Pyramid doctrine, the test for this task is the measurement itself. The "test" is the before/after comparison. Ensure that the measurement is reproducible and that the optimization does not break existing functionality (e.g., the offline banner in `Page.astro` still works).

**Accessibility:** This task inherits the global Definition of Done: keyboard-operable, one accessible name or label, no meaning carried by color alone, respects reduced-motion preferences. Ensure that the optimization does not introduce any accessibility regressions (e.g., if the optimization involves changing the DOM structure or loading order, verify that accessibility is preserved).

**Oral Defense:** A defensible oral-defense answer for this task sounds like: "I measured the initial LCP at X ms. I identified that the loading of `/visual-system/tokens.css` was the primary bottleneck. I optimized this by [specific action, e.g., minifying the CSS or adding a preload hint]. After the optimization, the LCP improved to Y ms. I designed a budget of Z ms based on [rationale], and the optimized code meets this budget."

## Closing

> "Verify Before You Fix - Not every symptom is a disease."
> — TTOD `arch-027`, *architecture*

This task requires you to verify the performance bottleneck through measurement before applying a fix, ensuring that the optimization addresses a real issue rather than a perceived one.