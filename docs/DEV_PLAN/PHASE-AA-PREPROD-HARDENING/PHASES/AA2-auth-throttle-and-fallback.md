# PHASE-AA2: Auth throttle, cookies, Host allowlist, oracle gate

> **Track:** accounts + oracle shore — F3–F5, F20, F22–F24, F26, F55 (API) · A2–A5, A16–A19, A34.  
> **Status:** BLOCKED until AA1 DONE (preferred; AA0 minimum) · AA0 O1 closed 2026-11-10: PATs follow the React authentication lesson (short expiry + `jti` denylist; see PHASE-AA0-REPORT §1)

**Exit gate:** [`AA2-auth-throttle-and-fallback.exit-gate.sh`](AA2-auth-throttle-and-fallback.exit-gate.sh). Read it first: it names the backend tests (`throttle_*`, `signed_fallback_off`, `pat_denylist`, `oracle_*`, `password_change`, `session_index`) and frontend tests it runs, and checks LAN login, cookie Secure, a 429 burst and oracle 401 on an isolated stack (`scripts/isolated-stack.sh`).

## Goal

Abuse budgets on register/login/proposal-create; signed-cookie fallback **off by default**; PAT disposition; **cookie Secure from real TLS signal** (not bare `PROD`); **Astro allowedDomains from env**; authenticate oracle stream/propose and route propose through **dual-write**; **change-password + profile endpoints** with a per-user session index (F55), which the AA3 User section consumes.

## Deliverables

- Redis-backed throttle (Phase Z client).
- `TTOD_ALLOW_SIGNED_SESSION_FALLBACK=0` default; PAT code or policy.
- `COOKIE_SECURE` / `PUBLIC_HTTPS` (or equivalent) wiring in login/register.
- Env-driven `allowedDomains` (document required hosts for LAN/classroom).
- Oracle routes: auth dependency + `DualWriteProposalDraftStore` for propose.
- **F55 API (A34):** `POST /api/v1/auth/password` `{current_password, new_password, revoke_others=true}`:
  `require_session`; bcrypt-verify current (constant-time, same 401 text as login); same length rules as
  register (`password_fits_bcrypt`); shares the F3 throttle bucket keyed by user id; on success rotate the
  caller's sid and revoke the others. Needs a **per-user session index** `ttod:user:{id}:sessions` (Redis SET, sids
  added on `issue_session`, removed on logout/expiry-sweep; memory store mirrors it). Optional
  `PATCH /api/v1/auth/profile {display_name}` (trimmed, 1–40 chars, no markup) and `display_name` added to `AuthUser`.
  No email change, no reset-by-email (no mail transport in Compose).
- Tests: 429, fallback-off, unauth oracle rejected, dual-write index hit; password change → old password fails,
  new succeeds, other sid 401, caller stays signed in; wrong current → 401 and counted by the throttle.
- `PHASE-AA2-REPORT.md` + cold review.

## Scope

**In:** backend auth/proposals/oracle; frontend cookie + `astro.config` allowlist.  
**Out:** Captcha SaaS; Postgres; always-student rule change; proposal **bind mount** (AA5 / F25).

## Prompt (Implementation Agent)

```text
Implement PHASE-AA2 per
docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING/PHASES/AA2-auth-throttle-and-fallback.md.

## Deliver
1. Rate-limit register + login (+ proposal POST); 429.
2. Signed session fallback default-off.
3. PAT denylist per AA0 D7 (b): `jti` claim, `ttod:pat:deny:{jti}` with TTL = remaining life; logout-all and password change write it.
4. Cookie Secure from explicit env / forwarded proto — not import.meta.env.PROD alone.
5. allowedDomains from env; document classroom Host values.
6. Auth-gate oracle stream + propose; propose via DualWriteProposalDraftStore.
7. POST /auth/password (+ optional PATCH /auth/profile) with per-user session index; revoke others.
8. Tests + cold review. Do NOT mark DONE yourself.

## Constraints
- Reuse redis_client. Always-student register. No ttod.yml. No commit unless asked.
```

## Acceptance

- [ ] Rapid register/login → 429.
- [ ] Fallback off + missing sid → unauthenticated.
- [ ] Non-PROD-secure story documented; LAN HTTP can set cookies when Secure=false.
- [ ] A browser on a configured non-localhost host can POST login/register: the matching **Host + Origin** pair returns non-403. Astro decides on the Origin header (AA0 probe-amend.log: today the LAN pair gets 403).
- [ ] Unauthenticated oracle stream/propose rejected; dual-write path used.
- [ ] Password change revokes other sessions; wrong current password throttled; `display_name` round-trips if PATCH shipped.
- [ ] Cold review green or amended.

## Risks

- Throttle-by-IP behind proxy → document `X-Forwarded-For` trust.
- Dual-write without AA5 bind mount still loses disk on recreate. A19 VERIFYING needs AA5 lane A (I7/F25) merged.
- Session index drift: sids that expire by TTL stay in the SET. Prune on read (drop members whose `ttod:session:{sid}` is gone), with no cron.
