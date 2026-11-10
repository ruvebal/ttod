# Verify log — PHASES/AA2-auth-throttle-and-fallback.md

**Run by:** cascade-harness.sh (runner process, not the implementing session)
**Worktree:** /Users/ruvebal/src/ttod-PHASE-AA-PREPROD-HARDENING-2
**Commit:** 712f24c4cc74008ff67adb92d29f17610933c1f9
**Started:** 2026-11-10T19:55:49Z

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
AA2 GATE FAIL: isolated register returned 429
```

**Exit code:** 1
**Verdict:** exit-gate FAILED. Do not promote. Return the phase to IN_PROGRESS.
