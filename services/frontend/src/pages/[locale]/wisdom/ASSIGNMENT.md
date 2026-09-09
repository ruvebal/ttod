# FE II · R3b assignment — faceted wisdom browse

Hello-world on this branch is **one localized index** and **one localized detail page**.
Both already fetch real `WisdomEntry` records from `GET /api/v1/wisdom/sample` via
`fetchWisdom(locale)` and render English and Spanish. Faceted taxonomy browsing is
**deliberately absent** — that is the assessed work, not a bug.

The instructor-removed routes (do not look for them on this branch):

| Deliverable | Hello-world state | Restore as |
| --- | --- | --- |
| Section browse | file removed | `pages/[locale]/wisdom/sections/[section].astro` |
| Tag browse | file removed | `pages/[locale]/wisdom/tags/[tag].astro` |
| Level browse | file removed | `pages/[locale]/wisdom/levels/[level].astro` |

`src/content/wisdom.ts` still exports `frequencies()`. Hello-world routes do not call it.
Your facet pages should.

---

## Learning outcomes

After this assignment you can:

1. **Dynamic file-based routes.** Add Astro pages whose filenames are the route contract
   (`[section]`, `[tag]`, `[level]`) and filter the same live `WisdomEntry[]` the index already
   fetched.
2. **i18n routing as a mandatory spine.** Every new browse URL exists under both `/en/` and
   `/es/`. Locale comes from `Astro.params.locale` and `isLocale()` — never from a hardcoded
   string.
3. **Content collections vs live corpus.** The `docs` collection in `content.config.ts` is
   markdown documentation. Wisdom is **not** a second collection: `ttod.yml` remains the single
   source of truth, exposed only through the backend sample endpoint.
4. **Semantic HTML for humanities content.** Quotations live in `<blockquote>` / `<article>`,
   browse pages expose headings and breadcrumbs, and attribution (`rights.holder`,
   `rights.license`) stays visible on every rendered entry.

---

## Constraints

- Reuse `fetchWisdom` and the frozen `WisdomEntry` type from `src/types/domain.ts` **exactly**.
  Do not widen, rename, or duplicate those shapes.
- Keep **both** locales working. A page that only exists in English fails the assignment.
- Filter client-side (or in the Astro frontmatter) from the payload `fetchWisdom` already
  returns. Do not add a new backend endpoint; do not edit `services/backend/**`.
- Prefer `frequencies(entries, 'section' | 'level' | 'tags')` for cluster counts rather than
  inventing a parallel counter.
- Do not read `ttod.yml`, `exports/`, or any static JSON dump of quotes.

---

## Acceptance criteria

1. **Section browse exists and is reachable** at `/{locale}/wisdom/sections/{section}/` for
   both `en` and `es`. It lists live entries whose `section` matches the param.
2. **Tag browse exists and is reachable** at `/{locale}/wisdom/tags/{tag}/` for both locales.
   It lists live entries whose `tags` include the param.
3. **Level browse exists and is reachable** at `/{locale}/wisdom/levels/{level}/` for both
   locales. It lists live entries whose `level` matches the param.
4. **Breadcrumbs** (or an equivalent `<nav>` trail) are present on each browse route: at least
   Home or Wisdom index → current facet value, with a working back link.
5. **One accessibility check per new route** (for example: unique `h1`, keyboard-reachable
   links, language on `<html>`, empty-state text when the facet has no entries in that locale).
   Record the check; do not claim it without running it.
6. Index and detail continue to render **real** backend data (not the localized empty-state
   copy) when the live sample payload contains entries for that locale.

---

## Prohibited shortcuts

- Do not hardcode a locale (`'en'` in a Spanish route, a single-locale `fetch`, or a link that
  drops `/{locale}/`).
- Do not bypass `fetchWisdom` with a static JSON file, a committed fixture, or an inlined
  array of quotes.
- Do not introduce an Astro content collection of wisdom markdown/YAML that shadows `ttod.yml`.
- Do not restore the missing routes by copying instructor-only reference history. Design the
  browse pages against this brief and the live payload.
- Do not edit `src/types/domain.ts`, `services/backend/**`, `ttod_core/**`, or `ttod.yml`.

---

## Extension choices (not prescribed)

How you wire counts, empty facets, and index cross-links is yours: pills vs lists, whether the
index calls `frequencies()` again, how breadcrumbs are marked up. The acceptance criteria name
the routes and the qualities; they do not name the implementation.
