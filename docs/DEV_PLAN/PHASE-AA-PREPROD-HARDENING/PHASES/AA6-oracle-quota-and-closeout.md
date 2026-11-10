# PHASE-AA6: Oracle quota and cascade closeout

> **Track:** oracle + visual + programme close — F13, F21, F39, F40 · A14–A15, A29–A30.  
> **Status:** BLOCKED until AA2, AA3b and AA5 (both lanes) DONE

## Goal

Classroom Redis budget on Oracle/SSE (auth already AA2); design QA rubric + graph token retune + single token source; close or defer **F1–F58**; hand evidence to Phase T without claiming Phase T DONE.

## Deliverables

- Oracle/SSE quota middleware (Redis); tests.
- Design QA rubric; graph palette vs tokens; token-layer audit.
- `PHASE-AA6-REPORT.md` disposition table for F1–F58.
- Optional dated completeness note.
- **Follow-ups carried from AA1** (dispose of each: done, scheduled with an owner, or explicitly deferred):
  - **CSP enforcement.** Give `script-src` one owner (Astro's per-page hashes, or TTOD's 4 inline scripts moved to modules), switch Caddy to `Content-Security-Policy`, browser smoke at 0 violations, and bump the service worker cache so cached pages drop the old policy (PHASE-AA1-REPORT §4).
  - **Duplicate `Cache-Control` on `/sw.js`.** Present before AA1; pick one rule (PHASE-AA1-REPORT §6).
- Whole-cascade cold review.

## Scope

**In:** oracle quota, visual checklist, FINDINGS ledger close.  
**Out:** New models; cloud inference; Phase T RC execution.

## Prompt (Implementation Agent)

```text
Implement PHASE-AA6 per
docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING/PHASES/AA6-oracle-quota-and-closeout.md.

## Deliver
1. Per-user/IP Redis quota on oracle SSE; 429; test (assumes AA2 auth gate).
2. Design QA rubric; retune graph colors; resolve dual token layers.
3. Walk F1–F58: closed with evidence or deferred with named owner.
4. Phase AA ≠ Phase T. Whole-cascade cold review. Do not self-certify DONE.

## Constraints
- Local Ollama only. No ttod.yml. No commit unless asked.
```

## Acceptance

- [ ] Oracle abuse → 429 under synthetic load.
- [ ] Design rubric linked; F39/F40 disposed.
- [ ] F1–F58 disposition complete; no silent won’t-fix.
- [ ] Cold review accepts closeout or lists amends.

## Risks

- Quota too tight for demos — env-tunable defaults.
