---
title: "Empty-state and error-state handling for content routes"
seam: content
team_number: 1
team_name: "Content, i18n & Proposals UI"
task_number: 3
area: "Content"
verb: keep
layout: default
lang: en
alt_lang_missing: true
---

# Assignment — Team 1, Task 3: Empty-state and error-state handling for content routes

**Seam:** content · **Team:** 1 · **Task:** 3 of ~10
**Area(s):** Content · **Verb served:** keep

## 1. Curriculum map

This task exercises the core principles of **Unit 5 — Testing strategy** (specifically the discipline of testing edge cases and failure modes) and **Unit 3 — Routing and Layouts** (ensuring layouts remain robust when content is absent).

*   [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/)
*   [Unit 3 — Routing and Layouts](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-3-routing-layouts/)

## 2. Worked example, from the real TTOD app

The current implementation in `services/frontend/src/pages/[locale]/wisdom/index.astro` and `services/frontend/src/pages/[locale]/wisdom/[slug].astro` assumes the presence of data. The `fetchWisdom(locale)` function in `services/frontend/src/content/wisdom.ts` returns a `WisdomEntry[]`. Currently, if this array is empty, or if the fetch fails, the routes render a blank page or throw an unhandled exception.

The "worked example" for this task is the **absence** of a guard. You will observe that `services/frontend/src/pages/[locale]/wisdom/index.astro` iterates directly over the fetched entries. Your task is to introduce the missing layer: a conditional branch that checks `entries.length === 0` and a `try/catch` block (or equivalent error boundary) that catches network failures from `fetchWisdom`.

## 3. What "done" looks like

**Visible result:**
A facet with zero matching entries shows a clear, styled empty state — never a blank page or an unhandled error. If the backend is unreachable, the user sees a real, human-readable error message, not a stack trace.

**What it includes:**
*   A single, reusable empty-state component or pattern (e.g., `<EmptyState />` or a shared partial) that is applied consistently across all content routes.
*   Application of this pattern to the index route (`services/frontend/src/pages/[locale]/wisdom/index.astro`).
*   Application of this pattern to the detail route (`services/frontend/src/pages/[locale]/wisdom/[slug].astro`) for the case where a specific slug does not exist in the current locale’s payload.
*   An error-state handler that catches failures from `fetchWisdom` in `services/frontend/src/content/wisdom.ts` and renders a localized error message.

**What has to be done:**
1.  Design one empty-state pattern that respects the existing design system (colors, typography, spacing).
2.  Apply this pattern to `services/frontend/src/pages/[locale]/wisdom/index.astro` when `entries.length === 0`.
3.  Apply this pattern to `services/frontend/src/pages/[locale]/wisdom/[slug].astro` when the requested `slug` is not found in the `entries` array.
4.  Wrap the `fetchWisdom` call in a `try/catch` block (or use Astro’s error handling mechanisms) to catch network errors.
5.  Render a localized error message in both `en` and `es` locales when the fetch fails.
6.  Ensure the empty/error states are keyboard-operable and have accessible names.

## 4. Success criteria (functional)

*   **Empty state visibility:** When `fetchWisdom` returns an empty array for a given locale, the index route displays a styled empty-state message instead of a blank page.
*   **Detail route 404 handling:** When a user navigates to a `/{locale}/wisdom/[slug]` that does not exist in the current locale’s payload, the route displays a styled "not found" or empty-state message instead of a blank page or crash.
*   **Error state visibility:** When `fetchWisdom` throws an error (e.g., network failure), the route displays a localized error message instead of a stack trace or blank page.
*   **Locale consistency:** The empty and error states are displayed in both `en` and `es` locales, using the correct language for the current `Astro.params.locale`.
*   **No regression:** When `fetchWisdom` returns a non-empty array, the index and detail routes continue to render the real backend data as before.

## 5. Quality criteria (the part that's new)

*   **Code organization:** The empty-state and error-state logic should be encapsulated in a reusable component or partial, not duplicated inline in each route. This follows the principle of **DRY** (Don't Repeat Yourself) and ensures consistency.
*   **AI-use/process documentation:** Document your decision on how to handle the error state (e.g., `try/catch` vs. Astro’s `error.astro` page) in your commit message or a brief note in your PR description. Explain why you chose this approach.
*   **Test shape:** Write unit tests for the empty-state component and the error-handling logic. Use a mocking library to simulate `fetchWisdom` returning an empty array and throwing an error. Verify that the correct localized message is rendered. Link to [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/) for the testing doctrine.
*   **Accessibility:** The empty and error states must be keyboard-operable, have one accessible name or label, no meaning carried by color alone, and respect reduced-motion preferences. Cite the **Accessibility Definition of Done** rather than restating it as task-specific.
*   **Oral defense:** Be prepared to explain why you chose a client-side empty state over a server-side 404 page for the detail route. Discuss the trade-offs of catching errors in the component vs. using Astro’s global error handling.

## Closing

> "The 404 page with no image is like a garden with no flowers — technically complete, spiritually empty."
> — TTOD `img-009`, *images*

This quote underscores the importance of designing for the empty state: a blank page is not just a technical failure, but a missed opportunity to guide the user and maintain the aesthetic integrity of the application.