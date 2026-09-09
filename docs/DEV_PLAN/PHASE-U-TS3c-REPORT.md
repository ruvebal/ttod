<!--
Phase U TS3c report — R5 Oracle hello-world reduction.
Follows cascade-forge evidence-state discipline (status first; claims checked live).
Executed on branch skeleton/ts3c-r5, worktree ../ttod-skeleton-ts3c, forked from
skeleton/ts1-contracts@47f15da9 — never main.
-->

# Phase U · TS3c Report — R5 React Oracle hello-world reduction

**Status:** DONE

**Scope executed:** [`PHASES/U-TS3c-r5-oracle-hello-world.md`](PHASES/U-TS3c-r5-oracle-hello-world.md)
§4 keep/cut on `OracleTerminal.tsx` only, plus `ASSIGNMENT.md`. Streaming core kept; offline
queue, multi-exchange history, global shortcut, and `propose()` UI removed.

**Date:** 2026-09-09

**Implementer:** TS3c engineer session (worktree `../ttod-skeleton-ts3c`)

**Independent verifier:** pending

**Owner:** `@crea-comm.net`

**Branch / worktree:** `skeleton/ts3c-r5` · `/Users/ruvebal/src/ttod-skeleton-ts3c`  
**Forked from:** `skeleton/ts1-contracts` (`47f15da9`) — not `main`

---

## 1. Status against §9

TS1 is `DONE` (`PHASE-U-TS1-REPORT.md`). All §5 mechanical gates passed live (see §4). `sse.ts`
and `lib/db.ts` are byte-identical to `main`. `ASSIGNMENT.md` filed.

---

## 2. TS4a coordination (no conflict; `lib/db.ts` not edited)

Read [`PHASES/U-TS4a-r6-pwa-hello-world.md`](PHASES/U-TS4a-r6-pwa-hello-world.md) §4 before the
cut. That seam’s “one observable local/offline boundary” is a service-worker stub + visible
`navigator.onLine` banner, **not** a requirement that `OracleTerminal` keep calling
`enqueueOracleQuery` / `flushQueue`. Both runbooks forbid editing `lib/db.ts`. TS3c stops
*calling* those functions; TS4a may still import `OfflineLogEntry` read-only. Student assignment
depth in both lanes still names “offline queue flush on reconnect.”

**Flag, not a unilateral resolve:** `OracleTerminal.test.tsx` still asserts the pre-reduction
queue and themes UI (see §6). That file is outside this lane’s touched-path budget (TS4b/R7).
Left untouched. Do not restore queue calls to make those tests green.

---

## 3. What changed

| Path | Action |
| --- | --- |
| `services/frontend/src/components/oracle/OracleTerminal.tsx` | Reduced 325 → 172 lines |
| `services/frontend/src/components/oracle/ASSIGNMENT.md` | New |
| `docs/DEV_PLAN/PHASE-U-TS3c-REPORT.md` | This file |

**Kept:** `fetch('/api/v1/oracle/stream')` + `readOracleStream` loop + `appendChunk`;
`grounded` / `creative` labels; `citedQuoteIds` links; `useReducedMotion`; busy/double-submit
guard; `locale` on the payload when the page knows it (required prop from
`/[locale]/oracle.astro`); `sessionHistory: []`; always-open terminal.

**Cut:** `enqueueOracleQuery` / `markEntrySynced` / `enqueueErrorReport` / `listUnsyncedEntries`
imports and calls; `flushQueue`; `online` listener; `syncing` state; `exchanges[]` (now one
`exchange`); `historyFrom`; Alt+Shift+O / Escape; `open` toggle; `propose()` and proposal
UI/state. Themes/tags **not** rendered (assignment depth; SSE parser may still accept them).

**Not touched:** `sse.ts`, `sse.test.ts`, `lib/db.ts`, `components/graph/**`,
`services/backend/**`, `services/mcp/**`, `ttod.yml`.

