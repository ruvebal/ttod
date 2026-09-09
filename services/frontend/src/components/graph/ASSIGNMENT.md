# FE II · R4 assignment — tag filter, URL state, and motion

Hello-world on this branch is **one hydrated Svelte island**: it fetches the live graph, joins
tags, lays every received node out with `radialLayout`, and reflects **one** click/keyboard
selection in an accessible `<aside>`. Tag filtering, URL state, and animation are
**deliberately absent** — that is the assessed work, not a bug.

The instructor-removed seams (do not look for them in `GraphIsland.svelte` on this branch):

| Deliverable | Hello-world state | Restore as |
| --- | --- | --- |
| Tag filter | `activeTag`, `<select>`, and `filterGraph(...)` call removed | dropdown (or equivalent) that filters the visible neighborhood |
| URL state | `setTag`, `syncFromUrl`, `popstate` removed | `?tag=` reflected in the address bar and restorable on load / back |
| Motion | `gsap` import, entrance animation, `hover()` removed | at least one entrance **or** selection animation |

`layout.ts` still exports `filterGraph` and `selectedTag`. Hello-world does not call them.
Your filter/URL work should.

The origin-color **legend** is still present. You may keep it, restyle it, or fold origin into
the filter UI — it is not the assessed seam.

---

## Learning outcomes

After this assignment you can:

1. **Svelte 5 runes.** Drive the island with `$state` / `$derived` (and events) rather than a
   parallel store. Filter and selection are reactive views over the same fetched payload.
2. **Island hydration.** `GraphIsland` mounts from `pages/[locale]/graph.astro` via `client:load`.
   The page owns locale (`en` / `es`); the island owns client fetch, layout, and interaction.
   Do not turn the graph into an Astro-only SSR drawing that skips hydration.
3. **SVG accessibility.** Each node stays a focusable control (`role="button"`, `tabindex`,
   `aria-label`, Enter/Space). A visual filter that drops keyboard parity fails the assignment.

---

## Constraints

- Keep calling **`joinTags`** and **`radialLayout`** from `./layout.ts` **exactly**. Do not fork
  the file, copy the math, or reimplement polar clustering in the `.svelte` file.
- `filterGraph` and `selectedTag` already exist in `layout.ts`. Prefer them for the induced
  subgraph and `?tag=` parse rather than a third copy of that logic.
- Do not edit `layout.ts` or `layout.test.mjs` except if a genuine shared-function bug is
  proven — in that case, flag it; do not silently rewrite layout math to make the filter easier.
- Fetch remains `GET /api/v1/graph` plus `GET /api/v1/wisdom/sample`. Do not add a backend
  endpoint; do not edit `services/backend/**`.
- Keep the existing click-to-select `<aside>` and the loading / error empty states.
- Do not read `ttod.yml`, `exports/`, or any static JSON dump of the graph.

---

## Acceptance criteria

1. **Tag filter is reflected in the URL.** Choosing a tag writes `?tag={value}` (and clearing
   the filter removes the param). Reloading and using the browser back/forward buttons restore
   the same visible neighborhood.
2. **At least one entrance or selection animation.** Nodes (or the selected node) animate with
   a real motion system — CSS transitions alone for a hover color change do not satisfy this
   line. GSAP is already a project dependency; you may use it or an equivalent.
3. **Keyboard parity is preserved.** Every visible node still has `role="button"`, `tabindex`,
   `aria-label`, and Enter/Space selection. Filtering must not leave focus on a removed node
   without a sensible next target.
4. **Layout stays shared.** The rendered positions still come from `radialLayout` after
   `joinTags` (and `filterGraph` when a tag is active). A hand-placed SVG or a second layout
   helper fails this criterion.
5. Hello-world selection still works: clicking **or** pressing Enter/Space on one node shows
   its `text` in the `<aside>`.

---

## Prohibited shortcuts

- Do not remove the existing keyboard / `aria-label` handling on node circles to make the
  filter "simpler."
- Do not hide the `<select>` with CSS, or keep `activeTag` / `history.pushState` as dead code,
  and call the assignment done — the hello-world cut is the starting point you extend.
- Do not bypass `joinTags` / `radialLayout` with a hardcoded coordinate list or a copied
  `layout.ts`.
- Do not restore the missing seams by copying instructor-only reference history. Design against
  this brief and the live payload.
- Do not edit `src/types/domain.ts`, `services/backend/**`, `ttod_core/**`, `ttod.yml`, or the
  Oracle island.

---

## Extension choices (not prescribed)

How the filter control looks (native `<select>`, chips, combobox), whether the legend stays,
and which motion library you use are yours. The acceptance criteria name the URL contract, one
real animation, and keyboard parity; they do not name the implementation.
