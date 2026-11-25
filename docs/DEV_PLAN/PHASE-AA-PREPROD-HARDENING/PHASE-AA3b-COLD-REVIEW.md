<!--
AA3b cold review: permanent locators, wisdom search, landing chapters, graph IA, language switch.
Reviewer: cascade cold reviewer (no implementation context). The reviewer does not mark DONE.
-->

# PHASE-AA3b cold review

**Verdict: PASS-WITH-AMENDMENTS.** No P0. Two P1s block DONE, and both are small, local fixes:

- **F1:** the new slash middleware is an **open redirect**. `GET //evil.com/x` answers `301 Location: //evil.com/x/`.
- **F2:** under a realistic mobile network, the landing deep link fails, and the scroll writer then **overwrites the
  reader's fragment**. `/es/#map-architecture` lands on the last stop and the URL becomes `#map-operations`;
  `/es/#doors` lands at the top and the hash is erased. So Acceptance item 2 only holds on a fast desktop link.

Most of the rest holds up when tested directly: search, filters, volumes, quote ids, the quote 404, both directions
of the twin, the graph IA and its 301s, the service worker and scope. The amendments to the gate are fair. The
gate's real gaps are elsewhere: it never probes an off-site `Location`, and it never runs the landing on a slow network.

Base `origin/main` = `b51401e9`, head `77f27bf2` (3 commits: gate before code `9e10fe82`, implementation `3566dd49`,
verify log `77f27bf2`).

## Evidence I ran (not taken from the report)

| Command | Result |
| ------- | ------ |
| `cd services/frontend && npx vitest run` | `Test Files 36 passed (36) · Tests 234 passed (234)` |
| `npm run check` | `0 errors · 0 warnings · 6 hints` |
| runner verify log | exit 0 at `3566dd49`. I did not re-run the gate's Python probe, the F54 mutation or Lighthouse; for those items I rely on this log |
| Isolated stack `ttod_aa3breview` :28380 (up, used, **down**; `ttod_oracle` untouched, its 6 containers still running) | |
| `curl --path-as-is` through Caddy | `//evil.com/x` → **`301 Location: //evil.com/x/`**; `/\evil.com/x` → **`//evil.com/x/`**; `///evil.com/x` → off-site; `//evil.com/x?y=1` → `//evil.com/x/?y=1`; `/es//evil.com/x` → `/es//evil.com/x/` (same origin, fine) |
| `curl` on redirects | `/es/wisdom` 301 `/es/wisdom/`; `/es/graph?tag=koan` 301 `/es/graph/plano/?tag=koan` (one hop); `/es/graph/path?s=a&node=b` 301 `/es/graph/?s=a&node=b`; `?section=architecture&p=2` 301 `/sections/architecture/?p=2`; `?q=%20&tag=koan` 301 `/tags/koan/`; `?section=Architecture` and `?section=a&section=x` stay 200; `/es/oracle?x=%E2%9C%93&y=a+b` keeps the query byte for byte; `/es/logout` 405 (exempt); `/health` 200 |
| `curl` on 404s | `/es/wisdom/zz-999/` 404; `/es/wisdom/wis-033/` (an English id under `/es/`) 404 |
| `curl` on the quote switch | `/es/wisdom/wis-034/`: header **and** footer switch `href="/en/wisdom/wis-033/"` |
| Cold twin lookup | `docker restart` of the frontend, then the first `/es/wisdom/wis-034/` took 0.080 s and later ones 0.005 s |
| Corpus | 230 en / 230 es quote ids, **0 shared**; 230 `translation_of` edges (no id appears twice); 435 `related` |
| Browser check `aa3b-browser-check.mjs` (my run, first visit after the stack came up) | **FAILED**: `390px /es/#map-architecture: current stop is "map-devops"`. Every other check passed, and the CSP counts equal the runner's |
| `scratchpad/landing.mjs`: `/es/#map-architecture`, 5 runs at 390 and 5 at 1440, no throttling | 10/10 land on `map-architecture`; no `replaceState` calls |
| The same with CDP network throttling (150 ms RTT, 1.6 Mb/s) + 4× CPU, 3 runs per width | **6/6 land on `map-operations`** (the last stop). Rewrites recorded: 390 `["#map-devops","#map-operations"]`, 1440 `["#map-ux","#map-operations"]` |
| The same with 4× CPU and no network throttling | 4/4 correct, so network latency is the trigger |
| Throttled, other chapters at 390 | `#doors` → **y 0, hash erased** (`replaceState("/es/")`); `#thesis`, `#map`, `#close` keep their hash |
| Unthrottled `#doors` | y 1981, hash kept |
| Malformed fragment `scratchpad/badhash.mjs` | `/es/wisdom/#%E0%A4%A` → `URIError: URI malformed`; `/es/#%E0%A4%A` → 10× `URIError` |
| `conEstado` (node `--experimental-strip-types`) | `?untranslated=wis-033` is carried to `/en/wisdom/`; `?next=%2Fes%2Flibrary%2F` is carried to `/en/login/`; `#arch-060` is carried to an English list; `?q=a&q=b` → `?q=a` |
| `curl` on search edges | `?q=` + 300×`a` → 200, input capped; `?q=%CC%81` (a lone combining mark) → heading `«́»: 230 citas`; `?untranslated=you-have-been-hacked` → notice "La cita you-have-been-hacked todavía no tiene versión en español"; `/es/wisdom/sections/nope/` → **200** with an empty list |
| Scope | `git diff origin/main -- ttod.yml proposals services/backend` is empty; every changed file is under `services/frontend` or `docs/DEV_PLAN`; `is:inline` count 1 → 1; the two new `<script>`s in `graph/index.astro` and `graph/code.astro` moved over from `path.astro` (CSP counts unchanged or lower) |

