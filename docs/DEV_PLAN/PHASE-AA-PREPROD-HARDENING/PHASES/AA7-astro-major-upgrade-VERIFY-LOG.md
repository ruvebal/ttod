# Verify log — PHASES/AA7-astro-major-upgrade.md

**Run by:** cascade-harness.sh (runner process, not the implementing session)
**Worktree:** /Users/ruvebal/src/ttod-PHASE-AA-PREPROD-HARDENING-7
**Commit:** dfb56d0fdf1a354966a200519c5a7de01d2b3452
**Started:** 2026-11-11T18:30:52Z

```
astro 7.4.11, @astrojs/node 11.1.12
npm audit --omit=dev: {'info': 0, 'low': 3, 'moderate': 2, 'high': 0, 'critical': 0, 'total': 5}
frontend: suite, check, build, PWA guard green
--- re-running AA2-auth-throttle-and-fallback
AA2 exit gate passed: throttles, fallback off, PAT denylist, oracle auth + dual-write, password API, cookie/Host wiring.
--- re-running AA3b-locators-wisdom-and-graph-ia
registry: 15 pages, 11 redirects, 4 not-found, 5 exempt
contract tests: Tests  45 passed
frontend suite: Tests  271 passed
F54 mutation: literal counts in ValleSigue, /es/ and /en/ each fail the fixture test
live registry probe: statuses, 301 Locations, ids, en/es parity, slash hrefs, search = corpus fold, twins, graph IA
AA3b GATE FAIL: off-site redirect: //evil.example/x → Location: /evil.example/x/ (open redirect)
AA7 GATE FAIL: AA3b-locators-wisdom-and-graph-ia exit gate fails on Astro 7
```

**Exit code:** 1
**Verdict:** exit-gate FAILED. Do not promote. Return the phase to IN_PROGRESS.
