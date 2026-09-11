---
title: "API documentation page and a minimal external example client"
seam: accounts
team_number: 5
team_name: "Accounts, Library, Proposals & Public API"
task_number: 6
area: "Accounts"
verb: contribute
layout: default
lang: en
alt_lang_missing: true
---

# Assignment — Team 5, Task 6: API documentation page and a minimal external example client

**Seam:** accounts · **Team:** 5 · **Task:** 6 of ~10
**Area(s):** Accounts · **Verb served:** contribute

## 1. Curriculum map

This task exercises the FE II unit on **API Documentation and Client Integration**. While the specific lesson link for this exact task is not yet published in the `assignments.md` "Lessons for these tasks" section, it directly applies the principles of **Unit 5 — Testing strategy** (https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/) by requiring the documentation to be verified against a running instance, ensuring the "contract" is not just written but proven. It also reinforces the session half of the **FE I Framework-mode auth lesson** ([HELIOS DECK's architecture](https://ruvebal.github.io/web-atelier-udit/tracks/es/geo-physical-aggregator/arch/) — cookie session, `requireUser` in the loader; that page does not cover bearer tokens, so the two-credential distinction this API documents is TTOD's own extension of that lesson, not itself curriculum content yet).

## 2. Worked example, from the real TTOD app

The real TTOD app already implements the backend authentication surface that this documentation must describe. Specifically, `services/backend/app/auth.py` exports `AuthService`, `current_user`, and `require_session_user`, which power the real, tested endpoints in `services/backend/app/main.py`:
*   `POST /api/v1/auth/login` (returns a session cookie)
*   `POST /api/v1/auth/token` (returns a bearer token)
*   `GET /api/v1/auth/me` (verifies the session)
*   `GET /api/v1/wisdom/sample` (a public endpoint that does not require auth)

The `services/backend/tests/test_backend.py` file contains the real test `test_auth_login_me_token_logout_are_separate_credentials`, which confirms that the login, me, token, and logout endpoints exist and function as distinct credential flows. This task requires documenting these *existing* endpoints and creating a client that consumes them, rather than inventing new backend routes.

## 3. What "done" looks like

**Visible result:** A documentation page any external developer could follow, and a small script (not a second application) proving the API works outside a browser.

**What it includes:** The documentation should be generated from or checked against the same `types/domain.ts` shapes governing every other module — "types are the contract," applied here too. It must accurately describe the `User` (`id`, `email`, `displayName`, `role`) and `FavoriteEntry` (`userId`, `quoteId`, `savedAt`) shapes defined in `services/frontend/src/types/domain.ts`. The example client must demonstrate the two distinct authentication flows: obtaining a session cookie via `POST /api/v1/auth/login` and obtaining a bearer token via `POST /api/v1/auth/token`.

**What has to be done:** Write the docs, then actually run the example script against your own running instance before calling this done — a script that's never been executed is not proof of anything. The script must successfully call at least one authenticated endpoint (e.g., `GET /api/v1/auth/me` with the session cookie, or a bearer-token-protected endpoint if one exists in the current `main.py` route list) and print the response.

## 4. Success criteria (functional)

*   The documentation page accurately lists the real endpoints available in `services/backend/app/main.py` (e.g., `/api/v1/auth/login`, `/api/v1/auth/token`, `/api/v1/auth/me`, `/api/v1/wisdom/sample`).
*   The documentation clearly distinguishes between the session cookie authentication (for SSR pages) and the bearer token authentication (for non-browser clients), as defined in the module's `ASSIGNMENT.md` Learning Outcomes.
*   The example client script successfully executes against a running TTOD instance and demonstrates at least one successful authenticated API call.
*   The documentation references the real type shapes from `services/frontend/src/types/domain.ts` (e.g., `User`, `FavoriteEntry`) rather than inventing new, undocumented types.

## 5. Quality criteria (the part that's new)

*   **Code Organization:** The example client should be a single, readable script (e.g., Python or Node.js) that clearly separates the authentication setup from the API call. It should not be a full application with a UI.
*   **AI-Use/Process Documentation:** The documentation should include a "How to verify" section that explicitly states the command to run the example script and the expected output. This ensures the "types are the contract" principle is not just asserted but demonstrated.
*   **Test Shape:** Per the Testing Trophy (not Pyramid) doctrine, the "test" here is the successful execution of the example client. The client itself acts as an integration test for the API's public surface. It should be simple, direct, and fail loudly if the API contract is broken.
*   **Accessibility:** The documentation page must be keyboard-operable, have one accessible name or label for all interactive elements, not carry meaning by color alone, and respect reduced-motion preferences, as per the global Definition of Done.
*   **Oral Defense:** A defensible answer for this task explains *why* the documentation is tied to the `types/domain.ts` shapes (to ensure the frontend and backend contracts remain synchronized) and *how* the example client proves the API is usable by external, non-browser clients (by demonstrating the bearer token flow, which is distinct from the session cookie flow).

## Closing

> "The documentation that deploys itself is the documentation that stays current."
> — TTOD `qa-014`, *qa-tooling*

This task embodies this principle by requiring the documentation to be verified against a running instance, ensuring that the "contract" described in the docs is not just aspirational but actively maintained and proven to work.