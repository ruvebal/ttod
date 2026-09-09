<!--
Phase U TS4c report — auth hello-world (session cookie + bearer PAT).
Follows cascade-forge evidence-state discipline (status first; claims checked live).
Executed on branch skeleton/ts4c-auth, worktree ../ttod-skeleton-ts4c, forked from
skeleton/ts1-contracts@47f15da9 (never main).
-->

# Phase U · TS4c Report — Auth hello-world seam

**Status:** DONE

**Scope executed:** the five deliverables in
[`PHASES/U-TS4c-auth-hello-world.md`](PHASES/U-TS4c-auth-hello-world.md) §4 — backend
login/logout/me/token, Astro `requireUser`/`requireRole`, one protected `/[locale]/account`
page, `ASSIGNMENT.md`, plus the TS1 `domain.ts` amendment named in that runbook §3.

**Date:** 2026-09-09

**Implementer:** TS4c lane session (worktree `../ttod-skeleton-ts4c`)

**Independent verifier:** pending

**Owner:** `@crea-comm.net`

---

## 0. Branch and TS1 gate

- Branch: `skeleton/ts4c-auth`
- Forked from: `skeleton/ts1-contracts` (`47f15da9`)
- `main` was not checked out and was not modified
- TS1 report status is **DONE**, so this lane is not BLOCKED

FE I lessons cited in the runbook §1 were present and read
(`react-authentication` §1–§3; `react-framework-mode-auth-i18n` §5). Architecture follows that
two-surface table: httpOnly session for SSR pages; bearer PAT for non-browser clients.

## 1. TS1 contract amendment (flag for TS1's owner)

`services/frontend/src/types/domain.ts` on `skeleton/ts1-contracts` did not yet contain `User` /
`FavoriteEntry`. This branch **adds** them exactly as the runbook §3 proposed. The session cookie
is **not** a `domain.ts` type.

| Symbol | Added |
| --- | --- |
| `UserRole` | `'student' \| 'reviewer' \| 'instructor'` |
| `User` | `id`, `email`, `displayName`, `role` |
| `FavoriteEntry` | `userId`, `quoteId`, `savedAt` (ISO-8601) |

Treat as unfrozen until TS1's owner confirms. Do not invent a second parallel shape.

## 2. §5 mechanical gates

| Gate | Result | Evidence |
| --- | --- | --- |
| Login works | **pass** | `POST /api/v1/auth/login` returns the public `User` and an `httponly; samesite=lax` `ttod_session` cookie; `/en/account` then renders `Signed in as student@ttod.local` |
| Logout works | **pass** | `POST /api/v1/auth/logout` is 204; cookie-jar `/me` is 401; `/en/account` is 302 to login with empty body |
| Guard runs server-side | **pass** | logged-out `curl` of `/en/account/` is **302**, body **0 bytes**, `grep -i email` matches nothing — not CSS-hidden |
| Bearer token issued | **pass** | `POST /api/v1/auth/token` is **401** without a session; **200** with session; `token_type=Bearer`, `shown_once=true`; token value ≠ session cookie |
| Passwords hashed | **pass** | passlib `CryptContext(schemes=["bcrypt"])`; no `$2a$`/`$2b$` hashes committed; teaching placeholder only in `.env.example` |
| No `ttod.yml` write path | **pass** | `git diff skeleton/ts1-contracts -- ttod.yml` is empty; `auth.py` does not import `ttod_core` |

Backend unittest (including the new auth cases): 10/10 OK. Root corpus suite: 218 OK.
`npm run check` in `services/frontend`: 0 errors, 0 warnings, 0 hints.

## 3. Curl transcript — server-side guard

The runbook's `:8080` compose URL is the *main* stack, not this worktree. Verification used the
lane's own processes: uvicorn `:8000` + Astro `:4321` with `BACKEND_URL=http://127.0.0.1:8000`.
(Docker on this machine already binds `:8080` / `:18080` for other projects.)

