<!--
AA2 report: auth throttle, cookies, Host allowlist, oracle gate, change-password API.
Author: Rubén Vega Balbás PhD (agent-assisted). Status VERIFYING. The agent does not mark DONE.
-->

# PHASE-AA2 report: auth throttle, cookies, Host allowlist, oracle gate

**Status:** VERIFYING · **Branch:** `cascade/PHASE-AA-PREPROD-HARDENING-2` · **Exit gate:**
[`PHASES/AA2-auth-throttle-and-fallback.exit-gate.sh`](PHASES/AA2-auth-throttle-and-fallback.exit-gate.sh)
· **Shared helper:** [`scripts/isolated-stack.sh`](scripts/isolated-stack.sh) (proxy + frontend + backend +
Redis built from the checkout, scratch ports, never `ttod_oracle`; reusable by AA3/AA3b/AA4)

The first commit on this branch carries the downstream amendments from AA1 and AA5 lane A into AA2,
AA3, AA3b, AA4 and AA5 lane B. It is planner work, done before the gate and the code.

## 1. What changed, by finding

| Finding | Change | Where |
| ------- | ------ | ----- |
| **F3 / F20** abuse budgets | Redis fixed-window throttle (memory in tests): login per client IP and per account; register per IP; proposals (form **and** oracle) per user. 429 with `Retry-After`. Every attempt counts, so a correct password cannot reset the counter. Budgets are env-tunable (`TTOD_THROTTLE_*`). Keys are hashed, so no email or IP appears in Redis key names | `app/throttle.py`, `main.py` (`guard`), `config.py` |
| F3, client IP | Login and register reach the backend through Astro's server, so Astro forwards the left-most `X-Forwarded-For` hop (Caddy's value) and the backend trusts it (`TTOD_TRUST_FORWARDED_FOR=1` in Compose; the backend is not published) | `lib/auth.server.ts` (`clientAddressOf`), login/register pages |
| **F4** signed fallback | With a session store, a signed cookie blob is refused unless `TTOD_ALLOW_SIGNED_SESSION_FALLBACK=1`. Logout now always means "delete the session row" | `auth.py` (`read_session`) |
| **F5** PAT revocation (AA0 D7 (b), React authentication lesson) | Every PAT carries a `jti`. Each user's jtis are indexed. `DELETE /api/v1/auth/token` revokes the presented PAT. `POST /api/v1/auth/logout-all` and a password change revoke all of them via `ttod:pat:deny:{jti}` (TTL = PAT TTL). Pre-AA2 PATs without a `jti` are refused; they expire within an hour anyway | `app/revocation.py`, `auth.py`, `main.py` |
| **F22** cookie Secure | `cookieSecure(request)`: `COOKIE_SECURE=auto` (default) is Secure only when the edge saw HTTPS; `true` behind an external TLS proxy; `false` for local HTTP. No longer `import.meta.env.PROD` | `lib/cookie-security.ts`, login/register pages, Compose `COOKIE_SECURE` |
| **F23** allowedDomains | `TTOD_ALLOWED_HOSTS` (comma-separated bare hostnames) extends Astro `security.allowedDomains`. It is a **build-time** value: Dockerfile build arg, Compose `build.args` | `astro.config.mjs`, `Dockerfile`, Compose |
| **F24** oracle unauthenticated | `POST /oracle/stream` and `/oracle/propose` require a session. The terminal shows a localized "sign in to ask" for 401 and "too many requests" for 429. Neither goes to the offline queue, since replaying would fail the same way | `main.py`, `OracleTerminal.tsx` |
| **F26** oracle propose bypassed dual-write | `OracleService.propose` saves through the app's proposal store (dual-write in Compose) and no longer returns `stored_at`, a server path | `oracle.py` |
| **F55 API** (A34) | `POST /api/v1/auth/password`: session required; constant-time check of the current password; same 401 text as login; shares the per-account budget; same length rules as register. On success it rotates the caller's sid and, by default, revokes every other session and every PAT. `PATCH /api/v1/auth/profile {display_name}`: trimmed, 1–40 characters, plain text. `display_name` appears in `AuthUser` only once set, so the login contract is unchanged | `main.py`, `models.py`, `auth.py` |
| F55 session index | `ttod:user:{id}:sessions` (SET, memory mirror). Sids are added on issue and removed on logout. Expired members are pruned on read (`user_sessions`), with no cron | `app/revocation.py`, `auth.py` |

### Defaults chosen, and why

- **Per-IP budgets fit a classroom NAT.** A whole cohort often shares one school address, so the
  defaults are `login-ip` 100 per 5 min and `register-ip` 40 per hour. The **per-account** budget
  (`account`, 10 per 5 min) is what stops password guessing. `proposal-user` is 20 per hour. On a host
  reachable from the internet, tighten them in `.env` (documented in `.env.example`).
- **Throttle storage.** The app uses the Redis versions when it built its own Redis client from
  `REDIS_URL`. An injected client is a test double, so tests use the in-memory versions.

## 2. Evidence

