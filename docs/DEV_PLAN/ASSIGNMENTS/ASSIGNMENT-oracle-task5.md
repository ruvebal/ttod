# Assignment — Team 3, Task 5: A "preparing" cold-start state instead of a silent hang on a fresh deployment

**Seam:** oracle · **Team:** 3 · **Task:** 5 of ~10
**Area(s):** Oracle · **Verb served:** keep

## 1. Curriculum map

This task exercises the FE II unit on **State Management and Asynchronous UI Patterns**, specifically the distinction between *loading*, *error*, and *empty* states. While the primary streaming logic is covered in [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/) (for the verification of state transitions), the UI design of the cold-start state aligns with general FE II principles on **Perceived Performance and User Feedback**.

*Note: A specific "Cold-Start UI Design" unit link is not yet published in the `assignments.md` "Lessons for these tasks" section for this specific task; therefore, we cite the broader FE II unit on asynchronous state handling which is the prerequisite for this work.*

## 2. Worked example, from the real TTOD app

The current `hello-world` implementation in `services/frontend/src/components/oracle/` demonstrates the *absence* of this state. When the `OracleQueryPayload` is sent, the UI currently relies on the `busy/double-submit guard` mentioned in the module brief. However, there is no distinct visual or semantic state for the period between the user clicking "Ask" and the first `OracleResponseChunk` arriving via `readOracleStream`.

The real code in `sse.ts` (specifically `readOracleStream`) does not emit a "preparing" event; it waits for the server to begin streaming. Therefore, the "worked example" is the **gap** in the current `OracleTerminal` component: the user sees a static input field, clicks, and then waits in silence. This task requires you to introduce a new UI state *before* the first chunk arrives, distinct from the "streaming" state that follows.

## 3. What "done" looks like

`docs/public/teaching/tasks.md` contains no existing prose for this specific item (Task 5). Therefore, this definition is grounded entirely in the module `ASSIGNMENT.md` and the board title.

**Visible result:**
When a user submits a query on a fresh deployment (or when the model is cold), the Oracle terminal does not appear frozen or broken. Instead, it displays a distinct "Preparing" state. This state must be visually and semantically distinct from:
1.  The **Idle** state (no query active).
2.  The **Streaming** state (chunks are arriving).
3.  The **Error** state (Task 6, which handles failures).

**What it includes:**
*   A clear, non-color-dependent indicator that the system is working (e.g., a spinner, a skeleton loader, or a text label like "Consulting the Oracle...").
*   The input field remains disabled or clearly marked as "processing" to prevent double-submission (leveraging the existing `busy` guard logic).
*   The state must be accessible: screen readers must announce the transition to "preparing" and then to "streaming" or "error" appropriately.

**What has to be done:**
1.  Identify the point in the `OracleTerminal` component where the `fetch` or `readOracleStream` call is initiated but before the first `onChunk` callback fires.
2.  Introduce a new UI state (e.g., `status: 'preparing'`) in the component's local state management.
3.  Render a distinct UI element for this state. This element must not be a generic "loading" spinner that is identical to other loading states in the app; it should convey the specific nature of the Oracle's work (e.g., "Gathering wisdom...").
4.  Ensure the transition from `preparing` to `streaming` (when the first chunk arrives) is smooth and does not cause layout shift.
5.  Ensure the `preparing` state is *not* triggered if the request fails immediately (that is Task 6's domain).

## 4. Success criteria (functional)

*   **Distinct State:** The UI must render a unique visual/semantic state for the "preparing" phase that is not identical to the "idle" or "streaming" states.
*   **No Silent Hang:** A user observing the terminal during a cold start must be able to determine that the system is actively processing their request, not frozen or broken.
*   **State Transition:** The "preparing" state must automatically transition to the "streaming" state upon receipt of the first `OracleResponseChunk` from `readOracleStream`.
*   **Guard Integration:** The existing `busy/double-submit guard` must remain functional; the "preparing" state must be part of the `busy` logic, preventing new submissions.

## 5. Quality criteria (the part that's new)

*   **Code Organization:** The "preparing" state logic should be encapsulated within the `OracleTerminal` component or a dedicated hook (e.g., `useOracleState`) that manages the lifecycle of the query. Do not scatter `isPreparing` flags across multiple components.
*   **AI-Use/Process Documentation:** Document in your PR description *why* you chose a specific visual representation for "preparing" (e.g., "Chose a pulsing text label over a spinner to convey 'thinking' rather than 'downloading'"). This demonstrates design intent, not just implementation.
*   **Test Shape (R7 Trophy-not-Pyramid):**
    *   **Unit Test:** Mock `readOracleStream` to delay the first chunk by 500ms. Assert that the component renders the "preparing" UI element during this delay.
    *   **Component Test:** Assert that the "preparing" state is *not* rendered if the stream errors immediately (to ensure separation from Task 6).
    *   **Accessibility Test:** Assert that the "preparing" element has an appropriate `aria-live` region or `role="status"` so screen readers announce the change.
    *   *Link:* [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/)
*   **Accessibility:** The "preparing" state must respect the global Definition of Done: keyboard-operable (though not interactive, it must not trap focus), one accessible name (e.g., `aria-label="Preparing Oracle response"`), no meaning carried by color alone (use text or iconography), and respects reduced-motion preferences (if using animation, provide a static fallback).
*   **Oral Defense:** Be prepared to explain the difference between a "cold start" (model loading) and a "network delay" (slow connection). How does your UI distinguish between them? (Hint: It may not need to, but you must articulate the assumption that *any* delay before the first chunk is treated as "preparing" for the sake of user confidence.)

## Closing

> "An empty field is not an error—it is an incomplete promise. Code can be perfect, but data can be absent."
> — TTOD `arch-019`, *architecture*

The "preparing" state is the UI's acknowledgment of that incomplete promise: the code is ready, the data (the model's response) is not yet here, and the user must be told that the wait is intentional, not a failure.