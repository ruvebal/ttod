<!--
Self-contained runbook. Derived from PHASE-U-FEII-TEACHING-SKELETON-CASCADE.md §2, §5 TS3 and
PHASE-U-WEEK0-ORCHESTRATION.md — that orchestration document is normative; regenerate this one if
it changes. Generated as part of the Week-0 skeleton-generator pass.
-->

# Phase U · TS3c — R5 React Oracle hello-world reduction

**Mode:** student lane (or instructor-built if executed before cohort start), 1 owner
**Entry:** TS1 `DONE`; TS3a's route/locale contract confirmed (independent of TS3b — may run in
parallel with it)
**Exit:** one prompt, one streamed response, visible grounded/creative mode, one cited-quote
path — no offline queue, no exchange history, no creative-to-proposal escalation

---

## 0. What this phase actually is — the largest reduction of the three TS3 lanes

`OracleTerminal.tsx` (325 lines) plus `sse.ts` (63 lines) is by far the richest file in the
reference build, because it already contains R5's *and* R6's assignment-depth work merged
together: full offline-queue integration (`flushQueue`, `enqueueOracleQuery`, `markEntrySynced`,
`enqueueErrorReport` — this is exactly the mechanism `PHASES/R6-pwa-cicd-audit.md` §4 item 2 says
R6 *extends*, meaning it must already exist for R6 to extend it, but Phase U's R5 hello-world row
explicitly lists "offline proposal flow" as deliberately absent), a global keyboard-shortcut
open/close UX layer, multi-exchange session history, and a creative-mode-to-human-proposal
escalation flow (`propose()`). This phase keeps only the streaming request/response core; every
other subsystem becomes a named assignment line.

**Coordinate with TS4a (R6) before deleting the offline-queue calls** — R6's own hello-world seam
(one observable offline boundary) may want a minimal stub of this same mechanism. Read
`PHASES/U-TS4a-r6-pwa-hello-world.md` §4 before finalizing this cut; if there is any conflict,
flag it back to TS1's owner rather than resolving it unilaterally in either lane.

## 1. Required reading

