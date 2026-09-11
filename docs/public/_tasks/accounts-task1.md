---
title: "Login/session (server-verified, one protected route)"
seam: accounts
team_number: 5
team_name: "Accounts, Library, Proposals & Public API"
task_number: 1
area: "Accounts"
verb: keep
layout: default
lang: en
alt_lang_missing: true
---

# Assignment — Team 5, Task 1: Login/session (server-verified, one protected route)

**Seam:** accounts · **Team:** 5 · **Task:** 1 of ~10
**Area(s):** Accounts · **Verb served:** keep

## 1. Curriculum map

This task exercises the **FE II Unit 3 — Server-side rendering and routing** concepts, specifically the application of server-side guards in Astro frontmatter. It builds directly on the **FE I Framework-mode auth lesson** —
[HELIOS DECK's architecture](https://ruvebal.github.io/web-atelier-udit/tracks/es/geo-physical-aggregator/arch/),
which documents the canonical `requireUser(request)` guard: reads the session in the *loader*,
before the component renders, and redirects to `/auth/login` if there is no `userId`, backed by
an `HttpOnly` cookie session (`createCookieSessionStorage`) rather than client-stored state.
`auth.server.ts`'s own `requireUser` is that exact same loader-timing pattern, translated into
Astro frontmatter. `requireRole` is **not** part of the FE I lesson — it is TTOD's own extension,
layering role-gating on top of the inherited session-guard pattern; do not present it as if FE I
already taught role-based access.

## 2. Worked example, from the real TTOD app

The existing baseline is the `accounts` module's seeded-user flow.
- **Backend:** `services/backend/app/auth.py` exports `AuthService`, `current_user`, and `require_session_user`. The route `POST /api/v1/auth/login` is already implemented and tested in `services/backend/tests/test_backend.py` (specifically `test_auth_login_me_token_logout_are_separate_credentials`).
- **Frontend:** `services/frontend/src/lib/auth.server.ts` exports `requireUser` and `requireRole`. These are currently used in `services/frontend/src/pages/[locale]/account/index.astro` and `.../account/login.astro`.
- **Pattern:** The current implementation uses an httpOnly signed session cookie for browser-based SSR pages. This task extends this by ensuring the guard runs *before* HTML emission, preventing client-side-only protection.

## 3. What "done" looks like

**Visible result:**
A logged-in user can access the protected account route. A logged-out user (or a `curl` request without a valid session cookie) receives a redirect or a 401/403 response *before* any protected HTML content is sent. The raw HTTP response body for an unauthenticated request contains no gated content (e.g., no user name, no library data).

**What it includes:**
- The `requireUser()` guard is called in the Astro frontmatter of the protected page.
- The guard returns a `Response` object (redirect or error) rather than throwing an exception.
- The session cookie is httpOnly and Secure, preventing client-side JavaScript access.
- The password verification happens server-side using passlib/bcrypt (already present in `auth.py`).

**What has to be done:**
1. Ensure `services/frontend/src/pages/[locale]/account/index.astro` (or the specific protected route you are extending) calls `requireUser(request)` in the frontmatter.
2. Verify that the return value of `requireUser` is handled correctly: if it returns a `Response`, return it immediately from the frontmatter. Do not throw it.
3. Confirm that no client-side component (Svelte/React island) is the *only* thing checking for user presence. The server must gate the route.
4. Test with `curl`: `curl -i http://localhost:4321/[locale]/account` should return a redirect or 401/403, and the body should not contain sensitive data.

## 4. Success criteria (functional)

1. **Server-side guard timing:** `requireUser()` runs in Astro frontmatter before any HTML is sent. A logged-out `curl` of the protected URL does not contain gated content in the raw response.
2. **Correct Response handling:** The guard returns a `Response` object (redirect or 401/403). Throwing a `Response` from an `.astro` page is avoided (which would cause a 500 error in Astro 5).
3. **Session isolation:** The session cookie is httpOnly and not accessible via `document.cookie`. The bearer token (if used for API) is separate from the session cookie.
4. **Password security:** Passwords are verified server-side using passlib/bcrypt. No plaintext passwords are logged or committed.

## 5. Quality criteria (the part that's new)

- **Code organization:** The auth logic is isolated in `auth.server.ts` and `auth.py`. No client-side code imports `auth.server.ts`.
- **AI-use/process documentation:** Document the decision to use server-side guards over client-side checks. Explain why `return` is used instead of `throw` for `Response` objects in Astro.
- **Test shape:** Per the Testing Trophy (not Pyramid) doctrine, write integration tests that verify the *behavior* (HTTP status code, response body content) rather than just unit-testing the `requireUser` function in isolation. The test `test_auth_login_me_token_logout_are_separate_credentials` is a good example of this.
- **Accessibility:** The protected route must be keyboard-operable, have one accessible name or label, not carry meaning by color alone, and respect reduced-motion preferences. (Cite the global Definition of Done, do not restate as task-specific.)
- **Oral defense:** Be prepared to explain the difference between session auth (cookie-based, for browsers) and bearer auth (token-based, for APIs). Explain why client-side-only guards are insecure (XSS, race conditions). Explain the Astro-specific pitfall of throwing `Response` objects.

## Closing

> "Before changing a domain entity, check for side effects in application use cases. Before trusting LLM output, parse it into a value object. The guard is not distrust — it is respect for the boundary."
> — TTOD `arch-051`, *architecture*

`requireUser()` running in frontmatter, before any HTML is sent, is exactly this discipline: the guard is not paranoia about your own users, it is respect for the boundary between "request arrived" and "request is trusted." Skip it and you have not saved a step — you have deleted the boundary.