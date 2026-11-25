# Verify log — PHASES/AA3b-locators-wisdom-and-graph-ia.md

**Run by:** cascade-harness.sh (runner process, not the implementing session)
**Worktree:** /Users/ruvebal/src/ttod-PHASE-AA-PREPROD-HARDENING-3b
**Commit:** cdb339cb51cea439378342ce07549cb4decb93c8
**Started:** 2026-11-11T12:10:46Z

```
registry: 15 pages, 11 redirects, 4 not-found, 5 exempt
contract tests: Tests  44 passed
frontend suite: Tests  239 passed
F54 mutation: literal counts in ValleSigue, /es/ and /en/ each fail the fixture test
live registry probe: statuses, 301 Locations, ids, en/es parity, slash hrefs, search = corpus fold, twins, graph IA
no off-site Location for //host, ///host, /\host
csp /es/                   4 (AA1 /es/: 4)
csp /es/wisdom/            3 (AA1 /es/wisdom/: 3)
csp /es/wisdom/wis-034/    3 (AA1 /es/wisdom/wis-034/: 3)
csp /es/graph/             5 (AA1 /es/graph/path/: 6)
csp /es/graph/plano/       5 (AA1 /es/graph/: 5)
csp /es/graph/code/        6 (AA1 /es/graph/path/: 6)
browser checks passed: handscroll hash at 390/1440 (+reduced motion), chapters, scroll writer, volumes, paged quote, copy-link, language switch, graph from/to/node, CSP ≤ AA1
/es/             a11y 100 CLS 0.0130 LCP 5120 (AA0 /es/: 100 / 0.0130 / 5047)
/es/wisdom/      a11y 100 CLS 0.0000 LCP 2337 (AA0 /es/wisdom/: 100 / 0.0000 / 2330)
/es/graph/       a11y 100 CLS 0.0003 LCP 4811 (AA0 /es/graph/path: 100 / 0.0003 / 4959)
/es/graph/plano/ (new baseline) a11y 100 CLS 0.4702 LCP 2426
live (isolated ttod_aa3bgate): registry probe, browser checks, AA0 UX rule
AA3b exit gate passed: slash policy, wisdom ids/search/filters, landing chapters, graph IA, language switch, F54 guard.
```

**Exit code:** 0
**Verdict:** exit-gate PASSED. Eligible for VERIFYING -> COLD_REVIEW.
**Reminder:** the runner does not flip status to DONE. A separate verifier session must review before promotion.
