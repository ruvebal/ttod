<!--
AA1 report: Caddy security response headers (F1 / A1).
Author: Rubén Vega Balbás PhD (agent-assisted). Status VERIFYING. The agent does not mark DONE.
-->

# PHASE-AA1 report: Caddy security headers

**Status:** DONE (owner, 2026-11-10: "AA1 done") · cold review **PASS-WITH-AMENDMENTS**
([PHASE-AA1-COLD-REVIEW.md](PHASE-AA1-COLD-REVIEW.md)), amended in the same session (§7) ·
**Branch:** `cascade/PHASE-AA-PREPROD-HARDENING-1` · **Exit gate:**
[`PHASES/AA1-caddy-security-headers.exit-gate.sh`](PHASES/AA1-caddy-security-headers.exit-gate.sh) ·
**Evidence:** [`baselines/aa1-2026-11-10/`](baselines/aa1-2026-11-10/)

## 1. What changed

`caddy/Caddyfile` defines the headers once, in a snippet `(seguridad)`, and imports it in two
places:

- **the site block**, for every response Caddy proxies (pages, API, assets) or serves;
- **`handle_errors`**, for the errors Caddy generates itself: a 502 when an upstream is down, and a
  `file_server` 404 under `/project-docs/`. Without it those responses skip the site's headers.
  Upstream errors such as Astro's 404 page or a FastAPI 404 are normal proxied responses and keep
  their own bodies.

Each line is explained in a comment in the Caddyfile.

