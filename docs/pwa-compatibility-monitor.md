# PWA/Oracle compatibility monitor

This repository checker protects the interface and replay behavior documented in
[the Task 4 contract](pwa-offline-queue.md). It runs locally, can watch the current
checkout, and extends the existing frontend CI workflow. It uses TypeScript and
Chromium rather than an LLM: no AI service, API key, or autonomous code author is
required.

## Running it

From `services/frontend`, with the repository's supported Node version and existing
dependencies installed:

```sh
npm ci
npx --no-install playwright install chromium
npm run pwa:guard
```

The full command checks the caller contract, runs the checker's regression checks,
Astro diagnostics and TypeScript, builds the frontend, and runs the PWA browser
cases selected by `playwright.pwa.config.ts`. Task 4 supplies six queue scenarios;
Task 5 adds two manifest/icon checks, for eight cases in total. It stops after a
failed phase. It starts its own built frontend on
`127.0.0.1:4327`, refuses to reuse an existing server there, and stops that server
when the browser suite finishes. Docker, Ollama and backend credentials are not
needed. On Linux, Playwright may also need its documented browser system
dependencies (`playwright install --with-deps chromium`, as used in CI).

For automatic checks while editing:

```sh
npm run pwa:watch
```

Leave this command running in a terminal. It checks immediately, then compares
content hashes approximately every second and waits another 500 ms after detecting
changes. Checks run sequentially. An edit during verification invalidates that
result and schedules another pass. `Ctrl+C` stops the watcher and active check
processes. No persistent background service is installed. Restart the watcher after
editing the checker scripts themselves so their new implementation is loaded.

For a quick contract/EOF check without building or launching Chromium:

```sh
npm run pwa:guard -- --static
npm run pwa:watch -- --static
```

Static mode does **not** establish runtime correctness. Exit codes are `0` for a
passing single run, `1` for a failing run, `2` for invalid options or another guard
owning the reports, and `130` when stopped. Watch mode keeps running after a failure
so the next edit can recover it. Only one guard can own this checkout's reports at
a time; stop the watcher before running a separate full check.

## What is checked

| Layer | Protection |
| --- | --- |
| Consumer contract | `contracts/pwa-queue.ts` compiles against the real domain types and DB exports. Existing payload/entry fields, old caller constructions, optional numeric `queueOrder`, and the three helper signatures must remain compatible. New optional fields are permitted; new required fields are rejected. |
| Checker regression coverage | Five Node checks prove that optional additions pass, incompatible required fields/types or missing helpers fail, literal whitespace is preserved, and changed-file comparisons detect additions/deletions/edits. |
| Application gates | Existing Astro diagnostics, TypeScript and production build must pass. |
| Browser integration | Real built Oracle pages, real service worker and real IndexedDB exercise English/Spanish offline UI submission, reload persistence, equal timestamps, sequential replay, repeated online events, competing tabs, and accessibility. |
| Migration and recovery | An actual version-1 database is upgraded without losing payloads, IDs, timestamps, synced flags or error reports. HTTP 503, empty/invalid streams and a synced transaction aborted **after request success** must retain pending work and stop the pass. A later reconnect must recover in order. |
| Manifest/icon checks (Task 5) | The new spec checks the served manifest/page metadata, required PNG/SVG entries, HTTP/MIME/PNG data and actual decoded PNG dimensions. It does not install the app. |

Browser tests deliberately control Oracle SSE responses to make success and failure
reproducible. They verify the frontend queue contract, not backend inference or
server-side exactly-once execution. The prior Task 4 live-backend smoke outcome is
recorded separately in the contract note. Tests follow the project's
[Unit 5 testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/).

### Task 5 manifest/icon selection

The authored `e2e/pwa-installability.spec.ts` adds two metadata/icon cases. They run
alongside the six queue cases through the `testMatch` property inside `defineConfig`
in **`playwright.pwa.config.ts`**:

```ts
testMatch: /pwa-(?:queue-reconnect|installability)\.spec\.ts/,
```

Keep the general `playwright.config.ts` free of that PWA-only filter so the normal
suite continues to include all existing coverage. The initial Task 5 run failed
because the matcher was misplaced in the general config, including a stray
top-level copy. That configuration has been corrected; the full local guard now
passes all eight cases. The [Task 5 install note](pwa-install-quality.md) records
separate CDP install/relaunch checks and developer-reported Brave installation.

The watcher covers `src/`, `public/`, `contracts/`, `e2e/`, `scripts/`, package and
lock files, frontend TypeScript/Astro/Playwright configuration, the frontend CI
workflow, `docs/pwa-offline-queue.md` and `docs/pwa-compatibility-monitor.md`. It
ignores generated build/test output. It sees
uncommitted edits and files arriving through a branch checkout or merge, but does
not fetch branches or inspect another team's unpublished work. Other configuration
changes can be checked with a manual full run.

