# Assignment — Team 3, Task 6: Recovery/error state when the Oracle is unavailable

**Seam:** oracle · **Team:** 3 · **Task:** 6 of ~10
**Area(s):** Oracle · **Verb served:** keep

## 1. Curriculum map

This task exercises the FE II unit on **Error Handling and Resilience**, specifically the distinction between transient states (loading/cold-start) and terminal states (failure). While the specific lesson link for "Oracle Error States" is not yet published in the `web-atelier-udit` FE II curriculum, this task directly applies the principles found in [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/) regarding verifying failure modes, and aligns with the general FE II focus on **Robust User Interfaces**.

## 2. Worked example, from the real TTOD app

The current `hello-world` implementation in `services/frontend/src/components/oracle/OracleTerminal.tsx` handles the *happy path* of streaming. It currently lacks explicit UI states for `network failure` or `5xx` responses. The `readOracleStream` helper in the colocated `sse.ts` throws or returns an error status, but the React component does not yet distinguish between a "cold start" (where the backend is alive but the model is loading) and a "hard failure" (where the backend is unreachable or returning 5xx). This task requires extending the component's state machine to explicitly render these two distinct failure modes, using the existing `OracleResponseChunk` types in `types/domain.ts` to determine the error type.

## 3. What "done" looks like

**Visible result:** When the Oracle is genuinely unavailable (not just cold-starting), the UI displays a clear, human-readable error message instead of hanging indefinitely or showing a raw JSON error.

**What it includes:**
*   **State Distinction:** The UI must explicitly distinguish between:
    1.  **"Still warming up" (Cold Start):** The backend is reachable, but the model is not yet ready. This state should show a "Preparing..." indicator, not an error.
    2.  **"Actually broken" (Unavailable):** The backend is unreachable (network error) or returns a 5xx status. This state must show a clear error message and a "Retry" action.
*   **Deliberate Triggering:** The implementation must be testable by:
    *   Killing the backend process to simulate a network failure.
    *   Simulating a cold Ollama volume (or using a mock that delays response) to simulate a cold start.

**What has to be done:**
1.  Extend the Oracle component's state management to include explicit `error` and `loading` states.
2.  Implement logic to differentiate between a `fetch` network error (unreachable) and a `5xx` HTTP response (server error) vs. a `200` response with a "loading" chunk (cold start).
3.  Render distinct UI components for each state:
    *   **Cold Start:** A spinner or "Preparing..." text.
    *   **Unavailable:** An error icon, a message like "The Oracle is currently unavailable," and a "Try Again" button.
4.  Ensure the error state is accessible (see Quality Criteria).

## 4. Success criteria (functional)

*   **Unreachable Oracle:** When the network is down or the backend returns a 5xx, the UI displays a clear error message and a "Retry" button. It does **not** hang indefinitely.
*   **Cold Start:** When the backend is alive but the model is loading, the UI displays a "Preparing..." state. It does **not** display an error message.
*   **Recovery:** Clicking "Retry" in the error state re-attempts the request. If the backend is now available, the stream begins normally.
*   **No Raw Errors:** The user never sees raw JSON, stack traces, or HTTP status codes in the UI.

## 5. Quality criteria (the part that's new)

*   **Code Organization:** The error handling logic should be encapsulated in the Oracle component or a dedicated hook (e.g., `useOracleStream`), not scattered across the page. The state machine should be explicit: `idle` → `loading` → `streaming` → `complete` | `error`.
*   **AI-Use/Process Documentation:** Document the distinction between "cold start" and "unavailable" in the component's JSDoc or a nearby `README.md` snippet. Explain *why* these are different states and how the UI responds to each.
*   **Test Shape (Trophy-not-Pyramid):** Write a component test that mocks `fetch` to return a 5xx error and asserts that the "Unavailable" UI is rendered. Write another test that mocks `fetch` to return a 200 with a "loading" chunk and asserts that the "Preparing..." UI is rendered. Link these tests to [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/).
*   **Accessibility:** The error state must be announced to screen readers. Use `role="alert"` or `aria-live="assertive"` on the error message container. The "Retry" button must be keyboard-focusable and have a clear accessible name. Ensure the error state does not rely on color alone to convey failure (use an icon or text label). This inherits the global Definition of Done: keyboard-operable, one accessible name, no meaning carried by color alone, respects reduced-motion preferences.
*   **Oral Defense:** Be prepared to explain how you distinguished between a "cold start" and a "hard failure" at the network level. How did you ensure the UI didn't flash an error during a legitimate cold start? How did you make the error state accessible to non-sighted users?

## Closing

> "Verify Before You Fix - Not every symptom is a disease."
> — TTOD `arch-027`, *architecture*

A cold-starting Oracle looks like a broken one if you only watch the symptom — silence. This task is the discipline of verifying which condition you actually have before prescribing a "Retry" button: a real failure is a disease; a warm-up delay is not.