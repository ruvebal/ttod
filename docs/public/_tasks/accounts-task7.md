---
title: "Unit and component tests for auth, the library, and the API"
seam: accounts
team_number: 5
team_name: "Accounts, Library, Proposals & Public API"
task_number: 7
area: "Testing"
verb: keep
layout: default
lang: en
---

# Assignment — Team 5, Task 7: Unit and component tests for auth, the library, and the API

**Seam:** accounts · **Team:** 5 · **Task:** 7 of ~10
**Area(s):** Testing · **Verb served:** keep

## 1. Curriculum map

This task exercises the testing strategies covered in [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/). Specifically, it applies the principles of testing boundaries, verifying negative cases (rejection of unauthorized access), and ensuring that security constraints are enforced by the system rather than assumed by the client.

## 2. Worked example, from the real TTOD app

The existing test suite in `services/backend/tests/test_backend.py` contains `test_auth_login_me_token_logout_are_separate_credentials`. This test demonstrates the required pattern: it verifies that the authentication endpoints (`/api/v1/auth/login`, `/api/v1/auth/me`, `/api/v1/auth/token`, `/api/v1/auth/logout`) function correctly and, crucially, that the session cookie and the bearer token are distinct credentials. This test is the precedent to extend, not replace, when adding tests for the favorites library and the propose-a-quote endpoint.

## 3. What "done" looks like

**Visible result:**
Auth, the library, and the API each have at least one real test.

**What it includes:**
- A test that a logged-out request to a protected route is actually rejected — not just that a logged-in one succeeds.
- Tests for the favorites library (save, view, remove) that verify `FavoriteEntry` creation and retrieval.
- Tests for the propose-a-quote backend endpoint that verify proposal creation.
- Tests for the bearer-token-authenticated public API endpoint that verify token-based access.

**What has to be done:**
- Never store the session in `localStorage`.
- Never hand-roll password hashing.
- Never reuse the session token as the bearer token.
- These are prohibited shortcuts, not style preferences, and a test that only checks the happy path won't catch them.

## 4. Success criteria (functional)

1. **Favorites library** — a signed-in student can save a `FavoriteEntry` (`userId`, `quoteId`, `savedAt`) and see their library; anonymous `curl` of that route contains no favorite rows.
2. **Propose while logged in** — the propose form is reachable only with a session; anonymous requests redirect before the form HTML is emitted. Submitting still creates a *proposal* (origin `blackbox`), never an accepted quote.
3. **Role-gated reviewer view** — `requireRole(request, 'reviewer')` (or `'instructor'`) wraps the reviewer page. The seeded student role receives 403; a reviewer sees the queue. Do not implement this check only in JSX/Svelte state.

Bearer surface: a logged-in session can `POST /api/v1/auth/token`, receive a PAT shown once, and a non-browser client can call a documented API with `Authorization: Bearer`. That token must not be the session cookie value.

## 5. Quality criteria (the part that's new)

**Code organization:**
- Tests must be organized by feature (auth, library, API) rather than by file.
- Each test file should focus on a single concern and use descriptive names that explain the behavior being tested.
- Test fixtures should be isolated and reset between tests to prevent state leakage.

**AI-use/process documentation discipline:**
- Document any AI-assisted test generation in the commit message or PR description.
- Ensure that AI-generated tests are reviewed for correctness and do not introduce prohibited patterns (e.g., client-side-only guards, localStorage session storage).
- Maintain a clear separation between test setup, execution, and assertion.

**Test shape per R7's own Trophy-not-Pyramid doctrine:**
- Prioritize integration tests that verify end-to-end behavior over unit tests that mock internal implementation details.
- Ensure that tests verify the system's behavior from the user's perspective, not just internal function calls.
- Avoid over-mocking; let the real components interact where possible to catch integration issues.

**Accessibility:**
- Every task inherits the same Definition of Done per `assignments.md`: keyboard-operable, one accessible name or label, no meaning carried by color alone, respects reduced-motion preferences. Cite this definition rather than restating it as if it were unique to this task.

**Defensible oral-defense answer:**
- "I ensured that the tests verify the security constraints by checking that unauthorized requests are rejected, not just that authorized requests succeed. I followed the existing test pattern in `test_backend.py` and extended it to cover the new features. I avoided prohibited shortcuts by ensuring that the tests verify server-side enforcement of security, not client-side assumptions."

## Closing

> "The wise instructor automates what repeats. The foolish instructor repeats what should be automated."
> — TTOD `qa-001`, *qa-tooling*

Manually re-checking, by hand, on every change, that a logged-out `curl` really is rejected is exactly the repeated verification this quote warns against doing by hand. Write it once as a test, and the boundary stays enforced automatically on every future change, not just the one you remembered to check today.