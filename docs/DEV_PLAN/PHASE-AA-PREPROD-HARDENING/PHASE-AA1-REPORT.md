<!--
AA1 report: Caddy security response headers (F1 / A1).
Author: Rubén Vega Balbás PhD (agent-assisted). Status VERIFYING. The agent does not mark DONE.
-->

# PHASE-AA1 report: Caddy security headers

**Status:** VERIFYING · **Branch:** `cascade/PHASE-AA-PREPROD-HARDENING-1` · **Exit gate:**
[`PHASES/AA1-caddy-security-headers.exit-gate.sh`](PHASES/AA1-caddy-security-headers.exit-gate.sh) ·
**Evidence:** [`baselines/aa1-2026-11-10/`](baselines/aa1-2026-11-10/)

## What changed

One `header` block at the top of the site in `caddy/Caddyfile`, so it applies to every response
(pages, API, assets). Each line is explained in a comment there.

| Header | Value | Why this value |
| ------ | ----- | -------------- |
| `X-Frame-Options` | `DENY` | TTOD has no iframes of its own and nobody embeds it. CSP is report-only, and in that mode `frame-ancestors` does not protect, so this header does the frame denial |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Outbound links (GitHub, Creative Commons) receive the origin only, never the path or query |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()` | The source uses none of these APIs (searched: no `getUserMedia`, geolocation or speech) |
| `X-Content-Type-Options` | `nosniff` | A wrong MIME type becomes a visible failure instead of a guess. The browser smoke found none |
| `Content-Security-Policy-Report-Only` | the **target** policy: scripts `'self'` only, styles `'self' 'unsafe-inline'`, images `'self' data: blob:`, `object-src 'none'`, `base-uri`/`form-action 'self'`, `frame-ancestors 'none'` | See "CSP: report-only, and what enforcing needs" |
| `Server` | removed | Caddy sent none here. The `-Server` line keeps it that way if a future version adds one |

**Not added, on purpose:** HSTS. The edge is plain HTTP (F2, AA5 lane B), and HSTS here would
claim HTTPS the stack does not have. `auto_https off` is unchanged. CSP is **not** enforced: AA0
authorized report-only first.

## Evidence

**Before and after with curl** ([`curl-evidence.log`](baselines/aa1-2026-11-10/curl-evidence.log)):

- **Before:** the live `/es/` sent only `Content-Type`, `Date` and `Via` (also in AA0's
  `probe.log`, F1).
- **After:** this branch's Caddyfile, served by a throwaway Caddy container on the live Compose
  network, sends all five headers on `/es/` and on the JSON API.
- The instructor stack was not reloaded.

**Browser smoke, before and after**
([`browser-smoke.mjs`](baselines/aa1-2026-11-10/browser-smoke.mjs), results in
`browser-smoke-{before,after}.json`). Chrome loads 8 views: `/es/`, `/es/wisdom/`, a quote page,
`/es/graph/`, `/es/graph/path/`, `/es/oracle/`, `/es/login/` and `/en/docs/`.

| | Before | After |
| --- | --- | --- |
| HTTP status | 200 × 8 | 200 × 8 |
| Console errors (non-CSP) | 0 | **0** |
| Failed requests or HTTP ≥ 400 (nosniff blocks would show here) | 0 | **0** |
| Service worker registered | 8 / 8 | **8 / 8** |
| CSP report-only violations | n/a | 32, all `script-src-elem` inline (see below) |

**Exit gate:** it validates the Caddyfile for the pinned image (`caddy:2.10-alpine`), serves it on
the live network, and checks:

- the headers on three pages, with no enforcing CSP and no HSTS;
- the API is JSON with no CORS header invented;
- `/_astro` assets return 200;
- `/sw.js` keeps its `no-cache` rule;
- scope covers only `caddy/` and `docs/`.

It failed on the old Caddyfile and passes on this one.

## CSP: report-only, and what enforcing needs

The first smoke also reported 5 `img-src blob:` violations. These are legitimate textures generated
in the browser (`components/estilo/cielo.ts`, `lib/tinta.ts`), so `blob:` joined `img-src`, and
the second smoke shows none.

What remains is exactly one class: **32 inline `<script>` elements**, 3–6 per page. They are
Astro's hydration and page scripts. The target policy would block them. Enforcement needs, in a
later phase or assignment:

1. Hashes for those scripts. Astro's built-in CSP support can emit `'sha256-…'` sources per page;
   a nonce is the alternative.
2. Then `Content-Security-Policy-Report-Only` becomes `Content-Security-Policy` with the same
   directives plus the hashes, and the browser smoke must report 0 violations.
3. A report endpoint (`report-to`) is optional for a classroom host. Today the browser console is
   the report channel, and `browser-smoke.mjs` reads it.

Styles keep `'unsafe-inline'`: `/es/` alone has 88 `style=` attributes from the visual system.
Removing that is a design-system change, not a header change.

## Rolling it out on Tanit (after the owner merges)

The Caddyfile reaches the container as a **single-file bind mount**. `git pull` replaces the file
(new inode), and a running container keeps seeing the old one, so a reload or restart is not enough
on its own. Recreate the proxy:

```bash
cd ~/src/ttod && git pull --ff-only
docker compose up -d --force-recreate reverse-proxy     # or: make rebuild
curl -sI http://127.0.0.1:18080/es/ | grep -iE 'x-frame|referrer|permissions|nosniff|report-only'
```

All five headers must be listed. Pages, API, login and the oracle keep working (browser smoke
above).

## Acceptance

- [x] Headers present on HTML responses from the public port (gate, curl evidence).
- [x] API JSON still usable; no CORS invented (gate).
- [ ] Cold review: no header that breaks Astro assets or the service worker without a documented
  exception (smoke: 0 errors, 0 failed requests, service worker 8/8; the reviewer decides).
