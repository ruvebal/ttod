# Verify log — PHASES/AA2-auth-throttle-and-fallback.md

**Run by:** cascade-harness.sh (runner process, not the implementing session)
**Worktree:** /Users/ruvebal/src/ttod-PHASE-AA-PREPROD-HARDENING-2
**Commit:** 328cb760e8e7b78ec0997b68f64fce88d209c09b
**Started:** 2026-11-10T19:58:31Z

```
tests 'throttle_register': 1 passed
tests 'throttle_login': 2 passed
tests 'throttle_proposal': 1 passed
tests 'signed_fallback_off': 2 passed
tests 'pat_denylist': 4 passed
tests 'oracle_requires_session': 2 passed
tests 'oracle_propose_dual_write': 2 passed
tests 'password_change': 7 passed
tests 'session_index': 3 passed
live (isolated ttod_aa2gate): LAN login 303, no Secure on HTTP (spoof-proof), oracle 401, register burst 429
AA2 exit gate passed: throttles, fallback off, PAT denylist, oracle auth + dual-write, password API, cookie/Host wiring.
```

**Exit code:** 0
**Verdict:** exit-gate PASSED. Eligible for VERIFYING -> COLD_REVIEW.
**Reminder:** the runner does not flip status to DONE. A separate verifier session must review before promotion.
