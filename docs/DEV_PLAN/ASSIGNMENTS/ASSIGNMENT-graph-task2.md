# Assignment — Team 2, Task 2: One accessible node selection reflected as text, not just a visual highlight

**Seam:** graph · **Team:** 2 · **Task:** 2 of ~10
**Area(s):** Graph · **Verb served:** question

## 1. Curriculum map

This task exercises the core principles of **SVG accessibility** and **state-driven UI** found in FE II. While specific unit links for "accessible node selection" are not yet published in the `assignments.md` "Lessons for these tasks" section, this work directly applies the accessibility standards defined in the module's Definition of Done. It reinforces the principle that interactive elements must be operable via keyboard and screen readers, a foundational concept in web development curricula.

## 2. Worked example, from the real TTOD app

The hello-world implementation on the `ts5` assembly worktree already contains the foundational pattern for this task. In `services/frontend/src/pages/[locale]/wisdom/GraphIsland.svelte` (or the equivalent graph island component), the code currently implements:

1.  **Focusable Nodes:** Each SVG `<circle>` or `<g>` element representing a node has `role="button"`, `tabindex="0"`, and a descriptive `aria-label`.
2.  **Keyboard Events:** Event listeners for `keydown` handle `Enter` and `Space` to trigger selection, mirroring the `click` event.
3.  **Text Reflection:** Upon selection, the component updates a reactive state variable (e.g., `selectedNode`) which drives the content of an `<aside>` element. This `<aside>` displays the node's `text` property, ensuring the selection is reflected as readable text, not just a visual highlight (e.g., a stroke change).

This existing pattern is the baseline. The task is to **confirm, harden, and extend** this pattern to ensure it remains robust as the graph grows and as other features (like filtering) are added.

## 3. What "done" looks like

*Note: No existing prose for this specific item exists in `docs/public/teaching/tasks.md`. The following is grounded in the module's `ASSIGNMENT.md` and the current hello-world state.*

**Visible result:**
When a user selects a node via mouse click or keyboard (Tab to focus, Enter/Space to select), the node’s associated text content is immediately displayed in a clearly labeled, accessible `<aside>` panel adjacent to the graph. The visual highlight (e.g., stroke color, size) is secondary to the textual feedback.

**What it includes:**
1.  **Preserved Accessibility Attributes:** Every node retains `role="button"`, `tabindex`, and a unique, descriptive `aria-label` (e.g., "Node: [Name], Tag: [Tag]").
2.  **Keyboard Parity:** Selection is fully operable via keyboard. Focus management is sensible; selecting a node does not trap focus, and the `<aside>` content is announced by screen readers (using `aria-live="polite"` or equivalent on the text container).
3.  **No Color-Only Meaning:** The selection state is not conveyed solely by color. The textual reflection in the `<aside>` is the primary indicator of "selected" state.
4.  **Reduced Motion Respect:** Any visual transitions associated with selection (e.g., stroke animation) respect `prefers-reduced-motion`.
5.  **Integration Readiness:** The selection state is reactive (Svelte `$state`/`$derived`) and ready to be consumed by future tasks (e.g., URL state, filtering) without breaking the accessibility contract.

**What has to be done:**
1.  **Audit Existing Code:** Review `GraphIsland.svelte` to verify that `aria-label` is dynamic and descriptive (not just "Node 1").
2.  **Harden Keyboard Handling:** Ensure `keydown` listeners correctly prevent default scrolling on `Space` and trigger selection on `Enter`/`Space`. Verify that `blur` or `focusout` does not inadvertently clear the selection if the user moves focus to the `<aside>`.
3.  **Enhance Text Reflection:** Ensure the `<aside>` has a clear heading (e.g., "Selected Node") and that the text content updates reactively. Add `aria-live="polite"` to the text container so screen readers announce changes.
4.  **Verify Reduced Motion:** If any CSS transitions or GSAP animations are applied to the selected node, ensure they are disabled or minimized when `prefers-reduced-motion` is set.
5.  **Test with Screen Reader:** Manually test with a screen reader (e.g., NVDA, VoiceOver) to confirm that selecting a node via keyboard announces the node name and that the `<aside>` content is read aloud.

## 4. Success criteria (functional)

1.  **Keyboard Selection Works:** Pressing `Enter` or `Space` on a focused node updates the `<aside>` text to that node’s `text` property.
2.  **Click Selection Works:** Clicking a node updates the `<aside>` text to that node’s `text` property.
3.  **Accessible Name Present:** Every node has a unique, descriptive `aria-label` that includes the node’s name and, if available, its tag.
4.  **Screen Reader Announcement:** Changes to the `<aside>` text are announced by screen readers (verified via `aria-live` or equivalent).
5.  **No Focus Trap:** After selecting a node, focus remains on the node or moves to a logical next element (e.g., the `<aside>` heading) without trapping the user.
6.  **Reduced Motion Compliance:** Visual selection effects (e.g., stroke animation) are disabled or reduced when `prefers-reduced-motion` is enabled.

## 5. Quality criteria (the part that's new)

*   **Code Organization:** The selection logic is encapsulated in the `GraphIsland.svelte` component. The `<aside>` is a separate, accessible component or clearly marked section. No global state pollution; selection is local to the island.
*   **AI-Use/Process Documentation:** Any AI-assisted code generation for accessibility attributes (e.g., `aria-label` templates) is documented in the PR description, explaining *why* specific attributes were chosen.
*   **Test Shape:** Per R7’s Trophy-not-Pyramid doctrine, tests should focus on **behavioral outcomes** (e.g., "selecting a node updates the aside text") rather than implementation details (e.g., "clicking a circle triggers a function"). Use testing libraries that simulate user interaction (e.g., `@testing-library/svelte`) to verify accessibility attributes and text updates.
*   **Accessibility:** This task inherits the global Definition of Done: keyboard-operable, one accessible name or label, no meaning carried by color alone, respects reduced-motion preferences. This is not a task-specific requirement but a baseline for all TTOD work.
*   **Defensible Oral-Defense Answer:** "I ensured that node selection is not just a visual highlight but a semantic event. By using `aria-live` on the text reflection and maintaining keyboard parity, I made the graph accessible to users who rely on screen readers or keyboard navigation. This aligns with the principle that accessibility is a foundation, not a feature."

**Testing Link:** [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/)

## Closing

> "Accessibility is not a feature. It is the foundation upon which all features rest."
> — TTOD `a11y-001`, *accessibility*

This task embodies that principle by ensuring that the core interaction of node selection is accessible from the start, not bolted on later.