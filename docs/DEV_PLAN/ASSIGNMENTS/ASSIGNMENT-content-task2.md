# Assignment — Team 1, Task 2: Breadcrumb navigation across all content routes

**Seam:** content · **Team:** 1 · **Task:** 2 of ~10
**Area(s):** Content · **Verb served:** keep

## 1. Curriculum map

This task exercises the **Semantic HTML for humanities content** learning outcome from the module's `ASSIGNMENT.md`, specifically the requirement that "browse pages expose headings and breadcrumbs." It also reinforces the **i18n routing as a mandatory spine** outcome, ensuring that navigation elements respect the `/{locale}/` prefix.

*Note: Specific web-atelier-udit FE II unit links for this exact task are not yet published in `assignments.md`'s "Lessons for these tasks" section. The curriculum grounding is derived directly from the module's own Learning Outcomes §4 and Acceptance Criteria §4.*

## 2. Worked example, from the real TTOD app

The current hello-world state includes `services/frontend/src/pages/[locale]/wisdom/index.astro` and `services/frontend/src/pages/[locale]/wisdom/[slug].astro`. These routes currently render content but lack a shared navigation trail. The `services/frontend/src/content/wisdom.ts` file exports `labels` and `frequencies()`, which will be used to generate the correct human-readable names for the breadcrumb segments (e.g., mapping a `section` slug to its localized label). The `WisdomEntry` type in `services/frontend/src/types/domain.ts` provides the `section`, `tags`, and `level` fields that define the hierarchy levels for the breadcrumb.

## 3. What "done" looks like

**Visible result:** Every content route (index, section/facet, and detail) displays a clear, consistent path back to the origin (e.g., `Wisdom → Section → Detail`), rather than relying on a flat browser back button.

**What it includes:**
*   A shared breadcrumb component or pattern (e.g., a `<nav aria-label="Breadcrumb">` block) that is reused across the index, facet (`[section]`, `[tag]`, `[level]`), and detail (`[slug]`) routes.
*   The breadcrumb hierarchy is designed to reflect the actual route structure: Home/Wisdom Index → Facet Value (if applicable) → Current Page.
*   The component is locale-aware, ensuring links within the breadcrumb respect the `/{locale}/` prefix.

**What has to be done:**
1.  Design the breadcrumb hierarchy logic once the facet routes exist (or are being built).
2.  Create a shared component (e.g., `components/Breadcrumbs.astro` or similar) that accepts the current route context and renders the appropriate trail.
3.  Wire this component into the layout of the index, facet, and detail routes.
4.  Ensure the breadcrumb is semantic HTML (`<nav>`, `<ol>`, `<li>`) and accessible.

## 4. Success criteria (functional)

*   **Breadcrumbs are present on each browse route:** At least Home or Wisdom index → current facet value, with a working back link (per Module AC4).
*   **Locale consistency:** Breadcrumb links correctly preserve the `/{locale}/` prefix for both `en` and `es` routes.
*   **Semantic structure:** The breadcrumb uses `<nav>` with an `aria-label` and an ordered list (`<ol>`) structure.
*   **Integration:** The breadcrumb is visible and functional on the index, section, tag, level, and detail routes.

## 5. Quality criteria (the part that's new)

*   **Code organization:** The breadcrumb logic is encapsulated in a single, reusable component. Do not duplicate the breadcrumb HTML in every route file.
*   **Accessibility:** The breadcrumb must be keyboard-operable, have one accessible name or label (`aria-label="Breadcrumb"`), and not carry meaning by color alone. It must respect reduced-motion preferences if any transitions are added. (Citing the global Accessibility Definition of Done).
*   **Testing:** Verify that the breadcrumb links resolve correctly for both locales. Ensure that the `aria-current="page"` attribute is applied to the last item in the trail. [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/)
*   **Oral defense:** Be prepared to explain why a shared component was chosen over inline HTML, and how the component handles the different depth levels (index vs. facet vs. detail).

## Closing

> "The best interface is no interface."
> — TTOD `ux-002`, *ux*

This quote reminds us that navigation should be intuitive and unobtrusive; a well-designed breadcrumb helps users orient themselves without demanding their attention, allowing them to focus on the content.