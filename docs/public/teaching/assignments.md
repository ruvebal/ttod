---
title: Assignments and backlog
eyebrow: What you build, for whom, and why
description: Personas, user journeys, the epic-by-epic assignment backlog, and the accessibility commitment behind TTOD's six teaching areas.
permalink: /teaching/assignments/
---

# What you build, for whom, and why

The [teaching model]({{ '/teaching/' | relative_url }}) page says how the six areas map to course
units. This page says why each one matters and what "done" looks like — a backlog in product
terms, not just an engineering task list.

## Who TTOD serves

| Persona | What they want |
| --- | --- |
| Visitor | Find a fragment of wisdom relevant to a moment, with no friction and no signup |
| Registered reader | Keep a personal library of quotes worth returning to |
| Contributor | Add a quote they believe belongs in the corpus |
| Reviewer | Judge proposals with the same tools already trusted for code review |
| External developer | Build something on top of TTOD's data without scraping HTML |

There is no separate "accessibility persona." Every story below inherits the same accessibility
commitment regardless of which persona it serves — see [Why accessibility is a
commitment](#why-accessibility-is-a-commitment-not-a-checklist).

## Four verbs

Every assignment in this backlog is one of four verbs, done for one persona: **find**, **keep**,
**question**, **contribute**. If a feature doesn't serve one of those four for a named persona, it
doesn't belong on the backlog.

## User journeys

**A visitor finds a quote that fits their moment.** Lands on the homepage → browses by section,
tag, or level → opens the knowledge graph and follows a connection → asks the Oracle a real
question → reads a quote-grounded answer → notices the invitation to log in and save it.

**A registered reader builds a personal library.** Logs in → returns to a quote page → saves it →
comes back later, opens their library → removes one that no longer fits.

**A contributor proposes a new quote.** Logs in → opens the propose form → submits a quote with
its source → the system opens a review request → a human reviewer reads it and may ask for
changes → the contributor revises → the quote goes live, credited to them. The wait for review is
deliberate, not friction to remove — only a named human ever accepts a quote into the governed
collection.

**A reviewer processes a proposal.** Sees the request in the normal review queue → reads the
proposed quote and its source → comments, requests changes, or approves → approval computes the
exact change to the governed collection → a second look at that specific change is what actually
publishes it. Two touchpoints, not one — approving the idea and approving the exact diff are kept
separate on purpose.

**An external developer integrates the public API.** Reads the API documentation → creates an
account, logs in → requests an access token → calls the API with it → gets back a quote.

## The backlog, by area

Every story below carries the same Definition of Done: keyboard-operable, one accessible name or
label, no meaning carried by color alone, respects reduced-motion preferences. That isn't repeated
per item — it's not optional for any of them.

**Browse & discover** — a visitor can browse by section, tag, or level in their language; every
quote page shows its source and context; breadcrumbs lead back to where you came from.

**Explore relationships** — a visitor can see how quotes relate to each other in a graph; a
keyboard or screen-reader user gets every graph selection reflected as accessible text, not just a
visual highlight.

**Ask the Oracle** — a visitor can ask a real question and get a quote-grounded answer, streamed
in as it's generated; a screen-reader user gets that streaming answer announced as it arrives, not
silence until it's done; a cold-started deployment shows a "preparing" state instead of hanging
quietly.

**Take it offline** — previously seen content keeps working without a connection; the app can be
installed like a native one.

**Make it mine** — a visitor can create an account and log in; a registered reader can save and
remove quotes from a personal library.

**Contribute wisdom** — a registered reader can propose a new quote; a contributor can see their
proposal's status; a reviewer can review proposals with the same tools already used for code;
only a named human's approval ever writes the governed collection — no automation, AI included,
ever does that silently.

**Build on TTOD** — an external developer gets a documented, token-authenticated API and a small
working example client, proof the API works outside the browser, not just inside this app's own
UI.

## Team task board

Eight students, five teams — three pairs on the richest, most contract-heavy areas; two solos on
the two most bounded ones. Every team's list below runs ~10 tasks, tagged by which of the six
areas each one actually touches: your own area is depth, the others are the breadth this course
explicitly grades (see [Why accessibility is a commitment](#why-accessibility-is-a-commitment-not-a-checklist)
for why the testing/accessibility tag applies to every row, every team, not just one).

### Team 1 — Content, i18n & Proposals UI (pair)

| # | Task | Area(s) |
| - | --- | --- |
| 1 | Build the localized wisdom index and detail routes (`en` + `es`) | Content |
| 2 | Section, tag, and level browse routes | Content |
| 3 | Breadcrumb navigation across all content routes | Content |
| 4 | Empty-state and error-state handling for content routes | Content |
| 5 | Build the "propose a quote" form UI — posts to the endpoint Team 5 owns | Content, Accounts |
| 6 | Source, rights, and provenance display on every quote page | Content |
| 7 | Unit and component tests for content routes and the propose form | Testing |
| 8 | Open one PR into a module you don't own | Cross-module |
| 9 | Formally review one PR outside your own module | Cross-module |
| 10 | Document one real design decision (taxonomy, fallback policy) for the oral defense | Process |

### Team 2 — Knowledge Graph (solo)

| # | Task | Area(s) |
| - | --- | --- |
| 1 | Fetch and render the graph from the governed API | Graph |
| 2 | One accessible node selection reflected as text, not just a visual highlight | Graph |
| 3 | Tag-filter interaction | Graph |
| 4 | URL state for the current selection/filter | Graph |
| 5 | Layout and performance at real corpus scale (the sample set is not small) | Graph |
| 6 | Keyboard operability audit on every interactive graph element | Testing |
| 7 | Unit and component tests for the graph island | Testing |
| 8 | Open one PR into a module you don't own | Cross-module |
| 9 | Formally review one PR outside your own module | Cross-module |
| 10 | Document one real design decision (layout choice, accessibility trade-off) for the oral defense | Process |

### Team 3 — Oracle Terminal (pair)

| # | Task | Area(s) |
| - | --- | --- |
| 1 | Streamed response rendering, one prompt to one cited answer | Oracle |
| 2 | Live-region announcement of the streaming answer for screen readers | Oracle |
| 3 | Grounded vs. creative mode disclosure in the UI | Oracle |
| 4 | Session/exchange history handling | Oracle |
| 5 | A "preparing" cold-start state instead of a silent hang on a fresh deployment | Oracle |
| 6 | Recovery/error state when the Oracle is unavailable | Oracle |
| 7 | Unit and component tests for the Oracle terminal and its streaming logic | Testing |
| 8 | Open one PR into a module you don't own | Cross-module |
| 9 | Formally review one PR outside your own module | Cross-module |
| 10 | Document one real design decision (state handling, disclosure design) for the oral defense | Process |

### Team 4 — PWA & Local Operations (solo)

| # | Task | Area(s) |
| - | --- | --- |
| 1 | Service worker registration and an installable manifest | PWA/Offline |
| 2 | One observable offline boundary — content that keeps working without a connection | PWA/Offline |
| 3 | Cache-first vs. network-first policy for the right routes | PWA/Offline |
| 4 | An offline queue that flushes once the connection returns | PWA/Offline |
| 5 | Install-quality checks (manifest correctness, icons, installability) | PWA/Offline |
| 6 | Measured performance budget before/after one optimization (Core Web Vitals) | PWA/Offline |
| 7 | Unit and component tests for the offline boundary | Testing |
| 8 | Open one PR into a module you don't own | Cross-module |
| 9 | Formally review one PR outside your own module | Cross-module |
| 10 | Document one real design decision (caching policy, install UX) for the oral defense | Process |

### Team 5 — Accounts, Library, Proposals & Public API (pair)

| # | Task | Area(s) |
| - | --- | --- |
| 1 | Login/session (server-verified, one protected route) | Accounts |
| 2 | Personal favorites library — save, view, remove | Accounts |
| 3 | The propose-a-quote backend endpoint Team 1's form posts to | Accounts, Content |
| 4 | The GitHub-native review pipeline: a proposal PR, human approval, computed accept-diff, second approval | Accounts |
| 5 | A bearer-token-authenticated public API endpoint (`GET` a random quote) | Accounts |
| 6 | API documentation page and a minimal external example client | Accounts |
| 7 | Unit and component tests for auth, the library, and the API | Testing |
| 8 | Open one PR into a module you don't own | Cross-module |
| 9 | Formally review one PR outside your own module | Cross-module |
| 10 | Document one real design decision (session vs. token design, review-pipeline trade-off) for the oral defense | Process |

**On headcount:** this board uses the confirmed 8-student, five-team split
(2+1+2+1+2 — three pairs on the richest areas, two solos on the most bounded ones). If your actual
roster is seven, keep the module boundaries fixed and fold one pair down to a trio rather than
dropping a module — the six areas and the ten-task shape per team don't need to change, just who's
on which team.

## Why accessibility is a commitment, not a checklist

An aphorism is offered as wisdom that holds regardless of who is reading it, when, or how. A
product built on that claim cannot then quietly narrow who is able to receive it based on how they
perceive a screen — that would contradict the content's own premise, not just create a UX gap.

This resolves into three commitments carried through every story above: **content parity** — no
meaning exists in only one channel, so a graph selection is always readable as text and a
streaming answer is always announced, not just rendered; **process, not a gate** — accessibility
checks run on every change, not as a scramble before submission; **a whole-product baseline** —
every story inherits the same Definition of Done, not just the areas that feel visually
interactive.

## Related pages

- [Teaching model]({{ '/teaching/' | relative_url }})
- [For students]({{ '/audiences/students/' | relative_url }})
- [Product areas]({{ '/platform/' | relative_url }})
- [Contributing — how to open a PR, how review works]({{ '/guides/contributing/' | relative_url }})
