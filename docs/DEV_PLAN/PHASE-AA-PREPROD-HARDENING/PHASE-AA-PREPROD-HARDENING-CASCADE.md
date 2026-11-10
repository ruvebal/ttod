# Technical director — Phase AA Pre-production hardening (AA0–AA6, incl. AA3b)

**Status:** IN PROGRESS · AA0 DONE, AA5 lane A DONE (2026-11-10) · drafted 2026-11-10 from live audit · **amended same day** (backend+frontend deep audits → F22–F48; owner walkthrough → F49–F58, [LOCATORS.md](LOCATORS.md), new phase AA3b).  
**Evidence:** [FINDINGS-2026-11-10.md](FINDINGS-2026-11-10.md) · **Why:** [RATIONALE.md](RATIONALE.md) · **Students:** [ASSIGNMENTS.md](ASSIGNMENTS.md) · **URL contract:** [LOCATORS.md](LOCATORS.md)  
**Depends on:** Phase Z DONE on `main`. **Does not supersede:** Phase T (public release).

## Programme (do not invert)

| Step | File | Deliverable | Gate |
| ---- | ---- | ----------- | ---- |
| 0 | [PHASES/AA0-assignment-cut-and-freeze.md](PHASES/AA0-assignment-cut-and-freeze.md) | Freeze student vs instructor ownership; owner decisions D1–D7 (slash, keys, graph IA, header, user scope, search, PAT/index); freeze LOCATORS; re-probe F1–F58; UX baselines; authorize code phases | READY until authorized; DONE when `PHASE-AA0-REPORT.md` cites assignment cut + live re-probe |
| 1 | [PHASES/AA1-caddy-security-headers.md](PHASES/AA1-caddy-security-headers.md) | Caddy `header` block: frame denial, referrer, permissions, nosniff; CSP report-only first (F1) | BLOCKED until AA0 DONE; DONE when `curl -sI` shows headers + cold review |
| 2 | [PHASES/AA2-auth-throttle-and-fallback.md](PHASES/AA2-auth-throttle-and-fallback.md) | Throttles (F3/F20); signed fallback off (F4); PAT (F5); **COOKIE_SECURE** (F22); **allowedDomains** (F23); oracle auth + dual-write propose (F24/F26) | BLOCKED until AA1 DONE; DONE when abuse/auth tests green + cookie/Host LAN story documented |
| 3 | [PHASES/AA3-nav-a11y-and-url-hygiene.md](PHASES/AA3-nav-a11y-and-url-hygiene.md) | **Classic header** (F56) + account entry (F7) + anchor offset (F58); a11y (F9–F12, F38); graph i18n (F32); **library layout** (F53); **User section UI** (F55); account shell polish (F33–F37) | BLOCKED until AA0 DONE; **may parallel AA1/AA2/AA3b**; DONE when screenshot strip + live HTML inventory + a11y/CLS vs AA0 baseline pass |
| 3b | [PHASES/AA3b-locators-wisdom-and-graph-ia.md](PHASES/AA3b-locators-wisdom-and-graph-ia.md) | Locator contract: slash policy (F8); wisdom ids + search + task-first order (F49/F50); landing chapter deep links (F51); **3D graph where the header points** (F52); language switch + real 404 (F57); figures guard (F54) | BLOCKED until AA0 DONE (LOCATORS frozen); may start parallel to AA3; **VERIFYING needs AA3 A31 merged**; DONE when LOCATORS registry test + live curl probe pass |
| 4 | [PHASES/AA4-seo-robots-and-meta.md](PHASES/AA4-seo-robots-and-meta.md) | robots/sitemap (F14); og/canonical/hreflang (F15); quote meta (F41); PWA honesty (F42–F44) | BLOCKED until AA3 + AA3b DONE; DONE when public files + head/manifest evidence (canonical/hreflang from LOCATORS) |
| 5 | [PHASES/AA5-container-and-deploy-ops.md](PHASES/AA5-container-and-deploy-ops.md) | **Proposal bind mount (F25)**; **health 503 on Redis down (F27)**; secrets/rebuild (F28); maxmemory (F29); Ollama port (F30); USER/healthchecks (F16–F17); TLS story (F2); CI backend tests (F45); Lilith + npm (F18–F19) | **Lane A** (F25/F27/F28) READY after AA0; **lane B** BLOCKED until AA1 DONE; DONE when checklist probes current `main` + recreate keeps proposals |
| 6 | [PHASES/AA6-oracle-quota-and-closeout.md](PHASES/AA6-oracle-quota-and-closeout.md) | Oracle quota (F21); design rubric (F13/F39/F40); FINDINGS disposition F1–F58; Phase T handoff | BLOCKED until AA2+AA3b+AA5 DONE; DONE when every finding closed or deferred with owner |

