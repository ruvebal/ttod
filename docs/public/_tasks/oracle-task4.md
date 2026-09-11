---
title: "Session/exchange history handling"
seam: oracle
team_number: 3
team_name: "Oracle Terminal"
task_number: 4
area: "Oracle"
verb: keep
layout: default
lang: en
---

# Assignment — Team 3, Task 4: Session/exchange history handling

**Seam:** oracle · **Team:** 3 · **Task:** 4 of ~10
**Area(s):** Oracle · **Verb served:** keep

## 1. Curriculum map

This task extends the state management and data flow patterns introduced in [Unit 3 — State and Data](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-3-state-data/). Specifically, it applies the principles of managing complex client-side state (the conversation history) and ensuring that data sent to the server (`sessionHistory`) accurately reflects the user's interaction history. It also reinforces the discipline of consuming existing APIs (the SSE stream) without reinventing the wheel, a core theme of the FE II curriculum regarding integration and reuse.

## 2. Worked example, from the real TTOD app

The current implementation in `services/frontend/src/components/oracle/OracleTerminal.tsx` demonstrates the "single exchange" pattern. It uses `readOracleStream` and `parseSseEvent` from the colocated `sse.ts` to handle the response. The key observation for this task is that `sessionHistory` is currently hardcoded to `[]` in the `OracleQueryPayload` construction. The existing code shows how to *receive* a stream, but not how to *accumulate* state across multiple streams. The `types/domain.ts` file already defines the `OracleQueryPayload` interface with a `sessionHistory` field, confirming that the type system is ready for this extension, even though the runtime logic to populate it is absent.

## 3. What "done" looks like

**Visible result:** The Oracle terminal displays a conversation history. When a user submits a second prompt, the previous question and answer remain visible above the new exchange. The UI does not reset or clear the previous context.

**What it includes:**
*   A state variable (e.g., `history`) that stores completed exchanges (question + answer).
*   Logic to append the current exchange to this state upon stream completion.
*   The `sessionHistory` field in the `OracleQueryPayload` is populated with this accumulated state before sending the next request.
*   The rendering logic iterates over the history array to display past exchanges, not just the latest one.

**What has to be done:**
1.  **State Management:** Introduce a state array to hold completed exchanges. Each exchange should be an object containing the user's prompt and the fully assembled assistant response.
2.  **Accumulation:** In the `onComplete` or `onClose` handler of the SSE stream, append the current prompt and the final assembled answer to the history state.
3.  **Payload Construction:** When constructing the `OracleQueryPayload` for the next request, map the history state into the `sessionHistory` field. Ensure the format matches the `OracleQueryPayload` type definition in `types/domain.ts`.
4.  **Rendering:** Update the component's render logic to map over the history state and display each exchange. The most recent exchange should be the one currently streaming or just completed.
5.  **Constraint Adherence:** Do **not** modify `readOracleStream` or `parseSseEvent`. Do **not** change the `OracleQueryPayload` type. The existing streaming logic must remain untouched; you are only adding the "memory" layer around it.

## 4. Success criteria (functional)

*   **Multi-turn persistence:** After submitting a second prompt, the first prompt and its answer are still visible in the UI.
*   **Contextual Accuracy:** The `sessionHistory` sent in the second request contains the first exchange. (Verify via network inspection or console logging if necessary, but the primary proof is the UI state).
*   **No Regression:** The first prompt still streams correctly. The `readOracleStream` and `parseSseEvent` helpers are unmodified.
*   **Type Safety:** The code compiles without errors, and the `sessionHistory` field is correctly typed according to `types/domain.ts`.

## 5. Quality criteria (the part that's new)

*   **Code Organization:** The logic for building `sessionHistory` should be isolated from the streaming logic. Consider a helper function or a custom hook if the logic becomes complex, but keep it simple for this task. The streaming logic (`readOracleStream`) must remain a pure consumer of the stream, unaware of history.
*   **AI-Use/Process Documentation:** Document in your PR description *why* you chose to store the history in React state versus a local storage or backend session. (Hint: React state is the correct choice for this task's scope, as it is client-side session memory, not persistent storage).
*   **Test Shape:** Per R7's Trophy-not-Pyramid doctrine, write a component test that simulates two consecutive prompts. Assert that after the second prompt, the DOM contains both the first and second answers. Do not mock the SSE stream entirely; use a mock server or a fake stream that yields two distinct responses to verify the accumulation logic.
*   **Accessibility:** The history list must be keyboard-navigable. Each exchange should have a clear heading or label indicating it is a past interaction. Ensure that the `aria-live` region for the *current* streaming answer does not conflict with the static history. The history should be static content, not live-updating, to avoid screen reader noise.
*   **Oral Defense:** Be prepared to explain how `sessionHistory` differs from a backend session. (Answer: It is client-side context sent with each request, allowing the server to be stateless. The client is the source of truth for the conversation order.)

## Closing

> "A departed member is not a bug, but a story with an ending."
> — TTOD `wis-011`, *wisdom*

This task ensures that the Oracle terminal remembers the user's previous interactions, treating the conversation as a continuous narrative rather than a series of disconnected, stateless requests.