<!--
AA4 cold review. Reviewer: cascade-cold-reviewer (agent), no implementation context.
Scope: noindex header, robots.txt, canonical/hreflang/og from the registry, quote meta, maskable manifest,
root locale negotiation, offline docs, the exit gate and its one amendment. Not marked DONE.
-->

# PHASE-AA4 cold review: robots, meta and PWA honesty

**Commits reviewed:** `7808afa3` … `84b1906f` (`git diff b07acc03..HEAD`, 4 commits). The gate was committed alone
first (`7808afa3`: the gate and INDEX only). The one later gate edit was compared against that commit.

**Verdict: PASS-WITH-AMENDMENTS.** There is no P1 and nothing blocks DONE. The owner decision is implemented
correctly, and I tested it live:
- `X-Robots-Tag: noindex` reaches pages, JSON, static files, the app's 404 and Caddy's own 400 and 404;
- `robots.txt` disallows nothing and names no sitemap;
- there is no sitemap anywhere.

Canonical, hreflang, og, the quote meta, the maskable icons and the root negotiation all behave as the report says
on the sample pages. Behind a trusted TLS proxy the canonical is `https://`.

Three P2s should be fixed inside AA4 before the owner marks it DONE:
- **F1:** `?p=` is kept on every path, so `/es/wisdom/?q=…&p=2` gets the canonical `/es/wisdom/?p=2`. That
  contradicts the AA3b carry ("`?q=` → canonical `/wisdom/`").
- **F2:** when the backend is down, the quote and facet pages answer 200 with a canonical. The quote page's title is
  then "Entrada de sabiduría no encontrada".
- **F3:** `e2e/i18n-routes.spec.ts` still asserts `/` → `/en/`. It now depends on the machine's locale.

F4–F10 are P3s: wording, comments, docs and gate coverage.

## What I ran (2026-11-12)

I never ran a command against `ttod_oracle` or port 18080. Live checks used
`isolated-stack.sh up ttod_aa4review 29080 TTOD_ALLOWED_HOSTS=ttod.lan.test`. That stack is down now
(`docker ps | grep -c aa4review` → `0`). `ttod_oracle` shows "Up 5 hours", untouched.

| Check | Command | Result |
| ----- | ------- | ------ |
| Frontend suite | `npx vitest run` | `Test Files 44 passed (44)`, `Tests 305 passed (305)` |
| Type check | `npm run check` | `0 errors, 0 warnings, 6 hints` |
| Verify log | `PHASES/AA4-…-VERIFY-LOG.md` | Exit 0 at `5d0056a8`; AA1/AA3b/AA3/AA5 re-run green, with their CSP lines in the log |
| Earlier gates and browser checks | `git diff --stat b07acc03..HEAD -- PHASES/*.exit-gate.sh scripts/` | Only the AA4 gate (new). Earlier gates and `scripts/` are unchanged |
| Gate first | `git show --stat 7808afa3` | The gate and INDEX only, no code |
| Gate amendment | `git diff 7808afa3..HEAD -- …exit-gate.sh` | One hunk, the forged-Host block (+10 −4), disclosed in report §6. A strengthening |
| Maskable, measured independently | PIL, any channel differs from pixel (0,0) at thresholds 0, 8 and 24 | `icon-192` r/w = **0.303**, `icon-512` **0.304** at every threshold; RGB, min alpha 255. The safe zone is 0.40 |
| Pure functions, edge cases | jiti script on `seo.ts` and `idioma.ts` (scratchpad) | See F1, F7, F8 and Q4 |
| 404 page (unmatched route) | `curl /es/nope/` | `404`, `robots noindex`, no canonical, no alternates |
| Pagination canonicals | `curl "/es/wisdom/?q=diseno&p=2"`, `/es/?p=7`, `/es/wisdom/tags/koan/?p=999` | Canonicals `…/es/wisdom/?p=2` (+ en/es/x-default `?p=2`), `…/es/?p=7`, `…/tags/koan/?p=999` (F1) |
| Docs subpage | `curl /es/docs/introduction/`; `curl /en/docs/introduction/` | Alternates point to `/en/docs/introduction/`, which answers `200` |
| Root | `curl -sI -H 'Accept-Language: es-ES,es;q=0.9' /` on :29080 and :29081 | `302`, `Location: /es/`, `Vary: Accept-Language`, `X-Robots-Tag: noindex` |
| Go-level rejections | `printf 'GET /es/ …Host: a b…' \| nc`, `printf 'BROKEN…' \| nc` | `400 Bad Request: malformed Host header` and `400 Bad Request`, plain text, **no X-Robots-Tag** (F6) |
| Untrusted proxy (from the backend container to `reverse-proxy:8080`) | Host `ttod.lan.test`, `X-Forwarded-Proto: https`, `X-Forwarded-Host` forged | canonical `http://ttod.lan.test/es/wisdom/`: Caddy replaced both headers. Forged host `evil.example` never in the head |
| Trusted proxy (`TTOD_TRUSTED_PROXIES=172.20.0.0/16`, Caddy recreated) | Same requests | canonical and `og:url` `https://ttod.lan.test/es/wisdom/`. With a forged XFH and an allowed Host: root-relative, no `og:url`. No `evil` anywhere |
| Allowed host, any port | `Host: localhost:6666` | canonical `http://localhost:6666/es/wisdom/` (F7c) |
| Backend down (`stop backend`, `restart frontend`) | `curl` quote, section, wisdom, quote-of-the-day | `/es/wisdom/wis-034/` **200**, canonical, title "Entrada de sabiduría no encontrada"; section 200 with a canonical; `/es/wisdom/` 200 with a canonical; `/es/quote/` 503 with noindex (F2) |
| `/quote/` "random" | `curl /es/quote/` three times | `href="/es/wisdom/arch-060/"` each time (F5) |
| HTML escaping | `curl /en/wisdom/img-045/`, `cc-012`, `es/…/cc-051` | `<title>…&lt;img srcset=&#39;...&#39;…`, `&quot;…` in title and in `content=`. Escaped correctly |
| Internal names served | `grep` of served `/es/`, `/en/wisdom/`, quote, login and the manifest for `AA[0-9]`, `D7`, `seguridad`, `Lilith`, `Tanit` | None in the HTML. `/robots.txt` carries `AA0 D7 (a)` and `(seguridad)` in its comments (F10). The only `crea-comm` is the existing rights-holder line in provenance, which is not AA4's |
| Corpus parity for swapped-locale alternates | Python over `ttod.yml` | tags 306/306, sections 13/13, levels 4/4; no value exists in only one locale. Docs: `src/content/docs/{en,es}/introduction.mdx` only |