| Check | Result |
| ----- | ------ |
| Contract tests (`services/backend/tests/test_aa2_auth_hardening.py`) | **25 OK**: every name in the gate's contract (throttle ×5, fallback ×2, PAT ×4, oracle ×4, password/profile ×6, session index ×2, Redis backends ×2) |
| Backend suite | **124 OK** (99 before + 25) |
| Root suite (`make test`) | **236 OK** |
| Frontend (`vitest`) | **195 OK** (30 files), including `cookie-security.test.ts` (4) and the new forwarding and 429 tests in `auth.server.test.ts` |
| `astro check` | 0 errors |
| **Live, isolated** (`ttod_aa2gate`, built from this branch) | LAN Host+Origin login (`aa2-gate.lan`) → **303** (signed in; it was 403 in AA0's probe) · HTTP login cookie **not** Secure · spoofed `X-Forwarded-Proto: https` → still not Secure · oracle stream without a session → **401** · register burst → **429** |
| Exit gate (runner) | see the verify log |

### Existing tests that changed, and why

Every one of these is a direct consequence of the findings. None was loosened:

- `support.py`, `test_favorites.py`, `test_review_pipeline.py` minted **signed** sessions with a
  store-less `AuthService`. F4 refuses those now, so the helpers share the app's
  `MemorySessionStore` and issue real, revocable sessions.
- `test_backend.py` (2), `tests/test_r7_platform.py` (2) called the oracle anonymously. Under F24
  they sign in first.
- Two exact-dict asserts on `user` keep passing unchanged, because `display_name` is omitted while
  unset.

## 3. Gate amendments made during the phase (for the cold reviewer)

1. **Cookie Secure live check.** The gate first expected a client-sent `X-Forwarded-Proto: https`
   to produce a Secure cookie. That is wrong for this edge: Caddy overwrites the header from
   untrusted clients. Trusting it would also let any LAN client spoof `X-Forwarded-For` and dodge
   the per-IP throttle. The live check now asserts the opposite, that a spoofed header **cannot**
   make the cookie Secure. The genuine HTTPS path (`COOKIE_SECURE=true`, or a trusted TLS proxy) is
   covered by `cookie-security.test.ts`.
2. **Register burst.** The per-IP defaults were raised to classroom size, so the gate now sets
   `TTOD_THROTTLE_REGISTER_IP=5/3600` for its isolated stack. It tests the mechanism, not the
   default. Compose now passes the `TTOD_THROTTLE_*` variables through to the backend.

3. **The isolated stack shared host data.** The first runner `verify` failed: the first registration
   returned 429, because the previous run's throttle counter survived. The isolated stack's Redis
   wrote to the checkout's `./data/redis` bind mount, which `down -v` does not remove. Run from the
   main checkout, it would even have shared the live stack's AOF and drafts. Fix: Compose takes
   `TTOD_REDIS_HOST_DIR` (default `./data/redis`, unchanged for Tanit), and
   `scripts/isolated-stack.sh` gives every stack fresh temporary directories for Redis and proposal
   drafts, deleted on `down`. The AA5 lane A gate predates the helper; it is safe only because the
   harness runs it in a worktree. AA5 lane B should move it onto the helper.

## 4. Rolling it out on Tanit (after the owner merges)

1. If the class reaches TTOD by a LAN name, set it in `.env`, for example
   `TTOD_ALLOWED_HOSTS=tanit.crea-comm.loc`. It is baked in at build time.
2. `make rebuild`. It runs `ensure_env_secrets.py`, rebuilds the frontend with the allowed hosts,
   and recreates the stack. Drafts survive on the bind mount (AA5 lane A).
3. **Everyone is signed out once.** Existing browser sessions remain valid Redis rows and survive.
   Old PATs (no `jti`) stop working; clients request a new one with `POST /api/v1/auth/token`.
4. Check:
   - `curl -s -o /dev/null -w '%{http_code}\n' -X POST -H 'content-type: application/json' -d '{"query":"x"}' http://127.0.0.1:18080/api/v1/oracle/stream`
     must print `401`;
   - signing in on `http://tanit.crea-comm.loc:18080/es/login/` works.

## 5. For students and later phases

- **AA3 (A35) consumes this API.** The `/account#password` form posts `current_password` and
  `new_password` to `POST /api/v1/auth/password`, then sets the returned `session_token` as the new
  cookie, because the old sid is revoked. The username field uses `PATCH /api/v1/auth/profile`.
- **AA6 (F21)** adds the oracle *quota*. AA2 only requires a session for the stream.
- **Not done here:** CAPTCHA (out of scope) and email change or reset (D5: no mail transport).

## 6. Acceptance

- [x] Rapid register/login → 429 (unit tests + live burst).
- [x] Fallback off + missing sid → unauthenticated (`signed_fallback_off`).
- [x] Non-PROD-secure story documented; LAN HTTP can set cookies when Secure=false (live: no Secure over HTTP; `COOKIE_SECURE` documented).
- [x] A configured LAN host can POST login with the matching Host + Origin pair (live: 303).
- [x] Unauthenticated oracle stream/propose rejected; dual-write store used (unit + live).
- [x] Password change revokes other sessions; wrong current password throttled; `display_name` round-trips.
- [ ] Cold review green or amended.
