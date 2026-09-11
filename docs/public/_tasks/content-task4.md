---
title: "Build the \"propose a quote\" form UI"
seam: content
team_number: 1
team_name: "Content, i18n & Proposals UI"
task_number: 4
area: "Content, Accounts"
verb: contribute
layout: default
lang: en
---

# Assignment — Team 1, Task 4: Build the "propose a quote" form UI

**Seam:** content · **Team:** 1 · **Task:** 4 of ~10
**Area(s):** Content, Accounts · **Verb served:** contribute

## 1. Curriculum map

This task exercises the FE II unit on **Client-Side State and Forms**, specifically the integration of user authentication gates with interactive UI components. It also touches on **API Integration Patterns**, focusing on the client-side preparation of payloads for backend endpoints owned by other teams.

*Note: Specific unit links for "Forms and Auth" are not yet published in the `assignments.md` "Lessons for these tasks" section for this specific board item. The curriculum mapping relies on the general FE II progression from static content (Task 1-3) to interactive state (Task 4).*

## 2. Worked example, from the real TTOD app

The existing application demonstrates the **authentication gate** pattern in `services/frontend/src/lib/auth.server.ts`. Specifically, the `requireUser` function (line 62) is the canonical example of how to enforce user identity before allowing sensitive actions. While the current hello-world routes (`services/frontend/src/pages/[locale]/wisdom/index.astro` and `services/frontend/src/pages/[locale]/wisdom/[slug].astro`) are read-only and do not yet contain a form, they demonstrate the correct usage of `fetchWisdom` to retrieve data and the `WisdomEntry` type from `services/frontend/src/types/domain.ts` to structure that data. Your form will mirror this type structure for the *input* fields (quote text, section, source) to ensure the payload matches the domain model the backend expects.

## 3. What "done" looks like

**Visible result:** A logged-in visitor sees a "Propose a Quote" form on the content routes (or a dedicated proposal page linked from them). The form contains fields for the quote text, its section, and its source. Upon submission, the user receives a clear "Success" or "Pending Review" state. If the user is *not* logged in, they see a graceful prompt to log in, rather than a broken form or a 403 error.

**What it includes:**
*   The HTML form structure with appropriate input types and labels.
*   Client-side validation logic (e.g., non-empty fields, basic length checks) that prevents submission of invalid data.
*   The `requireUser` gate: the form is only rendered/interactive if the user is authenticated.
*   The `fetch` call to the backend endpoint (owned by Team 5) with the correct JSON payload shape.
*   State management for "submitting," "success," and "error" conditions.

**What has to be done:**
1.  **Coordinate with Team 5:** Confirm the exact endpoint URL and the expected JSON payload shape (field names, types) before writing the `fetch` call. Do not guess the API contract.
2.  **Implement the Auth Gate:** Wrap the form component in a check for `requireUser`. If the user is not authenticated, render a "Log in to propose a quote" message with a link to the auth flow.
3.  **Build the Form:** Create the UI fields. Use semantic HTML (`<form>`, `<label>`, `<input>`).
4.  **Add Validation:** Implement client-side validation to catch obvious errors (empty fields) before hitting the network.
5.  **Handle Submission:** On submit, disable the button, show a loading state, send the `POST` request, and handle the response (success message or error display).

## 4. Success criteria (functional)

*   **Auth Gate Works:** The form is **not** visible or interactive to unauthenticated users. The `requireUser` check is present and functional.
*   **Payload Correctness:** The `POST` request sent to the Team 5 endpoint contains the correct field names and values as agreed upon in coordination.
*   **Validation Prevents Bad Data:** Submitting an empty form or a form with missing required fields triggers client-side validation errors and does **not** send a network request.
*   **State Feedback:** The user sees a distinct visual state for "Submitting," "Success," and "Error."
*   **No Backend Changes:** This task does **not** modify `services/backend/**` or `ttod.yml`. It only consumes the endpoint.

## 5. Quality criteria (the part that's new)

*   **Code Organization:** The form logic should be encapsulated in a reusable component or a dedicated script file, not inline in the Astro page template if it grows beyond simple HTML. Keep the "auth check" and "form submission" logic separate for clarity.
*   **AI-Use/Process Documentation:** Document the coordination with Team 5. Include a comment or a note in your PR description stating the agreed-upon API contract (endpoint, fields). This is critical for cross-team tasks.
*   **Test Shape (R7 Trophy-not-Pyramid):**
    *   **Unit Test:** Mock the `fetch` API and `requireUser`. Test that the form submits the correct payload when valid. Test that validation prevents submission when invalid.
    *   **Integration Test:** (If feasible) Test that the form is hidden when `requireUser` returns false.
    *   *Link:* [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/)
*   **Accessibility:**
    *   All form inputs must have associated `<label>` elements.
    *   Error messages must be linked to the input via `aria-describedby` or similar ARIA attributes.
    *   The "Success" state must be announced to screen readers (e.g., via `aria-live="polite"`).
    *   *Inherits the global Definition of Done:* keyboard-operable, one accessible name or label, no meaning carried by color alone, respects reduced-motion preferences.
*   **Oral Defense:** Be prepared to explain *why* you coordinated with Team 5 before building. Explain how you handled the "not logged in" case without breaking the user experience. Explain your choice of client-side validation vs. relying solely on server-side validation.

## Closing

> "The module that knows its boundaries serves the whole. The module that knows no boundaries becomes the whole—and collapses under its own weight."
> — TTOD `arch-001`, *architecture*

This task is a perfect example of modular boundaries: your form (Content team) must respect the API contract (Accounts team) without trying to implement the review pipeline itself. Knowing where your module ends and the next one begins is what makes the system robust.