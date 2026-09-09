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