## Findings

| # | Sev | Blocks DONE | Finding and evidence | Fix |
| - | --- | ----------- | -------------------- | --- |
| F1 | **P1** | yes | **Open redirect in the slash rule.** `src/lib/locators.ts:66` `if (!ruta.endsWith('/')) return \`${ruta}/${url.search}\`` puts the request path straight into `Location`. Astro's Node adapter keeps a leading `//`, and Node's URL parser turns `\` into `/`. As a result `https://<ttod>//evil.com/login` sends the browser to `https://evil.com/login/`, with a **cacheable 301**, on the same host as the sign-in form (probe above). This is new: `main` had no middleware. `middleware.test.ts:6` builds `new URL('http://localhost' + path)`, so its harness cannot express the attack. The last-segment dot rule (`:39`) hides the bare `//evil.com` case, which is why nobody noticed | Return `null` (or collapse to one slash) when `ruta` starts with `//`. Stronger: build every `Location` as `new URL(dest, url.origin)` and refuse any result whose `origin !== url.origin`. Tests: call `redireccionLocator('GET', new URL('http://localhost//evil.com/x'))` (pass the URL so the path is kept). Gate: probe `//evil.example/x` and `/\evil.example/x` and assert the `Location` is not protocol-relative or off-site |
| F2 | **P1** | yes | **The landing deep link is lost on a slow network, and the scroll writer overwrites the reader's fragment.** Throttled probe above: 6/6 land on `map-operations`. The cause is in `lib/capitulos.ts`. (a) `colocar` reads `location.hash` again on every scene-ready event (`:53`, `:60`), not the id the reader arrived with. (b) The writer (`:66-79`) starts before the scenes are live. Before then `inicioDe` falls back to `getBoundingClientRect().top` (`:39`), and every `li.parada` in the horizontal filmstrip has the **same** top, so the last stop wins. The writer replaces the hash, and the next `colocar(false)` faithfully goes to that wrong stop. For `#doors` the page is still at y < viewport when the writer runs, so `:70-72` erases the hash outright. Network latency alone triggers it (CPU 4× alone does not), and my cold, unthrottled run of the planner's browser check also failed this way. This is the classroom/phone condition the phase is for: "paste a link into a chat… land on the same stop" | Capture the requested id once in `enlazarCapitulos` and have `colocar` use it until the reader touches the page (`tocado`). Do not attach, or do not let act, the scroll writer until the initial placement is done: after `load` + the last `LISTA`, or on the first touch. In `inicioDe`, skip `data-ancla-desde` chapters whose scene is not live instead of falling back to the element's rect. Gate/browser check: run step 1 and `#doors` a second time with `Network.emulateNetworkConditions`, and assert that `location.hash` is unchanged after settling (today step 1 only checks `[data-actual]`) |
| F3 | P2 | no | **The random-quote dialog has no copy-link.** Deliverable 2 asks for "the random dialog shows the quote permalink + copy-link". `Mazo.astro:90` has only the permalink anchor. Report §2.2 (`PHASE-AA3b-REPORT.md:39`) says "copy-link is the stele id itself", which is a different element, so the gap reads as done. `copiarEnlace.ts:7-10` (`direccionDe`) can only copy *this page's path + #id*, so it cannot serve a permalink to another path anyway | Make `direccionDe` return `new URL(href, location.href).href`, so it handles fragments and paths alike. Add `<a data-copiar>` to the dialog, synced to the permalink in the script that sets `campo('cita')` (`Mazo.astro:183`). Correct the report sentence |
| F4 | P2 | no | **The language switch carries keys that mislead the target.** `lib/idioma.ts:42-45` copies every query key and the hash. Probes: (a) `?untranslated=wis-033` goes to `/en/wisdom/`, which then claims that the English quote wis-033 "has no English version yet"; (b) `?next=/es/library/` goes to `/en/login/`, so the student signs in and lands back in Spanish; (c) quote fragments: ids are disjoint per locale (0 of 230 shared), so `#arch-060` never resolves after the switch. LOCATORS §2 (`LOCATORS.md:37-38`) and §5.3 (`:125`) promise that "filters and positions survive the switch". That is true for structural ids and false for quote ids | Drop `untranslated`. Rewrite a `next` value's `/{l}/` prefix to the target locale. For quote fragments, either map them through the twin (a `data-gemela` on each stele, or a small id→twin map) or say plainly in §2/§5 that quote fragments do not survive. Add these three cases to `idioma.test.ts` |
| F5 | P3 | no | `?untranslated=` accepts any id-shaped string (`wisdom/index.astro:21-22`), so anyone can make the page print chosen text ("La cita you-have-been-hacked…") | Show the notice only if the id is a real corpus id of the other locale that has no twin. `loadWisdom(otro)` and `gemelasTraduccion()` are both cached |
| F6 | P3 | no | **A malformed fragment throws an uncaught `URIError`:** `lib/volumenes.ts:10` and `lib/capitulos.ts:53` call `decodeURIComponent` unguarded. On `/es/` it fires again on every scene-ready event (10×). Any setup after it is lost: the `hashchange` listener in `volumenes.ts:27`, the scroll writer and the module code after `enlazarCapitulos()` in `ValleSigue.astro` | `try { decodeURIComponent(…) } catch { return; }` in both places. Add one unit test |
| F7 | P3 | no | **Search edges.** A `q` that folds to nothing (a lone combining mark) counts as a search: `hayFiltros` reads the raw `q` (`buscar.ts:27`), `buscar` then finds no words and returns everything (`:35`), and the heading reads `«́»: 230 citas`. Separately, Bosque's sort form echoes the **uncapped** raw `q` into hidden inputs (`Bosque.astro`, the new `conservar`), while the page itself uses the capped one | Decide `hayFiltros` on `pliega(q).trim()`. Have `conservar` read from `leerFiltros` (capped) instead of `Astro.url` |
| F8 | P3 | no | **Twin lookup on quote pages.** `grafo.server.ts:85` awaits `refresca()`, and the `fetch` at `:34` has no timeout. A hung `/api/v1/graph` therefore holds every quote page for up to undici's default of about 300 s. If the graph endpoint fails while `/wisdom/sample` works, each quote page pays a new graph round-trip, because nothing is cached on failure. Cold cost is small when healthy (0.08 s measured) | `fetch(…, { signal: AbortSignal.timeout(1500) })` in `refresca`. Cache a failure for `VIDA_MS`, so `gemelasTraduccion` returns `null` (link to the index) and does not wait again |
| F9 | P3 | no | **Legibility and contract drift.** A student reading cold gets the "what" (LOCATORS §1 three layers, §2 keys) but not a recipe for "how to add one", and several statements no longer match the code. (a) Report §2.3 (`:45`): "The EmptyState shows above the section index". It renders **below** it (order verified: search → index → empty → draw → facets), which matches the copy "secciones de arriba". (b) LOCATORS §4 `#map` row (`:69`) still says "stop 1"; the code lands on the title (report §5). (c) LOCATORS §6 (`:129-132`) still says AA3 sets `scroll-padding-top`; AA3b now does. (d) LOCATORS §4 `?from={id}&to={id}` does not say the values are **graph node ids**. On `/es/` today these are English ids (F59), so a student sees `ARCH-060` on screen while the URL says `arch-008`, and `/es/wisdom/arch-008/` 404s. (e) §8 "Add it here first" is ambiguous now that the JSON is the source. (f) Report §3 (`:81`) says "handscroll hash at 390 and 1440 px" with no network caveat (F2) | Amend LOCATORS: (b), (c), a sentence in §4 on node ids, and §8 rewritten as a 4-step recipe ("1. add the row to `locators.registry.json`; 2. if it redirects, add the rule to `lib/locators.ts` and a case to `middleware.test.ts`; 3. if it is a new page, map it in `locators-registry.test.ts` `routeFor` or `LIVE_ONLY`; 4. mirror it in the §4 table"). Fix report §2.3 and §3 |
| F10 | P3 | no | **The single-facet 301 now leads into soft 404s.** `?section=nope` 301s to `/es/wisdom/sections/nope/`, which answers **200** with an empty list. The facet pages were already like this on `main`; AA3b now sends traffic there, and LOCATORS §1 rule 1 plus AA4 canonicals care about it | Facet pages answer 404 for a value that is not in the locale's corpus (same pattern as `[slug].astro:20`). Add `/{l}/wisdom/sections/zz-none/` to `notFound` |
| F11 | P3 | no | **Copy-link silently does nothing on non-secure origins.** `copiarEnlace.ts:15` returns early when `navigator.clipboard` is undefined, as it is on plain-HTTP hosts other than `localhost` (e.g. a LAN name), and the anchor just navigates. There is no announcement, so the reader cannot tell the copy failed. Students on `localhost` are fine | Fall back to selecting a hidden input + `document.execCommand('copy')`, or announce "Copia la dirección de la barra" in `#ttod-aviso`. At minimum, write the limitation in the module comment |

