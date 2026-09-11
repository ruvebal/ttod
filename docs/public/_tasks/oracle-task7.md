---
title: "Unit and component tests for the Oracle terminal and its streaming logic"
seam: oracle
team_number: 3
team_name: "Oracle Terminal"
task_number: 7
area: "Testing"
verb: keep
layout: default
lang: en
---

# Assignment — Team 3, Task 7: Unit and component tests for the Oracle terminal and its streaming logic

**Seam:** oracle · **Team:** 3 · **Task:** 7 of ~10
**Area(s):** Testing · **Verb served:** keep

## 1. Curriculum map

This task exercises **Unit 5 — Testing strategy** ([web-atelier-udit FE II](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/)).

While the preceding tasks (1–6) focused on building the streaming UI and state management, Task 7 shifts the focus to verifying that behavior. It requires applying the "Trophy-not-Pyramid" doctrine: prioritizing high-value integration and component tests that verify the *streaming state machine* and *rendered output* over exhaustive unit tests of trivial helpers. The goal is to prove that the `readOracleStream` and `parseSseEvent` helpers work correctly in the context of the React component, without mocking the network layer in a way that hides real streaming behaviors.

## 2. Worked example, from the real TTOD app

The existing `services/frontend/src/components/oracle/sse.ts` module provides the `readOracleStream` and `parseSseEvent` helpers. These are the "real" implementation details that the tests must target. A real starting example already exists at `services/frontend/src/components/oracle/OracleTerminal.test.tsx` — it mocks `fetch` to return a hand-built SSE `Response` and asserts the terminal streams a creative answer; extend this file's own pattern rather than inventing a new mocking strategy.

- **`readOracleStream`**: This function handles the `fetch` call and the `ReadableStream` consumption. It is the source of truth for how chunks are parsed and yielded.
- **`parseSseEvent`**: This function parses individual Server-Sent Events (SSE) lines into structured `OracleResponseChunk` objects.

The tests must verify that the React component correctly consumes the output of `readOracleStream`. For example, a test should simulate a stream that yields three chunks:
1. `{ type: 'start', ... }`
2. `{ type: 'delta', content: 'Hello' }`
3. `{ type: 'delta', content: ' world' }`

The test should assert that the component's state updates incrementally, rendering "Hello" and then "Hello world", rather than waiting for the stream to close before rendering anything. This verifies the "never buffer the whole answer before first paint" constraint.

## 3. What "done" looks like

**Visible result:** The terminal and its streaming logic each have at least one real test that passes in the CI pipeline. The tests are not just "smoke tests" that check if the component renders; they verify the *streaming behavior* and *state transitions*.

**What it includes:**
- **Unit tests for the streaming state machine:** Tests that verify the component correctly handles the sequence of SSE events (`start`, `delta`, `end`, `error`). These tests should mock the `readOracleStream` function to return a controlled stream of chunks and assert that the component's internal state (e.g., `isLoading`, `content`, `error`) updates as expected.
- **Component tests for the rendered terminal:** Tests that verify the DOM output matches the expected state. For example, when the stream is in progress, the `aria-busy` attribute should be `true`, and the `aria-live` region should contain the partial content. When the stream completes, `aria-busy` should be `false`, and the full content should be visible.
- **Error handling tests:** Tests that verify the component correctly handles network failures or 5xx responses. The component should display an error message and not crash.

**What has to be done:**
- Do **not** poll the stream endpoint or collapse SSE into one buffered response just to make testing easier. The tests must use the real `readOracleStream` helper (or a faithful mock of it) to ensure that the streaming behavior is preserved.
- Use a testing library that supports async streams (e.g., `@testing-library/react` with `jest` or `vitest`).
- Ensure that the tests are deterministic. Use fake timers or controlled streams to avoid flakiness.

## 4. Success criteria (functional)

- The tests verify that the component correctly handles the sequence of SSE events (`start`, `delta`, `end`, `error`).
- The tests verify that the component's state updates incrementally as chunks arrive, rather than waiting for the stream to close.
- The tests verify that the component correctly handles network failures or 5xx responses, displaying an error message and not crashing.
- The tests verify that the `aria-busy` and `aria-live` attributes are updated correctly during the streaming process.
- The tests pass in the CI pipeline and are deterministic.

## 5. Quality criteria (the part that's new)

- **Code organization:** The tests should be organized in a way that reflects the component's structure. For example, `oracle-terminal.test.tsx` should contain tests for the `OracleTerminal` component, and `sse.test.ts` should contain tests for the `readOracleStream` and `parseSseEvent` helpers.
- **AI-use/process documentation discipline:** If AI tools are used to generate or refine the tests, the process should be documented in the PR description. The AI should not be used to "guess" the expected behavior; the tests should be based on the real implementation details of `readOracleStream` and `parseSseEvent`.
- **Test shape per R7's own Trophy-not-Pyramid doctrine:** The tests should prioritize high-value integration and component tests over exhaustive unit tests of trivial helpers. The goal is to verify that the component works correctly in the context of the real streaming logic, not to test every possible edge case of a simple function.
- **Accessibility:** Every task inherits the same Definition of Done per `assignments.md` — do not restate it as if it were unique to this task, cite it. The tests should verify that the `aria-busy` and `aria-live` attributes are updated correctly during the streaming process.
- **Defensible oral-defense answer:** A defensible answer for this task would explain how the tests verify the streaming behavior and state transitions. It would also explain why the tests do not mock the network layer in a way that hides real streaming behaviors. The answer should demonstrate an understanding of the "Trophy-not-Pyramid" doctrine and the importance of testing the real implementation details.

## Closing

> "The path speaks to humans. The vault speaks to libraries. The scope speaks to machines. One string for three tongues, and at 3am the collision speaks loudest."
> — TTOD `cc-034`, *code-craft*

This quote reminds us that different layers of the system (UI, logic, infrastructure) have different concerns. In testing, we must ensure that the UI layer (the terminal) correctly communicates with the logic layer (the streaming state machine) without conflating their responsibilities. The tests should verify that the "path" (UI) and the "vault" (logic) speak to each other correctly, without collision.