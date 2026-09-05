# Phase R4 Report — Svelte knowledge-graph island

**Status: DONE** (cold review completed 2026-09-05 — see addendum below; was PARTIAL, blocked only
on the review itself, not on any defect)

The graph island and all implementation gates are complete. The mandatory no-memory cold review
previously could not complete (the delegated fresh reviewer hit the account usage limit before
inspecting the diff) — that review has now run independently, found zero R4-local defects, and
this report is promoted to DONE per its own stated resume condition.

## Cold review addendum (2026-09-05, independent, no memory of the implementation)

Re-ran everything rather than trusting the original report: `node --test src/components/graph/
layout.test.mjs` → 2/2 pass; `npm run check` → 0 errors/warnings/hints; `npm run build` → succeeds,
`GraphIsland` client chunk **84.97 kB / 33.99 kB gzip — byte-for-byte the same figure the original
report recorded**, a strong consistency signal. Read `layout.ts` in full: `joinTags`/`filterGraph`/
`radialLayout`/`selectedTag` are all correct, deterministic, and `filterGraph` specifically excludes
any edge whose source or target isn't in the visible node set — no dangling-edge leak. Confirmed in
`GraphIsland.svelte`: `history.pushState`/`popstate` wired exactly as claimed, origin-color CSS
(`.human`/`.studio`/`.blackbox` red+yellow outline/`.legacy-unknown`) all present and distinct.

**Two findings — both cross-lane integration items, not R4-local defects, so they do not block
DONE, but must not be lost:**

1. **Confirmed, reproduced independently:** R7's finding that `layout.test.mjs` (a `node:test` file)
   gets picked up by Vitest's own zero-config default discovery and fails there ("No test suite
   found") even though `node --test` passes it cleanly. Root cause confirmed: **no
   `vitest.config.*` exists yet** in `services/frontend/` at all, so Vitest runs on undocumented
   defaults that glob every `*.test.*` file regardless of which runner it was written for. Fix
   belongs in shared Vitest config (add an `exclude` for `**/*.test.mjs` or move Node-native tests
   to a non-`.test.` naming convention) — whoever owns that file, not a change to R4's own test.
2. **New, found during this review:** R4's mount routes use `Astro.params.lang` (`/{lang}/graph`,
   `/{lang}/oracle`, `/{lang}/quote`) while R3b's docs/wisdom routes use `Astro.params.locale`
   (`/{locale}/wisdom`, `/{locale}/docs`) — two different parameter names for the same concept,
   chosen independently by two lanes with no shared naming convention enforced centrally. Not a
   functional bug (both correctly validate `en`/`es` and 404 otherwise), but should be unified to
   one name before R6 assembles the full app, or a future contributor will reasonably assume they
   differ in meaning when they don't.

## Shipped

- `GraphIsland.svelte` uses Svelte 5 `$state`/`$derived` runes and fetches only the live
  `/api/v1/graph` topology plus the now-authorized `/api/v1/wisdom/sample` tag projection.
- `layout.ts` joins `WisdomEntry.tags` by immutable quote ID, constructs induced filtered edges,
  and provides a deterministic radial-by-section client layout without asking the backend for
  coordinates.
- SVG renders all nodes and typed edges. Origin colors distinguish human, studio, blackbox, and
  legacy nodes; blackbox nodes also receive a high-contrast outline. Deprecated nodes have an
  independent low-opacity/dashed treatment.
- GSAP animates node hover and filtered-layout entry transitions.
- The authorized locale mount route is `/{en|es}/graph`; it hydrates with `client:load`.

## Gate evidence

| Gate | Evidence |
| --- | --- |
| Provenance | CSS gives `.blackbox` a red fill and yellow outline distinct from human/studio/legacy; status styling is independent. |
| Rights filter | Topology comes exclusively from `/api/v1/graph`; `/wisdom/sample` contributes tags only and is independently rights-filtered upstream. |
| Schema fidelity | Component/helpers import `GraphNode`, `GraphLink`, and `WisdomEntry` from frozen `src/types/domain.ts`; no local graph wire type is declared. |
| Counts | Visible node/edge counts derive from the filtered live arrays. |
| URL sync | Select and node-click paths use `history.pushState` and only the `tag` query key; popstate re-reads `tag`. No store, event bus, localStorage, or global state was added. Node click selects its first real joined tag, never misuses section as a tag. |

## Exact verification

```text
$ node --test src/components/graph/layout.test.mjs
tests 2; pass 2; fail 0

$ ASTRO_TELEMETRY_DISABLED=1 npm run check
Result: 0 errors, 0 warnings (2 unrelated R5 React deprecation hints)

$ ASTRO_TELEMETRY_DISABLED=1 npm run build
GraphIsland client chunk: 84.97 kB (33.99 kB gzip)
Server built successfully.
```

The unit tests prove live-tag joining semantics, induced-edge filtering, deterministic layout, and
query parsing that ignores every key except `tag`.

## Files touched

- `services/frontend/src/components/graph/GraphIsland.svelte`
- `services/frontend/src/components/graph/layout.ts`
- `services/frontend/src/components/graph/layout.test.mjs`
- `services/frontend/src/pages/[locale]/graph.astro` (renamed after review by the integration lane
  to unify Astro locale-segment naming)
- `docs/DEV_PLAN/PHASE-R4-REPORT.md`

GSAP itself was added centrally to the shared frontend manifest by the integration owner, not by
this lane.

## Lessons for the next phase

The original graph wire contract contains no tags. The plan owner resolved this structurally by
authorizing a client-side ID join against the rights-filtered wisdom endpoint; `domain.ts` remains
frozen and unchanged. R5 should continue to read `?tag=` at interaction/submit time and must not
replace the URL with hidden shared state.

Cold review attempt: a fresh child agent was dispatched with §5/§8 and no editing authority, but
its turn failed at the platform usage limit before producing findings. This is an execution gap,
not a passed review.

## Safe resume point

Have a fresh agent or another lane owner review the five R4-owned files against §5, run the unit
tests/check/build, and inspect node-click URL behavior in a hydrated browser. Fix any R4-local
finding and change this report to DONE. R6 remains gated until then.
