---
title: "Streamed response rendering, one prompt to one cited answer"
seam: oracle
team_number: 3
team_name: "Oracle Terminal"
task_number: 1
area: "Oracle"
verb: question
layout: default
lang: en
alt_lang_missing: true
---

# Assignment — Team 3, Task 1: Streamed response rendering, one prompt to one cited answer

**Seam:** oracle · **Team:** 3 · **Task:** 1 of ~10
**Area(s):** Oracle · **Verb served:** question

## 1. Curriculum map

This task exercises the core principles of **Unit 3 — React State & Effects** (specifically managing asynchronous state updates and side effects) and **Unit 5 — Testing strategy**.

*   **Unit 3 Link:** [Unit 3 — React State & Effects](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-3-react-state-effects/)
*   **Unit 5 Link:** [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/)

*Note: Specific lesson links for "Streaming UI Patterns" are not yet published in the web-atelier-udit FE II curriculum; this task relies on the general state management principles established in Unit 3.*

## 2. Worked example, from the real TTOD app

The instructor-provided hello-world implementation in `services/frontend/src/components/oracle/` already demonstrates the target behavior. Specifically, `OracleTerminal.tsx` consumes the `readOracleStream` helper from the colocated `sse.ts` to handle the Server-Sent Events (SSE) connection.

*   **Real File:** `services/frontend/src/components/oracle/ASSIGNMENT.md` (module brief) and `OracleTerminal.tsx` (implementation)
*   **Real Function:** `readOracleStream` (from `services/frontend/src/components/oracle/sse.ts`)
*   **Real Behavior:** The current implementation sends a single prompt, receives a stream of `OracleResponseChunk` objects, and renders them sequentially. It already handles the `grounded` vs `creative` distinction in the payload and includes a busy/double-submit guard. This task requires you to understand, harden, and document this existing baseline, not build it from scratch.

## 3. What "done" looks like

**Visible result:**
A user submits a single prompt in the Oracle terminal. The response appears incrementally as chunks arrive, without waiting for the full response to buffer.

*Out of scope for this task, owned elsewhere on the board: live-region/screen-reader announcement of the streaming text is Task 2's deliverable, and the grounded/creative mode label plus navigable `citedQuoteIds` links are Task 3's deliverable. This task's own accessibility surface is the reduced-motion and busy-guard behavior below — do not re-implement or re-grade Task 2/3's work here.*

**What it includes:**
*   **Streaming State Management:** React state is updated as each SSE chunk arrives, without buffering the whole answer before first paint.
*   **Reduced Motion:** The streaming animation respects `prefers-reduced-motion`.
*   **Busy Guard:** The submit button is disabled or shows a loading state while the stream is active to prevent double-submission.

**What has to be done:**
1.  **Verify Existing Implementation:** Confirm that the current hello-world code uses `readOracleStream` and `parseSseEvent` from `sse.ts` unmodified.
2.  **Harden State Logic:** Ensure that React state updates are batched correctly to avoid layout thrashing during high-frequency chunk arrivals.
3.  **Reduced-Motion Audit:** Verify that the streaming animation itself (not the live-region announcement — that is Task 2) is disabled for users with reduced-motion preferences.
4.  **Document the Baseline:** Write a brief note in the module's `ASSIGNMENT.md` or a local `README` explaining how the streaming state is managed, citing the specific helper functions used.
5.  **Test the Guard:** Manually verify that submitting a second prompt while the first is streaming is prevented or queued (per the module's constraints, it should be prevented/guarded).

*Note: `docs/public/teaching/tasks.md` does not contain existing prose for this specific item (Board Item 1). The above is grounded entirely in the module’s `ASSIGNMENT.md` hello-world description.*

## 4. Success criteria (functional)

*   **Streaming Integrity:** The response is rendered incrementally as chunks arrive; the entire answer is not buffered before first paint.
*   **Busy Guard:** A double-submit guard prevents multiple concurrent streams from the same terminal instance.
*   **Reduced Motion:** The streaming animation is disabled when `prefers-reduced-motion` is set to `reduce`.

## 5. Quality criteria (the part that's new)

*   **Code Organization:** The streaming logic is encapsulated within the component or a custom hook, keeping the render function clean. No new SSE parsers are invented; the existing `sse.ts` helpers are used.
*   **AI-Use/Process Documentation:** A brief comment or docstring in the code explains *why* the state is updated on each chunk rather than batching, referencing the "no buffering before first paint" constraint.
*   **Test Shape:** Per the Testing Trophy (not Pyramid) doctrine, include at least one integration test that mocks the SSE stream and verifies that the UI updates incrementally, and that the busy guard correctly blocks a second submission mid-stream. Do not write unit tests for the `sse.ts` parser (it is frozen); test the *consumption* of the stream. (The live region itself is Task 2's own test surface, not this task's.)
*   **Accessibility:** The component inherits the global Definition of Done: keyboard-operable, one accessible name or label, no meaning carried by color alone, respects reduced-motion preferences. Cite this global standard rather than restating it as unique to this task.
*   **Oral Defense:** Be prepared to explain how you ensured React's batching behavior doesn't introduce a delay between a chunk arriving and it appearing on screen, and how the busy guard prevents a second submission from corrupting the in-flight stream's state.

## Closing

> "The model without memory is a stranger in your codebase. Feed it your architecture and it becomes a colleague. Feed it your conventions and it becomes a partner. But never mistake its fluency for understanding."
> — TTOD `arch-038`, *DevIAC Tao (§45): RAG as Memory*

This quote reminds us that while the Oracle’s streaming response is fluent and immediate, our job is to ensure the *context* (the architecture of the stream, the conventions of accessibility) is fed to the user correctly, so the interaction feels like a partnership rather than a black box.