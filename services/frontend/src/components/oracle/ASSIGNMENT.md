# R5 Oracle — student assignment (hello-world is not the finished terminal)

The instructor-provided hello-world is **one prompt, one streamed response, grounded vs creative
mode, cited quote ids, reduced-motion, and a busy/double-submit guard**. Locale is sent on the
payload when the page knows it (`en` | `es`). `sessionHistory` is sent as `[]`. Offline queue,
multi-turn history, creative-to-proposal escalation, and the global open/close shortcut are
deliberately absent — they are this assignment.

## Learning outcomes

- Drive React state while an SSE stream is still open: append segments as chunks arrive, keep a
  live region (`aria-live` / `aria-busy`) honest, and never buffer the whole answer before first
  paint.
- Consume the existing `readOracleStream` / `parseSseEvent` helpers — streaming UI state is the
  lesson; inventing a second parser is not.
- Distinguish `grounded` from `creative` in the UI, and surface `citedQuoteIds` on grounded
  segments as navigable quote links.

## Constraints

- Keep using `readOracleStream` and `parseSseEvent` from `sse.ts` **unmodified**. Do not replace
  streaming with a wait-for-full-response or polling loop.
- Keep the frozen `OracleQueryPayload` / `OracleResponseChunk` / `OracleProposeRequest` /
  `OfflineLogEntry` shapes in `types/domain.ts` exactly. `sessionHistory` stays on the payload type
  even when you start sending real history; `themes` and `tags` may arrive on chunks — rendering
  them is in scope here, changing the types is not.
- Extend, do not replace, the `OfflineLogEntry` mechanism in `lib/db.ts` (`enqueueOracleQuery`,
  `markEntrySynced`, `enqueueErrorReport`, `listUnsyncedEntries`). Do not invent a second queue.
  Coordinate with R6 (TS4a): that lane owns `lib/db.ts` and the PWA/offline-banner stub; this lane
  **calls** the queue from the terminal again.

## Acceptance criteria

- An unreachable oracle (network failure / 5xx) enqueues the query on this device; reconnect
  (`online`) flushes unsynced `oracle-query` entries in order and marks successes synced.
- Multi-turn session history is sent (`sessionHistory` built from completed exchanges) and
  rendered as more than one visible exchange.
- A completed creative answer can be proposed for human review (`POST /api/v1/oracle/propose`)
  only after an explicit click — never as a side effect of streaming.
- A global open/close shortcut exists (`Alt+Shift+O` opens and focuses; `Escape` closes).

## Prohibited shortcuts

- Do not poll `/api/v1/oracle/stream` or collapse SSE into a single buffered JSON body.
- Do not silently drop the grounded/creative distinction (color-only treatments without a text
  label are not enough).
- Do not call cloud inference, talk to Ollama from the browser, or write `ttod.yml`.
