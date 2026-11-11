<!--
AA3b report: permanent locators, wisdom search, landing chapters, graph IA, language switch.
Author: Rubén Vega Balbás PhD (agent-assisted). Status VERIFYING. The agent does not mark DONE.
-->

# PHASE-AA3b report: permanent locators, wisdom usability, graph IA

**Status:** VERIFYING (2026-11-11) · cold review pending · **Branch:** `cascade/PHASE-AA-PREPROD-HARDENING-3b` · **Exit gate:**
[`PHASES/AA3b-locators-wisdom-and-graph-ia.exit-gate.sh`](PHASES/AA3b-locators-wisdom-and-graph-ia.exit-gate.sh)
plus [`scripts/aa3b-browser-check.mjs`](scripts/aa3b-browser-check.mjs), both written before the code (commit `9e10fe82`).
**Contract:** [LOCATORS.md](LOCATORS.md), now backed by data:
[`services/frontend/src/lib/locators.registry.json`](../../../services/frontend/src/lib/locators.registry.json).

## 1. What a student can now do

Paste a link and have the reader land in the same place, in either language:

| Link | Lands on |
| ---- | -------- |
| `/es/#map-architecture` | stop 2 of 13 of the handscroll, "Arquitectura", ficha below the header ([shot 1](baselines/aa3b-2026-11-11/1-landing-map-architecture.png)) |
| `/es/wisdom/?q=diseno` | the 5 quotes containing "diseño", with JS off; `DISEÑO`, `Diseño` give the same 5 ([shot 2](baselines/aa3b-2026-11-11/2-wisdom-q-diseno.png)) |
| `/es/wisdom/?section=architecture&level=advanced` | the combined filter; `?section=architecture` alone 301s to `/es/wisdom/sections/architecture/` |
| `/es/wisdom/#volume-architecture` | that volume, open ([shot 3](baselines/aa3b-2026-11-11/3-wisdom-volume-architecture.png)) |
| `/es/wisdom/sections/architecture/?p=2#arch-0NN` | that stele, below the header |
| `/es/graph/?from=a11y-001&to=img-038` | the 3D constellation with that path lit, surviving reload ([shot 4](baselines/aa3b-2026-11-11/4-graph-from-to.png)) |
| language switch on `/es/wisdom/wis-034/` | `/en/wisdom/wis-033/` ([shots 5a/5b](baselines/aa3b-2026-11-11/5b-after-switch.png)); on a list it keeps `?q=` and `#id` |

## 2. Deliverables

1. **Slash policy (F8).** [`src/middleware.ts`](../../../services/frontend/src/middleware.ts) calls one pure function,
   [`lib/locators.ts`](../../../services/frontend/src/lib/locators.ts). It 301s slashless pages, GET/HEAD only (a POST
   redirect would drop the form body), and exempts `/api/`, assets, Astro files and `/{l}/logout`. The legacy
   `/graph/path` links and the single-facet query also redirect from there. All internal hrefs were normalized: nav,
   footer, landing doors, 404 page, account, login/register cross-links, the `?next=` sign-in redirects, and the
   oracle's sign-in link.
2. **Wisdom locators (F50).** Every stele, volume page and library card carries `id={quote.id}`. Volumes are
   `<details id="volume-{section}">`. [`lib/volumenes.ts`](../../../services/frontend/src/lib/volumenes.ts) opens one
   from the hash (also when `#wis-034` falls inside a closed volume) and `replaceState`s the hash on toggle. The
   random-quote dialog already exposed the permalink; copy-link is the stele id itself (`a.piedra-id[data-copiar]`).
3. **Wisdom usability (F49).** `/wisdom/` now opens with the H1, intro and count, then the search form
   (`#search`, `role="search"`, visible label, `GET ?q=`), then the sections as a compact index with counts. Next
   come either the **results** (the Bosque corridor with `orden`/`p`, whose sort form keeps the query) or the
   shelf, then the pile (`#draw`) and the facet lists (`#facets`). [`lib/buscar.ts`](../../../services/frontend/src/lib/buscar.ts)
   searches SSR over text, teaches, tags and id. It folds case and accents (NFD), caps `q` at 100 characters and
   requires every word. An empty result shows the EmptyState above the section index. `bosque.css` is linked
   only when results show; inlining it would have added 19 KB to every `/wisdom/` visit.
4. **Landing chapters (F51).** Ids: `#start #doors #thesis #map #map-{section} #close`, with stops generated from the
   corpus. [`lib/capitulos.ts`](../../../services/frontend/src/lib/capitulos.ts) maps a hash inside a live sticky scene
   (hero, handscroll) to `top + (height − viewport) × fraction`, the same arithmetic as the ‹ › buttons. It
   re-applies when each scene reports it is measured, until the reader touches the scroll. While reading, it writes
   the current chapter with `replaceState`, only on change and never in the first viewport. Reduced motion uses
   native jumps, because the scenes are static then. Chapter headings carry a `#` copy-link.