## Checklist answers

1. **Acceptance and LOCATORS §3–§8.**
   - Holds: every registry row I probed (redirects with exact `Location`, 404s, exemptions, POST not redirected via the gate log); `?q=` with no JS (curl); `#volume-` and the paged quote (browser check); the 3D view at the header link, the `/graph/path` 301 and from/to across reload (browser check); `wis-034 → wis-033` and `?q=diseno#search` carried; 404 on an unknown id; the F54 test structure (`<dt>`/`<dd>`, 3/2/1 in both locales; mutation per the runner log); the copy-link control (§7) with a real anchor, polite live region and 44 px target.
   - Does not hold: item 2 (`#map-architecture` cold) holds only on a fast network (F2); deliverable 2's dialog copy-link is missing (F3); §3 adds an off-site redirect (F1).
   - Not re-measured: item 8 (UX rule). I checked the runner log only; the plano CLS 0.4702 is pre-existing (F60) and correctly recorded as a new baseline.
2. **Gate and browser-check amendments.**
   - *Conditional parity*: fair. It covers one id (`related-wisdom-title`) on one row, and the underlying content gap is recorded as F59. It hides no locator defect.
   - *Scroll to top before the switch*: fair. The header hides by design, and the check still asserts that search and hash are carried.
   - *Graph step on any `related` edge, twin id accepted*: fair, since the original could not run (es has no `related` edges). It leaves the Spanish-id alias to `senderoUrl.test.ts` only, which is acceptable. It does expose the legibility point in F9(d).
   - *Case-insensitive comparison*: fair.
   - None of the four lets F1 or F2 through. Those slipped past because the gate never sends a `//` path and never throttles the network.
