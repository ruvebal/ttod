---
title: "Source, rights, and provenance display on every quote page"
seam: content
team_number: 1
team_name: "Content, i18n & Proposals UI"
task_number: 5
area: "Content"
verb: keep
layout: default
lang: en
alt_lang_missing: true
---

# Assignment — Team 1, Task 5: Source, rights, and provenance display on every quote page

**Seam:** content · **Team:** 1 · **Task:** 5 of ~10
**Area(s):** Content · **Verb served:** keep

## 1. Curriculum map

This task exercises **FE II Unit 4 — Semantic HTML & Accessibility**, specifically the requirement that attribution (`rights.holder`, `rights.license`) remains visible on every rendered entry. It also reinforces **FE II Unit 3 — Content Routing & i18n**, ensuring that provenance data travels with the content across both `/en/` and `/es/` routes without locale-specific hardcoding.

## 2. Worked example, from the real TTOD app

The existing detail route at `services/frontend/src/pages/[locale]/wisdom/[slug].astro` already fetches `WisdomEntry` records via `fetchWisdom(locale)`. The `WisdomEntry` type in `services/frontend/src/types/domain.ts` includes `rights` and `origin` fields. Currently, the detail page renders the quote text but does not consistently surface the `rights.holder`, `rights.license`, or `origin` fields in a dedicated, accessible provenance block. This task extends that existing pattern to all content views (index cards, facet listings, detail page) using the same data source.

## 3. What "done" looks like

**Visible result:** Every quote page visibly shows its holder, license, and origin — not just the text.

**What it includes:**
- A compact, accessible provenance block component that displays `rights.holder`, `rights.license`, and `origin` from the `WisdomEntry` object.
- Application of this block to:
  - Index cards on `services/frontend/src/pages/[locale]/wisdom/index.astro`
  - Facet listings (section, tag, level browse pages)
  - Detail page on `services/frontend/src/pages/[locale]/wisdom/[slug].astro`
- No new fetch calls or backend endpoints; the data is already present in the `WisdomEntry` payload returned by `fetchWisdom`.

**What has to be done:**
1. Design a reusable provenance block component (e.g., `<ProvenanceBlock />`) that accepts a `WisdomEntry` and renders the rights and origin fields.
2. Ensure the block is accessible:
   - Use semantic HTML (`<dl>`, `<dt>`, `<dd>` or equivalent) for label-value pairs.
   - Ensure keyboard operability and screen reader compatibility.
   - Do not rely on color alone to convey meaning.
3. Integrate the component into all three view types (index, facet, detail).
4. Verify that both `/en/` and `/es/` locales render the provenance block correctly, using the same data source.
5. Test that the block handles missing or null `rights` or `origin` fields gracefully (e.g., hide the block or show a placeholder if data is absent).

## 4. Success criteria (functional)

1. **Provenance visible on index cards:** Each quote card on the wisdom index page displays the holder, license, and origin from the `WisdomEntry` object.
2. **Provenance visible on facet listings:** Each quote entry on section, tag, and level browse pages displays the holder, license, and origin.
3. **Provenance visible on detail page:** The quote detail page displays the holder, license, and origin in a clearly labeled block.
4. **Both locales work:** The provenance block renders correctly on both `/en/` and `/es/` routes, using the same data source.
5. **No new backend calls:** The provenance data is sourced from the existing `fetchWisdom` payload; no new API endpoints or static files are introduced.
6. **Graceful handling of missing data:** If `rights` or `origin` is null or undefined, the block either hides itself or displays a clear placeholder without breaking the layout.

## 5. Quality criteria (the part that's new)

- **Code organization:** The provenance block is a single, reusable component (e.g., `src/components/ProvenanceBlock.astro`) that is imported and used consistently across all three view types. No duplication of provenance rendering logic.
- **AI-use/process documentation:** Document the design decision to use a shared component for provenance display, including why this approach was chosen over inline rendering. Note any trade-offs (e.g., component size vs. reusability).
- **Test shape:** Per the Testing Trophy (not Pyramid) doctrine, write one integration test that verifies the provenance block renders correctly on the detail page with a real `WisdomEntry` fixture. Unit tests for the component itself are optional if the integration test covers the behavior.
- **Accessibility:** The provenance block must meet the [Accessibility Definition of Done](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/): keyboard-operable, one accessible name or label, no meaning carried by color alone, respects reduced-motion preferences. Use semantic HTML (`<dl>`, `<dt>`, `<dd>`) for label-value pairs.
- **Defensible oral-defense answer:** "I created a single, reusable provenance block component that displays the holder, license, and origin from the `WisdomEntry` object. I applied it consistently across the index, facet, and detail pages to ensure that attribution is always visible, as required by the module's acceptance criteria. I used semantic HTML to ensure accessibility and tested that the block handles missing data gracefully."

## Closing

> "Content precedes design. Design in the absence of content is not design, it is decoration."
> — TTOD `cc-009`, *code-craft*

This task ensures that the provenance data (holder, license, origin) is treated as first-class content, not an afterthought, by making it visible and accessible on every quote page.