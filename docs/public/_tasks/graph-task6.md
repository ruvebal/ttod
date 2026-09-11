---
title: "Keyboard operability audit on every interactive graph element"
seam: graph
team_number: 2
team_name: "Knowledge Graph"
task_number: 6
area: "Testing"
verb: keep
layout: default
lang: en
---

# Assignment — Team 2, Task 6: Keyboard operability audit on every interactive graph element

**Seam:** graph · **Team:** 2 · **Task:** 6 of ~10
**Area(s):** Testing · **Verb served:** keep

## 1. Curriculum map

This task exercises the accessibility and testing foundations covered in **Unit 5 — Testing strategy** (https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/). While the primary implementation work for the graph island aligns with Svelte 5 runes and SVG accessibility concepts from earlier units, this specific task focuses on the *verification* and *audit* phase, which is the core competency of Unit 5. It requires moving beyond "does it work for me?" to "does it work for everyone, and can I prove it?"

## 2. Worked example, from the real TTOD app

The existing hello-world implementation in `services/frontend/src/pages/[locale]/wisdom/ASSIGNMENT.md` (referenced as the graph island context) and the actual `GraphIsland.svelte` component on the `ts5` worktree already establishes the baseline pattern. Specifically, the node circles in the SVG already implement:
- `role="button"`
- `tabindex="0"` (or equivalent focusable state)
- `aria-label` derived from the node's text content
- Event listeners for `keydown` handling `Enter` and `Space` keys to trigger selection.

This task is not about building this from scratch, but about **auditing** this existing pattern to ensure it remains intact as new features (like the tag filter from Task 3) are added, and extending this exact same pattern to the new filter control (e.g., a `<select>` or custom combobox) that will be introduced. The "worked example" is the current, working keyboard interaction on the nodes, which serves as the standard against which the new filter control must be measured.

## 3. What "done" looks like

**Visible result:** Every interactive graph element (nodes, the filter control) is fully operable by keyboard alone, with visible focus at every step.

**What it includes:**
- The existing hello-world selection already has `role=button`, `tabindex`, and `onkeydown` — the audit is confirming nothing you add breaks that.
- Extending the same pattern to your new filter control (e.g., ensuring the `<select>` or equivalent is focusable, has a clear label, and responds to keyboard navigation).
- Verifying that focus management is sensible when filtering (e.g., if a node is removed from the DOM due to filtering, focus should not be lost into the void; it should move to a sensible next target, such as the filter control itself or the first remaining node).

**What has to be done:**
- Tab through the entire graph experience with a keyboard only.
- Identify and fix any point where focus is lost or an action is mouse-only.
- Ensure the new filter control (from Task 3) is fully keyboard-accessible, including focus visibility and keyboard-operable selection.
- Document the audit process and any fixes made, linking to the specific lines of code or components where the audit was performed.

## 4. Success criteria (functional)

- **Keyboard parity is preserved.** Every visible node still has `role="button"`, `tabindex`, `aria-label`, and Enter/Space selection. Filtering must not leave focus on a removed node without a sensible next target.
- **The new filter control is keyboard-operable.** It must be focusable, have a clear accessible name, and allow selection via keyboard (e.g., arrow keys for `<select>`, or Enter/Space for custom controls).
- **Focus management is robust.** When filtering changes the visible set of nodes, focus is not lost. If the currently focused node is removed, focus moves to a sensible alternative (e.g., the filter control, the first remaining node, or a container element).

## 5. Quality criteria (the part that's new)

- **Code organization:** The keyboard event handlers and accessibility attributes should be consistent across all interactive elements. Avoid duplicating logic; consider a shared utility or composable if the pattern is repeated.
- **AI-use/process documentation discipline:** Document the audit process. Include a brief note in the PR description or a dedicated section in the task sheet detailing the steps taken to verify keyboard operability (e.g., "Tabbed through all nodes, verified Enter/Space selection, tested filter control with arrow keys, confirmed focus retention after filtering").
- **Test shape per [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/) and R7's own Trophy-not-Pyramid doctrine:** While this is an audit task, consider adding a simple integration test that simulates keyboard navigation (e.g., using `@testing-library/svelte` or similar) to verify that key events trigger the expected state changes. This is not a full unit test suite, but a targeted check that the keyboard handlers are wired correctly.
- **Accessibility:** Every module inherits the same Definition of Done per `assignments.md` — do not restate it as if it were unique to this task, cite it. The Definition of Done includes: keyboard-operable, one accessible name or label, no meaning carried by color alone, respects reduced-motion preferences. This task specifically focuses on the "keyboard-operable" and "one accessible name or label" aspects.
- **Defensible oral-defense answer:** Be prepared to explain *why* keyboard operability is critical (accessibility, efficiency for power users, compliance). Be able to describe the specific patterns used (e.g., `role="button"`, `tabindex`, `aria-label`) and how they were applied consistently. Be able to discuss the focus management strategy when filtering removes nodes.

## Closing

> "Accessibility is not a feature. It is the foundation upon which all features rest."
> — TTOD `a11y-001`, *accessibility*

This task is the practical application of that principle: by auditing and ensuring keyboard operability, you are not adding a "feature" but reinforcing the foundational accessibility that allows all other graph interactions (filtering, selection, layout) to be usable by everyone.