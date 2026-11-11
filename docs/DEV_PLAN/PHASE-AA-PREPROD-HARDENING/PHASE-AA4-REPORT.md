<!--
AA4 report: SEO robots, meta and PWA honesty.
Author: Rubén Vega Balbás PhD (agent-assisted). Status DONE by the owner. The agent does not mark DONE.
-->

# PHASE-AA4 report: robots, meta and PWA honesty

**Status:** DONE (owner, 2026-11-12: "AA4 DONE"; the cold review was still running, §8) · **Branch:** `cascade/PHASE-AA-PREPROD-HARDENING-4`, stacked on AA7 (PR #98 not yet merged).
**Exit gate:** [`PHASES/AA4-seo-robots-and-meta.exit-gate.sh`](PHASES/AA4-seo-robots-and-meta.exit-gate.sh). It was
committed alone (7808afa3) before any phase code. It re-runs the AA1, AA3b, AA3 and AA5 gates unchanged. There was one
later edit, a strengthening (§6). **Findings:** F14, F15, F41, F42, F43, F44 · **Assignments:** A12, A13, A27, A28.

## 1. Result

| Finding | Before (AA0 re-probe, 2026-11-10) | After |
| ------- | --------------------------------- | ----- |
| F14 robots | `/robots.txt`, `/sitemap.xml` → 404; nothing said noindex | `X-Robots-Tag: noindex` on **every** response, including Caddy's own 400 and 404 errors. `/robots.txt` has no `Disallow` and no `Sitemap`. No sitemap |
| F15 head | charset, viewport, theme-color, description, manifest, icon | + canonical, `hreflang` en/es/x-default, `og:*`, `twitter:card`; `robots noindex` where the registry says so |
| F41 quote meta | `<title>wis-034 · Sabiduría</title>`, the site's generic description | title = the quote's first words; description = what it teaches; `og:type article`; `hreflang` = the translation twin |
| F42 offline | the docs said nothing about what works offline | public platform docs (en, es): only `/en/oracle/` and `/es/oracle/` open offline, as anonymous copies, and installing does not change that |
| F43 manifest locale | English only; `start_url: "/"` always led to `/en/` | `lang`, `dir` and `description`. `/` now picks `/es/` or `/en/` from `Accept-Language` (302, `Vary`) |
| F44 maskable | `purpose: any` only | maskable 192 and 512 entries. They reuse the existing icons, whose glyph measures 0.30 of the width (the safe zone is 0.40) |

## 2. Decisions

1. **Noindex mechanism (AA0 D7 (a)).** `X-Robots-Tag "noindex"` sits in Caddy's `(seguridad)` snippet. The site
   block and `handle_errors` both import that snippet, so JSON, files and Caddy-generated errors carry it too
   (AA1 cold review R8). `noindex` alone, as decided; no `nofollow`. Reopening indexing is an owner decision.
2. **robots.txt allows everything, on purpose.** A crawler that may not fetch a page never reads its noindex.
   There is no sitemap while the host is noindex, and `@astrojs/sitemap` is not installed.
3. **Page-level rules, from the registry.** These hold even if the host header is ever lifted. The list of pages
   is not repeated: `lib/seo.ts` reads `locators.registry.json`.
   - A row with `"index": false` or `"auth": true`, `?untranslated=`, or any non-200 response gets
     `<meta name="robots" content="noindex">`. Such a page has **no canonical and no hreflang**: it would be
     contradictory to name a preferred URL for a page that asks not to be indexed.
   - The layout reads `Astro.response.status`. A unit test proves that a facet 404 is noindex.
4. **The five unregistered pages (AA3b cold review).**

   | Row | Decision | Why |
   | --- | -------- | --- |
   | `/{l}/login/`, `/{l}/register/` | indexable | public, stable, no personal data; A13 names login for OG and canonical |
   | `/{l}/wisdom/propose/` | `index: false` | a form behind sign-in; anonymous visitors only see a prompt |
   | `/{l}/quote/` | `index: false` | a different random quote on every visit; each quote's own page is the stable address |
   | `/{l}/account/reviewer/` | `auth: true` | signed in only |

5. **Canonical.** The canonical is the path without the query, and `?p=` is kept from page 2 up. So `?q=`,
   combined filters, `?from=&to=&node=`, `/graph/plano/?tag=`, `/graph/code/?s=` and `?next=` all point at their
   path. `hreflang` lists en, es and `x-default` (= en), all absolute and reciprocal. A quote's alternate is its
   twin (`gemelasTraduccion`, both directions). A quote with no twin, or a request where the graph is down,
   announces no alternates.
6. **Untrusted Host (found while verifying, §6).**
   - Astro only trusts hosts in `security.allowedDomains` (`TTOD_ALLOWED_HOSTS`, AA2). For any other host, its
     URL falls back to the container's own `http://localhost:4321`, and the first build wrote that address
     into the canonical, `og:url` and `hreflang`.
   - It happens with a forged Host, and with a classroom IP that nobody added to the list.
   - Now, when the host the browser asked for (Caddy's `X-Forwarded-Host`, or `Host`) is not the host in the
     URL, canonical and alternates are root-relative, and `og:url` and `og:image` are left out.
7. **No JSON-LD.** It would be an inline script, and the AA1 CSP backlog forbids new ones. The `<script>` count
   in `Page.astro` and the `is:inline` count are unchanged.
8. **One manifest.** `start_url` stays `/` (the PWA spec and the `id` depend on it), and the root does the
   locale choice. `lang: "en"` describes the manifest's own strings. Per-locale manifests would change the
   app's identity for no user gain.
9. **The service worker is not touched.** No bump is needed: v8 already serves the Oracle pages network-first
   from anonymous copies (AA3 F1). The browser's `/api/` GETs that the worker caches (`/api/v1/graph`,
   `/api/v1/wisdom/sample`) are public data; favorites are POST and DELETE only.
10. **F62 (breadcrumb alignment) is not done here.** AA4 does not touch `Breadcrumbs`, so it is carried to AA6.

## 3. Changes

- `caddy/Caddyfile`: `X-Robots-Tag "noindex"` in `(seguridad)`, with the reason.
- `services/frontend/public/robots.txt` (new); `public/site.webmanifest`: `lang`, `dir`, `description`, two maskable entries.
- `src/lib/seo.ts` (new):
  - `indexable`, `canonica`, `alternas` and `origenPublico`;
  - `recorte`, `tituloCita` and `descripcionCita`.
- `src/layouts/Page.astro`: new props `alterna`, `indexar` and `tipo`, and the head tags.
- `src/pages/[locale]/wisdom/[slug].astro`: the quote's title, description and type, and its twin alternate.
- `src/pages/index.astro` and `src/lib/idioma.ts` (`idiomaPreferido`): `/` picks the locale.
- `src/lib/locators.registry.json`: five rows, and the meaning of `index` in `$comment`. `LOCATORS.md` §4 records the same.
- `docs/public/platform/index.md` and `docs/public/es/platform/index.md`: an "Offline, today" paragraph.
- Tests:
  - `src/lib/seo.test.ts` (new);
  - `src/layouts/head-seo.test.ts` (new);
  - `src/lib/idioma.test.ts` (Accept-Language);
  - `src/tests/locators-registry.test.ts` (routes for login, register and propose; `/quote/` is live only);
  - `e2e/pwa-installability.spec.ts` (`lang`, `dir`, maskable).

## 4. Evidence

Taken from an isolated stack on 2026-11-12 (`curl`, abridged):

```text
$ curl -sI /es/wisdom/wis-034/
HTTP/1.1 200 OK
X-Robots-Tag: noindex
<title>El Tao que puede expresarse en un prompt no es el Tao… · Sabiduría</title>
<meta name="description" content="El prompt y la generación no sustituyen la comprensión necesaria para juzgar, mantener y asumir la responsabilidad del código.">
<link rel="canonical" href="http://127.0.0.1:28980/es/wisdom/wis-034/">
<link rel="alternate" hreflang="en" href="http://127.0.0.1:28980/en/wisdom/wis-033/">
<link rel="alternate" hreflang="es" href="http://127.0.0.1:28980/es/wisdom/wis-034/">
<link rel="alternate" hreflang="x-default" href="http://127.0.0.1:28980/en/wisdom/wis-033/">
<meta property="og:type" content="article">
<meta property="og:locale" content="es_ES"> <meta property="og:locale:alternate" content="en_US">
/es/wisdom/propose/          → <meta name="robots" content="noindex">, no canonical
/es/library/ (signed out)    → 302 /es/login/?next=%2Fes%2Flibrary%2F
Host: evil.example, /es/     → <link rel="canonical" href="/es/">, no og:url, no og:image
```

Before, for the same quote: `<title>wis-034 · Sabiduría</title>` and no canonical, alternates or OG tags.

**Tests:**
- frontend suite: 44 files, **305** tests passing (274 at the AA7 tip; 31 new); `astro check` 0 errors;
- PWA guard: 8 passing (Chromium installability: no errors with the maskable entries);
- live probe: the whole registry in both locales, eight quote twin pairs and two quotes without a twin, signed-in
  account, library and reviewer pages, a forged Host and an unlisted IP, root negotiation, the served manifest.

**Falsification.** Each new check was run against code put back the old way, failed, and the code was restored:

| Check | Old code put back | Result |
| ----- | ----------------- | ------ |
| X-Robots-Tag everywhere | line removed from `(seguridad)` | 11 failures (pages, JSON, files, app 404, file_server 404, `@rutadoble` 404, `@hostmalo` 400) |
| canonical drops the query | `url.search` kept | `?q=`, combined filters, `?from=&to=`, `?next=` canonicals and `og:url` fail |
| quote title from text | `` `${quote.id} · …` `` | every quote: "title starts with the id" and "lacks the quote's first words" |
| root picks the locale | `Location: '/en/'` | `es`, `es-ES,…` and `fr, es;q=0.5` fail |
| untrusted Host | `origen = Astro.url.origin` | `evil.example` and `192.168.77.7:8080`: `localhost:4321` in the canonical and `og:url` |
| quote row noindex | `"index": false` removed | gate step 3 and two unit tests fail (the live probe follows the registry, so it cannot see this, by design) |
| robots.txt | `Disallow: /es/account/`; `Sitemap: …` | each fails step 1 |
| maskable | maskable entries removed | gate step 4 and the PWA spec (`1 failed`) fail |
| offline docs | `/es/oracle/` renamed in the es doc | step 4 offline check fails |
| SW bump | `sw.js` edited, no version change | "sw.js changed without a cache version bump (next is v9)" |

The rebuild really swapped in each case: the failing messages quote the old output (`arch-060 · Sabiduría`,
`http://localhost:4321/es/`).

## 5. What AA4 does not change

- **Visible UI:** none, so there are no screenshots. The head is not rendered. The re-run AA3b and AA3 browser
  checks cover page errors, CSP counts and header geometry.
- **The service worker, and Caddy's routes:** unchanged. Caddy gained only one header line.
- **The corpus, `ttod.yml` and the backend:** untouched (gate step 6).

## 6. Gate amendments (disclosed)

1. **Forged Host, strengthened (during AA4, before verify).**
   - The first gate only refused the forged host (`evil.example`) in the canonical, `og:url` and `hreflang`.
     That passed trivially, because Astro never trusts that host.
   - Looking at the output showed `http://localhost:4321` there instead (§2.6).
   - The check now also sends an unlisted IP host. It requires no forged or internal address anywhere in the
     head, a root-relative canonical, and no `og:url` or `og:image`.
   - Falsified: with the old origin it fails on both hosts.

## 7. Carries to AA6

- **CSP enforcement:** when it lands, bump the SW to v9 in the same change (AA1 R8).
- **F62:** breadcrumb current-item alignment (AA4 did not touch `Breadcrumbs`).
- **Indexing:** if an owner ever opens a host to indexing, removing the Caddy header is the whole switch. The
  page-level rules (§2.3) and a sitemap built from `locators.registry.json` (indexable rows only, corpus values
  only) are then the follow-up.

## 8. Cold review

[PHASE-AA4-COLD-REVIEW.md](PHASE-AA4-COLD-REVIEW.md): **PASS-WITH-AMENDMENTS**, no P1, nothing blocking. It
returned **after** the owner marked AA4 DONE, so no amendment is applied without the owner's word.

- **P2s (awaiting the owner's decision):**
  - F1: `?p=` is kept on any path (`/es/wisdom/?q=x&p=2` → canonical `/es/wisdom/?p=2`, against the AA3b rule;
    `?p=1e1`, `?p=999`, `/es/?p=7`).
  - F2: with the backend down, the quote, facet and wisdom pages answer 200 with a canonical and no noindex.
  - F3: `e2e/i18n-routes.spec.ts` still asserts `/` → `/en/`, which fails on a Spanish-locale machine.
- **P3s (F4–F10):** carried to AA6 ([AA6 § Carried from AA4](PHASES/AA6-oracle-quota-and-closeout.md)).