5. **Graph IA (F52, D3).** `/{l}/graph/` is the 3D constellation. `?from=&to=&node=` are restored and written back
   ([`senderoUrl.ts`](../../../services/frontend/src/components/graph/senderoUrl.ts)). The 2D island moved to
   `/{l}/graph/plano/` ("Vista accesible, sin WebGL"). The code graph moved to `/{l}/graph/code/?s=`. `/graph/path`
   301s to `/graph/`, or to `/graph/code/` when it carries only `?s=`, and `/graph/?tag=` goes to `/plano/`. The header
   "Grafo" opens the 3D view.
6. **Language switch (F57).** Quote pages link to the `translation_of` twin, resolved in both directions from the
   server's graph copy (`gemelasTraduccion`). A quote with no twin goes to the other index with `?untranslated={id}`
   and a notice. A client enhancement ([`lib/idioma.ts`](../../../services/frontend/src/lib/idioma.ts)) carries
   `search + hash` on both switches (header and footer). An unknown quote now answers **404**.
7. **Landing figures guard (F54).** [`src/tests/landing-figures.test.ts`](../../../services/frontend/src/tests/landing-figures.test.ts)
   uses a 3/2/1 fixture in en and es. The figures are now `<dt>` label / `<dd>` number, and CSS keeps the number on top.
8. **Registry test.** [`src/tests/locators-registry.test.ts`](../../../services/frontend/src/tests/locators-registry.test.ts)
   walks the JSON registry: status, each id exactly once, no duplicate ids, en/es structural parity, 404s, twins and
   search. [`src/middleware.test.ts`](../../../services/frontend/src/middleware.test.ts) walks its redirects and exemptions.

## 3. Evidence

- **Exit gate (dry run on the dev stack, 2026-11-11):**
  - registry 15 pages / 11 redirects / 2 not-found / 5 exempt;
  - contract tests 38 passed; frontend suite 233 passed; `astro check` 0 errors (the runner's run below: 39 and 234,
    after the alias test was added);
  - F54 mutation: a literal count in ValleSigue, `/es/` and `/en/` each turns the fixture test red.
  - **Runner verify: exit 0** on commit `3566dd49`, with a fresh isolated stack (`ttod_aa3bgate`), the full live
    probe, the browser checks and Lighthouse:
    [`PHASES/AA3b-locators-wisdom-and-graph-ia-VERIFY-LOG.md`](PHASES/AA3b-locators-wisdom-and-graph-ia-VERIFY-LOG.md).
- **Live curl probe** of every registry row, both locales: [`baselines/aa3b-2026-11-11/probe.log`](baselines/aa3b-2026-11-11/probe.log)
  (script `probe.sh`, isolated stack). Pages 200; all 11 redirects 301 to the exact Location; `zz-999` and the
  other locale's id 404; exemptions untouched; `POST /es/login` is not redirected (403 from Astro's origin check).
- **Browser checks:** handscroll hash at 390 and 1440 px and under reduced motion; `#thesis` `#map` `#close` below the header;
  `#doors` visible; › writes the next stop with no history growth and the first viewport clears it; volume open
  and toggle; paged quote; copy-link puts the absolute URL in the clipboard and announces "Enlace copiado"; the
  switch keeps `?q=diseno#search`; graph `from`/`to` kept across reload; `?node=` kept; no page errors.
- **CSP report-only count** (inline scripts, AA1 backlog), never above AA1:

  | View | AA3b | AA1 (predecessor) |
  | ---- | ---- | ----------------- |
  | `/es/` | 4 | 4 |
  | `/es/wisdom/` | 3 | 3 |
  | `/es/wisdom/wis-034/` | 3 | 3 |
  | `/es/graph/` | 5 | 6 (`/es/graph/path/`) |
  | `/es/graph/plano/` | 5 | 5 (`/es/graph/`) |
  | `/es/graph/code/` | 6 | 6 (`/es/graph/path/`) |

- **AA0 UX rule** (Lighthouse 12.6.0, mobile 390, on Tanit). Two runs: the dev stack
  ([`baselines/aa3b-2026-11-11/ux/`](baselines/aa3b-2026-11-11/ux/ux-baseline.json)) and the runner's verify.

  | View | a11y | CLS | LCP (dev run / runner) | AA0 reference (a11y / CLS / LCP) |
  | ---- | ---- | --- | ---------------------- | -------------------------------- |
  | `/es/` | 100 | 0.0130 | 5040 / 5045 ms | 100 / 0.0130 / 5047 |
  | `/es/wisdom/` | 100 | 0.0000 | 2401 / 2339 ms | 100 / 0.0000 / 2330 |
  | `/es/graph/` | 100 | 0.0003 | 2714 / 4662 ms | `/es/graph/path` 100 / 0.0003 / 4959 |
  | `/es/graph/plano/` (new baseline) | 100 | **0.4702** | 2724 / 2734 ms | none (see F60) |

  No view regresses under the rule. The two `/es/graph/` LCP runs are 1.9 s apart, so the only claim is "within
  budget". Removing the code graph from that page may help, but two runs do not show it.