```text
$ curl -sS -D - -o /tmp/ts4c-out.txt http://127.0.0.1:4321/en/account/
HTTP/1.1 302 Found
location: /en/account/login?from=%2Fen%2Faccount%2F

$ wc -c /tmp/ts4c-out.txt
       0 /tmp/ts4c-out.txt

$ curl -s http://127.0.0.1:4321/en/account/ | grep -i "email" || echo "(no match)"
(no match)
```

Logged-in HTML (session cookie present) contains the seed email in the first paint:

```text
Signed in as student@ttod.local
```

Login cookie (value redacted):

```text
HTTP/1.1 200 OK
set-cookie: ttod_session=<redacted>; path=/; Max-Age=604800; httponly; samesite=lax

{"id":"user-seed-student","email":"student@ttod.local","displayName":"Cohort Student","role":"student"}

$ curl -sS -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8000/api/v1/auth/token
401
```

Astro login form POST (frontmatter → backend JSON → forwarded `Set-Cookie`) also returned
`303 Location: /en/account` with `httponly` cookie; subsequent GET rendered the email.

**Astro vs FE I throw:** throwing a `Response` from `.astro` frontmatter is a 500 in Astro 5.18.2
(`[ERROR] {}`). `requireUser` / `requireRole` **return** the redirect/403 `Response`; the page
`return`s it. Same request-lifecycle as FE I's loader `throw redirect()` — HTML of the gated
route is never generated.

## 4. No canonical mutation path

- `git diff skeleton/ts1-contracts -- ttod.yml` → empty
- `ttod_core/**`, `schema/**`, `services/mcp/**`, `components/graph/**`, `components/oracle/**`,
  existing wisdom pages → untouched
- `auth.py` docstring and tests assert no `import ttod_core`

Auth gates who may later propose or favorite. Acceptance remains `cli.py proposal accept --reviewer-id`.

## 5. Teaching credentials

Documented as placeholders in `.env.example` and `services/backend/.env.example`. **Not** a real
reused password:

- email: `student@ttod.local`
- password: `ttod-teaching-only-not-a-real-password`

`TTOD_SESSION_SECRET` and `TTOD_PAT_SECRET` default to two different insecure teaching strings
(`from_env` refuses to start if they are equal). Rotate both before any shared deployment.

## 6. ASSIGNMENT.md

Filed at `services/frontend/src/auth/ASSIGNMENT.md` (dedicated auth doc folder). Not under
`src/pages/`, because a first draft at `pages/[locale]/account/ASSIGNMENT.md` was published as a
route (`200`). Content:

---

# Module 06 — Authentication assignment

Instructor seam (`src/pages/[locale]/account/`): one seeded user, `requireUser()` on
`/[locale]/account`, an httpOnly signed session cookie, and a **separate** bearer token from
`POST /api/v1/auth/token`. You expand that seam. You do not invent a second auth stack.

This file lives outside `src/pages/` so Astro does not publish it as a route.

## Learning outcomes

By the end of this module you will be able to:

1. **Separate session auth from bearer auth.** TTOD SSR pages (`/library`, `/propose`, `/account`)
   authenticate with an httpOnly signed cookie. Non-browser clients (Module 07's bot, curl, docs
   examples) authenticate with `Authorization: Bearer <token>`. These are two credentials, not
   the same JWT stuffed into two headers. A leaked PAT must not be a live browser session, and
   a stolen cookie must not be a PAT.
2. **Explain SSR guard timing.** `requireUser()` / `requireRole()` run in Astro frontmatter —
   the loader-equivalent from FE I's Framework-mode auth lesson — *before* any HTML is sent.
   A logged-out `curl` of a protected URL must not contain gated content in the raw response
   (a client-only `<ProtectedRoute>` that paints then redirects is a failing answer). In Astro,
   **return** the Response from `requireUser` (React Router `throw redirect()` is the same idea;
   throwing a Response from an `.astro` page is a 500 in Astro 5).
