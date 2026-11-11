# Verify log — PHASES/AA7-astro-major-upgrade.md

**Run by:** cascade-harness.sh (runner process, not the implementing session)
**Worktree:** /Users/ruvebal/src/ttod-PHASE-AA-PREPROD-HARDENING-7
**Commit:** 70ab6b8d1517a25726dc21b532d392ad9f17fdbe
**Started:** 2026-11-11T19:11:04Z

```
astro 7.4.11, @astrojs/node 11.1.12
npm audit --omit=dev: {'info': 0, 'low': 3, 'moderate': 2, 'high': 0, 'critical': 0, 'total': 5}
frontend: suite, check, build, PWA guard green
--- re-running AA1-caddy-security-headers
AA1 exit gate passed: headers on HTML, CSP report-only, JSON/assets/SW intact, scope caddy+docs.
--- re-running AA2-auth-throttle-and-fallback
live (isolated ttod_aa2gate): LAN login 303, no Secure on HTTP (spoof-proof), Secure when forced, spoofed-XFF login burst throttled, oracle 401, register 429 by request 6
AA2 exit gate passed: throttles, fallback off, PAT denylist, oracle auth + dual-write, password API, cookie/Host wiring.
--- re-running AA3b-locators-wisdom-and-graph-ia
contract tests: Tests  47 passed
frontend suite: Tests  274 passed
live registry probe: statuses, 301 Locations, ids, en/es parity, slash hrefs, search = corpus fold, twins, graph IA
csp /es/                   4 (AA1 /es/: 4)
csp /es/wisdom/            3 (AA1 /es/wisdom/: 3)
csp /es/wisdom/wis-034/    3 (AA1 /es/wisdom/wis-034/: 3)
csp /es/graph/             5 (AA1 /es/graph/path/: 6)
csp /es/graph/plano/       5 (AA1 /es/graph/: 5)
csp /es/graph/code/        6 (AA1 /es/graph/path/: 6)
/es/             a11y 100 CLS 0.0130 LCP 5121 (AA0 /es/: 100 / 0.0130 / 5047)
/es/wisdom/      a11y 100 CLS 0.0000 LCP 2336 (AA0 /es/wisdom/: 100 / 0.0000 / 2330)
/es/graph/       a11y 100 CLS 0.0003 LCP 2717 (AA0 /es/graph/path: 100 / 0.0003 / 4959)
/es/graph/plano/ (new baseline) a11y 100 CLS 0.0984 LCP 2263
live (isolated ttod_aa3bgate): registry probe, browser checks, AA0 UX rule
AA3b exit gate passed: slash policy, wisdom ids/search/filters, landing chapters, graph IA, language switch, F54 guard.
--- re-running AA3-nav-a11y-and-url-hygiene
contract tests: Tests  58 passed
frontend suite: Tests  274 passed
live: signed-out header (Entrar, no Library, prefix current, one main#ttod-main), signed-in header, profile name, password change e2e, library card, localized 403, logout attrs
csp /es/               4 (AA1 /es/: 4)
csp /es/wisdom/        3 (AA1 /es/wisdom/: 3)
csp /es/login/         3 (AA1 /es/login/: 3)
csp /es/oracle/        5 (AA1 /es/oracle/: 5)
csp /en/docs/          3 (AA1 /en/docs/: 3)
csp /es/graph/plano/   5 (AA1 /es/graph/: 5)
csp /es/                   4 (AA1 /es/: 4)
csp /es/wisdom/            3 (AA1 /es/wisdom/: 3)
csp /es/wisdom/wis-034/    3 (AA1 /es/wisdom/wis-034/: 3)
csp /es/graph/             5 (AA1 /es/graph/path/: 6)
csp /es/graph/plano/       5 (AA1 /es/graph/: 5)
csp /es/graph/code/        6 (AA1 /es/graph/path/: 6)
/es/           a11y 100 CLS 0.0130 LCP 5122 (AA0 /es/: 100 / 0.0130 / 5047)
/es/wisdom/    a11y 100 CLS 0.0000 LCP 2344 (AA0 /es/wisdom/: 100 / 0.0000 / 2330)
/es/graph/     a11y 100 CLS 0.0003 LCP 4658 (AA0 /es/graph/path: 100 / 0.0003 / 4959)
live (isolated ttod_aa3gate): signed-out/in HTML, account e2e, browser checks, AA3b anchors, AA0 UX rule
AA3 exit gate passed: classic header, account and library UX, Spanish 2D graph, shell a11y hygiene.
--- re-running AA5-container-and-deploy-ops
live (isolated ttod_aa5gate): non-root (backend/frontend/mcp), drafts written, frontend+mcp healthy, maxmemory+noeviction, request id end to end, https login untrusted='403 plain' trusted='303 secure', recreate kept drafts, health 503 on Redis down
AA5 exit gate passed: lane A (bind, health 503, secrets) and lane B (non-root, health checks, pins, maxmemory, CI backend suite, request ids, TLS proxy trust, docs).
AA7 exit gate passed: Astro 7, clean production audit, and the AA1/AA2/AA3b/AA3/AA5 guarantees re-proven.
```

**Exit code:** 0
**Verdict:** exit-gate PASSED. Eligible for VERIFYING -> COLD_REVIEW.
**Reminder:** the runner does not flip status to DONE. A separate verifier session must review before promotion.
