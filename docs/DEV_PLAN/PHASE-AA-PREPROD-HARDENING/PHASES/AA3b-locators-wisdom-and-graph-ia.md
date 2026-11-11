# PHASE-AA3b: Permanent locators, wisdom usability, graph IA

> **Track:** Astro shell — F8, F49–F52, F54, F57 · A7, A32, A36–A40.  
> **Status:** IN_PROGRESS 2026-11-11 (owner: "go AA3b"; runs **before** AA3).
> *Amended 2026-11-11 (was: "VERIFYING requires AA3's header (A31) merged").* AA3b now carries the one global
> `html { scroll-padding-top: calc(var(--ttod-header-height, <fallback>) + 1rem) }` rule from LOCATORS §6, with a
> fallback measured on today's header. The exit gate measures the real header against each landing target, so it
> does not depend on AA3. AA3 defines `--ttod-header-height` for its new header, removes the per-view patches,
> and re-runs the AA3b anchor checks.

## Goal

Make every place a student would want to cite **linkable and restorable**: a quote, a filtered or
searched list, an open volume, a chapter or stop of the landing scroll, a path between two quotes,
in either language. Make `/wisdom/` serve the find-a-quote task first, and put the 3D graph
where the header says "Graph".

## Why this is a separate phase

AA3 owns the shell (header, account, a11y). This phase owns **URLs and content views**. Splitting
them keeps each PR reviewable and lets two Equipos work at once. The only shared file is
`Page.astro`: AA3 owns it, and AA3b touches only the language-switch enhancement there.

## Deliverables