## Acceptance (phase file `AA4-seo-robots-and-meta.md:77-80`)

- [x] **`/robots.txt` coherent; no private account URLs in sitemap.** It serves `User-agent: *`, `Allow: /` and
  no `Disallow`. There is no sitemap. D7 (a) is honoured (`PHASE-AA0-REPORT.md:47`).
- [x] **Sample pages: canonical + hreflang; quote titles not ID-only.** I verified this live, with two exceptions
  that need amending: F1 (`?p=`) and F2 (pages answering 200 while broken).
- [x] **Manifest/SW claims match behavior.** `sw.js` is unchanged; `OFFLINE_PAGES` = `/en/oracle/` and
  `/es/oracle/` (`sw.js:12`); the public docs say exactly that. One older doc now contradicts the manifest (F4).
- [ ] **Cold review green or amended.** This document.

## Findings

| ID | Sev | Blocks DONE | Finding and evidence | Fix |
| -- | --- | ----------- | -------------------- | --- |
| **F1** | P2 | no (amend in AA4) | **`?p=` survives on every path and every value, so a search page gets a pagination canonical.** `seo.ts:62-65` keeps `?p=N` for any integer N ≥ 2 on any route, and `canonica` (`:71`) and `alternas` (`:79`) append it. Live: `/es/wisdom/?q=diseno&p=2` → `canonical …/es/wisdom/?p=2`, hreflang `…/en/wisdom/?p=2`. The unfiltered `/es/wisdom/?p=2` is the plain shelf: `Estanteria.astro:95` renders `Bosque` only while filtering. So the search collapses onto a duplicate URL, not onto `/wisdom/` as the AA3b carry requires (`AA4-…md:44`). Also: `/es/?p=7` → self-canonical `/es/?p=7` (the landing has no pages). `/tags/koan/?p=999` → `?p=999` (`pasilloPedido` clamps the content to the last page, `content/bosque.ts:80-85`). `?p=1e1` → canonical `?p=10`, while the content shows page 1 (`parseInt("1e1")` = 1). The gate and the unit tests check only `?p=2` on a facet path (`seo.test.ts:32`), so none of this is seen | Keep `p` only where the page paginates and only for the page actually shown. Simplest: `Bosque` already computes `pasillo`. Let facet routes pass it to `Page` (e.g. `pagina={pasillo}`), and have `canonica` add `?p=` only when that prop is ≥ 2. On `/wisdom/` with `q` or filters, drop `p` (canonical `/wisdom/`). Add unit cases for `/es/wisdom/?q=x&p=2`, `/es/?p=2`, `?p=999`, `?p=1e1` |
| **F2** | P2 | no (amend in AA4) | **Pages that fail while the backend is down answer 200, carry a canonical, and are not noindex.** The "non-200 → noindex" rule (`Page.astro:64`, report §2.3) never sees them, because the routes keep 200 on `failed`: `wisdom/[slug].astro:22` sets 404 only `if (!failed && !quote)`. Live, with the backend stopped: `/es/wisdom/wis-034/` → `200`, `<link rel="canonical" href=".../es/wisdom/wis-034/">`, `<title>Entrada de sabiduría no encontrada`. `/es/wisdom/sections/architecture/` and `/es/wisdom/` → 200 with a canonical. `/es/quote/` already does it right (503 + noindex, `quote.astro:25`). The host header still covers this, so nothing is indexed today. But the report says the page rules "hold even if the host header is ever lifted" (§2.3) | On the routes that use `loadWisdom`, answer `503` when `failed` (as `/quote/` does), or pass `indexar={!failed}`. Either way, the layout then drops the canonical. Add one `head-seo.test.ts` case with `loadWisdom` mocked to `{ failed: true }` |
| **F3** | P2 | no (amend in AA4) | **An e2e test still asserts the old root redirect, and now depends on the machine's locale.** `e2e/i18n-routes.spec.ts:14-19` is "`/ redirects to the default locale`", `toHaveURL(/\/en\/?$/)`. The config sets no `locale` (`playwright.config.ts`). Playwright's `locale` "Defaults to the system default locale" (`node_modules/playwright-core/types/types.d.ts:11450-11452`), and that locale sets `Accept-Language`. On a machine set to Spanish, as a classroom in Spain may well be, `/` now goes to `/es/` and the test fails. On an English machine it passes, but it no longer describes the behaviour. The gate does not run this suite, so nothing caught it | Rename it to "/ picks the locale from Accept-Language". Pin `test.use({ locale: 'en-US' })` for the `/en/` case and add an `es-ES` case expecting `/es/` and `lang="es"` |
| **F4** | P3 | no | **An older PWA doc now contradicts the manifest.** `docs/pwa-install-quality.md:51` "All three entries use `purpose: any`; no maskable-icon claim is made"; `:33` "launching `/` reaches `/en/`"; the manifest table (`:19-28`) has no `lang`, `dir` or `description`. All three are false since `52ab7a5b`. It is the Task 5 team's evidence (linked from `docs/uso-ia-team-4.md:55`), so it should not be rewritten. Also, the new offline paragraph (`docs/public/platform/index.md:50`, es `:51`) does not say that the Oracle copies exist only after one online visit has installed the worker | Add a dated "Updated by AA4 (2026-11-12)" note under the manifest table and the icon paragraph: maskable 192/512 (glyph 0.30 of the width), `lang`/`dir`/`description`, and `/` → `/es/` or `/en/` by `Accept-Language`. In both platform docs, add "after one visit online" |
| **F5** | P3 | no | **The reason given for `/quote/` being noindex is false: it is not random.** The registry `$comment` (`locators.registry.json:27`), the report (§2.4 table, `:43`) and `LOCATORS.md:126` say "a different random quote on every visit". The page takes the first quote of the locale: `quote.astro:24` `payload?.find((entry) => entry?.lang === locale)`. Live, three fetches of `/es/quote/` all link `/es/wisdom/arch-060/`. Noindex is still right, for another reason: it duplicates that quote's own page. The page's copy "Una cita viva" / "A live quote" also promises something it does not do (pre-existing) | Correct the reason in the three places: "shows the first quote of the corpus, a duplicate of that quote's own page". Carry the product bug (a "live quote" that never changes) to AA6's disposition list |
| **F6** | P3 | no | **"Every response" is true of everything Caddy routes, not of everything a client can receive.** Report `:17` and §2.1, and the Caddyfile comment (`:31-34`). (a) Go's HTTP server rejects some requests before any Caddy handler runs: `Host: a b` → `400 Bad Request: malformed Host header`; a broken request line → `400 Bad Request`. Neither carries X-Robots-Tag or the AA1 headers (live, above). No crawler sends those, so the impact is nil. (b) A deploy that skips Caddy (`astro dev`/`preview`, `node dist/server/entry.mjs`, another proxy) has no host noindex at all. Then only the page rules apply, and they index the public pages. Students deploy on their own machines, so the docs should say where the noindex lives | Write "every response Caddy produces (pages, JSON, files, Caddy's own errors)" in the report and the Caddyfile comment. In the public platform or deploy doc, add one line: the classroom noindex is Caddy's `X-Robots-Tag`; serving the app any other way removes it |
| **F7** | P3 | no | **`origenPublico` is sound behind Caddy, with three loose ends.** (a) The comment at `seo.ts:57` ("without a host header … the URL is the request's own") is wrong. Without `Host`, Astro's URL is its fallback: `origenPublico(new URL('http://localhost:4321/es/'), new Headers({}))` → `"http://localhost:4321"`, the internal address this function exists to hide. It cannot happen through Caddy (an empty host fails `@hostmalo`, `Caddyfile:52`); only direct-to-Node callers hit it. (b) With an untrusted origin, `hreflang` goes root-relative (`/en/wisdom/`), and Google requires fully-qualified alternate URLs, so those tags are ignored at best. (c) Any host in `allowedDomains`, on any port, is reflected: `Host: localhost:6666` → canonical `http://localhost:6666/…`. Only the client who sent it sees that (no shared cache; the SW caches per browser), so it is acceptable | (a) Return `''` when no host header is present, and fix the comment. (b) When `origen` is `''`, emit no `hreflang`; keep the relative canonical, which search engines accept. Amend the gate's forged-Host line to match. (c) Say it in the doc comment: "only hosts in `allowedDomains` are ever printed" |
| **F8** | P3 | no | **Two Accept-Language rules in one app.** The root uses `idiomaPreferido` (q-values, `idioma.ts:76-87`). `404.astro:47-53` takes the first `es`/`en` tag and ignores `q`. `es;q=0.1, en;q=0.9` → the root sends `/en/`, but the 404 page renders in Spanish. Smaller points: `idiomaPreferido` ignores an upper-case `Q=` (`es;Q=0.1,en;q=0.5` → `es`), accepts `q=1.5`, and does not apply `*` | Make `404.astro` call `idiomaPreferido`. One rule is also easier to teach. Lower-case the parameter name before matching `q=` |
| **F9** | P3 | no | **Gate coverage gaps; no check passes trivially.** (a) The generic 404 page (`404.astro`, unmatched routes) has no check; I verified it by hand. (b) No check for the backend-down state (F2), the `?p=` cases (F1), or `https` in the canonical behind a trusted proxy (I verified this by hand; AA5 has the harness for it). (c) The gate header (`:19`) says the docs "name exactly the pages sw.js keeps offline", but step 4 checks presence only, so a doc that named extra pages would pass. (d) The live quote loop checks `hreflang` reciprocity for 8 pairs, but never fetches a swapped-locale alternate of a facet or docs page. That holds today only because the corpus has full facet parity (table above) | On amendment, add `/es/nope/` → 404 + noindex. Add F1's and F2's cases. Reword (c) as "name the pages" or add the inverse check (no other `/xx/` path in the offline paragraph). Optionally GET every non-quote alternate once and expect 200 |
| **F10** | P3 | no | **Small legibility points.** (a) `/robots.txt` is public, and its comments cite `AA0 D7 (a)` and "the (seguridad) snippet". A student reading it gets plan ids, not a reason. (b) Quote titles keep the corpus's Markdown backticks: `` The master writes: `<img srcset='...' …`. The… · Wisdom `` (img-045). (c) `recorte` cuts by UTF-16 unit, so a cut just before an emoji leaves a lone surrogate (`'a'.repeat(58)+'😀…'` → `…\ud83d…`). It is latent: the two emoji quotes (img-013, img-133) are cut earlier. (d) AA6 has no "Carried from AA4" section. Report §7 moves F62, the SW v9 bump and the indexing switch there, but `AA6-oracle-quota-and-closeout.md` does not mention F62 or AA4 | (a) "This classroom copy of TTOD asks search engines not to index it (an `X-Robots-Tag: noindex` header on every response). Nothing is disallowed: a crawler that may not fetch a page never reads its noindex." (b) Strip backticks in `tituloCita`. (c) Slice with `Array.from(texto)`. (d) Add "Carried from AA4" to the AA6 phase file in the amendment commit: F62, the indexing switch, F5's product bug |

