# Phase R5 Report — React oracle terminal island

**Status: DONE**

The React 19 oracle terminal is mounted at `/{locale}/oracle`, consumes R1's SSE endpoint,
preserves per-chunk provenance, stages creative answers only after an explicit human action, and
uses an IndexedDB queue when the oracle is unreachable. The focused suite, Astro type check, and
production build are green. An independent cold reviewer found no blocking §5 issue.

## Shipped behavior

- The incremental SSE reader handles CRLF/LF framing, byte-boundary splits, multiple events, the
  optional `[DONE]` sentinel, and rejects malformed provenance envelopes. Consecutive chunks with
  matching mode/citations accumulate into one visible segment; a mid-stream mode change creates a
  separately labelled segment instead of silently inheriting the first mode.
- Grounded segments render in green with the explicit label “Grounded in the TTOD corpus” and
  quote-ID links. Creative segments render in rust/orange with the explicit label “Creative
  reflection — not sourced from a TTOD quote” and never render corpus citations.
- “Save as a draft proposal” appears only after a completed response containing a creative
  segment. Only its click handler calls `/api/v1/oracle/propose`. Success copy says the result is a
  draft and explicitly warns that the current human acceptance path is not operational.
- `?tag=` is read from `window.location` when the user submits, so navigation that occurred after
  hydration still reaches `OracleQueryPayload.contextTag`. R5 does not write the parameter and
  introduces no store/event/localStorage channel between islands.
- Framer Motion provides terminal and exchange entrance/exit animation while
  `prefers-reduced-motion` disables spatial movement. `Alt+Shift+O` opens/focuses the terminal,
  `Ctrl/Command+Enter` submits, and Escape closes it.
- Network failures and HTTP 5xx responses enqueue an `OfflineLogEntry` with
  `kind: 'oracle-query'`; the `online` event retries entries in timestamp order and marks successful
  entries synced. Client failures can use the same store as `kind: 'error-report'`. IndexedDB
  failure is surfaced honestly rather than claiming a query was queued.
- The UI displays backend text unchanged and contains no client-side translation or alternate
  inference path.

## Gate evidence

| Gate | Evidence |
| --- | --- |
| Provenance | Component test proves creative disclosure has no grounded citation treatment; grounded test proves the real citation ID/link renders. Per-chunk parsing validates `mode` and mode changes remain separate visible segments. |
| Creative-mode disclosure | Distinct `.oracle-grounded` and `.oracle-creative` backgrounds/borders plus explicit textual labels; independent reviewer confirmed the treatments are distinguishable without relying on color alone. |
| Oracle-propose governance | Test observes exactly one stream request before the user clicks, then the proposal request after the click. Button exists only for a completed exchange with creative content. Success copy says “Saved as a draft proposal” and discloses the acceptance-path gap. |
| Local AI | Static scan found only the two same-origin R1 paths (`/api/v1/oracle/stream`, `/api/v1/oracle/propose`), with no cloud vendor, Ollama-direct, or fallback URL. Unreachable requests take the IndexedDB path. |
| Routing/navigation sync | Test submits from `?tag=simplicity` and asserts `contextTag: 'simplicity'`; static scan found no `localStorage`, custom event, or query-string write in R5. |
| PWA groundwork | `src/lib/db.ts` persists the frozen `OfflineLogEntry` shape, lists unsynced records deterministically, and marks successful reconnect retries synced for R6 to extend. |

## Verification

```text
$ npx vitest run src/components/oracle
Test Files  2 passed (2)
Tests       6 passed (6)

$ ASTRO_TELEMETRY_DISABLED=1 npm run check
Result (27 files):
- 0 errors
- 0 warnings
- 0 hints

$ ASTRO_TELEMETRY_DISABLED=1 npm run build
OracleTerminal.DLsRMhWf.js  137.35 kB | gzip: 45.85 kB
Server built in 1.53s
Complete!

$ git diff --check -- src/components/oracle src/lib/db.ts src/pages/'[lang]'/oracle.astro
(no output; exit 0)
```

The current sandbox denied binding the local Astro server (`listen EPERM`), so this report does
not claim a real Safari/Chromium IndexedDB run. Component behavior ran in jsdom; the SSE reader ran
against real `ReadableStream`/`Response` objects. Browser-matrix IndexedDB evidence remains a
recommended R6/R7 integration check, not an invented claim here.

The repository-wide `npx vitest run` is not green because the sibling R4
`layout.test.mjs` uses Node's test runner: its two TAP subtests pass, after which Vitest reports
“No test suite found.” This was reported to the R4/root owner and was not changed by R5. R5's own
focused suite is green.

## Cold review

A separate agent with no R5 implementation role reviewed §5/§8 without editing. It found no
blocking gate failure and specifically confirmed:

- creative and grounded responses have explicit labels and distinct styles, with citations only
  in grounded output;
- the proposal request requires an explicit click, is never triggered by streamed creative output,
  and the success copy does not overclaim the broken downstream acceptance path;
- `?tag=` is read at submission and no alternate inter-island state channel exists;
- the only inference request is R1's same-origin endpoint, while network/5xx failures queue and
  reconnect retries oracle queries.

The reviewer recorded two non-blocking limitations. IndexedDB transactions lack a real/fake-IDB
automated test in this lane, and `error-report` records are persisted but not flushed because no
error-report server endpoint exists. R6 may extend that durable record type when it owns service
worker synchronization; R5 does not invent an endpoint.

## Structural and cross-lane findings

Two initial contract gaps were escalated and resolved by the instructor before completion:

1. R5's original touched-path budget required Framer Motion and a mounted island but did not allow
   package integration or a mount page. The centrally owned dependency and the narrow
   `src/pages/[lang]/oracle.astro` authorization resolved this without R5 editing package/config.
2. The frozen `domain.ts` initially omitted the runbook's `OfflineLogEntry`; the R1-owned contract
   was completed centrally. R5 consumed it without editing the file.

No remaining structural false assertion was found in R5's gate contract.

## Files touched

- `services/frontend/src/components/oracle/OracleTerminal.tsx`
- `services/frontend/src/components/oracle/oracle-terminal.css`
- `services/frontend/src/components/oracle/sse.ts`
- `services/frontend/src/components/oracle/OracleTerminal.test.tsx`
- `services/frontend/src/components/oracle/sse.test.ts`
- `services/frontend/src/lib/db.ts`
- `services/frontend/src/pages/[locale]/oracle.astro` (narrow instructor-authorized mount route;
  renamed after review by the integration lane to unify locale-segment naming)
- `docs/DEV_PLAN/PHASE-R5-REPORT.md`

R5 did not edit `domain.ts`, package/config files, R3b/R4 directories, backend/MCP/core/schema,
compose/Caddy/environment files, or canonical content.

## Lessons for the next phase

R6 can treat `listUnsyncedEntries()`, `markEntrySynced()`, and the frozen `OfflineLogEntry` union as
the queue handoff. It should add service-worker/browser integration tests rather than replace this
store, decide whether an error-report endpoint exists before attempting to flush those records,
and record actual Safari/Chromium IndexedDB evidence. R6 may start against R5: every R5 §5 gate is
green and the durable queue does not depend on a cloud service or direct Ollama access.
