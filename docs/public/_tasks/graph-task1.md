---
title: "Fetch and render the graph from the governed API"
seam: graph
team_number: 2
team_name: "Knowledge Graph"
task_number: 1
area: "Graph"
verb: find
layout: default
lang: en
alt_lang_missing: true
---

# Assignment — Team 2, Task 1: Fetch and render the graph from the governed API

**Seam:** graph · **Team:** 2 · **Task:** 1 of ~10
**Area(s):** Graph · **Verb served:** find

## 1. Curriculum map

This task exercises the core concepts of **Svelte 5 runes** (`$state`, `$derived`) and **Island hydration** in Astro, as defined in the module's Learning Outcomes. While the specific "Lessons for these tasks" links for this exact task are not yet published in `docs/public/teaching/assignments.md`, the underlying competencies align with the FE II units covering reactive state management and component integration.

## 2. Worked example, from the real TTOD app

The baseline for this task is already present in the reference implementation. The file `services/frontend/src/components/graph/GraphIsland.svelte` demonstrates the required pattern:
1.  It mounts via `client:load` from `pages/[locale]/graph.astro`.
2.  It performs a client-side `fetch` to `GET /api/v1/graph` and `GET /api/v1/wisdom/sample`.
3.  It processes the payload using `joinTags` and `radialLayout` from `./layout.ts`.
4.  It renders the resulting nodes as SVG elements and handles a single click/keyboard selection to update an accessible `<aside>`.

This existing implementation is the "hello-world" state. The task is to understand, document, and lightly harden this specific fetch-and-render pipeline, ensuring it remains robust and accessible, without adding the filtering or URL-state logic that belongs to Tasks 3 and 4.

## 3. What "done" looks like

*Note: `docs/public/teaching/tasks.md` contains no existing prose for this specific item. The following description is grounded entirely in the module's `ASSIGNMENT.md` hello-world description and constraints.*

**Visible result:**
The graph island loads successfully from the governed API endpoints. All nodes received in the payload are laid out using the shared `radialLayout` function and rendered as SVG elements. The origin-color legend is visible. A single node can be selected via mouse click or keyboard (Enter/Space), and its text content is displayed in the accessible `<aside>` panel.

**What it includes:**
-   A working client-side fetch to `GET /api/v1/graph` and `GET /api/v1/wisdom/sample`.
-   Correct usage of `joinTags` and `radialLayout` from `./layout.ts` to process the data.
-   SVG rendering of nodes with appropriate `role="button"`, `tabindex`, and `aria-label` attributes.
-   A functional selection mechanism that updates the `<aside>` text.
-   Loading and error empty states are present and functional.
-   The code does **not** include tag filtering, URL state synchronization, or animation (these are explicitly excluded from this task).

**What has to be done:**
1.  Verify that the existing `GraphIsland.svelte` correctly fetches and renders the graph without errors.
2.  Ensure that the layout is derived strictly from `radialLayout` and `joinTags` in `layout.ts`; do not reimplement layout logic in the component.
3.  Confirm that keyboard operability is intact: every node is focusable, has an accessible name, and responds to Enter/Space.
4.  Verify that the `<aside>` updates correctly upon selection.
5.  Document the data flow: API response → `joinTags` → `radialLayout` → SVG render → Selection state.
6.  Ensure no prohibited shortcuts are used (e.g., no hardcoded coordinates, no bypassing `layout.ts`).

## 4. Success criteria (functional)

1.  **Layout stays shared.** The rendered positions still come from `radialLayout` after `joinTags`. A hand-placed SVG or a second layout helper fails this criterion.
2.  **Hello-world selection still works.** Clicking **or** pressing Enter/Space on one node shows its `text` in the `<aside>`.
3.  **Keyboard parity is preserved.** Every visible node still has `role="button"`, `tabindex`, `aria-label`, and Enter/Space selection.
4.  **Fetch integrity.** The island successfully fetches from `GET /api/v1/graph` and `GET /api/v1/wisdom/sample` without adding new backend endpoints or editing `services/backend/**`.

## 5. Quality criteria (the part that's new)

-   **Code Organization:** The component must remain a single hydrated Svelte island. State management should use Svelte 5 runes (`$state`, `$derived`) rather than parallel stores. The separation between data fetching, layout calculation (in `layout.ts`), and rendering (in `GraphIsland.svelte`) must be clear.
-   **AI-Use/Process Documentation:** Any AI-assisted code generation must be documented in the commit message or PR description, specifying which parts of the fetch/render logic were generated and how they were verified against the module constraints.
-   **Test Shape:** Per the Testing Trophy (not Pyramid) doctrine, tests should focus on the integration of the fetch and layout pipeline. A test should verify that given a mock API response, the rendered SVG nodes correspond to the output of `radialLayout(joinTags(payload))`. Unit tests for `layout.ts` functions are already present; this task ensures the component correctly consumes them.
-   **Accessibility:** The task inherits the global Definition of Done: keyboard-operable, one accessible name or label, no meaning carried by color alone, respects reduced-motion preferences. Specifically, the `<aside>` must be announced by screen readers when selection changes.
-   **Oral Defense:** A defensible answer for this task explains *why* the layout logic is kept in `layout.ts` (shared, testable, pure) and *how* the island hydration pattern ensures the graph is interactive without blocking initial page load. It should also address how the current selection mechanism meets accessibility standards without relying on visual cues alone.
-   **Testing Strategy:** This task involves verifying the integrity of the data pipeline. Refer to [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/) for guidance on testing reactive components and data flow.

## Closing

> "The module that knows its boundaries serves the whole. The module that knows no boundaries becomes the whole—and collapses under its own weight."
> — TTOD `arch-001`, *Architecture*

This task enforces the boundary between the data-fetching/rendering island and the layout logic, ensuring that `GraphIsland.svelte` remains a focused component that consumes shared, pure functions rather than absorbing layout complexity.