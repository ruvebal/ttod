---
title: Dev sprint & hackathon timeline
eyebrow: Three weeks of build, three PR reviews, then Unit 7
description: How the five teams' task boards land across a three-week dev sprint — the third week run as a four-hour hackathon — with three PR-review checkpoints before Unit 7 measures the app.
permalink: /teaching/timeline/
lang: en
alt_lang_missing: true
---

# Dev sprint & hackathon timeline

The [team task board]({{ '/teaching/assignments/' | relative_url }}) says *what* each team builds.
This page says *when* — three weeks of development, the third run as a four-hour hackathon, three
PR-review checkpoints along the way, then [Unit 7](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-7-performance/)
measures the app the cohort has actually built.

> "Ship the module when it works alone. Ship the system when the modules work together. Ship the
> platform when the systems compose without speaking."
> — TTOD `arch-007`, *architecture*

## Where this sits in the course

Three short sessions — welcome, kickoff, and a session that reached
[Unit 3](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-3-astro-advanced/) — are
already behind the cohort. What follows replaces three separate weekly content sessions for
[Unit 4](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-4-pwa-offline/),
[Unit 5](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/), and
[Unit 6](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-6-ai-code-review/) with
one continuous sprint. All three are fully published lessons — this isn't skipping content, it's
folding lecture time that was already mostly lab (per each unit's own hour split) into the sprint
itself, removing the session boundary rather than the material.

| Stage | Focus | Format |
| --- | --- | --- |
| Done | Welcome, kickoff, Units 2–3 | three 2-hour sessions |
| Dev Week 1 | Foundations | 4h, light framing |
| Dev Week 2 | Core features | 4h, mostly lab |
| Dev Week 3 — **Hackathon** | Breadth: tests, cross-module PRs, design decisions | 4h, zero lecture |
| [Unit 7](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-7-performance/) | Measure the built app | 4h — Core Web Vitals, budgets |
| Defense | Oral "diff review" | a distinct event, not a content session |

## The one hard dependency

Team 5's propose-a-quote **endpoint** and Team 1's propose-a-quote **form** are two halves of the
same feature, owned by different teams — the form posts to the endpoint. That ordering only works
one way: **the endpoint's request shape has to exist before the form can be built against it.**
Everything else across the five teams is parallel-safe.

## Week by week

Every one of the 49 real tasks across the five boards lands somewhere below — nothing is left
unscheduled. Solos (Graph, PWA) carry three tasks a week; pairs (Content, Oracle, Accounts) split
three a week across two people.

### Dev Week 1 — foundations, and the one blocker

Draws on [Unit 4](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-4-pwa-offline/)
for PWA's own tasks this week.

| Team | This week |
| --- | --- |
| Content | [Section/tag/level browse routes]({{ '/teaching/tasks/content-task1/' | relative_url }}) · [breadcrumb navigation]({{ '/teaching/tasks/content-task2/' | relative_url }}) |
| Graph | [Fetch and render the graph, hardened]({{ '/teaching/tasks/graph-task1/' | relative_url }}) · [accessible node selection]({{ '/teaching/tasks/graph-task2/' | relative_url }}) · [tag-filter interaction]({{ '/teaching/tasks/graph-task3/' | relative_url }}) |
| Oracle | [Streamed response rendering, hardened]({{ '/teaching/tasks/oracle-task1/' | relative_url }}) · [live-region announcement]({{ '/teaching/tasks/oracle-task2/' | relative_url }}) · [session/exchange history]({{ '/teaching/tasks/oracle-task4/' | relative_url }}) |
| PWA | [Service-worker lifecycle correctness]({{ '/teaching/tasks/pwa-task1/' | relative_url }}) · [one observable offline boundary]({{ '/teaching/tasks/pwa-task2/' | relative_url }}) · [install-quality checks]({{ '/teaching/tasks/pwa-task5/' | relative_url }}) |
| **Accounts** | [Login/session, hardened]({{ '/teaching/tasks/accounts-task1/' | relative_url }}) · [personal favorites library]({{ '/teaching/tasks/accounts-task2/' | relative_url }}) · **[the propose-a-quote endpoint]({{ '/teaching/tasks/accounts-task3/' | relative_url }}) — priority, Content depends on this next week** |

### Dev Week 2 — core features, the form now unblocked

| Team | This week |
| --- | --- |
| Content | [Empty/error states]({{ '/teaching/tasks/content-task3/' | relative_url }}) · **[the propose form (now unblocked)]({{ '/teaching/tasks/content-task4/' | relative_url }})** · [rights & provenance display]({{ '/teaching/tasks/content-task5/' | relative_url }}) |
| Graph | [URL state for the current selection]({{ '/teaching/tasks/graph-task4/' | relative_url }}) · [layout and performance at real corpus scale]({{ '/teaching/tasks/graph-task5/' | relative_url }}) · [keyboard-operability audit]({{ '/teaching/tasks/graph-task6/' | relative_url }}) |
| Oracle | [Grounded vs. creative mode disclosure]({{ '/teaching/tasks/oracle-task3/' | relative_url }}) · [the "preparing" cold-start state]({{ '/teaching/tasks/oracle-task5/' | relative_url }}) · [recovery/error state]({{ '/teaching/tasks/oracle-task6/' | relative_url }}) |
| PWA | [Cache-first vs. network-first policy]({{ '/teaching/tasks/pwa-task3/' | relative_url }}) · [offline queue]({{ '/teaching/tasks/pwa-task4/' | relative_url }}) (coordinated with Oracle, who calls into it) · [measured performance budget]({{ '/teaching/tasks/pwa-task6/' | relative_url }}) |
| Accounts | [The GitHub-native review pipeline]({{ '/teaching/tasks/accounts-task4/' | relative_url }}) · [bearer-token public API]({{ '/teaching/tasks/accounts-task5/' | relative_url }}) · [docs and example client]({{ '/teaching/tasks/accounts-task6/' | relative_url }}) |

### Dev Week 3 — the Hackathon: breadth, not new depth

Every team closes the same four shared task types this week, now that two weeks of real feature
work make them genuine rather than a formality — each one is its own real task, not a generic
placeholder:

| Team | Tests | Open a PR | Review a PR | Design decision |
| --- | --- | --- | --- | --- |
| Content | [tests]({{ '/teaching/tasks/content-task6/' | relative_url }}) | [PR]({{ '/teaching/tasks/content-task7/' | relative_url }}) | [review]({{ '/teaching/tasks/content-task8/' | relative_url }}) | [taxonomy/fallback design]({{ '/teaching/tasks/content-task9/' | relative_url }}) |
| Graph | [tests]({{ '/teaching/tasks/graph-task7/' | relative_url }}) | [PR]({{ '/teaching/tasks/graph-task8/' | relative_url }}) | [review]({{ '/teaching/tasks/graph-task9/' | relative_url }}) | [layout/a11y design]({{ '/teaching/tasks/graph-task10/' | relative_url }}) |
| Oracle | [tests]({{ '/teaching/tasks/oracle-task7/' | relative_url }}) | [PR]({{ '/teaching/tasks/oracle-task8/' | relative_url }}) | [review]({{ '/teaching/tasks/oracle-task9/' | relative_url }}) | [state/disclosure design]({{ '/teaching/tasks/oracle-task10/' | relative_url }}) |
| PWA | [tests]({{ '/teaching/tasks/pwa-task7/' | relative_url }}) | [PR]({{ '/teaching/tasks/pwa-task8/' | relative_url }}) | [review]({{ '/teaching/tasks/pwa-task9/' | relative_url }}) | [caching/install design]({{ '/teaching/tasks/pwa-task10/' | relative_url }}) |
| Accounts | [tests]({{ '/teaching/tasks/accounts-task7/' | relative_url }}) | [PR]({{ '/teaching/tasks/accounts-task8/' | relative_url }}) | [review]({{ '/teaching/tasks/accounts-task9/' | relative_url }}) | [session/token design]({{ '/teaching/tasks/accounts-task10/' | relative_url }}) |

- **Unit and component tests** — closing remaining gaps, not starting from zero; the Testing
  Trophy doctrine ([Unit 5](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/))
  treats tests as pairing with each feature as it lands, so most of this should already be partly
  real.
- **Open one PR into a module you don't own, and formally review one PR outside your own module** —
  the direct test of the course's breadth requirement, run against the human-in-the-loop review
  discipline [Unit 6](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-6-ai-code-review/)
  teaches: AI may comment, never approve or merge — a human approves. Reviewing or contributing to
  a teammate's module only means something once that module has real, running code to read — which
  is exactly why this waits for the hackathon and not Week 1.
- **Document one real design decision** for the oral defense — the decision has to already exist
  to be worth documenting.

## Three PR reviews before Unit 7

Each checkpoint is scored against the same rubric — contract adherence, correctness, test
coverage, accessibility, CI status, and AI-disclosure honesty — but what's reasonable to expect
grows heavier as the sprint goes on.

**Checkpoint 1 — end of Week 1.** Is the one hard blocker actually gone? Specifically: does the
propose-endpoint contract exist, and is it documented well enough for the form to be built against
it next week?

**Checkpoint 2 — end of Week 2.** Is the board mostly real? By now most teams should have items
2 through 6 substantively shipped, not stubbed — this is where contract adherence and correctness
start scoring for real.

**Checkpoint 3 — end of the hackathon.** The heaviest pass: a full board, a genuine cross-module
contribution, and real test coverage across every team — the natural moment to review everything
before the cohort turns to measuring, not building, in the Unit 7 session that follows.

## Related course pages

- [Team task board]({{ '/teaching/assignments/' | relative_url }})
- [Task details — every task expanded]({{ '/teaching/tasks/' | relative_url }})
- [Teaching model]({{ '/teaching/' | relative_url }})
- [Unit 4 — PWA & Offline Capabilities](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-4-pwa-offline/)
- [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/)
- [Unit 6 — AI-Assisted Code Review](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-6-ai-code-review/)
- [Unit 7 — Performance](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-7-performance/)