3. **Keep passwords hashed.** Verification uses passlib/bcrypt on the server. Passwords are
   never logged, never committed as plaintext fixtures, never rendered into HTML. The seeded
   user in `.env.example` is teaching-only; do not reuse a real password.

## Constraints (must reuse the seam)

- Import `requireUser` / `requireRole` from `src/lib/auth.server.ts`. Call them **only** from
  Astro page frontmatter. Do not import that module from an island, a React/Svelte component,
  or client script.
- Do not read the `ttod_session` cookie from `document.cookie` or from any component.
- Do not add a third-party identity provider. TTOD stays local-only.
- Auth may **gate** who can submit a proposal or save a favorite. It must not write `ttod.yml`.
  Canonical mutation stays `python cli.py proposal accept --reviewer-id …`.
- Registration may stay a single seeded user unless you deliberately add a sign-up flow; if
  you do, hash with passlib/bcrypt and keep credentials out of git.

## Acceptance criteria

The assignment is complete when all three journeys work end to end, each guarded server-side:

1. **Favorites library** — a signed-in student can save a `FavoriteEntry` (`userId`, `quoteId`,
   `savedAt`) and see their library; anonymous `curl` of that route contains no favorite rows.
2. **Propose while logged in** — the propose form is reachable only with a session; anonymous
   requests redirect before the form HTML is emitted. Submitting still creates a *proposal*
   (origin `blackbox`), never an accepted quote.
3. **Role-gated reviewer view** — `requireRole(request, 'reviewer')` (or `'instructor'`) wraps
   the reviewer page. The seeded student role receives 403; a reviewer sees the queue. Do not
   implement this check only in JSX/Svelte state.

Bearer surface: a logged-in session can `POST /api/v1/auth/token`, receive a PAT shown once,
and a non-browser client can call a documented API with `Authorization: Bearer`. That token
must not be the session cookie value.

## Prohibited shortcuts

- Client-side-only route guards (`if (!user) return <Navigate />` as the only protection).
- Storing the session in `localStorage` or a public JS bundle.
- Reusing the session JWT/cookie as the API bearer token (or vice versa).
- Hand-rolled password hashing (`hashlib.sha256`, homemade HMAC, etc.).
- Logging passwords, committing real reused passwords, or putting secrets in `domain.ts`.
- Importing `auth.server.ts` from a `client:*` island.
- Bypassing `proposal accept --reviewer-id` to write the canonical corpus.

## Teaching credentials (local only)

Documented in `.env.example` as placeholders, not as a production identity:

- email: `student@ttod.local`
- password: `ttod-teaching-only-not-a-real-password`

Treat them as classroom fixtures. Rotate the defaults in any shared deployment.

## FE I map (do not unlearn)

| FE I | TTOD seam |
| --- | --- |
| `session.server.js` `requireUser` / `requireRole` in the loader | `auth.server.ts` in Astro frontmatter |
| httpOnly cookie, components never import the session module | same — `.server.ts` is not for islands |
| `tokenStorage.js` + `Authorization: Bearer` | `POST /api/v1/auth/token` then header on API/bot clients |

---

## 7. Explicit non-claims

This report does **not** claim:

- The compose stack on `:18080` (canonical checkout `main`) was rebuilt with this branch
- Favorites library, propose-while-logged-in, or reviewer queue UI exist (those are assignment depth)
- `User` / `FavoriteEntry` are frozen on `main` (amendment lives on `skeleton/ts4c-auth` only)
- Registration / sign-up is implemented (one seeded user, per hello-world contract)

## 8. Resume rule

| Status | Meaning | Next action |
| --- | --- | --- |
| **DONE (current)** | Both credential surfaces work; SSR guard proven with curl; ASSIGNMENT filed; no corpus write path | Independent reader re-curls `/en/account` logged out; TS1 owner confirms `domain.ts` amendment |
| **PARTIAL** | Named §5 gate unmet | Fix that gate before treating the seam as cohort-ready |
| **BLOCKED** | TS1 not DONE | Do not open this lane |
