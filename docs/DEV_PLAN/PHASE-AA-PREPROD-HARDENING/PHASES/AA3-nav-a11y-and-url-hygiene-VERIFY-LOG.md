# Verify log — PHASES/AA3-nav-a11y-and-url-hygiene.md

**Run by:** cascade-harness.sh (runner process, not the implementing session)
**Worktree:** /Users/ruvebal/src/ttod-PHASE-AA-PREPROD-HARDENING-3
**Commit:** 709f590e8f036975a5b12ee895cc9b6be00c566b
**Started:** 2026-11-11T14:21:47Z

```
contract tests: Tests  56 passed
frontend suite: Tests  269 passed
live: signed-out header (Entrar, no Library, prefix current, one main#ttod-main), signed-in header, profile name, password change e2e, library card, localized 403, logout attrs
csp /es/               4 (AA1 /es/: 4)
csp /es/wisdom/        3 (AA1 /es/wisdom/: 3)
csp /es/login/         3 (AA1 /es/login/: 3)
csp /es/oracle/        5 (AA1 /es/oracle/: 5)
csp /en/docs/          3 (AA1 /en/docs/: 3)
csp /es/graph/plano/   5 (AA1 /es/graph/: 5)
AA3 browser checks passed: header geometry 390/768/1440, disclosure menu, skip link, anchors, reduced motion, Spanish 2D graph, CSP ≤ AA1
csp /es/                   4 (AA1 /es/: 4)
csp /es/wisdom/            3 (AA1 /es/wisdom/: 3)
csp /es/wisdom/wis-034/    3 (AA1 /es/wisdom/wis-034/: 3)
csp /es/graph/             5 (AA1 /es/graph/path/: 6)
csp /es/graph/plano/       5 (AA1 /es/graph/: 5)
csp /es/graph/code/        6 (AA1 /es/graph/path/: 6)
browser checks passed: handscroll hash at 390/1440 (+reduced motion), chapters, scroll writer, volumes, paged quote, copy-link, language switch, graph from/to/node, CSP ≤ AA1
/es/           a11y 100 CLS 0.0130 LCP 5117 (AA0 /es/: 100 / 0.0130 / 5047)
/es/wisdom/    a11y 100 CLS 0.0000 LCP 2336 (AA0 /es/wisdom/: 100 / 0.0000 / 2330)
/es/graph/     a11y 100 CLS 0.0003 LCP 2404 (AA0 /es/graph/path: 100 / 0.0003 / 4959)
live (isolated ttod_aa3gate): signed-out/in HTML, account e2e, browser checks, AA3b anchors, AA0 UX rule
AA3 exit gate passed: classic header, account and library UX, Spanish 2D graph, shell a11y hygiene.
```

**Exit code:** 0
**Verdict:** exit-gate PASSED. Eligible for VERIFYING -> COLD_REVIEW.
**Reminder:** the runner does not flip status to DONE. A separate verifier session must review before promotion.
