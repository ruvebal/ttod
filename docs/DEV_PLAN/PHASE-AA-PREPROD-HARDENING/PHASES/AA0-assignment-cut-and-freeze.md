# PHASE-AA0: Assignment cut and freeze

> **Track:** programme — student vs instructor ownership, and the URL contract, before code.  
> **Status:** READY (opens when product owner authorizes Phase AA)

## Goal

Freeze which FINDINGS are student assignments and which are instructor ops. Freeze the
[locator contract](../LOCATORS.md). Re-probe the live stack against
[FINDINGS-2026-11-10.md](../FINDINGS-2026-11-10.md), record UX baselines, and authorize AA1+.

## Owner decisions to record (each one is a line in the report)

| # | Decision | Recommended | Blocks |
| - | -------- | ----------- | ------ |
| D1 | Trailing-slash policy | always-slash + 301 middleware ([LOCATORS §3](../LOCATORS.md#3-trailing-slash)) | AA3b, AA4 |
| D2 | Query/fragment keys | "keys are code, labels are copy"; English for new keys, shipped keys frozen ([§2](../LOCATORS.md#2-keys-are-code-labels-are-copy)) | AA3b |
| D3 | Graph IA (F52) | 3D at `/graph/`, 2D at `/graph/plano/`, code at `/graph/code/`, 301 from `/graph/path` (or the minimal header-link fallback) | AA3b, A20 |
| D4 | Header (F56) | full-width classic bar per [AA3 spec](AA3-nav-a11y-and-url-hygiene.md#header-spec-f56); confirm it counts as a component restyle, not a brand redesign | AA3 |
| D5 | User section scope (F55) | username (`display_name`) + change password + revoke others; **no** email change, **no** reset-by-email | AA2 A34, AA3 A35 |
| D6 | Wisdom search (F49) | SSR `?q=` over the locale corpus; no backend search endpoint | AA3b |
| D7 | PAT policy (F5) and index/noindex (F14) | already listed in AA2/AA4: decide here so students do not | AA2, AA4 |

## Deliverables

- `PHASE-AA0-REPORT.md` affirming or amending [ASSIGNMENTS.md](../ASSIGNMENTS.md) and D1–D7.
- Live re-probe table: headers, TLS, cookie Secure, allowedDomains, proposal volume, `/health` on Redis
  down, register open, robots, graph locale, **slash duplicates (F8), id inventory of `/es/` and
  `/es/wisdom/` (F50/F51), language switch on `/es/wisdom/wis-034/` (F57), header at 390/768/1440 (F56)**.
- **UX baseline** for later "no regression" gates: Lighthouse a11y + CLS + LCP at 390 px on `/es/`,
  `/es/wisdom/`, `/es/graph/path`, plus screenshots of the same views, stored with the report.
- Explicit list: student A1–A40 · instructor I1–I16 · any deferred with owner (**covers F1–F58**).
- Cold review + report.

## Scope

**In:** decisions + FINDINGS/ASSIGNMENTS/LOCATORS/cascade text amendments; measurements.  
**Out:** application code, Compose behavior changes, merging student PRs.

## Prompt (Implementation Agent)

```text
Implement PHASE-AA0 per
docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING/PHASES/AA0-assignment-cut-and-freeze.md.

## Deliver
1. Re-run FINDINGS live probes (curl headers, robots, health, slash duplicates, id inventory,
   language switch on a quote page, sample nav).
2. Record UX baselines (Lighthouse a11y/CLS/LCP at 390 px; screenshots) for /es/, /es/wisdom/, /es/graph/path.
3. Ask the product owner D1–D7; record answers verbatim in PHASE-AA0-REPORT.md. Do not decide them yourself.
4. Freeze the assignment cut (A* vs I*) and any reassignments; freeze LOCATORS.md (status → FROZEN).
5. Confirm Phase T remains separate; AA does not authorize public release.
6. Hand off for cold review — do NOT mark DONE yourself.

## Constraints
- No code/Compose in AA0. Do not commit unless asked.
```

## Acceptance

- [ ] Live probes recorded with dates/commands.
- [ ] Every **F1–F58** mapped to A*, I*, or deferred-with-owner (the 2026-11-10 draft checked only F1–F21, and F48 had no owner. Both are fixed in this amendment and must stay fixed).
- [ ] D1–D7 answered by the owner, not inferred by the agent.
- [ ] UX baselines stored; later phases cite them for "no regression".
- [ ] LOCATORS.md status FROZEN (or amended + frozen).
- [ ] Cold review filed; blocking surprises amend FINDINGS/ASSIGNMENTS same session.

## Risks

- Shipping headers before freezing ownership → students duplicate instructor work. Keep AA0 first.
- Starting AA3b before D1–D3 are frozen → URLs ship twice. The registry is the contract.
