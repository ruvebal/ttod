<!--
AA1 cold review: Caddy security headers (F1 / A1). Reviewer: cascade cold reviewer (agent), 2026-11-10.
Reviewed: git diff HEAD~2 HEAD on cascade/PHASE-AA-PREPROD-HARDENING-1 (e5468bc5 + f9d6447a).
The reviewer does not mark DONE; the product owner triages.
-->

# PHASE-AA1 cold review: Caddy security headers

**Verdict: PASS-WITH-AMENDMENTS.** The header block is correct for every proxied response, and it
breaks nothing. Verified: pages, API, SSE stream, service worker, fonts and manifest. The CSP
report-only target is sound. Three P1s need fixing before DONE: a false "every response" claim,
an enforcement recipe that would not work, and an Acceptance box ticked without public-port
evidence.

## What I ran (live stack `ttod_oracle` untouched; all probe containers removed)

| Check | Command | Result |
| --- | --- | --- |
| Exit gate | `bash PHASES/AA1-caddy-security-headers.exit-gate.sh` | `AA1 exit gate passed …`, exit 0 (matches VERIFY-LOG) |
| Browser smoke | `node baselines/aa1-2026-11-10/browser-smoke.mjs http://127.0.0.1:28090 <scratch>` | 8×200, XFO=DENY, cspRO, SW 8/8, 0 errors, 0 failed, violations 4/3/3/5/6/5/3/3 = 32. Same as `browser-smoke-after.json` |
| Route coverage (probe on live network, :28090) | `curl -D -` on `/health`, `/api/v1/wisdom/sample`, `/api/v1/nonexistent` (404), `/es/this-does-not-exist/` (404), `/sw.js`, `/site.webmanifest`, `/visual-system/fonts/nope.woff2` | All five headers present on each, plus 404s from Astro and FastAPI |
| Caddy-originated errors | `/project-docs/x` (file_server 404); `/es/`, `/health` on a probe **not** joined to the network (502) | **No security headers; `Server: Caddy` present** (see R1) |
| Oracle stream | `curl -sN -X POST /api/v1/oracle/stream` via the probe | `200 text/event-stream`, no `Content-Encoding`, 70 separate reads: the drip survives the deferred header wrapper |
| Header precedence | `grep -rn -i 'x-frame\|content-security\|referrer-policy\|permissions-policy\|nosniff' services/backend services/frontend/src` | No upstream sets any of these; `-Server` makes the block deferred, so Caddy's values would win anyway |
| Pre-fix gate would fail | live `curl -sI :18080/es/` (`curl-evidence.log:3-7`) | No `X-Frame-Options`, so gate step 2 fails |
| Scope | `git diff --name-only $(git merge-base HEAD origin/main) HEAD` | `caddy/Caddyfile` + 6 files under `docs/` only. No HSTS, `auto_https off` unchanged |
| Rollout command | `cd ~/src/ttod && docker compose --dry-run up -d --force-recreate reverse-proxy` | Only `reverse-proxy-1 Recreate`; deps stay `Running` |
| Bind-mount claim | throwaway container, single-file bind, `mv` new file over it, then `docker restart` | Running container: `cat: can't open '/f'`. After `docker restart`: new content (see R4) |

## Findings

