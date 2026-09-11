---
title: "Section, tag, and level browse routes"
seam: content
team_number: 1
team_name: "Content, i18n & Proposals UI"
task_number: 1
area: "Content"
verb: find
layout: default
lang: en
alt_lang_missing: true
---

# Assignment — Team 1, Task 1: Section, tag, and level browse routes

**Seam:** content · **Team:** 1 (Content, i18n & Proposals UI — pair) · **Task:** 1 of ~10
**Area(s):** Content · **Verb served:** find

## 1. Curriculum map

[Unit 3 — Astro advanced](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-3-astro-advanced/)
— content collections, i18n routing, and data fetching, worked entirely through TTOD's own source
code. This is a prerequisite for this exact task, named as such on
`docs/public/teaching/assignments.md`'s own "Lessons for these tasks" section. Unit 2 (routing and
layouts) is the prerequisite before that, for every team's own task 1.

## 2. Worked example, from the real TTOD app

The starting point is not hypothetical — it is the real hello-world already on the reference implementation:

- `src/pages/[locale]/wisdom/index.astro` and `.../[slug].astro` already call
  `fetchWisdom(locale)` and render real `WisdomEntry[]` records in `en`/`es` — read these two
  files first, this task extends their pattern, it does not start from nothing.
- `src/content/wisdom.ts` exports `frequencies(entries: WisdomEntry[], field: 'section' | 'level'
  | 'tags')` (confirmed at line 31 of that file) — already written, **not yet called by any
  route**. This task's whole job is building the three routes that call it.
- The three route files this task adds do not exist on the reference implementation — they were the instructor's own
  deliberate removal, named explicitly in `wisdom/ASSIGNMENT.md`'s "instructor-removed routes"
  table, not an oversight to work around.

## 3. What "done" looks like

**Visible result:** three working routes — `/{locale}/wisdom/sections/{section}/`,
`/{locale}/wisdom/tags/{tag}/`, `/{locale}/wisdom/levels/{level}/` — each filtering the same live
payload the index route already fetches, reachable in both `en` and `es`.

**What it includes:** three new Astro dynamic routes, a facet-list UI element (pills, list, or
equivalent — not prescribed), and a breadcrumb trail back to the wisdom index (breadcrumbs
themselves are Task 2's own scope on `docs/public/teaching/tasks.md` — this task only needs a
working back-link, not the full breadcrumb component).

**What has to be done:** call `frequencies()` from each new route to compute the facet's own
count/list where relevant, filter the already-fetched `WisdomEntry[]` by the route's own param
(`section`, `tag` in `tags`, or `level`), and render an empty state when a facet has zero matches
in that locale — not a blank page.

## 4. Success criteria (functional)

Reused directly from `wisdom/ASSIGNMENT.md`'s own Acceptance criteria — this task closes items 1–3
and the "real data" clause of item 6; items 4–5 (breadcrumbs, the explicit accessibility check) are
this same module's Task 2 and a cross-cutting requirement respectively, not re-litigated here:

1. Section browse reachable at `/{locale}/wisdom/sections/{section}/`, both locales, lists live
   entries whose `section` matches the param.
2. Tag browse reachable at `/{locale}/wisdom/tags/{tag}/`, both locales, lists live entries whose
   `tags` includes the param.
3. Level browse reachable at `/{locale}/wisdom/levels/{level}/`, both locales, lists live entries
   whose `level` matches the param.
4. Index and detail routes continue rendering real backend data, not localized empty-state copy,
   for any locale where the live sample payload actually has entries.

## 5. Quality criteria (the part that's new)

- **Reuse discipline, not reinvention.** `frequencies()` is called, not reimplemented as an inline
  filter — a review that finds a hand-rolled facet counter next to an unused `frequencies()`
  import is a quality failure, not a style nitpick, per `wisdom/ASSIGNMENT.md`'s own "prefer
  `frequencies()`... rather than inventing a parallel counter" constraint.
- **i18n as structural, not cosmetic.** Locale comes from `Astro.params.locale` and `isLocale()` —
  a route that works in `en` and silently 404s or shows English copy in `es` fails this task
  regardless of whether the `en` acceptance criteria pass.
- **Test shape.** Per [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/)
  and the Testing Trophy (not Pyramid) doctrine on the reference build: an integration/component test
  that a real facet route renders real filtered data is worth more here than a unit test of
  `frequencies()` itself (already tested where it's defined). This task's own dedicated testing
  task (Team 1, Task 7) owns the full suite; this bullet is the bar *this* task's own code should
  already meet before Task 7 formalizes it.
- **Accessibility — inherited, not task-specific.** Every module task inherits the same
  Definition of Done from `docs/public/teaching/assignments.md`: keyboard-operable, one
  accessible name/label, no meaning by color alone, respects reduced motion. Cite that inherited
  bar in review; do not restate it as if this task invented an accessibility requirement.
- **Oral-defense bar.** A defensible answer names the exact `frequencies()` call site, explains
  why filtering happens against the already-fetched payload rather than a new endpoint (the
  module's own constraint against editing `services/backend/**`), and can show the empty-state
  render live, not describe it from memory.

## Closing

> "The best navigation is one you forget is there—until you need it."
> — TTOD `arch-016`, *architecture*

A facet route that makes a visitor stop and think about the router, rather than about which
quotes actually match their tag, has already missed the point of this task.
