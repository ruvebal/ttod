# PWA Task 4 — offline queue contract and design

## Status

Repaired on 2026-10-08 on top of Task 3 head `63e5d3b`, which includes current teacher main `4b4e774` and merged Task 1 #51. `.aws` is absent; accepted layout and manifest are preserved. Merge order remains #46 → #47 → #49 → #50. Final integration onto main follows #47; no dependency PR was merged as part of this repair.

Maintained queue coverage and the [compatibility monitor](pwa-compatibility-monitor.md) prove reconnect behavior. Team 3 #42 remains separate and unmerged; human acknowledgment of the shared interface is still pending.

The optional `queueOrder` field, database version 2 migration, atomic order allocation, committed-write handling, reconnect-loop improvements, and worker cache v5 are applied. Oracle attempts replay on online mount and the window `online` event.

## Interface contract

PWA Task 4 adds optional `queueOrder` to `OfflineLogEntry` as internal ordering metadata. Existing callers continue using `enqueueOracleQuery(payload)`, `listUnsyncedEntries()`, and `markEntrySynced(entry)` unchanged. The same `ttod-oracle` / `offline-log` store is upgraded from database version 1 to 2 without clearing records. New entries receive an increasing order inside a `readwrite` transaction; updates retain their original order. Legacy records are backfilled by timestamp, then ID for deterministic ties; exact historical order for tied legacy timestamps was never stored and cannot be recovered.

Oracle continues owning payload submission and SSE display. The window `online` event and online Oracle mount trigger replay. Synced means a successful nonempty Oracle stream was received and the synced update committed. A failed replay stops the pass and retains pending queries. Error reports are retained without inventing a delivery endpoint. Replay requires the Oracle component to be mounted; background delivery with all pages closed is outside this implementation.

## Design choices

- **Extend the existing queue.** Retain entry IDs, payloads, timestamps, synced flags, database/store names, and helper signatures. The optional field is an additive amendment to the shared domain contract.
- **Record enqueue order explicitly.** Timestamps can tie or move backwards. Allocate numeric order inside the same transaction that inserts an entry, and preserve it when the entry is updated.
- **Preserve saved work during migration.** Backfill existing records in the upgrade transaction. Retain their payloads and synced flags. Deterministic legacy ties do not establish an order that was never recorded.
- **Use transaction completion as the write-success boundary.** A successful individual request does not establish that its transaction committed. Queue/save acknowledgements and synced updates must await completion.
- **Replay sequentially through Oracle's existing sender.** Await each response and synced update before sending the next pending query. Stop after failure; another reconnect or online mount can retry. Do not add a continuous retry timer.
- **Coordinate overlapping replay.** Retain the component's guard and add a shared Web Lock where available. The fallback provides only per-component exclusion; cross-tab exclusion is not claimed without Web Locks.
- **Keep worker caching and action storage separate.** The worker supplies the offline Oracle page and assets; the mounted Oracle handles queued POSTs. The v5 cache refresh delivers updated assets through the existing install/activate lifecycle. Cache retirement must not clear IndexedDB. No second sender is added to the worker.

Successful client acknowledgement does not provide server-side exactly-once execution: if a processed request loses its response, a later replay may repeat it. Backend idempotency would require a separate API contract.

## Current repair verification — 2026-10-08

The repaired PWA source passed `npm test` (six unit/component tests) and the complete `npm run pwa:guard`: consumer contract, five checker regression tests, Astro diagnostics, TypeScript, production build and all six queue browser cases. Repository `make check` passed strict validation, metadata consistency and all 236 Python tests. All 25 scoped Task 1–3 Chromium regressions passed against the exact built worker and an isolated real corpus backend (lifecycle, both offline Oracle shells, static/API cache policies and locale routes).

A disposable three-way integration preview with Team 3 #42 pinned at `70e7717` passed all 20 unit/component tests and the complete six-case queue guard. It used the repaired branch's lockfile-installed dependencies. OracleTerminal.tsx merged cleanly and retained replay guards and committed synced-state handling. Package scripts were resolved by retaining `test` and all `pwa:*` commands; the CI comment conflict was resolved while preserving one `npm test` step and both jobs. These results describe the pinned preview, not a future merged revision or Team 3 approval.