| ID | Sev | Blocks DONE | Evidence | Fix |
| --- | --- | --- | --- | --- |
| R1 | P1 | amend first | `caddy/Caddyfile:6` says the headers apply "a toda respuesta", and `PHASE-AA1-REPORT.md:14` says "every response". The block is deferred (because of `-Server`, `Caddyfile:23`). Errors that Caddy itself raises skip it: `/project-docs/x` gives `404` with only `Server: Caddy`; upstream down gives `502` with only `Server: Caddy`. So `-Server` does not hold there either, which contradicts `REPORT.md:24`. Low exposure (empty bodies), but the claim is false. | Move the block into a snippet `(seguridad) { header { … } }`. Use `import seguridad` in the site, and add `handle_errors { import seguridad; respond "{err.status_code} {err.status_text}" {err.status_code} }`. I validated this on `caddy:2.10-alpine`: the 502 and the file_server 404 then carry XFO + nosniff and no `Server`. Add a gate check on a Caddy-originated 404 (`/project-docs/__aa1_missing__`). |
| R2 | P1 | amend first | `REPORT.md:74-77`: "hashes … Astro's built-in CSP support … then CSP-RO becomes CSP with the same directives plus the hashes". Caddy sends one static header for every page. Astro's CSP (`experimental.csp` in Astro 5; `package.json:25` `^5.13.5`, installed 5.18.2) puts per-page, per-build hashes in a `<meta>` policy. If both are enforced, the header's `script-src 'self'` still blocks every inline script, hashes in the meta or not. Hand-copying hashes into the Caddyfile breaks on every build that touches those scripts. | Rewrite the enforcement section so `script-src` has **one** owner. Either (a) at enforcement, Caddy drops `script-src` from its header and Astro's meta carries it, while Caddy keeps frame/object/base/form/connect (this is not "meta as the only fix", which the contract rules out), or (b) move TTOD's own inline scripts into external modules (see R5) so only Astro's version-stable island runtime needs hashing. Say that Astro 5's CSP is experimental. |
| R3 | P1 | amend first | `REPORT.md:101` ticks "Headers present on HTML responses **from the public port**". The only public-port evidence is the **before** capture (`curl-evidence.log:3-7`). The after evidence comes from :28081, and the gate runs on :28080. The public port cannot pass until the owner rolls out, because the phase may not reload the stack. | Reword the box: "met on a throwaway proxy running the identical Caddyfile on the live network; public-port :18080 confirmation = rollout curl (`REPORT.md:93`), owner step". The owner then decides whether DONE waits for that curl. |
| R4 | P2 | no | `REPORT.md:87-88`: "a reload or restart is not enough". Measured on this host (Docker Desktop): after the inode swap the running container sees **no file**, so a reload fails. `docker restart` sees the new file. `REPORT.md:92` "or: `make rebuild`" runs `up --build -d --force-recreate` on the whole stack (`Makefile:83-86`). That recreates the backend, and F25 says recreate loses container-only proposal files. | Say "reload fails (the old inode is gone inside the container); restart or recreate works". Keep the `--force-recreate reverse-proxy` line (dry-run: only the proxy is recreated). Delete the `make rebuild` alternative. |
| R5 | P2 | no | `REPORT.md:51,70-71`: "32 inline `<script>` … Astro's hydration and page scripts". Hashing every executable inline script on the 8 views gives **7 distinct**. 24 are TTOD's three layout scripts on every page (`[data-pie]` footer, `#ttod-site-header` nav toggle, `#ttod-network-boundary`). 1 is the `/es/` pre-paint `is:inline` script. 7 are Astro island runtime (`Astro.load`, `astro-island`, `client:visible`). All violation `sample` fields in `browser-smoke-after.json` are `""`. | Characterize the backlog as "7 distinct scripts, 4 of them ours". Add `'report-sample'` to `script-src` while it is report-only, so the console and smoke name the script. |
| R6 | P2 | no | The gate checks headers only on `/es/ /en/ /es/wisdom/` (`exit-gate.sh:39-51`). It does not check them on API, `/health` or error responses, so R1 passed unseen. `exit-gate.sh:68` accepts `/sw.js` even though it sends two `Cache-Control` headers (`max-age=0, no-cache` **and** `public, max-age=0`). That duplicate exists before AA1 too (live :18080 shows the same), so it is not AA1's regression. | Add header checks for `/api/v1/wisdom/sample`, `/health` and one Caddy-originated 404. Note the `/sw.js` duplicate as a separate small finding (use `>Cache-Control` or `header_down` to replace instead of add). |
| R7 | P2 | no | `REPORT.md:27-28`: "AA0 authorized report-only first". `PHASE-AA0-REPORT.md` has no CSP decision. Report-only is the contract default (`AA1-caddy-security-headers.md:10`, "unless AA0 authorizes enforce"). `Permissions-Policy` includes `interest-cohort=()` (`Caddyfile:20`), a token for FLoC, which Chrome has retired. It is harmless (no Chrome log entry on `/es/`), but it teaches a dead feature. | "AA0 did not authorize enforcement, so the contract default (report-only) applies." Drop `interest-cohort=()`. |
| R8 | P2 | no | No downstream phase owns CSP enforcement: grep of `PHASES/AA[2-6]*.md`, `ASSIGNMENTS.md` and the cascade file finds no enforce step, so the backlog lives only in this report. The service worker stores full responses, headers included (`services/frontend/public/sw.js:51-52`), so after enforcement, cached and offline pages keep serving the old policy. AA4 may add `X-Robots-Tag` (AA0 D7). | Record "CSP enforcement" as a follow-up row in FINDINGS or AA6's closeout, including "bump the SW cache name in the same change". AA4: if it uses `X-Robots-Tag`, put it in the same block or snippet as R1. |

## Answers to the brief

1. **Header values and safety.** All values are correct and safe for a same-origin, plain-HTTP
   classroom app. The service worker (8/8 registered), the SSE stream (drips, not compressed),
   fonts (`font-src 'self' data:`), the manifest (`/site.webmanifest`, `manifest-src 'self'`,
   same-origin icons) and login/register (same-origin POST, `form-action 'self'`) are all
   unaffected. Coverage is complete for proxied responses and missing on Caddy-originated
   errors (R1).
2. **CSP report-only.** Sending the target policy and logging violations as backlog is sound.
   The target needs no extra directives for current traffic: the oracle stream and SW fetches
   are same-origin under `connect-src 'self'`; `worker-src 'self'` covers `/sw.js`;
   `type="application/json"` data blocks are not subject to `script-src`. The policy itself is
   right. The enforcement recipe (R2) and the description of the 32 violations (R5) are not.
3. **Gate fidelity and rollout.** The gate encodes Acceptance 2 and 3 faithfully. Acceptance 1
   uses a scratch port as a stand-in for the public port (R3), and the gate's coverage is thin
   (R6). The force-recreate rollout works and touches only the proxy. Its explanation is
   partly wrong (R4).
4. **Scope.** Only `caddy/` and `docs/` changed. No HSTS, no HTTPS claim, `auto_https off`
   kept.
5. **Legibility.** The Caddyfile comment block (`:6-16`) and the report's "Why this value" table
   are clear for a student. The XFO-versus-report-only `frame-ancestors` explanation and the
   "no HSTS" line are especially good. Fix the "toda respuesta" claim (R1) and the enforcement
   section (R2), because a student doing A1 follow-up would act on both.
