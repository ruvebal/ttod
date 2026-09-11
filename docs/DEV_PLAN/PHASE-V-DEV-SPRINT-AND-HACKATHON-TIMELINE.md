<!--
Revises PHASE-V-SPRINT-SESSIONS-AND-METHODOLOGY.md §3 (Sessions 3-6) against confirmed real
pacing, not the projected one that document was written against. Narrative framing text in §3
below was drafted by qwen3.8:27b (local Ollama), verified against this document's own facts
before inclusion — no fact in that section originates from the model, only the connective
"why this order" prose.
-->

# Phase V — Dev Sprint & Hackathon Timeline (supersedes §3 Sessions 3–6)

**Status:** PROPOSED — compresses three planned weekly content sessions (originally U4/U5/U6,
`PHASE-V-SPRINT-SESSIONS-AND-METHODOLOGY.md` §3) into a continuous 3-week dev sprint, the third
week run as a 4-hour hackathon, followed by Unit 7 (performance) and the defense. Professor
confirmation needed on the exact calendar dates in §2 — the *ordering* and *dependencies* are
grounded in the real, already-built task boards (49 files under
[`ASSIGNMENTS/`](ASSIGNMENTS/)); the *dates* are this document's best reading of the confirmed
cadence, not independently re-confirmed.
**Date:** 2026-09-11

## 0. What changed, and why this document exists

Per the live conversation record: the cohort has run **three 2-hour sessions** (welcome day,
"discussing the idea," and a session that reached Unit 3 content) — not the
`PHASE-V-SPRINT-SESSIONS-AND-METHODOLOGY.md` §3 plan's **Session 1 (2h, U2, 2026-09-10) then
Session 2 (4h, U3, week of 09-17)**. The cohort is running roughly a week ahead of that written
plan, having covered U2+U3 in three short sessions rather than one short plus one long. This
document does not silently overwrite §3 — it records the divergence here and supersedes only the
sessions that have not yet happened (originally Sessions 3–6, U4 through U7).