## Answers to the brief's questions

**1. Does the noindex reach every response?** It reaches every response Caddy produces, and I found no path through
Caddy that escapes it.
- **Mechanism:** `X-Robots-Tag "noindex"` sits inside `(seguridad)` (`Caddyfile:40`). The site block imports
  the snippet first (`:47`), before the `@hostmalo` and `@rutadoble` handles, so their `respond`s carry it.
  `handle_errors` imports it again (`:131`) for errors Caddy generates itself (file_server 404, a 502 when an
  upstream is down).
- **Tested live by the gate:** pages, `/api/v1/wisdom/sample`, `/health`, `/robots.txt`, `/site.webmanifest`,
  `/sw.js`, an app 404, a `/project-docs/` file_server 404, `@rutadoble` 404 and `@hostmalo` 400. I re-checked
  `/` on both ports.
- **The only misses:** requests Go rejects before routing (malformed Host, a broken request line), and any deploy
  that skips Caddy (F6).

**2. Canonical and hreflang.**
- **Query:** the query is dropped, which is right for `?q=`, filters, `?from=&to=&node=`, `?tag=`, `?s=` and
  `?next=`. But `p` is kept too widely (F1).
- **Reciprocity:** the alternates are reciprocal, and x-default is the English page (`seo.ts:79-88`).
- **Quotes:** each quote points to its twin in both directions (`[slug].astro:25-29`). The gate checked 8 twin pairs
  live, including back-links. With no twin, or with the graph down (`gemelas === null`), the quote has a canonical
  and no alternates (unit-tested, `head-seo.test.ts:116`).
