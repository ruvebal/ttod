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