## 4. Amendments (disclosed)

**At gate writing** (recorded in the phase file): global `scroll-padding-top` moved into AA3b, so there is no AA3
header dependency; search example `diseno` instead of `deuda` (0 matches); legacy-link rows; `?untranslated=`;
slash-form sign-in redirects and SW v7; `baseline.sh` gained `VIEWS=`.

**During the phase, gate and browser check** (each marked `Amended during AA3b` in the script):

1. **en/es structural parity ignores ids a registry row declares `conditional`.** Today that is only
   `related-wisdom-title` on quote pages. The Spanish corpus has **no `related` edges at all** (0 of 230,
   against 192 in English; F59), so every English quote page has a "Related wisdom" heading that Spanish pages never get.
2. **The language-switch step scrolls to the top before clicking.** After the jump to `#search`, the header has hidden
   itself, which is its designed behaviour on downward scroll.
3. **The graph step picks any `related` edge and accepts the twin id on screen.** It follows from F59: 3D nodes carry the
   related (English) quote's id and display the Spanish twin.
4. **That comparison is case-insensitive**, because the path list renders ids with `text-transform: uppercase`.

**To the contract** (LOCATORS §4): the registry file is named; rows added for `?untranslated=`,
`/graph/path?s=` → `/graph/code/` and `/graph/?tag=` → `/graph/plano/`; the 3D view's `?node=` row
no longer claims `&tag=`.

## 5. Decisions taken while implementing (for the reviewer to challenge)

- **Graph URLs use the node id, not the displayed id.** On `/es/graph/` a node shows its Spanish twin's id, but its
  key is the English quote's id, the same in both locales. So `?from=&to=` survives the language switch
  unchanged. A Spanish id typed by hand is accepted as an alias and rewritten to the node id.
- **`#map` lands on the handscroll's title** (`#sigue-rollo` just above the sticky scene), so the reader sees
  the map heading and then stop 01. The registry note said "stop 1".
- **Per-view scroll patches removed now.** Keeping them on top of the new global rule would add the offsets
  together. Removed: `oracle.astro` `scroll-padding-top: 6rem` and the `CodigoGrafo` `scroll-margin-top: 7rem`.
- **`Page.astro` touches (AA3 owns the file):** slash nav hrefs, a `cambioIdioma` prop, `data-cambio-idioma` on the switch,
  a polite live region `#ttod-aviso`, the global scroll-padding rule, and two module imports inside the
  existing header `<script>`. There is no new inline script (`is:inline` count unchanged; CSP counts above).
- **Footer "Sendero / Path" now reads "Grafo del código / Code graph"** (`/graph/code/`), since "Grafo" now opens
  the path view.
- **e2e specs** for the 2D island now target `/en/graph/plano/`, and the PWA spec targets `/xx/oracle/`.

## 6. New findings (added to FINDINGS)

- **F59.** The Spanish corpus carries no `related` edges, so es quote pages show no related quotes, and the 3D graph in
  `/es/` borrows English topology. This is corpus content, outside AA3b's scope (no `ttod.yml` edits).
- **F60.** The 2D plano (`GraphIsland`, now `/graph/plano/`) measures CLS **0.4702** at 390. The same 2D page
  measures the same on `main` (`/es/graph`, CLS 0.4702 on the live stack today), so it predates AA3b. Owner: AA3
  (a11y/UX) or the F32 graph-i18n assignment.
- **F61.** `cascade-harness.sh` parses only numeric steps, so the `3b` row can never be `start`ed by the runner.
  This worktree was opened by hand with the harness's naming and `.cascade-lane`. `verify` works by file name.

## 7. Rollout (owner)

`make rebuild` on Tanit. There is no backend or data change. The service worker cache moves to `v7` (offline
pages are now `/xx/oracle/`); old clients refresh on their next visit. Links already pasted keep working via
301. Check: `curl -sI http://127.0.0.1:18080/es/graph/path | head -3` → `301`, `location: /es/graph/`.

## 8. Not done here

- `GraphIsland` (2D) is still English-only (F32, a student assignment); it lives at `/graph/plano/` now.
- The no-twin path (`?untranslated=`) is proven by unit and registry tests only: every live quote has a twin.
- The account fragments (`#profile #password #sessions`) are AA3's; their registry row is marked `owner: AA3`.