- **Non-200 and `404.astro`:** non-200 pages get noindex and no canonical; I checked `404.astro` live
  (`/es/nope/`). Pages that are broken but answer 200 are not covered (F2).
- **Docs subpages** (`/{l}/docs/<slug>/`, not in the registry): they are indexable, with the same path as the
  alternate. That is valid today: the collection has only `introduction` in both locales, and both answer 200.
  Facet pages are valid for the same reason: tag, section and level sets are identical across locales.
- **Swapped-locale 404s:** I found no other page whose swapped-locale alternate 404s. Nothing guarantees it in the
  future, though (F9d). A docs page or tag added to one locale only would announce a 404 alternate.

**3. Untrusted Host.**
- **Behind Caddy, it is sound.** Caddy overwrites `X-Forwarded-Host` and `X-Forwarded-Proto` for any client
  outside `trusted_proxies`, so a client cannot send a forwarded host separate from its `Host`.
- **How Astro builds the URL:** it takes `Host` only if it is in `allowedDomains`, and otherwise falls back to
  `localhost:4321` (`astro/dist/core/app/node.js:44-48`). It then applies a validated forwarded host and proto
  (`fetch-state.js:872-891`).
- **The comparison:** `origenPublico` compares the forwarded or direct host with `url.host`, and gives an empty
  origin exactly when Astro fell back.
