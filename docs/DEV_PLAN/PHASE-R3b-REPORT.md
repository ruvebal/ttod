# Phase R3b Report — Astro content engine

**Status: DONE**

Implementation and all executable R3b gates are green. A memory-independent cold review completed
with no implementation-blocking finding.

## Delivered content and routes

- Typed Astro `docs` collection with bilingual MDX frontmatter validation.
- Paired English and Spanish “Walking the path / Caminar el sendero” editorial pages.
- Zero-client-JavaScript docs index and catch-all document routes.
- Backend-fed wisdom index, detail, section, level, and tag routes.
- Strict route-locale filtering through `WisdomEntry.lang`.
- Honest localized Spanish empty states across every wisdom route while the accepted corpus remains
  English-only. `/es/wisdom/img-001/` does not display the English record.
- Live-derived section, level, and tag counts; no corpus count is embedded in source.
- Attribution on every rendered quotation using the backend-provided holder and license.
- Tailwind v4 theme tokens, the typography plugin for MDX prose, and reusable CSS custom properties.

## Gate evidence

| Gate | Evidence |
| --- | --- |
| Rights filter | The only quote source is `BACKEND_URL/api/v1/wisdom/sample`; static scan found no `ttod.yml` or export read under R3b paths. |
| i18n | Live matrix returned HTTP 200 for docs index/detail and wisdom index/detail/section/level/tag routes under both `/en/` and `/es/`. Spanish wisdom responses all contained `Todavía no hay sabiduría aceptada en español.` |
| Counts never hardcoded | `frequencies()` derives section/level/tag counts from the request-time backend payload after locale filtering. Static scan found no hardcoded quote-count prose. |
| License | Live English index and detail responses contained `CC-BY-NC-SA-4.0`; every quote card/detail template emits holder and license. |
| Integration test shape | Verification ran the built Node SSR artifact against a real local R1 backend and asserted rendered HTML across 14 locale/route combinations. |
| Content/build | `astro check` reported 0 errors, warnings, or hints. `astro build` completed successfully with the Node adapter, MDX, and Tailwind Vite integration. |

Representative final route matrix:

```text
200 en/docs                    200 es/docs
200 en/docs/introduction       200 es/docs/introduction
200 en/wisdom                  200 es/wisdom
200 en/wisdom/img-001          200 es/wisdom/img-001
200 en/wisdom/sections/images  200 es/wisdom/sections/images
200 en/wisdom/levels/beginner  200 es/wisdom/levels/beginner
200 en/wisdom/tags/optimization 200 es/wisdom/tags/optimization
content assertions: OK
```

## Cold review

A separate agent inspected R3b against §5 and §7 with no edits. It confirmed: the only quote source
is R1's rights-filtered endpoint; locale filtering is immediate; Spanish routes are honestly empty;
counts derive from filtered live entries; every quote-rendering template emits holder and license;
EN/ES MDX are paired; built route-manifest entries carry `scripts: []`; and no R3b route reads a
canonical/export file, uses a client directive, or edits `domain.ts`.

The implementation self-audit had already found and fixed two issues before that handoff:

1. List/index cards initially omitted per-quote attribution; holder and license now appear on every
   template that renders quote text.
2. The Spanish individual route initially returned a bare localized 404 for an English ID; it now
   resolves to the same explicit Spanish empty-state page as the other Spanish wisdom routes.

Structural finding: the runbook names `src/content/config.ts` and permits `src/content/**`, while
Astro 5 recognizes `src/content.config.ts`. The checked, working implementation necessarily uses the
latter. The master/runbook touched-path wording must be amended to authorize that real Astro 5 path;
this was escalated to the plan owner and is not an implementation defect. The reviewer also noted
that the 14-route matrix is manual live integration evidence rather than a committed R3b test; R7
should automate it.

## Files touched

- `services/frontend/src/content.config.ts`
- `services/frontend/src/content/wisdom.ts`
- `services/frontend/src/content/docs/en/introduction.mdx`
- `services/frontend/src/content/docs/es/introduction.mdx`
- `services/frontend/src/pages/[locale]/docs/index.astro`
- `services/frontend/src/pages/[locale]/docs/[...slug].astro`
- `services/frontend/src/pages/[locale]/wisdom/index.astro`
- `services/frontend/src/pages/[locale]/wisdom/[slug].astro`
- `services/frontend/src/pages/[locale]/wisdom/sections/[section].astro`
- `services/frontend/src/pages/[locale]/wisdom/levels/[level].astro`
- `services/frontend/src/pages/[locale]/wisdom/tags/[tag].astro`
- `services/frontend/src/styles/tokens.css`
- `services/frontend/tailwind.config.mjs`
- `docs/DEV_PLAN/PHASE-R3b-REPORT.md`

## Lessons for the next phase

- R6 must preserve request-time locale filtering; Spanish editorial documentation exists, but no
  accepted Spanish wisdom record exists yet.
- The CSS tokens and Tailwind `ttod-*` theme names are the shared visual vocabulary for later
  islands and PWA polish.
- R3b is a green R6 dependency. R7 should turn the live route matrix into durable automation.
