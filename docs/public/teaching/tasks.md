---
title: Task details
eyebrow: Every assignable task, expanded
description: Per-task detail for the team task board — what visible result each task looks for, what it includes, and what has to be done, straight from each module's own ASSIGNMENT.md.
permalink: /teaching/tasks/
---

# Every task, expanded

The [team task board]({{ '/teaching/assignments/#team-task-board' | relative_url }}) lists ~10
tasks per team. This page is the detail behind each one — grounded directly in the `ASSIGNMENT.md`
file that ships inside the module's own code, not a separate retelling of it. Three tasks recur
identically on every team's list (cross-module PR, cross-module review, defense documentation) —
[explained once, near the bottom](#the-three-recurring-tasks), linked from every team section
instead of repeated five times.

## Team 1 — Content, i18n & Proposals UI

**Starting point:** one localized index route and one localized detail route, both already
fetching real entries and rendering `en`/`es`. Section, tag, and level browsing do not exist on
this branch yet — that absence is deliberate, not a bug to report.

**Task 1 — Section, tag, and level browse routes**
- *Visible result:* three working routes (`/wisdom/sections/<id>/`, `/tags/<id>/`, `/levels/<id>/`)
  that filter the same live data the index page already fetches.
- *What it includes:* new Astro routes, using the existing `frequencies()` helper (already
  exported, not yet called by anything) to compute the facet lists.
- *What has to be done:* build the route, the facet-list UI, and the filtered listing — the data
  layer already exists, this is the missing presentation and routing layer.

**Task 2 — Breadcrumb navigation**
- *Visible result:* every content route shows a clear path back to where the visitor came from
  (index → section → detail, not just a flat "back").
- *What it includes:* a shared breadcrumb component or pattern reused across index, facet, and
  detail routes.
- *What has to be done:* design the breadcrumb hierarchy once the facet routes above exist, then
  wire it into each route's layout.

**Task 3 — Empty-state and error-state handling**
- *Visible result:* a facet with zero matching entries shows a clear, styled empty state — never a
  blank page or an unhandled error.
- *What it includes:* every content route, including the ones you build in Task 1.
- *What has to be done:* design one empty-state pattern, apply it consistently, and confirm the
  backend-unreachable case degrades to a real error message, not a stack trace.

**Task 4 — Source, rights, and provenance display**
- *Visible result:* every quote page visibly shows its holder, license, and origin — not just the
  text.
- *What it includes:* the existing detail route already has this data (`WisdomEntry.rights`,
  `.origin`) — the task is surfacing it clearly, not fetching anything new.
- *What has to be done:* design a compact, accessible provenance block and apply it to every quote
  view (index cards, facet listings, detail page).

**Task 5 — The "propose a quote" form UI**
- *Visible result:* a logged-in visitor can fill in a quote, its section, and its source, and
  submit it — the request reaches the backend endpoint Team 5 owns.
- *What it includes:* the form itself, client-side validation, and a clear success/pending state
  after submission. It does **not** include the review pipeline itself (that's Team 5's task 4).
- *What has to be done:* coordinate the request shape with Team 5 before building against it;
  build the form behind `requireUser()`-gated access; handle the "not logged in" case gracefully.

**Task 6 — Unit and component tests**
- *Visible result:* content routes and the propose form each have at least one real test, wired
  into the same CI job every other module's tests run in.
- *What it includes:* one unit test (e.g., a pure content-filtering function) and one component
  test (a rendered route or the form), matching the Testing Trophy layering the whole project uses
  — see [Team 2's testing task](#team-2--knowledge-graph) for the shared philosophy.
- *What has to be done:* pick the cheapest layer that gives real confidence — do not write a heavy
  E2E test for something a unit test already proves.

## Team 2 — Knowledge Graph

**Starting point:** one hydrated Svelte island that fetches the live graph, lays every node out,
and reflects one click/keyboard selection in an accessible panel. Tag filtering, URL state, and
motion are deliberately absent.

**Task 1 — Tag-filter interaction**
- *Visible result:* a dropdown (or equivalent control) that narrows the visible graph to one tag's
  neighborhood.
- *What it includes:* `layout.ts` already exports `filterGraph` and `selectedTag` — hello-world
  never calls them. This task is wiring existing, tested logic into a UI control.
- *What has to be done:* build the control, call `filterGraph`, and confirm the graph re-renders
  correctly when the filter changes or clears.

**Task 2 — URL state for the current selection/filter**
- *Visible result:* the current tag filter and node selection are reflected in the address bar,
  and reloading or hitting back restores them.
- *What it includes:* reading and writing query parameters, and handling the browser's `popstate`
  event.
- *What has to be done:* pick a URL shape (e.g., `?tag=architecture&node=arch-031`), keep it in
  sync with the filter/selection state, and restore state from it on load.

**Task 3 — Layout and performance at real corpus scale**
- *Visible result:* the graph stays responsive and legible with the full governed dataset loaded
  — not just a small sample.
- *What it includes:* the existing `radialLayout` function; this task is about tuning it, not
  replacing it, unless you can justify why.
- *What has to be done:* measure actual render/interaction performance at full scale, identify the
  real bottleneck (layout computation vs. DOM node count vs. re-renders), and fix that specific
  bottleneck.

**Task 4 — One entrance or selection animation**
- *Visible result:* at least one moment in the graph (nodes appearing, or a selection changing)
  has a deliberate, justified animation — not decoration for its own sake.
- *What it includes:* the origin-color legend already exists and can stay as-is, be restyled, or
  fold into your filter UI — it is not the assessed seam here.
- *What has to be done:* choose one animation moment, implement it, and be ready to explain in the
  defense why that moment specifically earns motion.

**Task 5 — Keyboard operability audit**
- *Visible result:* every interactive graph element (nodes, the filter control) is fully operable
  by keyboard alone, with visible focus at every step.
- *What it includes:* the existing hello-world selection already has `role="button"`, `tabindex`,
  and `onkeydown` — the audit is confirming nothing you add breaks that, and extending the same
  pattern to your new filter control.
- *What has to be done:* tab through the entire graph experience with a keyboard only, fix any
  point where focus is lost or an action is mouse-only.

**Task 6 — Unit and component tests**
- *Visible result:* the graph island has at least one unit test (a pure function like
  `filterGraph` or `radialLayout`) and one component test (the island rendering and responding to
  a selection).
- *What it includes:* this is the shared Testing Trophy approach every team uses — see the
  project's [testing philosophy]({{ '/guides/contributing/' | relative_url }}) for what "the
  cheapest useful layer" means in practice.
- *What has to be done:* test the pure logic directly (fast, no rendering needed), and test the
  rendered island only for what a unit test can't cover (actual DOM interaction).

## Team 3 — Oracle Terminal

**Starting point:** one prompt, one streamed response, grounded-vs-creative mode, cited quote IDs,
and a busy/double-submit guard. Offline queueing, multi-turn history, and propose-from-answer are
deliberately absent.

**Task 1 — Streamed response rendering**
- *Visible result:* already working on this branch — this task is about *extending* it, not
  building from zero: multi-turn history rendered as more than one visible exchange.
- *What it includes:* the existing `readOracleStream`/`parseSseEvent` helpers, which must stay
  exactly as they are — the lesson is consuming a stream correctly, not writing a second parser.
- *What has to be done:* build `sessionHistory` from completed exchanges and send it on
  subsequent requests; render the growing conversation, not just the latest answer.

**Task 2 — Live-region announcement for screen readers**
- *Visible result:* a screen-reader user hears the answer as it streams in, not silence followed
  by the full text at the end.
- *What it includes:* the existing `aria-live`/`aria-busy` pattern already used for the busy
  guard — extend the same discipline to the streaming text itself.
- *What has to be done:* confirm with a real screen reader (not just visual inspection) that
  incremental updates are actually announced, not just present in the DOM.

**Task 3 — Grounded vs. creative mode disclosure**
- *Visible result:* already partially working — the task is making the distinction unmistakable,
  never color-only (a text label is required, not optional).
- *What it includes:* `citedQuoteIds` on grounded segments must render as navigable links, not
  just plain text.
- *What has to be done:* audit every place mode is shown and confirm a color-blind or
  screen-reader user gets the same information a sighted user does.

**Task 4 — Offline queue integration**
- *Visible result:* an unreachable Oracle enqueues the query on-device; reconnecting flushes
  unsynced entries in order.
- *What it includes:* `lib/db.ts`'s existing `OfflineLogEntry` mechanism (`enqueueOracleQuery`,
  `markEntrySynced`, `enqueueErrorReport`, `listUnsyncedEntries`) — owned by Team 4, **called**
  from here. Do not build a second queue.
- *What has to be done:* coordinate the exact call shape with Team 4 before wiring it in; confirm
  the flush-on-reconnect path actually fires on a real `online` event, not just in a mocked test.

**Task 5 — Recovery/error state**
- *Visible result:* when the Oracle is genuinely unavailable (not just cold-starting), the UI says
  so clearly instead of hanging or showing a raw error.
- *What it includes:* distinguishing "still warming up" from "actually broken" — these are
  different states with different correct UI responses.
- *What has to be done:* design both states explicitly and trigger each one deliberately (kill the
  backend vs. simulate a cold Ollama volume) to confirm the right one shows.

**Task 6 — Propose-from-answer**
- *Visible result:* a completed creative (non-grounded) answer can be proposed for human review —
  but only on an explicit click, never as a side effect of streaming finishing.
- *What it includes:* `POST /api/v1/oracle/propose`, already a real endpoint.
- *What has to be done:* add the UI affordance, confirm it only appears on creative-mode answers,
  and confirm the click is the only trigger.

**Task 7 — Unit and component tests**
- *Visible result:* the terminal and its streaming logic each have at least one real test.
- *What it includes:* testing the streaming state machine (a unit-level concern) separately from
  the rendered terminal's behavior (component-level).
- *What has to be done:* do not poll the stream endpoint or collapse SSE into one buffered
  response just to make testing easier — test the real streaming behavior.

## Team 4 — PWA & Local Operations

**Starting point:** one service worker, one installable manifest, and one visible online/offline
banner — enough to observe a local/offline boundary. Not a finished PWA, performance programme, or
CI/CD pipeline.

**Task 1 — Cache-First vs. Network-First policy**
- *Visible result:* static assets load instantly from cache; `/api/*` responses are never served
  stale from cache.
- *What it includes:* the starter's `sw.js` already Cache-Firsts exactly one file
  (`tokens.css`) — the task is extending that policy correctly, asset by asset, never applying
  Cache-First to `/api/*` "just for the stub."
- *What has to be done:* read `public/sw.js` fully first — its own comments name what's
  deliberately unimplemented; extend from there, don't rewrite it.

**Task 2 — Offline queue that flushes on reconnect**
- *Visible result:* actions taken offline (like an Oracle query from Team 3) are queued and
  replayed once the connection returns, in order.
- *What it includes:* `src/lib/db.ts`'s existing queue, which you own and Team 3 calls into — read
  and extend it, do not rewrite it out from under them.
- *What has to be done:* coordinate the exact interface with Team 3; confirm ordering is preserved
  and successes are marked synced, not silently retried forever.

**Task 3 — Install-quality checks**
- *Visible result:* a Chromium browser treats the app as genuinely installable — correct icon,
  name, theme color, and `display: standalone`.
- *What it includes:* the starter manifest already has the minimum fields; this task verifies and
  completes them for a real install prompt, not just a technically-valid JSON file.
- *What has to be done:* actually trigger the install flow in a real browser and confirm it looks
  right, not just that DevTools' manifest checker is silent.

**Task 4 — Measured performance budget**
- *Visible result:* a specific, named optimization with a measured before/after number (Core Web
  Vitals or equivalent) — never a claimed improvement without a measurement.
- *What it includes:* designing your own budget is explicitly part of this assignment — the
  starter deliberately ships with no Lighthouse CI gate yet, so you aren't inheriting someone
  else's numbers.
- *What has to be done:* measure first, pick one real bottleneck, fix it, measure again, and keep
  both numbers for the defense.

**Task 5 — Service-worker lifecycle correctness**
- *Visible result:* you can demonstrate `install`, `activate`, and `fetch` behaving correctly,
  including the worker claiming clients and updating its cache name on a new version.
- *What it includes:* explaining this is itself a learning outcome — the defense will ask you to
  walk through what happens when the token/cache version changes.
- *What has to be done:* deliberately trigger an update (change the cache name, reload) and
  confirm old caches get cleaned up, not silently accumulated.

**Task 6 — Unit and component tests**
- *Visible result:* the offline boundary (queue + banner) has at least one real test.
- *What it includes:* testing the queue's ordering/flush logic directly, separately from the
  banner's visual online/offline state.
- *What has to be done:* simulate `online`/`offline` events in the test rather than requiring an
  actual network change to verify behavior.

## Team 5 — Accounts, Library, Proposals & Public API

**Starting point:** one seeded user, `requireUser()` protecting `/account`, an httpOnly signed
session cookie, and a separate bearer token from `POST /api/v1/auth/token`. This is the one team
whose area has no existing reference code to reduce — it's new, not a subtraction.

**Task 1 — Login/session**
- *Visible result:* already working on this branch for the seeded account — the task is
  extending it to real registration, not just the one fixture user.
- *What it includes:* the existing `requireUser()`/`requireRole()` guards run in Astro frontmatter
  — before any HTML is sent, matching the FE I SSR-auth pattern this is directly built on.
- *What has to be done:* never protect a route only in client-side JSX/Svelte state — a
  logged-out `curl` of a protected URL must not contain gated content in the raw response.

**Task 2 — Personal favorites library**
- *Visible result:* a logged-in user can save a quote, see their saved list, and remove one from
  it.
- *What it includes:* a new, small backend store for favorites — deliberately **not** `ttod.yml`,
  since favorites are per-user preference data, not governed corpus data.
- *What has to be done:* design the minimal favorites schema, the three endpoints (save, list,
  remove), and the UI page that uses them.

**Task 3 — The propose-a-quote backend endpoint**
- *Visible result:* Team 1's propose form successfully creates a real proposal record when
  submitted.
- *What it includes:* calling the exact same `ttod_core.proposals.create_proposal(...)` primitive
  `cli.py proposal create` already uses — this reuses 100% of existing proposal infrastructure, it
  does not build a parallel one.
- *What has to be done:* agree the request shape with Team 1 first; the endpoint's only job is
  translating an authenticated web request into that existing primitive.

**Task 4 — The GitHub-native review pipeline**
- *Visible result:* a submitted proposal becomes a real PR; a reviewer's approval computes the
  exact canonical diff; a second approval on that diff is what actually publishes it.
- *What it includes:* the pipeline already exists and is documented on the [contributing
  guide]({{ '/guides/contributing/' | relative_url }}) with its own diagram — your task is
  operating it correctly for real proposals, and explaining the two-touchpoint design in your
  defense.
- *What has to be done:* trace one real proposal through the entire pipeline end to end at least
  once before considering this task done.

**Task 5 — Bearer-token-authenticated public API**
- *Visible result:* an external client (not a browser) can call `GET /api/v1/wisdom/random` with
  `Authorization: Bearer <token>` and get a quote back.
- *What it includes:* the token comes from `POST /api/v1/auth/token` — a genuinely separate
  credential from the session cookie, never the same JWT reused in both places.
- *What has to be done:* verify the endpoint rejects requests with no token, an invalid token, and
  a valid session cookie presented as if it were a bearer token (it must not work).

**Task 6 — API documentation and a minimal example client**
- *Visible result:* a documentation page any external developer could follow, and a small script
  (not a second application) proving the API works outside a browser.
- *What it includes:* the documentation should be generated from or checked against the same
  `domain.ts` shapes governing every other module — "types are the contract," applied here too.
- *What has to be done:* write the docs, then actually run the example script against your own
  running instance before calling this done — a script that's never been executed is not proof of
  anything.

**Task 7 — Unit and component tests**
- *Visible result:* auth, the library, and the API each have at least one real test.
- *What it includes:* a test that a logged-out request to a protected route is actually rejected
  — not just that a logged-in one succeeds.
- *What has to be done:* never store the session in `localStorage`, never hand-roll password
  hashing, never reuse the session token as the bearer token — these are prohibited shortcuts, not
  style preferences, and a test that only checks the happy path won't catch them.

## The three recurring tasks

Every team's list ends with the same three tasks — explained once here, not five times above.

**Cross-module PR.** Open at least one real PR into a module you don't own — a genuine fix or
small enhancement, not a drive-by typo commit. This is graded as process evidence, not extra
credit, and it's the one task that genuinely cannot be one-shotted by an AI coding assistant: it
requires reading and modifying code you didn't write.

**Cross-module review.** Formally review at least one PR outside your own module, using that
module's own `ASSIGNMENT.md` as your review checklist — the same document that told its own team
what "done" looks like tells you what to check.

**Defense documentation.** Pick one real design decision you made — not a hypothetical one — and
be ready to explain it, and a real alternative you considered, in the oral defense. "I didn't
think about alternatives" is a weaker defense answer than "I considered X, rejected it because Y."

## Related pages

- [Team task board]({{ '/teaching/assignments/' | relative_url }})
- [Teaching model — the six expansion areas]({{ '/teaching/' | relative_url }})
- [Contributing — how to open a PR, how review works]({{ '/guides/contributing/' | relative_url }})
