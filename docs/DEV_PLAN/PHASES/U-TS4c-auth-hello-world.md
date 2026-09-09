<!--
Self-contained runbook. New lane, not in Phase R's original seven — added per product-owner
request to bring FE I's authentication curriculum into TTOD as Module 06. Derived from
PHASE-U-FEII-TEACHING-SKELETON-CASCADE.md's own template, the FE I lessons named in §1, and the
existing ttod_core proposal infrastructure. Generated as part of the Week-0 skeleton-generator
pass, second wave.
-->

# Phase U · TS4c — Auth hello-world seam (new module, not a Phase R reduction)

**Mode:** student lane (or instructor-built if executed before cohort start), pair — may run
parallel to all of TS3/TS4a/TS4b, gated only on TS1
**Entry:** TS1 `DONE`
**Exit:** login/logout, one server-verified protected route, one bearer-token endpoint working
end to end — genuinely new code, not a subtraction from an existing rich reference (none exists)

---

## 0. What this phase is — the one lane that is not a reduction

Every other TS3/TS4 lane subtracts assignment depth out of an already-working reference file.
**There is no existing auth code anywhere in this repository** (confirmed by search) — this is a
first build, matching Phase U's own invariant 1 ("explain before collaborate"): the instructor
seam here is a small, genuinely complete login/logout/one-protected-route path, not a stripped
version of something richer.

**This is also the one lane that touches the backend.** Every other lane's touched-path budget
excludes `services/backend/**` — auth cannot avoid it (token issuance and verification are
inherently server-side). This is a deliberate, named exception to Phase R's original "backend is
instructor-only" boundary, scoped narrowly to auth endpoints only.

**Two credential surfaces, not one — this is the actual pedagogical point.** FE I's own two auth
lessons teach two different, complementary patterns:

| FE I taught this... | ...as | TTOD reuses it for |
| --- | --- | --- |
| `react-authentication` (Declarative Mode): `tokenStorage.js`, bearer token in `Authorization` header | client-managed JWT | **Module 07's bot test app and the public API docs** — a non-browser client cannot hold a cookie, so it authenticates with a bearer token |
| `react-framework-mode-auth-i18n` §5: `session.server.js`, httpOnly cookie, `requireUser`/`requireRole` in the **loader**, no flash of protected content | server-verified session | **TTOD's own SSR pages** (`/library`, `/propose`) — Astro's frontmatter is the loader-equivalent; the guard runs server-side before any HTML is sent, exactly matching that lesson's request-lifecycle diagram |

Building both in one small feature is genuinely richer pedagogy than picking one — it is the same
"one concept, cleanly separated" idea Phase U already applies everywhere else, applied to the two
auth patterns the cohort already has fresh from FE I.

## 1. Required reading

- `PHASE-U-FEII-TEACHING-SKELETON-CASCADE.md` §1 (pedagogical invariants) — this lane must still
  satisfy "one concept per slice," "no answer leakage," "expansion seams are contracts."
- FE I, in full, not skimmed: `web-atelier-udit/web-foundations/docs/lessons/en/react/react-authentication/index.md`
  §1–§3 (mental model, JWT vs session, `tokenStorage.js`/`authApi.js`/`AuthContext.jsx`) and
  `.../react-framework-mode-auth-i18n/index.md` §5 in full (the client↔server mapping table
  above is drawn directly from this section — read the section itself, the table is a summary,
  not a replacement).