- `PHASE-U-FEII-TEACHING-SKELETON-CASCADE.md` §2 (R5's row).
- Live files: `services/frontend/src/components/oracle/OracleTerminal.tsx` (325 lines),
  `sse.ts` (63 lines, pure parsing — has its own `sse.test.ts`, do not touch, R7's territory),
  `services/frontend/src/lib/db.ts` (the offline-queue functions this lane stops calling but does
  not delete — `lib/db.ts` itself is R6/TS4a's file, not this lane's to edit).
- `docs/DEV_PLAN/PHASES/U-TS1-subtraction-and-contracts.md`'s subtraction table.
- `docs/DEV_PLAN/PHASES/U-TS4a-r6-pwa-hello-world.md` §4 — read before cutting the offline-queue
  calls (see §0 above).

## 2. Non-negotiable boundaries

- **Work on `skeleton/ts3c-r5`, forked from `skeleton/ts1-contracts`.**
- **Do not touch `sse.ts` or `sse.test.ts`.** `parseSseEvent`/`readOracleStream` are pure,
  tested parsing logic shared infrastructure — R5's hello-world reduction keeps calling them
  exactly as-is.
- **Do not touch `lib/db.ts`.** That file belongs to TS4a (R6). This lane *stops calling*
  `enqueueOracleQuery`/`markEntrySynced`/`enqueueErrorReport`/`listUnsyncedEntries` from
  `OracleTerminal.tsx`, it does not edit or delete those functions where they live.
- **Do not touch the backend.** `/api/v1/oracle/stream` and `/api/v1/oracle/propose` in
  `services/backend/app/main.py` are out of scope.
- **Streaming itself is instructor-provided, not assignment depth.** Phase U's contract keeps "one
  streamed response" in the hello-world column — do not simplify SSE parsing into a
  wait-for-full-response pattern; that would remove the exact concept (streaming UI state) Unit 3
  teaches.

## 3. Domain contract slice

```typescript
// services/frontend/src/types/domain.ts — frozen on skeleton/ts1-contracts (67 lines; see PHASE-U-TS1-REPORT.md §2)
export type Locale = 'en' | 'es';
export interface OracleQueryPayload { query: string; contextTag?: string; sessionHistory: string[]; locale?: Locale; }
export interface OracleResponseChunk { mode: 'grounded' | 'creative'; citedQuoteIds?: string[]; themes?: string[]; tags?: string[]; text: string; }
export interface OracleProposeRequest { query: string; creativeAnswer: string; suggestedSection?: string; suggestedTags?: string[]; locale?: Locale; }
```

`sessionHistory` stays in the type even though this lane sends an empty array (single-exchange
hello-world has no history to send) — do not narrow the type itself. Send `locale` when the page
knows it. Do **not** add themes/tags UI at hello-world depth — those fields exist on the frozen
chunk type so the SSE parser may accept them; rendering them is assignment work.

## 4. Scope — exact keep/cut

| Block in `OracleTerminal.tsx` | Keep | Cut → assignment |
| --- | --- | --- |
| `sendPayload`'s `fetch('/api/v1/oracle/stream', ...)` + `readOracleStream` loop + `updateExchange` segment append | Yes — this is the streaming core | — |
| `mode: 'grounded' \| 'creative'` display, `citedQuoteIds` rendering | Yes — Phase U names both explicitly | — |
| `sendPayload`'s catch block: `enqueueOracleQuery`, `markEntrySynced`, error → `enqueueErrorReport` | No | "Offline proposal flow" — coordinate wording with TS4a |
| `flushQueue`, the `online` event listener `useEffect`, `syncing` state | No | Same assignment line as above |
| `exchanges: Exchange[]` array + history rendering; replace with a single `exchange: Exchange | null` | Partial — collapse to one active exchange | "Session UX / multi-turn history" — assignment line |
| `historyFrom(exchangesRef.current)` → send `sessionHistory: []` | Simplify | "Session state machine" — assignment line |
| Global keyboard shortcut `useEffect` (Alt+Shift+O open, Escape close), `open` state | No | "Shortcuts and recovery" — assignment line |
| `propose()` function, proposal UI, `proposalState` | No | "Offline proposal / creative-to-human escalation" — assignment line |
| `reduceMotion` (`useReducedMotion`) | Yes — accessibility baseline, instructor-provided | — |
| `busy` guard on submit | Yes — prevents double-submit, cheap and correct even at hello-world depth | — |

**Net effect:** one textarea, one submit, one streamed exchange rendered with its grounded/creative
mode and cited quote ids, reduced-motion respected. No queue, no history array, no global shortcut,
no proposal button.

**`ASSIGNMENT.md`** (new, `services/frontend/src/components/oracle/ASSIGNMENT.md`): learning
outcomes (React state during streaming UI, SSE consumption, accessible live-region updates),
constraints (must keep using `readOracleStream`/`parseSseEvent` from `sse.ts` unmodified, must
keep the `OracleQueryPayload`/`OracleResponseChunk` shapes exactly), acceptance criteria (offline
queue flushes on reconnect, multi-turn history sent and rendered, creative answers can be proposed
for human review, a global open/close shortcut exists), prohibited shortcuts (do not poll instead
of streaming, do not silently drop the grounded/creative distinction).

## 5. Mechanical gates

| Gate | Required proof |
| --- | --- |
| Streaming works | one submitted query renders incremental text as it streams, not all at once |
| Mode + citation visible | grounded responses show cited quote ids; creative responses are visually distinguishable |
| No offline queue calls | `enqueueOracleQuery`/`markEntrySynced`/`enqueueErrorReport`/`listUnsyncedEntries` are not imported by this file on this branch |
| No proposal UI | no `propose()` function, no proposal button/state |
| `sse.ts` untouched | `git diff main -- services/frontend/src/components/oracle/sse.ts sse.test.ts` empty |
| `lib/db.ts` untouched | `git diff main -- services/frontend/src/lib/db.ts` empty |
| Reduced motion respected | `useReducedMotion` still gates any animation this lane keeps |

## 6. Rollback and mutation law

- No write path to `ttod.yml` exists in this component regardless of scope.
- If cutting the offline-queue calls breaks a test in `db.ts`'s own test suite, that indicates the
  test exercises `OracleTerminal.tsx` directly rather than `db.ts` in isolation — flag to TS4a/TS1,
  do not restore the queue calls unilaterally to make an unrelated test pass.

## 7. Touched-path budget

**Allowed:** `services/frontend/src/components/oracle/OracleTerminal.tsx`, a new `ASSIGNMENT.md`
in the same directory.

**Forbidden:** `sse.ts`, `sse.test.ts`, `lib/db.ts`, anything under `components/graph/`,
`services/backend/**`, `services/mcp/**`.

## 8. Post-phase review

A second reader confirms (by reading network/devtools, not just source) that the reduced terminal
genuinely streams rather than buffering, and that no offline-queue write occurs on a simulated
network failure (that failure should now simply show an error state, since the queue path was cut).

## 9. Phase report status enum

- **DONE** — all §5 gates pass, `ASSIGNMENT.md` filed, `sse.ts`/`lib/db.ts` untouched.
- **PARTIAL** — name exactly which gate is unmet.
- **BLOCKED** — TS1 has not filed `DONE`.

## 10. Exact commands

```bash
cd /Users/ruvebal/src/ttod
git worktree add ../ttod-skeleton-ts3c -b skeleton/ts3c-r5 skeleton/ts1-contracts
cd ../ttod-skeleton-ts3c/services/frontend
npx vitest run src/components/oracle/sse.test.ts   # must still pass, untouched
npm run dev   # visit /en/oracle/, submit one query, watch it stream
```

## 11. Report requirements

File `docs/DEV_PLAN/PHASE-U-TS3c-REPORT.md`: status (§9), confirmation `sse.ts`/`lib/db.ts`
are byte-identical to `main`, evidence the response genuinely streams (a screen recording note or
network-tab description, not just "it works"), and the `ASSIGNMENT.md` content.

## 12. Agent prompt — paste this into a fresh agent session with no other file open

```text
Act as TTOD Phase U TS3c engineer. Work only inside a new git worktree on branch skeleton/ts3c-r5,
forked from skeleton/ts1-contracts (never main). This runbook
(docs/DEV_PLAN/PHASES/U-TS3c-r5-oracle-hello-world.md) is self-contained. Also skim
docs/DEV_PLAN/PHASES/U-TS4a-r6-pwa-hello-world.md's §4 before cutting anything offline-queue
related, since R6 may want a minimal stub of the same mechanism — flag any conflict rather than
resolving it yourself.

Read services/frontend/src/components/oracle/OracleTerminal.tsx and sse.ts in full before changing
anything. Keep the core streaming path exactly: fetch('/api/v1/oracle/stream', ...), the
readOracleStream loop from sse.ts, incremental segment rendering, the grounded/creative mode
display, and cited quote id rendering. Keep useReducedMotion and the busy/double-submit guard.

Remove: all offline-queue integration inside sendPayload's catch block (enqueueOracleQuery,
markEntrySynced, enqueueErrorReport calls) and the flushQueue function plus its 'online' event
listener useEffect and the syncing state. Remove the propose() function and any proposal UI/state.
Remove the global keyboard shortcut useEffect (Alt+Shift+O / Escape) and the open state — render
the terminal always-open instead. Collapse the exchanges array to a single active exchange (send
sessionHistory: [] instead of historyFrom(...)).

Do not edit services/frontend/src/components/oracle/sse.ts, sse.test.ts, or
services/frontend/src/lib/db.ts at all — run `npx vitest run src/components/oracle/sse.test.ts`
before and after and confirm it is unchanged and passing.

Write services/frontend/src/components/oracle/ASSIGNMENT.md: learning outcomes (streaming UI
state, SSE consumption, accessible live regions), constraints (must keep sse.ts's functions and
the domain.ts Oracle types unmodified), acceptance criteria (offline queue flushes on reconnect,
multi-turn history works, creative answers can be proposed, a global shortcut exists), prohibited
shortcuts (no polling instead of streaming, no dropping the grounded/creative distinction).

Verify at /en/oracle/ that one submitted query streams incrementally (not all at once) and shows
its mode and any cited quote ids.

File docs/DEV_PLAN/PHASE-U-TS3c-REPORT.md with status (DONE/PARTIAL/BLOCKED per this
runbook's §9), confirmation sse.ts/lib/db.ts are unchanged, streaming evidence, and the
ASSIGNMENT.md content.
```
