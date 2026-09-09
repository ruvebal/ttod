<!--
Self-contained runbook. Derived from PHASE-U-FEII-TEACHING-SKELETON-CASCADE.md §2, §5 TS3 and
PHASE-U-WEEK0-ORCHESTRATION.md — that orchestration document is normative; regenerate this one if
it changes. Generated as part of the Week-0 skeleton-generator pass.
-->

# Phase U · TS3b — R4 Svelte graph hello-world reduction

**Mode:** student lane (or instructor-built if executed before cohort start), 1 owner
**Entry:** TS1 `DONE`; TS3a's route/locale contract confirmed (this lane does not need TS3a's
files, only its frozen contract)
**Exit:** one hydrated island, a tiny real node/edge neighborhood, one selection reflected in
accessible text — no tag filter, no URL state, no GSAP

---

## 0. What this phase actually is

`GraphIsland.svelte` today is 104 lines that already merge the hello-world seam and the full
assignment depth into one file: it fetches the live graph, lays it out radially, renders it as
accessible SVG with keyboard support — *and* it also has a tag-filter dropdown synced to the URL,
GSAP entrance/hover animation, and a legend. Phase U's own contract table names the second half
("full graph exploration, filtering, layout controls, animation, URL-state design, large-corpus
performance") as *deliberately absent* — this phase's job is exactly that subtraction, not a
rewrite of the fetch/render/select core, which already is hello-world shaped.

## 1. Required reading

- `PHASE-U-FEII-TEACHING-SKELETON-CASCADE.md` §2 (R4's row).
- Live files: `services/frontend/src/components/graph/GraphIsland.svelte` (104 lines),
  `services/frontend/src/components/graph/layout.ts` (51 lines, has its own `layout.test.mjs` —
  do not touch, R7's territory), `services/frontend/src/pages/[locale]/graph.astro` (the page that
  mounts this island).
- `docs/DEV_PLAN/PHASES/U-TS1-subtraction-and-contracts.md`'s subtraction table.

## 2. Non-negotiable boundaries

- **Work on `skeleton/ts3b-r4`, forked from `skeleton/ts1-contracts`.**
- **Do not touch `layout.ts` or `layout.test.mjs`.** `radialLayout`, `filterGraph`, `joinTags`,
  and `selectedTag` are pure functions with their own test file — R4's hello-world reduction keeps
  calling `radialLayout`/`joinTags` and simply stops calling `filterGraph`/`selectedTag`. Deleting
  or editing `layout.ts` is out of scope; it is shared, tested infrastructure, not this lane's file.
- **Do not touch `/api/v1/graph` or `/api/v1/wisdom/sample`.** Same backend-boundary rule as TS3a.
- **Keep the accessibility contract.** `role="button"`, keyboard handling (`Enter`/`Space`), and
  `aria-label` on each node are instructor-provided, not assignment depth — Phase U's invariant 2
  ("complete spine, shallow organs") means the *organ* is small, not that accessibility is cut to
  make it smaller.

## 3. Domain contract slice

```typescript
// services/frontend/src/types/domain.ts — frozen by TS1
export interface GraphNode { id: string; section: string; origin: WisdomEntry['origin']; status: 'active' | 'deprecated' | 'erased'; text: string; lang: string; }
export interface GraphLink { source: string; target: string; rel: 'related' | 'immediate_parent' | 'root_source' | 'deprecated_by' | 'superseded_by' | 'translation_of'; }
```

Fetch contract unchanged: `GET /api/v1/graph` → `{ nodes: GraphNode[], edges: GraphLink[] }`,
joined with `GET /api/v1/wisdom/sample` via `layout.ts`'s existing `joinTags()`.

## 4. Scope — exact keep/cut

| Block in `GraphIsland.svelte` (by responsibility) | Keep | Cut → assignment |
| --- | --- | --- |
| `onMount` fetch of `/api/v1/graph` + `/api/v1/wisdom/sample`, `joinTags` | Yes | — |
| `radialLayout(filtered.nodes)` call | Yes, but call `radialLayout(allNodes)` directly (no `filterGraph` step) | — |
| `activeTag` state, `<select>` dropdown, `setTag()`, `syncFromUrl()`/`popstate` listener | No | "Tag filter with URL state" — assignment line |
| GSAP import, `hover()` handler, entrance animation in `setTag` | No | "Motion/animation system" — assignment line |
| `selected` state, click-to-select, `<aside>` detail panel | Yes — this is the "one selection reflected in accessible text" Phase U's contract names explicitly | — |
| Origin-color legend (`.legend` markup + CSS) | Optional keep (cheap, already accessible via `<title>`); if cut, name it as a small assignment line too | — |
| `loading`/`error` states | Yes — empty/limitation states are instructor-provided per Phase U invariant 5 | — |

**Net effect:** the hello-world island fetches, lays out, and renders every real node/edge it
receives (no filtering — Phase U's contract says "a tiny real node/edge neighborhood," so consider
whether the *backend* sample response is already small enough, or whether R3b/backend should be
asked to cap it — flag to TS1's owner rather than truncating client-side in a way that hides real
data), and lets a user click exactly one node to see its text via an accessible panel. No dropdown,
no URL parameter, no animation library import.

**`ASSIGNMENT.md`** (new, `services/frontend/src/components/graph/ASSIGNMENT.md`): learning
outcomes (Svelte 5 runes, island hydration, SVG accessibility), constraints (must keep using
`radialLayout`/`joinTags` from `layout.ts` — do not fork or reimplement layout math), acceptance
criteria (tag filter reflected in the URL, at least one entrance/selection animation, keyboard
parity preserved), prohibited shortcuts (do not remove the keyboard/`aria-label` handling that
already exists to make the filter "simpler").

## 5. Mechanical gates

| Gate | Required proof |
| --- | --- |
| Island renders | `/en/graph/` shows real nodes/edges from the live backend |
| One selection works | clicking (and pressing Enter/Space on) one node shows its text in the aside panel |
| No filter UI | no `<select>`, no `activeTag`, no URL-param read/write in this branch's file |
| No animation import | `gsap` is not imported by this file on this branch |
| `layout.ts` untouched | `git diff main -- services/frontend/src/components/graph/layout.ts` and `layout.test.mjs` are both empty |
| Keyboard/a11y preserved | `role="button"`, `tabindex`, `aria-label`, `onkeydown` all still present on each node |

## 6. Rollback and mutation law

- Read-only against the backend; no write path exists in this component regardless.
- If `layout.test.mjs` fails after this reduction, that is a signal the reduction touched shared
  layout code — it should not have; revert and re-scope to the `.svelte` file only.

## 7. Touched-path budget

**Allowed:** `services/frontend/src/components/graph/GraphIsland.svelte`, a new `ASSIGNMENT.md` in
the same directory, `services/frontend/src/pages/[locale]/graph.astro` (only if the mount point
needs a prop change — expect none).

**Forbidden:** `layout.ts`, `layout.test.mjs`, anything under `components/oracle/`, `lib/db.ts`,
`services/backend/**`, `services/mcp/**`.

## 8. Post-phase review

A second reader confirms the cut features are genuinely absent from the *rendered* output (open
devtools, confirm no dropdown, no URL param appears after a click) rather than just visually
hidden via CSS.

## 9. Phase report status enum

- **DONE** — all §5 gates pass, `ASSIGNMENT.md` filed, `layout.ts` untouched.
- **PARTIAL** — name exactly which gate is unmet.
- **BLOCKED** — TS1 has not filed `DONE`.

## 10. Exact commands

```bash
cd /Users/ruvebal/src/ttod
git worktree add ../ttod-skeleton-ts3b -b skeleton/ts3b-r4 skeleton/ts1-contracts
cd ../ttod-skeleton-ts3b/services/frontend
npx vitest run src/components/graph/layout.test.mjs   # must still pass, untouched
npm run dev   # visit /en/graph/, click one node
```

## 11. Report requirements

File `docs/DEV_PLAN/PHASE-U-TS3b-REPORT.md`: status (§9), confirmation `layout.ts`/
`layout.test.mjs` are byte-identical to `main`, a real screenshot of the reduced island with one
node selected, and the `ASSIGNMENT.md` content.

## 12. Agent prompt — paste this into a fresh agent session with no other file open

```text
Act as TTOD Phase U TS3b engineer. Work only inside a new git worktree on branch skeleton/ts3b-r4,
forked from skeleton/ts1-contracts (never main). This runbook
(docs/DEV_PLAN/PHASES/U-TS3b-r4-graph-hello-world.md) is self-contained.

Read services/frontend/src/components/graph/GraphIsland.svelte in full before changing anything.
It already fetches /api/v1/graph and /api/v1/wisdom/sample, lays nodes out via layout.ts's
radialLayout, and lets a user click a node to see its text in an accessible aside panel — keep all
of that exactly.

Remove: the activeTag state, the <select> tag-filter dropdown, setTag()'s URL push-state logic,
syncFromUrl() and its popstate listener, the gsap import and every call to it (entrance animation
in setTag, the hover() handler). Do not remove the click-to-select behavior, the loading/error
states, or any accessibility attribute (role="button", tabindex, aria-label, onkeydown) on the
node circles.

Do not edit services/frontend/src/components/graph/layout.ts or layout.test.mjs at all — run
`npx vitest run src/components/graph/layout.test.mjs` before and after your changes and confirm it
still passes unmodified.

Write services/frontend/src/components/graph/ASSIGNMENT.md: learning outcomes (Svelte 5 runes,
island hydration, SVG accessibility), constraints (must keep using layout.ts's radialLayout/
joinTags, must not fork layout math), acceptance criteria (tag filter reflected in the URL, at
least one animation, keyboard parity preserved), prohibited shortcuts (do not remove existing
keyboard/aria-label handling).

Verify at /en/graph/ that the graph renders real data and one node can be selected by click and by
keyboard, with no dropdown or URL parameter present anywhere in the reduced version.

File docs/DEV_PLAN/PHASE-U-TS3b-REPORT.md with status (DONE/PARTIAL/BLOCKED per this
runbook's §9), confirmation layout.ts/layout.test.mjs are unchanged, a screenshot, and the
ASSIGNMENT.md content.
```