1. **URL policy (F8):** middleware 301 per [LOCATORS §3](../LOCATORS.md#3-trailing-slash); all nav/footer hrefs normalized.
2. **Wisdom locators (F50):** `id={entry.id}` on every rendered quote (Estela, Libro pages, search
   results, library cards); `#volume-{section}` opens and scrolls to its `<details>`; toggling a volume
   `replaceState`s the hash; the random dialog shows the quote permalink + copy-link (no dialog URL).
3. **Wisdom usability (F49):**
   - Order: H1 + intro + live count → `<form role="search" method="get">` with a visible label
     (`?q=`) → sections as a compact index with counts → **results** (when `q`/filters present,
     reusing the Bosque pasillo with `orden`/`p`) **or** the shelf → the pile as a secondary block
     → full facet lists.
   - Search runs in SSR over `text`, `teaches`, `tags`, `id`; NFD-folded, case-insensitive; `q`
     capped (≤ 100 chars); empty result → `EmptyState` with the facet index as the way out.
   - Combined filters `?section=&level=&tag=`; a single facet with no `q` 301s to its path form.
   - No new visual system: books, pile, tokens and ink animations stay.
4. **Landing chapters (F51):** ids `#start #doors #thesis #map #map-{section} #close` (generated
   from the corpus, not hand-listed). On load and on `hashchange`, map the hash to a scroll offset
   after ScrollTrigger is ready, reusing the `data-ir` stop arithmetic. On scroll, `replaceState`
   the current chapter (not inside the first viewport). The ‹ › buttons update the hash too.
   Under `prefers-reduced-motion`, jump without easing. Chapter headings get copy-link.
5. **Graph IA (F52)**, as decided in AA0. Recommended:
   - `/{l}/graph/` = the 3D constellation (move `SenderoAforismos` from `/graph/path`), with
     `?from=&to=` (path) and `?node=` restored from the URL and written with `replaceState`/`pushState`
     like `GraphIsland`'s `urlState.ts`;
   - the 2D radial `GraphIsland` → `/{l}/graph/plano/`, linked from `/graph/` as "vista accesible / sin WebGL"
     (F32's localization lands here);
   - the code graph → `/{l}/graph/code/?s=`;
   - `/{l}/graph/path` → 301 to `/{l}/graph/` keeping the query.
   - *Minimal fallback if AA0 declines the move:* header "Graph" → `/graph/path`, and `/graph` gets a
     visible link "Ver la constelación 3D".
6. **Language switch (F57):** a client enhancement carries `search + hash`; quote pages resolve the
   `translation_of` twin **in both directions** (edges are one-way in `ttod.yml`); quote not-found → **404**.
7. **Landing figures guard (F54):** component test with a fixture corpus (3 quotes / 2 sections / 1 level
   → renders 3/2/1, en and es); `<dt>` label / `<dd>` number.
8. **Registry test:** Vitest walks the [LOCATORS §4](../LOCATORS.md#4-registry-what-aa3b-implements) registry
   (status codes, each id unique in SSR HTML, en/es id sets equal).
9. `PHASE-AA3b-REPORT.md` with a live `curl` probe of the registry plus a short screen recording or
   screenshot strip of: a landing deep link to `#map-css`, `/es/wisdom/?q=deuda`, `#volume-architecture`,
   `/es/graph/?from=…&to=…`, and the language switch on a quote page. Then cold review.

## Scope

**In:** `services/frontend` pages under `[locale]/wisdom`, `[locale]/graph*`, `en|es/index.astro`,
`ValleSigue`/`ValleHero` (ids + hash script only), `Estanteria`/`Libro`/`Mazo`/`Estela`/`Bosque`,
the `Page.astro` language-switch script, middleware for slashes.  
**Out:** header visual redesign and `scroll-padding` (AA3, A31); canonical/hreflang/sitemap (AA4, which
consumes this registry); any backend change other than reading existing endpoints; `ttod.yml`
(missing reverse `translation_of` edges are resolved in code, not by editing the corpus).

## Prompt (Implementation Agent)

```text
Implement PHASE-AA3b per
docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING/PHASES/AA3b-locators-wisdom-and-graph-ia.md
and the frozen contract docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING/LOCATORS.md.

## Deliver
1. Slash policy middleware (301) + href normalization.
2. Wisdom: quote ids, #volume-{section}, search ?q= (SSR, no JS needed), combined filters,
   task-first order; dialog exposes permalink + copy-link.
3. Landing: chapter ids + hash<->scroll mapping for the sticky handscroll (reuse data-ir math).
4. Graph IA per AA0 decision (default: 3D at /graph/, 2D at /graph/plano/, 301 from /graph/path,
   ?from=&to=&node= restorable).
5. Language switch keeps search+hash; quote twin resolved both directions; not-found = 404.
6. Landing figures fixture test; registry test over LOCATORS §4.
7. Evidence in PHASE-AA3b-REPORT.md; cold review. Do NOT mark DONE yourself.

## Constraints
- Keys are code, labels are copy: same query keys/ids in en and es; values are corpus keys.
- Do not rename shipped params (orden, p, s, tag, node).
- Never hardcode a corpus count. No ttod.yml edits. Reuse tokens/components. No commit unless asked.
```

## Planner amendments at gate writing (2026-11-11)

- **Exit gate:** [`AA3b-locators-wisdom-and-graph-ia.exit-gate.sh`](AA3b-locators-wisdom-and-graph-ia.exit-gate.sh) plus
  [`scripts/aa3b-browser-check.mjs`](../scripts/aa3b-browser-check.mjs). The registry becomes data
  (`services/frontend/src/lib/locators.registry.json`), walked by both the Vitest test and the live probe.
- **Search example:** `deuda` matches **0** quotes in today's Spanish corpus (tags are English keys). The gate
  uses `diseno` / `DISEÑO` (5 quotes, which also proves the accent fold) and compares against an independent
  Python fold over `/api/v1/wisdom/sample`. The report's screenshot uses `?q=diseno`.
- **Shipped links keep working:** `/{l}/graph/path?s=…` (the code graph's key) 301s to `/{l}/graph/code/?s=…`;
  `/{l}/graph/?tag=…` (a 2D-island key) 301s to `/{l}/graph/plano/?tag=…`. These rows join the registry.
- **No twin:** the switch goes to the other locale's index as `?untranslated={id}`, which shows the notice
  (a new registered key). Today every quote has a twin (230 `translation_of` edges).
- **Slashless redirects already shipped:** the library and account sign-in redirects point at `/{l}/login?next=`;
  they move to `/{l}/login/?next=`. The service worker's `OFFLINE_PAGES` move to slash form, and its cache
  version goes up.
- **UX rule tooling:** `baseline.sh` accepts `VIEWS=` (default unchanged), so AA3b measures `/es/graph/` and
  `/es/graph/plano/`.

## Carried from AA1 (amended 2026-11-10)

- **CSP (AA1, live in report-only):** add no new inline `<script>`; when you touch a layout or page script, prefer moving it to a module. Every inline script is one more hash to manage at enforcement (PHASE-AA1-REPORT §4). Re-run `baselines/aa1-2026-11-10/browser-smoke.mjs`: the CSP report count must not grow.

- **Live checks (AA2):** run the LOCATORS curl probe on `scripts/isolated-stack.sh up <project> <port>`, not on the instructor stack.

## Acceptance

- [ ] Every row of LOCATORS §4 probes as documented (200/301/404); slashless page URLs 301.
- [ ] `/es/#map-architecture` opened cold lands on that stop, header not covering it, both at 390 and 1440 px.
- [ ] `/es/wisdom/?q=<word>` returns matching quotes with JS disabled; accents ignored (`deuda` = `Deuda`, `diseno` finds `diseño`).
- [ ] `/es/wisdom/#volume-architecture` opens that volume; `/es/wisdom/sections/architecture/?p=2#arch-0NN` lands on the quote.
- [ ] The header "Graph" link opens the 3D view; `/es/graph/path?…` still works (301); a path between two quotes survives reload and copy-paste.
- [ ] Language switch on `/es/wisdom/wis-034/` lands on `/en/wisdom/wis-033/`; on a list it keeps `?q=`/`#id`; an unknown id returns HTTP 404.
- [ ] F54 fixture test fails if a literal count is typed into `ValleSigue`.
- [ ] No UX regression on `/es/` and `/es/wisdom/` at 390 px under the [AA0 regression rule](../PHASE-AA0-REPORT.md#5-ux-baseline-the-no-regression-reference). The AA0 graph view `/es/graph/path` becomes a 301, so compare its baseline against its successor `/es/graph/`, and record a **new** baseline for the 2D page `/es/graph/plano/` (no AA0 baseline exists for it).
- [ ] Cold review green or amended.

## Risks

- **ScrollTrigger timing:** offsets computed before `refresh()` land on the wrong stop. Compute after
  the existing "ready" point and re-apply once on `load`.
- **Hash spam:** writing the hash on every scroll frame floods history. Use `replaceState`, only on chapter change.
- **Moving the 3D view** changes its LCP budget page. Re-measure on `/graph/`, and keep the
  `<link rel="modulepreload">` / data preloads that `path.astro` already does.
- **Search scope creep:** SSR filter over the already-loaded locale corpus only. No new backend
  search endpoint, no client index library.
