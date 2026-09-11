---
title: "Layout and performance at real corpus scale"
seam: graph
team_number: 2
team_name: "Knowledge Graph"
task_number: 5
area: "Graph"
verb: keep
layout: default
lang: en
---

# Assignment — Team 2, Task 5: Layout and performance at real corpus scale

**Seam:** graph · **Team:** 2 · **Task:** 5 of ~10
**Area(s):** Graph · **Verb served:** keep

## 1. Curriculum map

This task exercises the performance and optimization principles inherent in **FE II Unit 5 — Testing strategy** (specifically the profiling and debugging components required to identify bottlenecks) and **FE II Unit 3 — Routing and State** (managing reactive state under load).

*Note: Specific unit links for "Performance Optimization" are not yet published in the `assignments.md` "Lessons for these tasks" section for this specific task. Per the skill's discipline, we do not invent a unit link. However, the testing/profiling methodology is grounded in the general FE II curriculum standards for debugging and performance.*

## 2. Worked example, from the real TTOD app

The current hello-world implementation in `services/frontend/src/components/graph/GraphIsland.svelte` already calls `radialLayout` from `./layout.ts` to position nodes. The function `radialLayout` is the single source of truth for node positioning. In the current state, it works for the small sample set provided by `GET /api/v1/wisdom/sample`. This task requires you to analyze the performance characteristics of this exact function and its interaction with the Svelte 5 rendering pipeline when the dataset size increases. You are not replacing `radialLayout`; you are measuring its cost and the cost of the DOM updates it triggers.

## 3. What "done" looks like

**Visible result:** The graph remains responsive and legible when the full governed dataset is loaded, not just the small sample. Interactions (hover, click, keyboard focus) do not cause noticeable lag or frame drops.

**What it includes:**
*   Profiling data identifying the specific bottleneck (layout computation time, DOM node creation/update cost, or Svelte re-render overhead).
*   Code changes that address that specific bottleneck. This may involve:
    *   Optimizing the `radialLayout` algorithm if it is the primary cost (e.g., caching calculations, reducing iterations).
    *   Reducing the number of DOM nodes rendered (e.g., virtualization, culling off-screen nodes, or simplifying node representations).
    *   Improving Svelte reactivity to minimize unnecessary updates (e.g., using `$derived` more effectively, avoiding deep object mutations).
*   A clear explanation in your PR description of *why* the chosen optimization was selected and how it was verified.

**What has to be done:**
1.  **Measure:** Use browser DevTools (Performance tab, Memory tab) to profile the graph rendering with a larger dataset. Identify the top time-consuming function.
2.  **Analyze:** Determine if the bottleneck is in `radialLayout` (CPU), in the DOM updates (paint/layout), or in Svelte's reactivity system (JS execution).
3.  **Optimize:** Implement a targeted fix. Do not blindly add `requestAnimationFrame` or `debounce` without evidence they solve the identified problem.
4.  **Verify:** Re-profile to confirm the improvement. Ensure keyboard accessibility and visual legibility are preserved.

*Note: The `tasks.md` prose for this item is present and has been reconciled above. The note about the orphaned "Task 4 - Animation" is acknowledged as a separate site inconsistency and is **not** included in this task's scope. This task is strictly about layout and performance.*

## 4. Success criteria (functional)

This task does not close a specific numbered Acceptance Criterion from the module `ASSIGNMENT.md` in the same way a feature task does, but it must satisfy the underlying constraints that enable the other criteria to be met at scale:

*   **Constraint Compliance:** The solution must continue to use `radialLayout` from `./layout.ts` exactly. You may not fork the file or reimplement the math in the `.svelte` file. If you optimize, you must do so within the constraints of the existing API or by proving a genuine shared-function bug (which is unlikely for a layout function).
*   **Accessibility Preservation:** The optimization must not break keyboard operability. Every visible node must still be focusable (`role="button"`, `tabindex`, `aria-label`). If you cull nodes, you must ensure that the remaining nodes are still navigable and that the "next" focus target is sensible.
*   **State Integrity:** The reactive state (`$state` / `$derived`) must remain consistent. Optimizations must not introduce race conditions or stale data in the selection or filter state.

## 5. Quality criteria (the part that's new)

*   **Evidence-Based Optimization:** Your PR must include profiling data (screenshots or metrics) showing the bottleneck before and after your change. "It feels faster" is not sufficient.
*   **Code Organization:** Any new performance-related code (e.g., caching, virtualization logic) must be clearly separated from the core layout math. Do not clutter `layout.ts` with UI-specific performance hacks.
*   **AI-Use/Process Documentation:** If you used AI to suggest optimizations, document the specific prompts and the reasoning behind accepting or rejecting the suggestions. Show your critical evaluation of the AI's output.
*   **Testing:** While this is a performance task, you must ensure that your changes do not break existing unit tests for `layout.ts`. If you add new logic, write unit tests for that logic. Link to [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/) for guidance on testing performance-critical code (e.g., using mocks to simulate large datasets in tests).
*   **Accessibility:** Adhere to the global Definition of Done: keyboard-operable, one accessible name or label, no meaning carried by color alone, respects reduced-motion preferences. If your optimization involves animations (e.g., staggered entry), it must respect `prefers-reduced-motion`.
*   **Oral Defense:** Be prepared to explain *why* you chose your specific optimization. Why not virtualization? Why not Web Workers? Why not a different layout algorithm? Defend your decision based on the profiling data and the constraints of the module.

## Closing

> "The browser does not judge your aesthetics. Only your kilobytes."
> — TTOD `img-025`, *images*

This task is a direct application of this principle: the graph's beauty is irrelevant if the browser cannot render it quickly enough. Your job is to ensure the "kilobytes" (or rather, the computational cost) are optimized so that the user experiences the graph, not the lag.