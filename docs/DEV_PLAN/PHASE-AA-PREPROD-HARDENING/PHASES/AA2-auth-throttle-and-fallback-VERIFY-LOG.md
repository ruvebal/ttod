# Verify log — PHASES/AA2-auth-throttle-and-fallback.md

**Run by:** cascade-harness.sh (runner process, not the implementing session)
**Worktree:** /Users/ruvebal/src/ttod-PHASE-AA-PREPROD-HARDENING-2
**Commit:** 23abfc339d61b81c16a4bb380cd5e541594576c5
**Started:** 2026-11-10T20:14:48Z

```
tests 'throttle_register': 1 passed
tests 'throttle_login': 3 passed
tests 'throttle_proposal': 1 passed
tests 'signed_fallback_off': 2 passed
tests 'pat_denylist': 4 passed
tests 'oracle_requires_session': 2 passed
tests 'oracle_propose_dual_write': 3 passed
tests 'password_change': 9 passed
tests 'session_index': 3 passed
live (isolated ttod_aa2gate): LAN login 303, no Secure on HTTP (spoof-proof), Secure when forced, spoofed-XFF login burst throttled, oracle 401, register 429 by request 6
AA2 exit gate passed: throttles, fallback off, PAT denylist, oracle auth + dual-write, password API, cookie/Host wiring.
```

**Exit code:** 0
**Verdict:** exit-gate PASSED. Eligible for VERIFYING -> COLD_REVIEW.
**Reminder:** the runner does not flip status to DONE. A separate verifier session must review before promotion.