The maintained HTTP 503 test accepts the current PWA retry notice or Team 3's unavailable notice. Other failure expectations remain strict; queue ordering, pending/synced state, migration, no unsolicited retries and recovery assertions are unchanged. `npm test` is now available and runs in the existing typecheck/build CI job, alongside the separate PWA guard job. Team 3 feature code and tests are not copied into this PR.

Controlled SSE responses prove client queue behavior; live backend/model inference was not rerun for this repair. Hosted CI must be checked at the published revision, and final main integration must be reverified after #47 merges.

## Historical verification — 2026-10-07

The following checks passed against the earlier source on 2026-10-07:

- `npm run check`: zero errors, warnings, or hints.
- `npx --no-install tsc --noEmit` and `npm run build`: passed.
- `docker compose up -d --build frontend`: rebuilt and started the frontend; backend remained healthy and `/health` returned status `ok`.
- `npx --no-install vitest run`: all 6 existing frontend unit/component checks passed.
- `E2E_BASE_URL=http://localhost:8080 npx --no-install playwright test --project=chromium`: all 23 existing browser checks passed, including previous caching, worker lifecycle, offline hydration, locale, and accessibility coverage.
- `make PYTHON=/tmp/ttod-test-venv/bin/python check`: strict corpus validation, stored metadata consistency, and all 236 Python checks passed outside the sandbox. The temporary environment was restored from the existing dependency declarations. In-sandbox attempts encountered missing dependencies and then stalled in the platform HTTP checks; those attempts are not reported as passes.
- `git diff --check`: no whitespace errors after cleanup.

Following [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/), additional smoke checks used disposable Chromium contexts, the rebuilt application, its real worker, and real IndexedDB:

- Both locales: submitted two questions through the UI while offline with identical timestamps; confirmed increasing order and persistence across an offline reload; held the first controlled SSE response to establish sequential replay and unsynced state until completion; confirmed committed synced flags and no duplicate delivery after another reconnect.
- Overlap: repeated online events and a second tab while the first response was held produced no competing replay with Web Locks available.
- Migration: seeded an actual version-1 database and confirmed version-2 migration preserved IDs, payloads, timestamps, and synced flags, with deterministic legacy tie ordering.
- Failure/recovery: a controlled HTTP 503 left both queries pending, stopped before the second query, and produced no unsolicited retry during the observation period. The next reconnect replayed both in order. Existing error reports were retained.
- Real backend: two offline submissions survived reload, replayed sequentially through the running local Oracle with no mocked requests or responses, became synced, and were not resent on another reconnect.

The original smoke scripts remain local verification artifacts. Their deterministic queue coverage is now maintained in `services/frontend/e2e/pwa-queue-reconnect.spec.ts`: all six isolated Chromium scenarios passed locally, including additional empty/invalid-stream and synced-transaction-abort recovery cases. The compatibility monitor runs this coverage against a fresh production build and extends the existing CI workflow. Those local results predate the 2026-10-08 repair and do not establish its hosted CI status. Cross-tab exclusion on browsers without Web Locks and background delivery with all pages closed were not verified or claimed.

## Coordination and AI-use record

Share this interface note with Team 3 through the team's normal coordination process before sharing the contract change for integration. Team 3 approval or agreement has not been established. Creating this document sends no messages and does not constitute approval.

AI assistance was used to inspect the existing PWA queue integration, explain the assignment, propose additive implementation snippets, type-check temporary copies, and prepare this note. The developer applied the implementation. During the 2026-10-08 repair, AI assistance rebased the task, adapted the test/CI interfaces and verified the separate combined Team 3 preview. During earlier review, AI assistance corrected the database version left at 1, removed a duplicated completion block so the synced commit precedes complete UI state, cleaned whitespace, rebuilt the frontend, and executed the checks above. This shareable note documents the additive domain-contract amendment, design decisions, and verification limits.