**What does not change:** the six-module team structure (§2 below, unchanged from
`PHASE-V-FEII-COHORT-COLLABORATION-AND-ASSESSMENT.md` §2), the PR evaluation rubric (§5 there),
the oral defense rubric (§6 there), and Unit 7's own position as "measure the already-built app,"
last before the defense (confirmed directly in that document's §8.6, not re-litigated here).

**What does change:** Units 4, 5, and 6's dedicated weekly sessions collapse into one continuous
3-week development sprint. This is possible, not just convenient, because the original
session-by-session chart already noted each of those three sessions carries close to zero
dedicated lecture time (`PHASE-V-SPRINT-SESSIONS-AND-METHODOLOGY.md` §3: U4 "~0h theory, mostly
lab," U5 "~0h theory, 3h content," U6 "~0h theory, 3h content") — removing the session boundary
between them removes redundant context-switching, not curriculum content. Unit 6's own workflow
content (the AI-review PR pattern) is folded into ordinary practice across the sprint's PR
checkpoints (§3 below) rather than taught as a separate block.

## 1. The real task boards this schedules (no new tasks invented)

Every task named below already exists as a reviewed, promoted sheet under
[`docs/DEV_PLAN/ASSIGNMENTS/`](ASSIGNMENTS/) — `ASSIGNMENT-<seam>-task<n>.md` — cold-reviewed
against live `ttod.yml` and the real `ts5` source tree (see each team's own
`TEAM<N>-BATCH-COLD-REVIEW.md`). This document only sequences them; it does not redefine what any
task is.

| Team | Seam | Students | Board items (file numbering; see each team's own numbering note) |
| --- | --- | --- | --- |
| 1 | Content, i18n & Proposals UI | Pair (2) | 1 (done) · 2 browse · 3 breadcrumb · 4 empty/error · 5 propose form · 6 rights/provenance · 7 tests · 8 PR · 9 review · 10 design-doc |
| 2 | Knowledge Graph | Solo (1) | 1 fetch/render · 2 node-selection a11y · 3 tag filter · 4 URL state · 5 layout/perf · 6 keyboard audit · 7 tests · 8 PR · 9 review · 10 design-doc |
| 3 | Oracle Terminal | Pair (2) | 1 streaming · 2 live-region a11y · 3 mode disclosure · 4 session history · 5 cold-start state · 6 recovery/error · 7 tests · 8 PR · 9 review · 10 design-doc |
| 4 | PWA & Local Operations | Solo (1) | 1 SW lifecycle · 2 observable boundary · 3 cache policy · 4 offline queue · 5 install-quality · 6 perf budget · 7 tests · 8 PR · 9 review · 10 design-doc |
| 5 | Accounts, Library, Proposals & API | Pair (2) | 1 login/session · 2 favorites · 3 propose endpoint · 4 review pipeline · 5 bearer API · 6 docs/client · 7 tests · 8 PR · 9 review · 10 design-doc |

## 2. The compressed calendar (dates are this document's proposal, not re-confirmed)

Reading the original plan's now-freed session slots (Sessions 3–5 were U4/09-24, U5/10-01,
U6/10-08) as the three dev-sprint weeks, and Session 6's slot (U7/10-15) as the performance week —
this reclaims one full week versus the original six-remaining-session count, since U6's dedicated
slot is absorbed rather than skipped:

| Week | Dates (proposed) | Format | PR-review checkpoint |
| --- | --- | --- | --- |
| Dev Week 1 | week of 09-17 | 4h, light framing only | **Checkpoint 1**, end of week |
| Dev Week 2 | week of 09-24 | 4h, ~0h framing, lab | **Checkpoint 2**, end of week |
| Dev Week 3 — **Hackathon** | week of 10-01 | 4h, zero lecture, pure build | **Checkpoint 3**, end of week |
| U7 (performance) | week of 10-08 | 4h — measure the built app | — (Entrega-1-adjacent, not a new checkpoint) |
| Defense | week of 10-15 (TBD) | oral "diff review" | — |

If the professor's actual next-session date differs from "week of 09-17," shift every row below
by the same offset — the *relative* ordering (three dev weeks, then U7, then defense) is what's
load-bearing, not these specific Monday labels.

## 3. Per-week task pulls, and why this order (not an arbitrary split)

Sequencing follows the real dependency the teams' own task-board notes already name — most
importantly, **Team 5's item 3 (the propose-a-quote endpoint) must exist before Team 1's item 5
(the propose form) is built against it** (`ASSIGNMENT-content-task5.md`'s own note: "coordinate
the exact interface with Team 3 first" — for accounts read Team 5 — is the same pattern
`ASSIGNMENT-accounts-task3.md` states from the other side). Cross-module PR/review tasks (every
team's items 8/9) are scheduled last because reviewing a teammate's module requires that module to
already contain real, running code — scheduling them in Week 1 would make the task a formality,
not the genuine cross-module reading `PHASE-V-FEII-COHORT-COLLABORATION-AND-ASSESSMENT.md` §8.6
item 3 relies on to resist one-shot agentic completion.

### Why the sprint is 3 weeks, not spread across separate unit-by-unit sessions

Because the official lecture content for Units 4 through 6 is minimal and primarily consists of
lab time, compressing these topics into a continuous development sprint preserves all curriculum
value. This approach eliminates the redundant context-switching between short lecture blocks and
hands-on work, allowing teams to maintain deep focus on building.

### Dev Week 1 — foundations, and the one hard blocker

**Correction (2026-09-12):** the first version of this table pulled only 2–3 curated items per
team and left roughly half the two boards' items unscheduled entirely — including all of
Accounts' own item 1 (login/session) and three of Oracle's six core items. Every core item (1–6
per team) now lands in Week 1 or Week 2; nothing sits unscheduled. Solos (Graph, PWA) take 3
items/week; pairs (Content, Oracle, Accounts) split 3 items/week across two people.

| Team | Pulls this week |
| --- | --- |
| 1 (Content) | item 2 (browse routes), item 3 (breadcrumb) |
| 2 (Graph) | item 1 (fetch/render, hardened), item 2 (accessible node selection), item 3 (tag filter) |
| 3 (Oracle) | item 1 (streamed response, hardened), item 2 (live-region announcement), item 4 (session history) |
| 4 (PWA) | item 1 (SW lifecycle), item 2 (observable offline boundary), item 5 (install-quality checks) |
| **5 (Accounts)** | item 1 (login/session, hardened), item 2 (favorites), **item 3 (propose endpoint) — priority, Team 1 depends on this contract next week** |

**Why Team 5's propose-endpoint work must land in Week 1:** Team 1's propose-a-quote form,
scheduled for Week 2, relies entirely on an endpoint that Team 5 owns and must implement first.
Establishing this contract early prevents a critical blocker, so Team 1 builds against a stable
interface rather than waiting on an undefined one.

**Checkpoint 1 (end of week):** review each team's foundational PRs — is the baseline hardened,
have 1–2 real feature items landed, and specifically: does Team 5's propose-endpoint contract
exist and is it documented well enough for Team 1 to build against next week? A checkpoint that
finds this contract still undefined is the one failure this schedule cannot absorb without
slipping Week 2.

### Dev Week 2 — core features, the form now unblocked

| Team | Pulls this week |
| --- | --- |
| 1 (Content) | item 4 (empty/error states), **item 5 (propose form — now unblocked)**, item 6 (rights/provenance) |
| 2 (Graph) | item 4 (URL state), item 5 (layout/perf at scale), item 6 (keyboard audit) |
| 3 (Oracle) | item 3 (grounded/creative disclosure), item 5 (cold-start state), item 6 (recovery/error state) |
| 4 (PWA) | item 3 (cache policy), **item 4 (offline queue — coordinate with Team 3, who calls into it)**, item 6 (measured performance budget) |
| 5 (Accounts) | item 4 (review pipeline + role-gate), item 5 (bearer API), item 6 (docs + example client) |

**Checkpoint 2 (end of week):** by now most of every team's board (items 2–6) should be
substantively real. This is where the rubric's Contract Adherence and Correctness dimensions
(`PHASE-V-FEII-COHORT-COLLABORATION-AND-ASSESSMENT.md` §5) start applying meaningfully — a PR
still stubbing acceptance criteria at this checkpoint is a real signal, not noise.

### Dev Week 3 — the Hackathon: breadth, tests, and the cross-module requirement

| Team | Pulls this week |
| --- | --- |
| every team | item 7 (finish tests), item 8 (open a PR into another team's module), item 9 (formally review a PR outside your own module), item 10 (document one real design decision) |

**Why cross-module PR/review tasks wait until the hackathon week:** reviewing or contributing to
a teammate's module requires that the code actually functions and is readable, which only becomes
realistic after two weeks of feature building. Scheduling this in the final week makes the review
a genuine technical exercise rather than a hollow formality.

**Why testing is woven through, not saved for one week:** the Testing Trophy doctrine treats tests
as pairing with each feature as it lands, so item 7 should already be partially real by this week,
not starting from zero — the hackathon's testing push is about closing remaining gaps and
hardening what exists, matching R7's own "continuous, not a dedicated week" design
(`PHASE-V-FEII-COHORT-COLLABORATION-AND-ASSESSMENT.md` §2).

**Checkpoint 3 (end of week) — the heaviest pass, functioning as an Entrega-1-style gate:** by
this point every team has a full board of shipped work, at least one genuine cross-module
contribution, and real test coverage — a complete snapshot of the term's work so far. This is the
natural moment for the heaviest review pass, matching the original plan's own "Entrega 1 is due
here" framing for Unit 6 (`PHASE-V-FEII-COHORT-COLLABORATION-AND-ASSESSMENT.md` §8, Unit 6
curriculum-alignment note) — folded into this checkpoint rather than a separate session, since the
content that would have justified a dedicated U6 session is now ordinary sprint practice.

## 4. What this document does not do

It does not change the module/team boundaries, the PR rubric's point values, the defense rubric,
or Unit 7's own content (§2.5–§2.6, §5, §6 of
`PHASE-V-FEII-COHORT-COLLABORATION-AND-ASSESSMENT.md` are all unchanged). It does not confirm the
exact calendar dates in §2 — that remains the professor's call, same as the original document's
own open items (§10 there). It does not publish anything to `docs/public/` — the task-board links
above point at `docs/DEV_PLAN/ASSIGNMENTS/`, the pre-publication source, per the assignment-forger
skill's own "separate, later, explicit step" rule.