3. **Correctness edges.**
   - *Redirects*: GET/HEAD only, the query is kept raw, the facet rule reserializes only when it removes a key, `/graph?tag=` resolves in one hop. The only defect is F1.
   - *Search*: the NFD fold is correct; the 100-char cap is enforced server-side and by `maxlength`; F7.
   - *Language switch*: cannot build an off-origin URL (`new URL(href, origin)`, returns path only), but it carries keys that mislead (F4).
   - *Scroll writer*: `replaceState` only, no history growth (verified), stops re-placing once touched. It does fight the reader's deep link during load (F2).
   - *Twin lookup*: F8.
   - *404*: correct, including the other locale's id.
   - *Copy-link a11y*: accessible names include the visible text (`wis-034 · Copiar el enlace…`, `#` + heading); F11.
   - *Service worker*: v7 purges v6, and `OFFLINE_PAGES` in slash form means the precache stores 200s, not redirected responses. A slashless offline navigation to `/es/oracle` is no longer served from cache, which is acceptable.
4. **Legibility.** The code comments explain *why* well: the `locators.ts` header lists its rules in order, and `capitulos.ts` explains the sticky-scene arithmetic. The registry `$comment` defines its placeholders. What is missing is the add-a-locator recipe and four drifted statements (F9). The report overclaims in three places: §2.2 (F3), §2.3 and §3 (F9).
5. **Scope.** Clean: no `ttod.yml`, `proposals/` or backend changes, and no new inline script.

## Downstream phases to amend (same commit as this review)

- **AA3** (`PHASES/AA3-nav-a11y-and-url-hygiene.md`): when it re-runs the AA3b anchor checks after defining `--ttod-header-height`, run them **with network throttling** and assert the hash is preserved (F2). The header hides on downward scroll, so a fragment jump lands with the header hidden; AA3 should decide whether that is intended for deep links.
- **AA4** (`PHASES/AA4-seo-robots-and-meta.md`): it consumes `locators.registry.json`. The registry has no rows for `/{l}/login/`, `/{l}/register/`, `/{l}/wisdom/propose/`, `/{l}/quote/` or `/{l}/account/reviewer/`; decide which belong in the sitemap. Facet pages are soft 404s (F10). For canonicals, `/{l}/graph/?from=&to=` values are node ids (F9(d)).
- **LOCATORS.md** §2, §4 (`#map`, graph node ids), §6, §8 per F4 and F9.