## Repair and failure reporting

By default the checker leaves source unchanged. A failure prints diagnostics and
writes ignored local artifacts under `services/frontend/test-results/`:

- `pwa-guard/report.md`: readable result, phases and findings.
- `pwa-guard/report.json`: machine-readable result and phase timings. During a run
  it explicitly says `status: running`; the old green result is replaced.
- `pwa-guard/guard.log`: output of the check/build/browser phases.
- `pwa-guard/browser-results.json` and `pwa-browser/`: browser results and failure
  traces according to the existing Playwright settings.
- `pwa-guard/formatting.patch`: a repair proposal when EOF whitespace needs cleanup.

The regular Playwright suite writes to `test-results/browser/` so its cleanup
preserves the monitor's separate reports and lock.

The only automatic source repair is normalization to one final newline in
`src/lib/db.ts`, `src/types/domain.ts`,
`src/components/oracle/OracleTerminal.tsx`, and `public/sw.js`. It parses each file
first, refuses malformed source, preserves whitespace inside literals/JSX, and
refuses to overwrite a file changed since the proposal was made:

```sh
npm run pwa:fix
# For the narrow repair plus the static check only:
npm run pwa:fix -- --static
```

To review the proposed patch instead, run from the repository root:

```sh
git apply --check services/frontend/test-results/pwa-guard/formatting.patch
git apply services/frontend/test-results/pwa-guard/formatting.patch
```

Semantic failures get diagnostics and test evidence. For example, making a payload
field mandatory fails the consumer fixture; accepting an empty stream as synced
fails browser recovery coverage. Inspect the named phase, repair the implementation
against the documented contract, and rerun. An intentional interface change needs
an updated shared note, relevant checks, and coordination with Team 3. The tool does
not silently update the baseline to accept drift, rewrite replay logic, create a
commit, open a PR, or claim anyone approved a change.

## CI and coordination

`.github/workflows/ci.yml` keeps the existing required `typecheck-and-build` job
and adds `pwa-compatibility`. Once the changes are committed and pushed, this
workflow runs on every pull request, relevant pushes on any branch, and manual
dispatch. Push paths include the frontend, this workflow and the two PWA notes.
The expanded push trigger also runs the existing frontend job on feature branches.
The compatibility job installs Chromium, runs the same guard, adds the result to
the job summary, and uploads reports/repair proposals/failure traces for seven days.
It has read-only repository permissions and a five-minute timeout. Actual hosted
runtime has not been measured locally.

The failed check and job summary are the automatic notification surfaces. GitHub
email/web notifications depend on each person's
[Actions notification settings](https://docs.github.com/en/actions/concepts/workflows-and-actions/notifications-for-workflow-runs).
No Slack/email message is sent by this implementation. Installing these files
locally does not activate remote CI; publication and repository check requirements
are separate steps. The trigger configuration follows
[GitHub's workflow event documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).
The isolated server follows [Playwright's web-server configuration](https://playwright.dev/docs/test-webserver).

A passing check covers this checkout and these scenarios. It cannot prove every
semantic change safe or replace the Team 3 agreement on payloads, helper APIs,
replay ownership and synced semantics. Team 3 acknowledgment remains pending.

## Local verification — Task 4 history

The full guard passed locally on 2026-10-07, including five checker regression
checks, zero Astro diagnostics, TypeScript/build and all six isolated Chromium
scenarios. Disposable-copy command/watch experiments proved failure detection,
recovery, patch validity, lock exclusion and clean shutdown. The complete browser
suite passed all 29 checks against the rebuilt local stack; the existing six
frontend unit/component checks and repository validation plus 236 Python checks
also passed. No hosted Actions run is claimed.

### Task 5 verification

After correcting the misplaced matcher, a fresh full guard passed locally on
2026-10-07, including the caller contract, five checker regressions, zero Astro
diagnostics, TypeScript/build and all eight isolated Chromium cases in 10.9 seconds.
This is verification of the applied Task 5 checkout, separate from the historical
queue-only run above. The complete Chromium suite also passed all 31 tests against
the rebuilt Docker application in 25.2 seconds. The developer subsequently reported
successful manual installation; standalone launch and installed accessibility
details remain unreported. See the install-quality note for evidence status.
No hosted Actions result is claimed.

AI assistance designed and implemented this checker, regression coverage, CI
extension and documentation, and ran local verification. The existing Task 4
application implementation is described in its own contract/design note.