- `AGENTS.md` — specifically the proposal-lifecycle rule ("Mutations go through `proposal
  accept`... requires `--reviewer-id`") — this lane's "propose while logged in" backlog item
  (owned by Module 06, wired by `PHASE-V`'s new CI/CD section) must never bypass this.
- `services/backend/app/main.py`, `config.py`, `models.py` — read the existing endpoint/settings
  conventions before adding new ones; match the style, do not introduce a second one.

## 2. Non-negotiable boundaries

- **Work on `skeleton/ts4c-auth`, forked from `skeleton/ts1-contracts`.**
- **No third-party identity provider.** FE I's lesson names Firebase as one production option;
  TTOD stays local-only (matching the studio's own "no cloud AI, no vendor lock-in" posture,
  applied here to identity too) — a self-issued JWT against a local user store, not an external
  auth vendor.
- **Passwords are hashed, never logged, never in a committed fixture.** Use an established library
  (e.g. `passlib`/`bcrypt` on the FastAPI side) — do not hand-roll hashing.
- **The session cookie is httpOnly and signed** — exactly `session.server.js`'s own header comment
  ("Components never import this directly — they go through loaders/actions"): no TTOD island or
  page component reads the cookie directly; only Astro frontmatter (the SSR "loader" equivalent)
  does, via one shared helper.
- **The bearer token is a separate credential from the session cookie**, not the same JWT reused
  in two places — a leaked API token must not also be a live browser session, and vice versa.
- **No new canonical-mutation path.** Auth gates *who* can submit a proposal or save a favorite;
  it never itself writes `ttod.yml` — that stays exactly `proposal accept --reviewer-id`'s job,
  unchanged.
- **Registration, at hello-world depth, may be a single seeded test user** rather than a working
  sign-up flow — Phase U's own contract pattern (one real path, not every path) applies here too;
  a full registration UI is reasonable *assignment* depth, not required seam depth.

## 3. Domain contract slice (new — TS1 should add these on confirmation)

```typescript
// services/frontend/src/types/domain.ts — proposed additions, confirm with TS1's owner before
// treating as frozen; do not invent a second, parallel shape if TS1 lands something adjacent.
export interface User {
  id: string;
  email: string;
  displayName: string;
  role: 'student' | 'reviewer' | 'instructor';
}

export interface FavoriteEntry {
  userId: string;
  quoteId: string;
  savedAt: string; // ISO-8601
}
```

The session itself is server-only and deliberately **not** a `domain.ts` type — mirroring
`session.server.js`'s own boundary ("never imported into a component"). The bearer token is a
plain string the client stores and sends as `Authorization: Bearer <token>`; no client-side type
needed beyond that.

## 4. Scope — what this seam builds

1. **Backend, `services/backend/app/auth.py` (new)** — `POST /api/v1/auth/login` (email/password
   against the seeded user, returns a session cookie), `POST /api/v1/auth/logout` (clears it),
   `GET /api/v1/auth/me` (returns the current `User` or 401 — this is the server-side
   equivalent of FE I's client `/auth/me`, called from Astro frontmatter, never from the browser
   after first paint, exactly avoiding the "flash of protected content" the lesson calls out).
2. **Backend, `POST /api/v1/auth/token` (new)** — once logged in (session cookie present), issue a
   long-lived bearer token ("personal access token") for API/bot use. This is the seam's second
   credential surface — document clearly in the response that this token is shown once and the
   user is responsible for storing it (standard PAT UX).
3. **Astro, `services/frontend/src/lib/auth.server.ts` (new, `.server.ts` naming deliberately
   mirrors FE I's `.server.js` convention)** — `requireUser()`/`requireRole()` helpers reading the
   session cookie server-side, called from page frontmatter (Astro's loader-equivalent), `throw`ing
   a redirect on failure exactly as the lesson's `session.server.js` does.
4. **One protected route** — a minimal `/[locale]/account` page using `requireUser()` in its
   frontmatter, rendering the logged-in user's email. This is the "one server-verified protected
   route" the exit criteria name; `/library` and `/propose`'s full UI are Module 06's assignment
   depth, not this seam's.
5. **`ASSIGNMENT.md`** (new, `services/frontend/src/pages/[locale]/account/ASSIGNMENT.md` or a
   dedicated `auth/` doc folder): learning outcomes (session vs. bearer auth, SSR guard timing,
   password hashing), constraints (must reuse `requireUser`/`requireRole`, must not read the
   cookie from any component), acceptance criteria (the favorites library, the propose-while-
   logged-in form, and a role-gated reviewer view all work end to end), prohibited shortcuts (no
   client-side-only route guards — Phase U's "no flash of protected content" lesson is the point).

## 5. Mechanical gates

| Gate | Required proof |
| --- | --- |
| Login works | valid credentials return a session cookie; `/en/account` renders the user's email |
| Logout works | cookie cleared, `/en/account` redirects |
| Guard runs server-side | viewing page source of a protected route while logged out shows no protected content (not just CSS-hidden) |
| Bearer token issued | `POST /api/v1/auth/token` returns a token while a session is present, 401 otherwise |
| Passwords hashed | no plaintext password appears in any log, fixture, or committed file |
| No `ttod.yml` write path added | `git diff main -- ttod.yml` empty; auth code contains no call into `ttod_core.repository` |

## 6. Rollback and mutation law

- Nothing in this seam writes `ttod.yml`, `schema/`, or calls `ttod_core.repository`'s atomic
  write path directly — auth only gates access; proposal acceptance stays exactly where it already
  lives (`cli.py proposal accept --reviewer-id`, or its CI-triggered equivalent per `PHASE-V`'s new
  CI/CD section).
- If the seeded test user's credentials must be committed for local dev, they go in
  `.env.example`-style placeholder form only, matching this repo's existing secrets discipline —
  never a real, reused password.

## 7. Touched-path budget

**Allowed:** `services/backend/app/auth.py` (new), minimal additions to `services/backend/app/main.py`
(mounting the new routes) and `config.py` (session-secret setting), `services/frontend/src/lib/auth.server.ts`
(new), `services/frontend/src/pages/[locale]/account/**` (new), a new `ASSIGNMENT.md`.

**Forbidden:** `ttod_core/**`, `ttod.yml`, `schema/**`, `services/mcp/**`, any other lane's
component tree (`components/graph/`, `components/oracle/`, existing wisdom pages).

## 8. Post-phase review

A second reader confirms the protected-route guard by viewing raw page source (curl, not just
devtools) while logged out — the whole pedagogical point of server-side auth is that the HTML
itself never contains the gated content, not that it's hidden by client JS.

## 9. Phase report status enum

- **DONE** — all §5 gates pass, `ASSIGNMENT.md` filed, both credential surfaces (session + bearer)
  demonstrated working.
- **PARTIAL** — name exactly which gate is unmet.
- **BLOCKED** — TS1 has not filed `DONE`.

## 10. Exact commands

```bash
cd /Users/ruvebal/src/ttod
git worktree add ../ttod-skeleton-ts4c -b skeleton/ts4c-auth skeleton/ts1-contracts
cd ../ttod-skeleton-ts4c
# after building: verify the guard server-side, not just in-browser
curl -s http://localhost:8080/en/account/ | grep -i "email" # expect nothing while logged out
```

## 11. Report requirements

File `docs/DEV_PLAN/PHASE-U-TS4c-REPORT.md`: status (§9), a curl transcript proving the
server-side guard, confirmation no `ttod.yml`/`ttod_core` write path was introduced, and the
`ASSIGNMENT.md` content.

## 12. Agent prompt — paste this into a fresh agent session with no other file open

```text
Act as TTOD Phase U TS4c engineer. Work only inside a new git worktree on branch
skeleton/ts4c-auth, forked from skeleton/ts1-contracts (never main). This runbook
(docs/DEV_PLAN/PHASES/U-TS4c-auth-hello-world.md) is self-contained. Also read, in full, the two
FE I lessons it cites: web-atelier-udit/web-foundations/docs/lessons/en/react/react-authentication/index.md
§1-3 and .../react-framework-mode-auth-i18n/index.md §5 — the second lesson's own client↔server
mapping table is this runbook's architectural blueprint, ported from React Router loaders to Astro
frontmatter.

Build services/backend/app/auth.py: POST /api/v1/auth/login (hashed-password check against one
seeded user, sets an httpOnly signed session cookie), POST /api/v1/auth/logout (clears it), GET
/api/v1/auth/me (returns the User or 401), and POST /api/v1/auth/token (issues a separate
long-lived bearer token, only when a session is present). Use bcrypt/passlib for hashing, never
hand-roll it. Mount these in main.py following the existing endpoint style.

Build services/frontend/src/lib/auth.server.ts with requireUser()/requireRole() reading the
session cookie server-side — these are called ONLY from Astro page frontmatter (the SSR
loader-equivalent), never from a component. Build one protected page,
services/frontend/src/pages/[locale]/account/index.astro, using requireUser() in its frontmatter
to render the logged-in user's email, redirecting when absent.

Add User and FavoriteEntry interfaces to services/frontend/src/types/domain.ts (propose the
addition, don't silently assume it's already frozen — flag it to TS1's owner). The session itself
is server-only and must not become a domain.ts type, mirroring the FE I lesson's own boundary.

Do not touch ttod_core/**, ttod.yml, schema/**, services/mcp/**, or any other lane's component
tree. Nothing here writes ttod.yml — auth only gates access.

Verify the guard is genuinely server-side: curl the protected route's HTML directly while logged
out and confirm no protected content appears in the raw response, not just that it's hidden by
CSS/JS.

Write an ASSIGNMENT.md: learning outcomes (session vs. bearer auth, SSR guard timing, password
hashing), constraints (reuse requireUser/requireRole, no client-side-only guards), acceptance
criteria (favorites library, propose-while-logged-in form, role-gated reviewer view all work),
prohibited shortcuts (no client-only route guards).

File docs/DEV_PLAN/PHASE-U-TS4c-REPORT.md with status (DONE/PARTIAL/BLOCKED per this
runbook's §9), the curl transcript proving the server-side guard, confirmation no ttod.yml/
ttod_core write path was added, and the ASSIGNMENT.md content.
```