---

## 4. Gate evidence (§5)

| Gate | Result | Evidence |
| --- | --- | --- |
| Streaming works | PASS | Live `/en/oracle/` against the running compose backend (see §5). MutationObserver: 121 distinct `textLen` steps; first token `"The"` at t+6.3s while `aria-busy=true` and status `Listening…`; length 3 → 10 → 13 → 20 → … → 695 over ~25s — not a single buffered paint. |
| Mode + citation visible | PASS | Label **Grounded in the TTOD corpus**; citation links `cc-029`, `cc-043`, `cc-002`, `cc-036`, `cc-026` → `/en/wisdom/{id}`. `proposeEver: false`. |
| No offline queue calls | PASS | Those four symbols are not imported or referenced in `OracleTerminal.tsx`. Unreachable path now shows the error notice (jsdom: `network unavailable`), not a queued copy. |
| No proposal UI | PASS | No `propose()`; terminal buttons = `[Ask]` only. |
| `sse.ts` / `sse.test.ts` untouched vs `main` | PASS | `git diff main -- services/frontend/src/components/oracle/sse.ts sse.test.ts` empty. Hashes `94b754f00a3f…` / `dc58ba5f5031…` match `main`. |
| `lib/db.ts` untouched vs `main` | PASS | `git diff main -- services/frontend/src/lib/db.ts` empty. Hash `223c69f98167…` matches `main`. |
| Reduced motion | PASS | `useReducedMotion` still gates `motion.div` / `motion.article` duration (`0` when reduced). |
| `sse.test.ts` still passes | PASS | `npx vitest run src/components/oracle/sse.test.ts` → 3 passed / 3 (before and after). |

`npx astro check`: 0 errors, 0 warnings, 0 hints (30 files).

---

## 5. Live streaming method

The student-facing stack is already up as `ttod_oracle` on `http://localhost:18080` (Caddy →
frontend image + backend). That **image** still serves the unreduced terminal, so it cannot prove
this branch’s UI.

Verification used the worktree Astro dev server on `127.0.0.1:4331` plus a **throwaway**
same-origin reverse proxy on `127.0.0.1:18081` (`/api/*` → `:18080` live backend, pages →
`:4331`). No repo file was edited for that proxy (`astro.config.mjs` stays out of this lane).

Query submitted in the hydrated island: **“How should I name a variable?”** (`locale: en`,
`sessionHistory: []`).

Byte-level backend stream (separate curl/python client to `:18080`) had already shown 346 SSE
events over 59s for a related naming query, first event at 4.538s — confirming the instructor
stream is token-grained, not one envelope.

UI observer (compact):

```text
dt=0ms     len=0   busy=false
dt=6265ms  len=3   busy=true  mode=Grounded…  preview="The"   cites=5  status=Listening…
dt=6286ms  len=10  preview="The seeker"
dt=6312ms  len=13  preview="The seeker of"
dt=6335ms  len=20  preview="The seeker of wisdom"
… 121 length steps …
dt=25421ms len=695 still Listening… then complete; Ask re-enabled; no proposal button
```

---

## 6. Flags (not blockers for DONE)

1. **`OracleTerminal.test.tsx` (untouched).** Focused file: 1 passed (grounded citations, no
   proposal), 2 failed by construction — still expects themes/tags UI and IndexedDB queue copy.
   TS4b should rewrite those cases against the hello-world contract. Per runbook §6, queue calls
   were not restored.
2. **Themes/tags display** cut from the terminal even though chunks still carry those fields
   (frozen `OracleResponseChunk`). Assignment work, not a type change.
3. **TS3a locale/route contract consumed, not its files.** `oracle.astro` already guards
   `en`/`es` and passes `locale` into the island; this lane did not edit that page.

---

## 7. `ASSIGNMENT.md` (filed at `services/frontend/src/components/oracle/ASSIGNMENT.md`)

```markdown
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
```
