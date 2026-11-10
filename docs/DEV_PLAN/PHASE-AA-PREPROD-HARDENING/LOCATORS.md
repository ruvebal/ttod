<!--
Proposed URL / locator contract for the Astro shell. Drafted 2026-11-10 from an owner walkthrough
plus live probes (F8, F49–F58). AA0 freezes it; AA3b implements it; AA4 canonicalizes it.
Author: Rubén Vega Balbás PhD (agent-assisted). Not a DONE claim.
-->

# Locator contract — permanent, semantic URLs (proposal)

**Status:** PROPOSED · frozen by [AA0](PHASES/AA0-assignment-cut-and-freeze.md) · implemented in
[AA3b](PHASES/AA3b-locators-wisdom-and-graph-ia.md) · canonical/sitemap in [AA4](PHASES/AA4-seo-robots-and-meta.md).  
**Evidence:** [FINDINGS F8, F49–F58](FINDINGS-2026-11-10.md#usability-ia--permanent-locators-owner-walkthrough).

A student should be able to paste a link into a PR, a lesson or a chat and have the reader land
on **the same quote, the same filtered list, the same stop of the scroll**, in either language,
months later. Today almost nothing below page level can be linked (live id inventory, 2026-11-10:
`/es/wisdom/` has no ids on volumes or quotes, `/es/` has 3 ids for 13+ scroll stops).

## 1. Three layers, three jobs

| Layer | Carries | Server sees it | Example |
| ----- | ------- | -------------- | ------- |
| **Path** | the *resource* (permanent identity) | yes | `/es/wisdom/wis-034/` |
| **Query** | *view state that changes the result set* (search, filter, sort, page, graph selection) | yes — SSR renders it without JS | `/es/wisdom/?q=deuda&level=advanced` |
| **Fragment** | *position inside the rendered page* (a chapter, a quote in a list, an open volume) | no — client only | `/es/#map-architecture` |

Rules that follow from the table:

1. If two URLs return the same resource, one **301s** to the other (no duplicate 200s — see F8).
2. Anything that changes *which items* are shown is a query parameter and works with JS off.
3. Anything that only changes *where you are* is a fragment, written with `history.replaceState`
   (never `pushState` on scroll — the Back button must not replay a scroll).
4. Ephemeral UI (the random-quote dialog, hover cards) is **not** a locator. It exposes the
   permalink of the resource it shows instead of inventing a URL for itself.

## 2. Keys are code, labels are copy

- Query keys and fragment ids are **identical in `/en/` and `/es/`**, so the language switch can
  carry `search + hash` verbatim (F57).
- **Values are corpus keys**, never translated labels: `level=advanced`, not `nivel=avanzado`;
  `#map-architecture`, not `#mapa-arquitectura`. Labels on screen stay localized.
- **New keys use English** to match schema field names (`section`, `level`, `tag`) and the
  shipped path segments (`/sections/`, `/levels/`, `/tags/`).
- **Shipped keys are frozen as-is** even where Spanish: `orden`, `p` (Bosque), `s` (CodigoGrafo),
  `tag`, `node` (GraphIsland). Renaming a shipped parameter breaks links already pasted in PRs.
- Ids are lowercase ASCII, hyphenated, start with a letter. Corpus ids (`wis-034`) already qualify.

## 3. Trailing slash

**Recommendation: always-slash for pages** (`/es/library/`, `/es/graph/`), 301 from the
slashless form via Astro middleware (one place, testable) rather than Caddy. Reason: most
shipped internal links already end in `/` (wisdom, docs, facets, quote permalinks), so this
choice rewrites the fewest hrefs. Endpoints that are not pages (`/es/logout`, `/api/…`) are exempt.
AA0 may choose never-slash instead. What it must not do is leave both forms returning 200,
which is the state today.

## 4. Registry (what AA3b implements)

### Landing `/{locale}/`

| Locator | Lands on | Notes |
| ------- | -------- | ----- |
| `#start` | hero / flagship quote | `#flagship-quote-heading` kept as heading id |
| `#doors` | the four doors (Wisdom, Docs, Graph, Oracle) | |
| `#thesis` | thesis + live figures | `#sigue-tesis` kept (it is an `aria-labelledby` target) |
| `#map` | the handscroll, stop 1 | `#sigue-rollo` kept |
| `#map-{section}` | that stop of the handscroll, e.g. `#map-architecture` | one per corpus section, generated, never hand-listed |
| `#close` | closing colophon | |

The handscroll is a sticky scene with a horizontal filmstrip, so a native anchor jump **cannot**
reach stop *n*. AA3b maps `#map-{section}` to a scroll offset with the same arithmetic the
existing ‹ › buttons use (`ValleSigue.astro` `data-ir`). The fragment updates as the reader
scrolls past each chapter, but not inside the first viewport, so a plain visit keeps a clean `/es/`.

### Wisdom `/{locale}/wisdom/…`

| Locator | Meaning |
| ------- | ------- |
| `/{l}/wisdom/{id}/` | **quote permalink** (exists). Not-found must return **404**, not 200 (F57) |
| `/{l}/wisdom/sections/{s}/` · `levels/{v}/` · `tags/{t}/` | single-facet lists (exist; canonical for one facet) |
| `/{l}/wisdom/?q=` | full-text search over text, teaches, tags, id (accent- and case-insensitive) |
| `/{l}/wisdom/?section=&level=&tag=&q=` | combined filters. A **single** facet with no `q` 301s to its path form above |
| `&orden=` · `&p=` | sort and page (shipped keys, unchanged) |
| `#wis-034` | that quote inside any list that renders it (facets, search results, volumes, library) |
| `#volume-{section}` | opens that volume on the shelf (`<details>` gets `open`) and scrolls to it |
| `#search` · `#draw` · `#facets` | search form · random-quote pile · facet lists |

### Graph `/{locale}/graph/…`

Recommended IA (decided in AA0, see [AA3b](PHASES/AA3b-locators-wisdom-and-graph-ia.md)):

| Locator | Meaning |
| ------- | ------- |
| `/{l}/graph/` | **the 3D constellation** (today at `/graph/path`) — what the header "Graph" opens |
| `/{l}/graph/?from={id}&to={id}` | the path between two quotes, restorable from the URL |
| `/{l}/graph/?node={id}` · `&tag=` | selected node / tag filter (shipped GraphIsland keys) |
| `/{l}/graph/plano/` | the 2D radial view, kept as the accessible / no-WebGL alternative (localized, F32) |
| `/{l}/graph/code/?s=` | the repository code graph (shipped key `s`) |
| `/{l}/graph/path` | **301** → `/{l}/graph/` with the query kept (links already pasted keep working) |

### Account and library

| Locator | Meaning |
| ------- | ------- |
| `/{l}/library/#wis-034` | a saved quote |
| `/{l}/account/#profile` · `#password` · `#sessions` | the User section's blocks (F55) |

## 5. Language switch

The switch is rendered server-side from the path alone; the browser never sends the fragment, so
the server cannot preserve it. AA3b adds:

1. **Client enhancement:** on click, append `location.search + location.hash` to the target.
2. **Quote pages:** `/es/wisdom/wis-034/` switches to its `translation_of` twin
   (`/en/wisdom/wis-033/`). The edge is stored **one way only** (verified 2026-11-10:
   `wis-034 → translation_of → wis-033`, no reverse edge on `wis-033`), so the lookup must resolve
   both directions. If there is no twin, it switches to the other locale's wisdom index with
   a notice, never to a "not found" page (today it lands on a 200 "not found" page; F57).
3. Keys are shared across locales (§2), so filters and positions survive the switch.

## 6. Sticky header and anchors

Every fragment jump must land **below** the header, not under it (WCAG 2.2 SC 2.4.11 *Focus Not
Obscured*). AA3 defines `--ttod-header-height` with the new header and sets
`html { scroll-padding-top: calc(var(--ttod-header-height) + 1rem) }` once, globally. That replaces
the per-view patches (`oracle.astro` `scroll-padding-top: 6rem`, `CodigoGrafo` `scroll-margin-top: 7rem`).

## 7. Copy-link affordance

Quote cards, volume headers and landing chapter headings get a small "Copiar enlace / Copy link"
control: a real `<a href="#id">` whose click handler copies the absolute URL. It stays visible on
focus, and announces "Enlace copiado / Link copied" through the existing polite live region. With
JS off it is still a working anchor.

## 8. How it is proven

A table-driven test (Vitest) walks this registry: each path/query returns 200 (or the documented
301/404), each fragment id exists exactly once in the SSR HTML, and en/es share the same id set.
The live probe in the AA3b report runs `curl` over the same table. **A locator that is not in this
registry is not a contract.** Add it here first.
