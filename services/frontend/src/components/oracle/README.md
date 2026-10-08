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

# Live-region announcement (Team 3, Task 2)

Brief: [`docs/public/_tasks/oracle-task2.md`](../../../../../docs/public/_tasks/oracle-task2.md).

## Where the live region lives

Each exchange wraps its streamed segments in `div.oracle-answer` with `aria-live="polite"`,
`aria-atomic="false"` and `aria-busy={exchange.state === 'streaming'}`. It is the only
`aria-live` node in the terminal: `.oracle-log` used to be one, so the query echo, the "Listening…"
status and the notices were announced together with the answer. The status indicator is now a
sibling `role="status"` element outside the answer.

- **`polite`, not `assertive`:** a streaming answer produces many small updates. `assertive` would
  interrupt whatever the screen reader is saying on every chunk; `polite` queues them.
- **`aria-atomic="false"`:** only the changed text is announced, not the whole answer again on
  every chunk (or once more at the end).
- **`aria-busy`:** `true` while the SSE stream is open, `false` when it closes (complete, queued
  or error). It is scoped to the answer, so it never hides the notices or the proposal status.

The region is in the DOM, empty, before the first chunk arrives (the exchange is added before
`fetch`), because many screen readers ignore live regions that appear already filled.
`readOracleStream` / `parseSseEvent` are untouched; no polling or buffering was added.

## Limits to verify by ear

- Screen readers treat `aria-busy="true"` differently: VoiceOver may hold announcements until it
  turns `false`, while NVDA usually ignores it. That would contradict "announce as it arrives", so
  the real-screen-reader check below decides whether to keep it.
- Checked with `@guidepup/virtual-screen-reader` (run once, not a project dependency): each chunk is
  announced on its own ("The river" → "bends" → "around the stone."). This needs `appendChunk` to
  keep every chunk in `segment.parts` and render it as its own `<span>`; merging them into one
  text node made the reader repeat the whole paragraph on every chunk. The virtual reader
  follows the ARIA spec, not the quirks of NVDA or VoiceOver, so it does not replace the manual check.

**Manual check (step 4 of the brief):** with NVDA + Firefox/Chrome and VoiceOver + Safari, ask a
question with the terminal focused and note whether the answer is heard while it streams, whether
the query or "Listening…" are repeated, and whether the full answer is read again at the end.

## Test

`OracleTerminal.test.tsx` → *live-region announcement (Task 2)* streams two chunks and checks that
the single live region grows chunk by chunk, holds neither the query nor the status, and switches
`aria-busy` from `true` to `false` when the stream closes. It also checks that each chunk is its own
`<span>`.