| Header | Value | Why this value |
| ------ | ----- | -------------- |
| `X-Frame-Options` | `DENY` | TTOD has no iframes of its own and nobody embeds it. CSP is report-only, and in that mode `frame-ancestors` does not protect, so this header does the frame denial |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Outbound links (GitHub, Creative Commons) receive the origin only |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=(), payment=(), usb=()` | The source uses none of these APIs (searched: no `getUserMedia`, geolocation or speech) |
| `X-Content-Type-Options` | `nosniff` | A wrong MIME type fails visibly instead of being guessed. The browser smoke found none |
| `Content-Security-Policy-Report-Only` | the **target** policy: `script-src 'self' 'report-sample'`, `style-src 'self' 'unsafe-inline'`, `img-src 'self' data: blob:`, `object-src 'none'`, `base-uri`/`form-action 'self'`, `frame-ancestors 'none'`, everything else `'self'` | §4 |
| `Server` | removed | Caddy-generated errors used to send `Server: Caddy`; now no response does |

**Not added, on purpose:** HSTS. The edge is plain HTTP (F2, AA5 lane B), and HSTS here would
claim HTTPS the stack does not have. `auto_https off` is unchanged. CSP is **not** enforced:
report-only first is AA1's own contract (`AA1-caddy-security-headers.md`, Goal). AA0 recorded no
decision on CSP.

## 2. Evidence

**Before and after with curl** ([`curl-evidence.log`](baselines/aa1-2026-11-10/curl-evidence.log)):

- **Before:** the live `/es/` on :18080 sent only `Content-Type`, `Date` and `Via` (also in AA0's
  `probe.log`, F1).
- **After:** this branch's Caddyfile, served by a throwaway Caddy container on the live Compose
  network, sends all five headers.
- Route coverage, after the R1 amendment: `/es/`, the Astro 404 page, `/health`, the API, an API
  404, a Caddy `file_server` 404, and a 502 from a proxy that cannot reach its upstream all carry
  the five headers and no `Server`.

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
| CSP report-only violations | n/a | 32 reports from **7 distinct inline scripts** (§4) |

The cold reviewer independently confirmed the oracle stream through the new headers:
`text/event-stream`, uncompressed, still dripping in 70 reads.

**Exit gate:** it validates the Caddyfile for `caddy:2.10-alpine` and serves it on the live network.
It checks:

- the headers on three pages and, after R6, on `/health`, the API, an API 404 and a Caddy
  `file_server` 404, with no `Server` header;
- no enforcing CSP and no HSTS;
- the API is JSON with no CORS header invented;
- `/_astro` assets return 200, and `/sw.js` keeps its `no-cache` rule;
- scope covers only `caddy/` and `docs/`.

It failed on the old Caddyfile and passes on this one.

## 3. What the gate does not prove

The **public port :18080** still runs the old Caddyfile until the owner rolls this out (§5). All
"after" evidence comes from a throwaway proxy running the same file. The rollout `curl` in §5 is
what confirms :18080; whether DONE waits for it is the owner's call.

## 4. CSP: report-only, and what enforcing needs

The first smoke also reported `img-src blob:`. These are legitimate textures generated in the
browser (`components/estilo/cielo.ts`, `lib/tinta.ts`), so `blob:` joined `img-src`.

What remains is one class: **7 distinct inline scripts** (32 reports across the 8 views).
`'report-sample'` makes each report name its script.

| Script | Origin | Reports |
| ------ | ------ | ------- |
| Footer (`[data-pi…]`), nav toggle (`ttod-si…`), network notice (`ttod-ne…`) | **TTOD layout**, on every page | 8 + 8 + 8 |
| Pre-paint script ("Antes de pintar…") | **TTOD**, `/es/` | 1 |
| Island hydration (3 variants) | **Astro** | 3 + 3 + 1 |

**`script-src` must have one owner at enforcement.** Caddy sends one static header for every page,
so it cannot carry per-page hashes. The browser also applies every CSP it receives, so a Caddy
`script-src 'self'` would keep blocking inline scripts even if a page's `<meta>` CSP listed their
hashes. Two workable paths:

- **(a)** Astro owns `script-src` through its CSP support, which emits per-page hashes in a
  `<meta>`. It is still `experimental.csp` in the installed Astro 5.18. Caddy then drops
  `script-src` from its header and keeps every other directive.
- **(b)** Move TTOD's four inline scripts into external modules, and check whether Astro's three
  hydration scripts can be emitted as files. Caddy's static `script-src 'self'` then becomes
  enforceable.

Either path ends with `Content-Security-Policy` instead of `-Report-Only`, the browser smoke at 0
violations, and a **service worker cache bump**. `sw.js` caches whole responses, headers included,
so already-cached pages would keep the old policy. The follow-up is recorded in AA6 (§6).

Styles keep `'unsafe-inline'`: `/es/` alone has 88 `style=` attributes from the visual system.
Removing that is a design-system change, not a header change.

## 5. Rolling it out on Tanit (after the owner merges)

The Caddyfile reaches the container as a single-file bind mount. Measured by the cold reviewer:
after `git pull` replaces the file, `caddy reload` inside the running container fails, but a
**restart or a recreate** picks up the new file. Use the proxy-only command:

```bash
cd ~/src/ttod && git pull --ff-only
docker compose up -d --force-recreate reverse-proxy
curl -sI http://127.0.0.1:18080/es/ | grep -iE 'x-frame|referrer|permissions|nosniff|report-only'
```

All five headers must be listed. `make rebuild` would also work (the AA5 lane A bind mount now keeps
proposal drafts), but it recreates the whole stack for a one-file change.

## 6. Follow-ups recorded elsewhere

- **CSP enforcement** (§4 path (a) or (b), service worker cache bump): a row in the AA6
  disposition, `PHASES/AA6-oracle-quota-and-closeout.md`.
- **Duplicate `Cache-Control` on `/sw.js`.** Two values are sent, on the live stack too, so this
  predates AA1. Also recorded in AA6.
- **AA4:** if it adds `X-Robots-Tag` (noindex, D7 (a)), it belongs in the `(seguridad)` snippet so
  Caddy-generated errors carry it too.

## 7. Cold review amendments (PASS-WITH-AMENDMENTS)

| Finding | Amendment |
| ------- | --------- |
| R1 (P1) Caddy-generated errors skipped the headers | Snippet `(seguridad)` imported in the site and in a new `handle_errors`; verified on the 404, the 502 and the Astro 404 page |
| R2 (P1) The enforcement recipe could not work | §4 rewritten: one owner for `script-src`, paths (a) and (b), Astro CSP flagged as experimental |
| R3 (P1) Public-port box ticked without :18080 evidence | §3 and §8: met on the throwaway proxy; :18080 waits for the owner's rollout curl |
| R4 (P2) Rollout restart claim | §5: reload fails, restart or recreate works; proxy-only command kept |
| R5 (P2) Inaccurate backlog | §4: 7 distinct scripts, 4 by TTOD; `'report-sample'` added |
| R6 (P2) Shallow gate | Gate checks `/health`, the API, an API 404 and a Caddy 404, with no `Server`. Disclosed: amended during the phase |
| R7 (P2) Wording and a dead token | Report-only attributed to AA1's contract; `interest-cohort` dropped |
| R8 (P2) No owner for enforcement | AA6 rows for CSP enforcement and the `/sw.js` duplicate |

## 8. Acceptance

- [x] Headers present on HTML responses **through a proxy running this Caddyfile on the live
  network** (gate, curl). On public port :18080 after the owner's rollout curl (§5).
- [x] API JSON still usable; no CORS invented (gate).
- [x] Cold review: nothing breaks Astro assets or the service worker (smoke: 0 errors, 0 failed
  requests, service worker 8/8; the reviewer re-ran it and agreed). The CSP is report-only, so it
  blocks nothing.
