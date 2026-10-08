# Oracle terminal — streamed response rendering (Team 3, Task 1)

How `OracleTerminal.tsx` turns one prompt into one incrementally rendered answer.
Brief: [`docs/public/_tasks/oracle-task1.md`](../../../../../docs/public/_tasks/oracle-task1.md).

## Streaming state

1. `submit()` builds an `OracleQueryPayload` and calls `sendPayload()`, which appends an
   `Exchange` with `state: 'streaming'` and `POST`s to `/api/v1/oracle/stream`.
2. The response goes to `readOracleStream(response, onChunk)` from `sse.ts`, which splits the
   body on blank lines and validates each event with `parseSseEvent`. Both helpers are used
   unmodified (the parser is frozen).
3. `onChunk` calls `updateExchange()`, a functional `setExchanges` update, and `appendChunk()`
   either extends the last segment's text (same mode/citations/themes/tags) or opens a new segment.
4. After the stream ends the exchange becomes `complete` (or `queued` / `error`).

**Why one update per chunk:** the answer must never be buffered before first paint. React 18+
batches updates that fire in the same task, so the chunks decoded from one network read commit in
a single render (no layout thrashing), and each later read paints on its own.

## Busy guard

- `busy` is derived from state: any exchange still `streaming`. It disables the **Ask** button
  and makes `submit()` return early, so Ctrl/⌘+Enter and form submit are blocked too.
- `submittingRef` also blocks a second submit fired before React re-renders, so only one stream
  per terminal writes to `exchanges` at a time.

## Reduced motion

`useReducedMotion()` (framer-motion) disables the terminal's open/close transition and the
fade-in of each streamed exchange when `prefers-reduced-motion: reduce` is set. The streamed text
itself is never animated.

Accessibility follows the project's global Definition of Done. The live region announcement
belongs to Task 2 and the grounded/creative label and citation links belong to Task 3.

## Tests

`OracleTerminal.test.tsx` → *streamed rendering (Task 1)* mocks the SSE body with a
`ReadableStream`, checks that the first chunk paints before the stream closes, and checks that a
second submit mid-stream never reaches `fetch`.

```bash
cd services/frontend && npx vitest run src/components/oracle
```
