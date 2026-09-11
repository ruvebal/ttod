---
title: "Personal favorites library — save, view, remove"
seam: accounts
team_number: 5
team_name: "Accounts, Library, Proposals & Public API"
task_number: 2
area: "Accounts"
verb: keep
layout: default
lang: en
---

# Assignment — Team 5, Task 2: Personal favorites library — save, view, remove

**Seam:** accounts · **Team:** 5 · **Task:** 2 of ~10
**Area(s):** Accounts · **Verb served:** keep

## 1. Curriculum map

This task exercises the **FE II Unit 3 — State and Data** concepts, specifically managing client-side state that persists across sessions and interacts with server-side storage. It also touches **FE II Unit 4 — Forms and Validation** for the UI interactions (save/remove buttons) and **FE II Unit 5 — Testing strategy** for verifying the state transitions.

*Note: Specific unit links are not yet published in `assignments.md` for this exact task; the above references the standard FE II curriculum structure that this module inherits.*

## 2. Worked example, from the real TTOD app

The type contract for this feature already exists in the codebase. In `services/frontend/src/types/domain.ts` at line 80, the `FavoriteEntry` interface is defined:

```typescript
export interface FavoriteEntry {
  userId: string;
  quoteId: string;
  savedAt: string; // ISO 8601
}
```

This frozen type is the single source of truth for the shape of a favorite. The backend store and the three endpoints (save, list, remove) do **not** exist yet in `services/backend/app/main.py`. This task is about building the backend logic that honors this existing type contract, and the frontend UI that consumes it. The `requireUser` guard from `services/frontend/src/lib/auth.server.ts` is the existing pattern for protecting the route that will display this library.

## 3. What "done" looks like

**Visible result:** A logged-in user can save a quote, see their saved list, and remove one from it.

**What it includes:**
*   A new, small backend store for favorites (deliberately **not** `ttod.yml`, since favorites are per-user preference data, not governed corpus data).
*   Three backend endpoints: `POST /api/v1/favorites` (save), `GET /api/v1/favorites` (list), `DELETE /api/v1/favorites/{quoteId}` (remove).
*   A UI page (likely `/[locale]/library`) that uses these endpoints to display the user's favorites and provide save/remove controls.

**What has to be done:**
1.  **Backend:** Implement a minimal favorites store (e.g., in-memory dict or SQLite, as per module constraints) and the three endpoints in `services/backend/app/main.py`. Ensure all endpoints are guarded by `require_session_user` (or equivalent bearer token check if API-first) to enforce that only the owner can access their favorites.
2.  **Frontend:** Create the `/[locale]/library` page (or extend an existing one) that calls these endpoints. Use `requireUser` in the Astro frontmatter to guard the page. Implement the UI to list `FavoriteEntry` objects and provide buttons to save/remove quotes.
3.  **Integration:** Ensure the frontend correctly serializes/deserializes the `FavoriteEntry` type from `domain.ts`.

## 4. Success criteria (functional)

*   A signed-in student can save a `FavoriteEntry` (`userId`, `quoteId`, `savedAt`) and see their library.
*   Anonymous `curl` of the favorites route contains no favorite rows (401/403 response).
*   A user can remove a favorite from their library, and it no longer appears in the list.
*   The favorites data is stored separately from the canonical `ttod.yml` corpus.

## 5. Quality criteria (the part that's new)

*   **Code Organization:** The favorites store logic should be isolated in a separate module (e.g., `services/backend/app/favorites.py`) to keep `main.py` clean. The frontend UI should be a component that receives the list of favorites as props, making it testable in isolation.
*   **AI-Use/Process Documentation:** Document the decision to use a separate store for favorites rather than `ttod.yml`. Explain why this separation is important (per-user preference vs. governed corpus).
*   **Test Shape:** Write unit tests for the backend favorites store (save, list, remove) and integration tests for the endpoints (auth guard, correct user isolation). Follow the Trophy-not-Pyramid doctrine: focus on high-value integration tests that verify the full request/response cycle, rather than mocking every internal function.
*   **Accessibility:** The library page must be keyboard-operable, have one accessible name or label for the save/remove controls, not carry meaning by color alone, and respect reduced-motion preferences. (This is the standard Definition of Done inherited by all tasks; see `assignments.md`.)
*   **Oral Defense:** Be prepared to explain why favorites are not stored in `ttod.yml`. The answer should highlight the difference between user-generated preference data and the canonical, reviewed corpus. Be ready to discuss how the `FavoriteEntry` type in `domain.ts` serves as the contract between frontend and backend.

## Closing

> "Dependencies flow inward like water seeking the center. Let nothing in the center know the shape of the shore."
> — TTOD `arch-004`, *architecture*

`ttod.yml` is the center: governed, reviewed, canonical. The favorites store is the shore — shaped by whatever a given user happens to like today, free to change without ceremony. The corpus must never know a favorites row exists; the dependency, if any, flows the other way.