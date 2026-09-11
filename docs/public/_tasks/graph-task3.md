---
title: "Tag-filter interaction"
seam: graph
team_number: 2
team_name: "Knowledge Graph"
task_number: 3
area: "Graph"
verb: question
layout: default
lang: en
---

# Assignment — Team 2, Task 3: Tag-filter interaction

**Seam:** graph · **Team:** 2 · **Task:** 3 of ~10
**Area(s):** Graph · **Verb served:** question

## 1. Curriculum map

This task exercises the core principles of **Svelte 5 Runes** and **Reactive State Management** within a Web Atelier FE II context. Specifically, it maps to the unit covering **Client-Side Interactivity and State Synchronization**.

*Note: The specific unit link for "Svelte 5 Runes & Reactive Filtering" is not yet published in the `assignments.md` "Lessons for these tasks" section. Per skill discipline, we do not invent a link. The underlying concepts align with the general FE II curriculum on client-side state management.*

## 2. Worked example, from the real TTOD app

The foundation for this task already exists in the `ts5` assembly worktree. In `services/frontend/src/pages/[locale]/wisdom/components/graph/layout.ts`, the functions `filterGraph` and `selectedTag` are already implemented and exported.

Currently, `GraphIsland.svelte` does **not** call these functions. The hello-world state renders the full graph via `radialLayout` but lacks any filtering mechanism. This task requires wiring the existing, tested `filterGraph` logic into the UI, rather than writing new filtering algorithms. The "worked example" is the successful execution of `filterGraph` in the unit tests (`layout.test.mjs`), which proves the logic is sound; the student's job is to bridge the gap between this tested logic and the reactive UI layer.

## 3. What "done" looks like

**Visible result:**
A dropdown (or equivalent accessible control) appears in the graph island. Selecting a tag from this control narrows the visible graph to the neighborhood of nodes associated with that tag. Clearing the selection restores the full graph view.

**What it includes:**
- A reactive state variable (e.g., `activeTag`) in `GraphIsland.svelte` that drives the filter.
- A UI control (native `<select>` or accessible combobox) bound to this state.
- A call to `filterGraph` from `layout.ts` that generates the filtered node/edge set based on the current `activeTag`.
- Re-rendering of the SVG graph to reflect only the filtered nodes and their connections.
- Preservation of the existing selection `<aside>` behavior: if a node is selected, its details remain visible if it is part of the filtered set; if the selected node is filtered out, the selection state should be cleared or handled gracefully to avoid dangling references.

**What has to be done:**
1.  Identify the list of available tags from the fetched graph data (likely derived from the node metadata or a separate tag list in the payload).
2.  Implement the UI control in `GraphIsland.svelte` using Svelte 5 runes (`$state`, `$derived`).
3.  Wire the control's change event to update the `activeTag` state.
4.  Use `$derived` to compute the filtered graph by calling `filterGraph` with the current `activeTag`.
5.  Ensure the SVG rendering loop iterates over the filtered nodes/edges, not the raw payload.
6.  Verify that clearing the filter (selecting "All" or empty value) restores the full graph.

*Note: `docs/public/teaching/tasks.md` contains prose for this item, which has been reconciled above. The prose correctly identifies that `filterGraph` and `selectedTag` exist but are uncalled. This task sheet expands on the "what has to be done" by specifying the reactive wiring required.*

## 4. Success criteria (functional)

These criteria are drawn directly from the parent module `ASSIGNMENT.md` (Graph seam) and apply specifically to the tag-filter interaction:

1.  **Tag filter is reflected in the URL.** Choosing a tag writes `?tag={value}` (and clearing the filter removes the param). Reloading and using the browser back/forward buttons restore the same visible neighborhood.
    *   *Note: While URL state is a separate task (Task 4), the filter interaction itself must be structured to support this. The `activeTag` state must be the single source of truth for the filter.*
2.  **Keyboard parity is preserved.** Every visible node still has `role="button"`, `tabindex`, `aria-label`, and Enter/Space selection. Filtering must not leave focus on a removed node without a sensible next target.
    *   *Specific to this task: When the filter changes and nodes are removed, if the currently focused node is removed, focus must move to a sensible alternative (e.g., the first visible node, or the filter control itself) to prevent focus loss.*
3.  **Layout stays shared.** The rendered positions still come from `radialLayout` after `joinTags` (and `filterGraph` when a tag is active). A hand-placed SVG or a second layout helper fails this criterion.
    *   *Specific to this task: The filtered subset must be passed through `radialLayout` (or the layout must be re-computed for the filtered subset) to ensure correct spatial relationships within the filtered neighborhood.*
4.  **Hello-world selection still works:** Clicking **or** pressing Enter/Space on one node shows its `text` in the `<aside>`.
    *   *Specific to this task: This must continue to work even when a filter is active. If the selected node is filtered out, the selection should be cleared to avoid displaying stale data.*

## 5. Quality criteria (the part that's new)

-   **Code Organization:** The filtering logic must remain in `layout.ts`. The `GraphIsland.svelte` component should only contain UI state and rendering logic. Do not duplicate the filtering algorithm in the Svelte file.
-   **AI-Use/Process Documentation:** If using AI assistance to generate the Svelte runes or accessibility attributes, document the specific prompts used and the verification steps taken to ensure the generated code adheres to the module's constraints (e.g., no forbidden shortcuts).
-   **Test Shape (R7 Trophy-not-Pyramid):**
    -   **Unit Tests:** Extend `layout.test.mjs` if new edge cases for `filterGraph` are discovered (e.g., filtering by a tag with no nodes).
    -   **Component Tests:** Write a test for `GraphIsland.svelte` that simulates changing the `activeTag` state and asserts that the rendered SVG contains only the expected nodes. Use a testing library that supports Svelte 5 runes (e.g., Vitest with Svelte plugin).
    -   **Integration Test:** Verify that selecting a tag in the UI updates the `activeTag` state and triggers a re-render.
    -   *Link: [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/)*
-   **Accessibility:**
    -   The filter control must have an accessible name (e.g., `<label for="tag-filter">Filter by tag</label>`).
    -   The control must be keyboard operable (Tab to focus, Arrow keys to navigate options, Enter to select).
    -   When the filter changes, announce the change to screen readers (e.g., `aria-live="polite"` region announcing "Filtered to tag: X").
    -   *Inherited Definition of Done: keyboard-operable, one accessible name or label, no meaning carried by color alone, respects reduced-motion preferences.*
-   **Oral Defense Answer:** "I wired the existing `filterGraph` logic into the Svelte 5 reactive state. I ensured that the filter control is accessible and that focus management is handled when nodes are removed. I did not reimplement the filtering logic; I reused the tested function from `layout.ts` to maintain a single source of truth for the graph's topology."

## Closing

> "The best navigation is one you forget is there—until you need it."
> — TTOD `arch-016`, *Architecture*

This task is about making the filter control invisible in its complexity: the student should not have to think about *how* the graph is filtered, only *what* they want to see. The underlying `filterGraph` logic is the "navigation" that should be forgotten, allowing the user to focus on the content.