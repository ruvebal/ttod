# Assignment — Team 2, Task 4: URL state for the current selection/filter

**Seam:** graph · **Team:** 2 · **Task:** 4 of ~10
**Area(s):** Graph · **Verb served:** keep

## 1. Curriculum map

This task exercises the client-side state management and browser API integration concepts covered in **Unit 3 — Routing and State** of the web-atelier-udit FE II curriculum. Specifically, it applies the principles of deriving UI state from the URL and handling browser history events (`popstate`) to maintain a single source of truth for the application's view.

## 2. Worked example, from the real TTOD app

The current `GraphIsland.svelte` implementation on the `ts5` assembly worktree demonstrates the reactive foundation required for this task. It uses Svelte 5 runes (`$state`, `$derived`) to manage the `selectedNode` and `activeTag` (currently hardcoded or absent in the hello-world cut). The `layout.ts` file already exports `selectedTag` and `filterGraph`, which are the exact utility functions this task must integrate with. The existing `<aside>` element that displays the selected node's text serves as the visual target for the "selection" part of the URL state, while the (currently missing) tag filter UI will be the target for the "filter" part.

## 3. What "done" looks like

**Visible result:** The current tag filter and node selection are reflected in the address bar. Reloading the page or hitting the browser's back/forward buttons restores the exact same visible neighborhood and selection state.

**What it includes:**
*   Reading and writing query parameters (`?tag=...`, `?node=...`).
*   Handling the browser's `popstate` event to sync internal state with URL changes.
*   A consistent URL shape (e.g., `?tag=architecture&node=arch-031`).

**What has to be done:**
1.  **Define the URL contract:** Decide on the parameter names (e.g., `tag`, `node`) and their expected values (tag ID, node ID).
2.  **Implement `syncFromUrl`:** On initial load and on `popstate` events, parse the URL query string to determine the active tag and selected node.
3.  **Implement `setTag`/`setNode`:** When the user changes the filter or selection, update the URL using `history.pushState` (or `replaceState` for initial load) without triggering a full page reload.
4.  **Integrate with `layout.ts`:** Use the existing `selectedTag` and `filterGraph` functions to ensure the graph rendering matches the URL state.
5.  **Handle edge cases:** Ensure that invalid tag/node IDs in the URL are handled gracefully (e.g., reset to default state) and that clearing the filter removes the `tag` parameter from the URL.

## 4. Success criteria (functional)

1.  **Tag filter is reflected in the URL.** Choosing a tag writes `?tag={value}` (and clearing the filter removes the param). Reloading and using the browser back/forward buttons restore the same visible neighborhood.
2.  **URL state drives rendering.** The graph displayed on load matches the tag and node specified in the URL query parameters.
3.  **Back/Forward navigation works.** Using the browser's back/forward buttons updates the graph view and selection state without requiring a manual refresh.
4.  **Invalid state handling.** If the URL contains an invalid tag or node ID, the application resets to a valid default state (e.g., no filter, no selection) without crashing.

## 5. Quality criteria (the part that's new)

*   **Code organization:** The URL sync logic should be encapsulated in a dedicated module or composable (e.g., `useUrlState.ts`) to keep `GraphIsland.svelte` focused on rendering. This aligns with the module's constraint to keep `layout.ts` pure and shared.
*   **AI-use/process documentation:** Document the decision to use `pushState` vs `replaceState` and how `popstate` is handled. Explain why the URL is the source of truth for filter/selection state.
*   **Test shape:** Per R7's Trophy-not-Pyramid doctrine, write integration tests that simulate user interactions (clicking a tag, selecting a node) and assert that the URL updates correctly. Write unit tests for the `syncFromUrl` and `setTag`/`setNode` functions to verify they parse and generate the correct query strings. Link to [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/) for guidance on testing browser API interactions.
*   **Accessibility:** Ensure that the URL state changes do not disrupt keyboard focus. If the filter changes and the previously selected node is no longer visible, move focus to a sensible next target (e.g., the first visible node or the filter control) as per the module's Acceptance Criteria #3. Cite the global Accessibility Definition of Done: keyboard-operable, one accessible name or label, no meaning carried by color alone, respects reduced-motion preferences.
*   **Oral defense:** Be prepared to explain why the URL is a better source of truth for filter/selection state than local component state (shareability, persistence, back/forward support). Discuss how you handled the `popstate` event to avoid infinite loops or state desynchronization.

## Closing

> "The best navigation is one you forget is there—until you need it."
> — TTOD `arch-016`, *architecture*

This task ensures that the graph's state is always recoverable and shareable via the URL, making the navigation invisible until the user needs to restore or share a specific view.