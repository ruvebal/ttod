---
title: "Unit and component tests for content routes and the propose form"
seam: content
team_number: 1
team_name: "Content, i18n & Proposals UI"
task_number: 6
area: "Testing"
verb: keep
layout: default
lang: en
---

# Assignment — Team 1, Task 6: Unit and component tests for content routes and the propose form

**Seam:** content · **Team:** 1 · **Task:** 6 of ~10
**Area(s):** Testing · **Verb served:** keep

## 1. Curriculum map

This task exercises the testing strategies covered in [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/). Specifically, it applies the "Trophy-not-Pyramid" doctrine to select the cheapest layer of testing that provides real confidence, ensuring that unit tests are used for pure logic and component tests for rendering behavior, rather than defaulting to heavy E2E tests.

## 2. Worked example, from the real TTOD app

The natural target for the unit test layer is the `frequencies(entries, field)` function exported from `services/frontend/src/content/wisdom.ts`. This is a pure function that takes an array of `WisdomEntry` objects (defined in `services/frontend/src/types/domain.ts`) and a field name (`'section' | 'level' | 'tags'`), returning a count of occurrences. Because it is pure and already exported, it is the ideal candidate for a unit test that verifies the filtering logic without requiring a browser or network environment.

For the component test layer, the existing localized detail route at `services/frontend/src/pages/[locale]/wisdom/[slug].astro` serves as the reference pattern. While this specific task focuses on testing the *propose form* (which is a new UI element to be built in Task 4), the testing approach mirrors how one would test the rendering of the detail page: verifying that the component renders the expected DOM structure (e.g., `<form>` elements, input fields) and that it correctly handles state changes (e.g., validation errors) without submitting to the backend.

## 3. What "done" looks like

**Visible result:**
Content routes and the propose form each have at least one real test, wired into the same CI job every other module's tests run in.

**What it includes:**
- One unit test targeting a pure content-filtering function (specifically `frequencies()` from `services/frontend/src/content/wisdom.ts`).
- One component test targeting a rendered route or the propose form UI, verifying DOM structure and basic interaction logic.
- Both tests are integrated into the existing CI pipeline, ensuring they run alongside other module tests.

**What has to be done:**
1. Identify the cheapest layer that gives real confidence for each target.
2. Write a unit test for `frequencies()` that verifies it correctly counts entries by the specified field.
3. Write a component test for the propose form (or a representative content route) that verifies it renders the expected form elements and handles basic state changes.
4. Ensure both tests are wired into the CI job so they run automatically on every commit.

## 4. Success criteria (functional)

1. A unit test for `frequencies()` exists and passes, verifying that it correctly counts entries by the specified field (`'section'`, `'level'`, or `'tags'`).
2. A component test for the propose form (or a content route) exists and passes, verifying that the expected DOM structure is rendered and that basic interaction logic (e.g., validation) works as intended.
3. Both tests are wired into the CI job and run successfully alongside other module tests.

## 5. Quality criteria (the part that's new)

- **Code organization:** Tests are colocated with the code they test or follow the project's established test directory structure. Test files are named clearly to reflect the module and function/component under test.
- **AI-use/process documentation discipline:** Any AI assistance used in writing the tests is documented in the commit message or PR description, explaining what was generated and what was manually verified.
- **Test shape per R7's Trophy-not-Pyramid doctrine:** The tests follow the "Trophy" shape, with a broad base of unit tests for pure logic and a narrower top of component tests for rendering behavior. No heavy E2E tests are used for what can be covered by unit or component tests.
- **Accessibility:** The component test verifies that the propose form is keyboard-operable, has accessible names or labels, does not carry meaning by color alone, and respects reduced-motion preferences, as per the project's Definition of Done.
- **Defensible oral-defense answer:** A student can explain why they chose unit tests for `frequencies()` (pure function, no side effects) and component tests for the form (rendering behavior, state management), and how this aligns with the Trophy-not-Pyramid doctrine. They can also explain how the tests are wired into CI and how they ensure the tests are not just passing but actually verifying the intended behavior.

## Closing

> "The path to mastery begins with reading. The path to enlightenment continues with practice."
> — TTOD `qa-008`, *qa-tooling*

This task embodies the principle that testing is not just about writing code but about practicing the discipline of verifying that code works as intended, ensuring that the path to mastery in testing is paved with consistent, well-structured tests.