- **Live through Caddy:** a forged host never appears in the head. The worst a client can do is pick another
  allowed host or port and see it reflected to itself (F7c). Without a shared cache, that is not poisoning.
- **Trusted proxy (Traefik → Caddy → Node):** Caddy keeps Traefik's `X-Forwarded-Proto: https` and
  `X-Forwarded-Host`, Astro accepts them (the `allowedDomains` entries name no protocol), and the canonical and
  `og:url` are `https://ttod.lan.test/…` (verified live).
- **Loose ends:** a request with no `Host` (direct to Node only) prints the internal origin (F7a), and relative
  hreflang is not valid (F7b).

**4. Quote title and description.**
- **Title:** `recorte` collapses whitespace and cuts at the last space before the limit when that space falls past
  half the limit; otherwise it cuts hard. It strips trailing punctuation and adds "…". Short text passes through
  unchanged.
- **Description:** `teaches` if non-blank, else the text, cut at 155 (`seo.ts:91-107`). In the corpus every quote
  has `teaches` (shortest 21 characters: "Lazy loading strategy"); 56 descriptions are cut.
- **Escaping:** Astro escapes `<`, `'` and `"` in `<title>` and in `content=`. I checked img-045, cc-012 and
  cc-051 live.
- **Cosmetic issues:** Markdown backticks in titles, a possible lone surrogate (F10b, c), and an opening quotation
  mark left unclosed by the cut (cc-012). A blank text would give " · Sabiduría", but the corpus schema always has
  text.