Parallel after AA0: **AA1 ∥ AA3 ∥ AA3b ∥ AA5-lane-A** allowed; AA2 after AA1 preferred (A34 before A35); AA4 after AA3 + AA3b; AA5 lane B after AA1; AA6 last. `Page.astro` has one owner at a time: AA3 (header). AA3b touches only the language-switch script there.

## Master paste (start / resume)

```text
Implement Phase AA (pre-production hardening) per
docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING/PHASE-AA-PREPROD-HARDENING-CASCADE.md.

## Context
- Evidence: docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING/FINDINGS-2026-11-10.md
- Why: docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING/RATIONALE.md
- Students: docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING/ASSIGNMENTS.md
- URL contract: docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING/LOCATORS.md (frozen in AA0)
- Prior shore: Phase Z DONE — reuse Redis client; do not invent a second store
- Out of scope: mutating ttod.yml; cloud LLM; Postgres; public GitHub release (Phase T);
  claiming HTTPS from Caddyfile alone; publishing Redis host ports; redesigning brand
  (fonts/palette/logo — the AA3 header restyle on existing tokens is IN scope);
  committing unless the human asks

## Programme
Execute the next incomplete phase only (respect parallel rules above).
After each phase: VERIFYING → cold subprocess review → PHASE-AAn-COLD-REVIEW.md →
triage/amend → PHASE-AAn-REPORT.md.
Do not start a dependent phase until its Gate is green. Implementer must not self-certify DONE.

## Hard constraints
- Security headers and rate limits are falsifiable with curl/tests — screenshots alone fail.
- Registration stays always-student; never open self-serve admin.
- Session cookie remains httpOnly; opaque Redis sid preferred; signed fallback off by default in Compose.
- Design changes reuse Equipo visual tokens / shared icons — no new design system.
- Locators follow LOCATORS.md: keys are code, labels are copy; shipped params never renamed; no corpus count hardcoded.
- UX claims carry a number (CLS, Lighthouse a11y, test) against the AA0 baseline, not screenshots alone.
- Keep Phase T separate: AA closes classroom-host readiness, not partner-demo release.
```

## Layer map

| Layer | Owner phase | Findings |
| ----- | ----------- | -------- |
| Edge headers / TLS story | AA1, AA5 | F1, F2 |
| Auth abuse + cookies + Host + oracle gate + password API | AA2 | F3–F5, F20, F22–F24, F26, F55 (API) |
| Shell header / a11y / graph i18n / account + library UX | AA3 | F7, F9–F12, F32–F38, F53, F55 (UI), F56, F58 |
| Locators / wisdom usability / graph IA / lang switch | AA3b | F8, F49–F52, F54, F57 |
| SEO / PWA honesty | AA4 | F14, F15, F41–F44 |
| Permanence / health / containers / CI | AA5 | F6, F16–F19, F25, F27–F31, F45–F48 |
| Oracle quota + visual closeout | AA6 | F13, F21, F39, F40 |

## Closing protocol

`BLOCKED → READY → IN_PROGRESS → VERIFYING → COLD_REVIEW → DONE`

Cold review: fresh `cascade-cold-reviewer` / Task; output `PHASE-AAn-COLD-REVIEW.md`.  
Amend on surprise: same commit as report — orchestrator + FINDINGS + ASSIGNMENTS + downstream phases.

## Resume rule

Enum: `BLOCKED | READY | IN_PROGRESS | VERIFYING | COLD_REVIEW | PARTIAL | DONE`

- **DONE** → next eligible phase · **PARTIAL** → finish current · **IN_PROGRESS** → resume, do not advance  
- **VERIFYING** → finish suite/probes → cold review · **COLD_REVIEW** → triage → DONE or back to IN_PROGRESS  
- **BLOCKED** → named blocker · **READY** → start (one IN_PROGRESS per sequential lane; AA1∥AA3∥AA3b∥AA5-A OK)

## Relation to students and Phase T

- [ASSIGNMENTS.md](ASSIGNMENTS.md) is the teaching cut of FINDINGS — AA0 freezes who owns what.
- Phase T RC* gates remain independent; AA evidence may *inform* RC trust-boundary work but does not mark RC DONE.
