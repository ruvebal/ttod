# Assignment — Team 2, Task 7: Unit and component tests for the graph island

**Seam:** graph · **Team:** 2 · **Task:** 7 of ~10
**Area(s):** Testing · **Verb served:** keep

## 1. Curriculum map

This task exercises the testing strategies outlined in [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/). While the broader graph module touches on Svelte 5 runes and island hydration (covered in earlier units), this specific task isolates the verification layer, applying the "Trophy-not-Pyramid" doctrine to ensure that pure logic is tested fast and rendered behavior is tested only where necessary.

## 2. Worked example, from the real TTOD app

The graph island is implemented in `services/frontend/src/components/graph/GraphIsland.svelte`. It relies on two pure functions exported from `services/frontend/src/components/graph/layout.ts`: `joinTags` and `radialLayout`. Currently, `layout.ts` contains the mathematical logic for polar clustering and tag joining, while `GraphIsland.svelte` handles the reactive state (`$state`/`$derived`) and DOM rendering. The existing `layout.test.mjs` file (referenced in the module constraints) demonstrates the pattern for testing these pure functions in isolation, providing a concrete starting point for extending coverage to the component level.

## 3. What "done" looks like

**Visible result:** The graph island has at least one unit test (targeting a pure function like `filterGraph` or `radialLayout`) and one component test (verifying the island renders and responds to a selection).

**What it includes:** This is the shared Testing Trophy approach every team uses. It distinguishes between fast, isolated logic verification and slower, integration-style DOM interaction checks.

**What has to be done:**
1.  **Unit Test (Pure Logic):** Write a test for a pure function in `layout.ts` (e.g., `radialLayout` or `filterGraph`). This test must run without rendering any DOM, verifying that given a specific graph payload and tag, the returned coordinates or filtered nodes match the expected mathematical output.
2.  **Component Test (Rendered Behavior):** Write a test for `GraphIsland.svelte` that mounts the component. This test must verify that the island renders the expected number of nodes and that simulating a click or keyboard selection on a node updates the accessible `<aside>` with the correct text. This covers the "actual DOM interaction" that unit tests cannot.

*Note: This aligns with the existing prose in `docs/public/teaching/tasks.md` for this item, which explicitly calls for testing pure logic directly and the rendered island only for what a unit test can't cover.*

## 4. Success criteria (functional)

This task does not close a specific functional acceptance criterion from the parent module `ASSIGNMENT.md` (which focuses on tag filtering, URL state, and motion). Instead, it provides the **verification infrastructure** required to prove that the functional criteria (specifically Criterion 3: "Keyboard parity is preserved" and Criterion 5: "Hello-world selection still works") are met.

The functional success of this task is defined by:
1.  The unit test for `radialLayout` (or `filterGraph`) passes, confirming the layout math is deterministic and correct.
2.  The component test for `GraphIsland` passes, confirming that the `role="button"`, `tabindex`, and `aria-label` attributes are present on nodes and that selection updates the `<aside>` content.

## 5. Quality criteria (the part that's new)

*   **Test Shape (Trophy-not-Pyramid):** The unit test must be fast and isolated (no DOM). The component test must be minimal, testing only the interaction that cannot be verified by the unit test (i.e., the binding between the Svelte event handler and the DOM update). Avoid testing internal implementation details; test the public behavior (selection updates the aside).
*   **Accessibility:** Every test must respect the [Accessibility Definition of Done](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/): keyboard-operable, one accessible name or label, no meaning carried by color alone, respects reduced-motion preferences. The component test must explicitly assert that the selected node has an `aria-label` and that the `<aside>` updates with the correct text, ensuring the accessible name is maintained.
*   **AI-Use/Process Documentation:** Document in the test file comments or a companion note *why* the component test is necessary (i.e., "Unit test verifies math; component test verifies DOM binding and accessibility attributes"). This demonstrates the "Trophy" strategy: testing the right layer for the right reason.
*   **Defensible Oral Defense:** A defensible answer explains the distinction between testing `radialLayout` (pure function, fast, no DOM) and testing `GraphIsland` (rendered component, slower, verifies accessibility and interaction). It should cite the module's constraint to "Keep calling `joinTags` and `radialLayout` from `./layout.ts` exactly" and explain how the tests enforce this by verifying the output of these functions without mocking them (if possible) or by mocking the fetch and verifying the rendered output.

## Closing

> "Tests guard the code. Mocks stand in for the cloud. Confidence grows strong."
> — TTOD `qa-019`, *qa-tooling*

This task embodies that principle by guarding the graph island's core logic (layout math) and interaction (selection) with tests, ensuring that the "cloud" (the live API payload) is handled with confidence through deterministic, isolated verification.