**5. Root negotiation.**
- **Behaviour:** `/` answers 302 with `Vary: Accept-Language` (`pages/index.astro:5-6`), and it reaches the client
  through Caddy on both ports. There is no `Cache-Control`, so browsers do not store the 302.
- **Service worker:** it does not intercept `/` (`sw.js:163-175`), so the installed app's `start_url` is negotiated
  online on every launch. Offline, `/` fails as it did before AA4, and the docs say only the Oracle pages work
  offline.
- **Parsing:** q-values are handled correctly for the cases tested. `404.astro` uses a different rule (F8).
- **Stale assumption:** `e2e/i18n-routes.spec.ts:14-19` still assumes `/` → `/en/` (F3), and so does
  `docs/pwa-install-quality.md:33` (F4). No gate depended on it. Historical reports (R3a, R7) record the old
  behaviour, as they should.

**6. Manifest and offline honesty.**
- **Maskable:** the maskable claim holds. The same PNGs are fully opaque on a paper-coloured background, and I
  measured the glyph radius independently at 0.303 and 0.304 of the width, inside the 0.40 safe zone at every
  threshold.
- **`lang` and `dir`:** `lang: "en"` and `dir: "ltr"` describe the manifest's own strings. That is a defensible
  single-manifest choice (report §2.8), and the PWA guard passes with them.
- **Offline docs:** the new paragraphs match `sw.js` v8: network-first, an anonymous copy, the Oracle pages only.
  Two gaps: they omit "after one visit online" (F4), and `docs/pwa-install-quality.md` now contradicts the
  manifest (F4).
- **Report §2.9 (cached API GETs):** it names `/api/v1/graph` and `/api/v1/wisdom/sample`. The worker also caches
  `GET /api/v1/wisdom/random` (`Mazo.astro:157`, sent with a bearer token). That data is public corpus data, so the
  conclusion stands, but the list is incomplete.

**7. The gate.**
- **Legibility:** it is legible. Its header lists the decisions it encodes and the test-file contract.
- **Trivial passes:** I found none. Each check ties to a falsification in report §4, and I re-derived several
  (X-Robots-Tag on Caddy's own errors, the title-from-id check, the query canonicals, the forged-Host check).
- **Gaps:** some claims and cases are missing (F9).
- **The amendment:** justified, disclosed in §6 and in the gate's own comment, and it is a strengthening. The first
  version passed trivially, because Astro never trusts `evil.example`. The new version adds an unlisted IP and
  forbids `localhost:4321`.
- **Earlier gates and browser checks:** byte-identical to the base (`git diff --stat` above). They were re-run
  green, with their CSP and Lighthouse lines in the committed log.

**8. Legibility.**
- **Code:** `seo.ts` reads well for a student. Each function has one rule and a short Spanish doc comment saying
  why, and the registry is named as the single list. `Page.astro:60-69` explains in four lines why a noindex page
  has no canonical.
- **What would trip a student:** the wrong comment in F7a, and the two Accept-Language rules (F8).
- **Internal names:** none in the served HTML, the manifest or the public docs. `/robots.txt` cites plan ids
  (F10a). The quote descriptions show corpus `teaches` as written, so dop-008 shows "Tao de DevIAC (§49)…". That
  text already appears on the quote page itself; AA4 only promotes it to the meta description.

**9. CSP backlog.**
- **Inline scripts:** none added. `Page.astro` gained no `<script>`, and `is:inline` did not grow (gate step 6).
- **JSON-LD:** none (`git grep application/ld+json` is empty).
- **Served counts:** in the re-run AA3b and AA3 browser checks they equal AA1's: `/es/` 4, `/es/wisdom/` 3, quote 3.

## Gate amendment

| Amendment | Judgement |
| --------- | --------- |
| Forged Host strengthened (unlisted IP, no `localhost:4321`, relative canonical, no `og:url`/`og:image`) | **Legitimate; a strengthening, disclosed** (report §6, gate comment). If F7b is adopted (no relative hreflang), amend this line again and disclose it the same way |

## Downstream

- **AA6** (close-out): it has no "Carried from AA4" section. Add F62, the indexing switch (report §7), F5's
  product bug, and the SW v9 bump in the same change as CSP enforcement. The last of these is already in AA6
  (`:48`). Make that edit in the same commit as the AA4 amendments (F10d).
- **Indexing, if ever reopened:** F1, F2 and F7b must be fixed first. The page rules are what a sitemap and the
  canonicals would then rely on.
