<!--
Third companion to PHASE-V-FEII-COHORT-COLLABORATION-AND-ASSESSMENT.md, alongside
PHASE-V-PRODUCT-BACKLOG-AND-JOURNEYS.md. Phase V §2 says how engineering work is organized; the
backlog doc says why/for whom; this document says WHEN, at the level of an actual class session —
the sprint/task/deadline chart Phase V §8.5 named in week-sized blocks but never broke into the
theory → team meeting → lab-time rhythm the professor actually runs each session, and never
grounded against the real per-session hour allocation.

Session Duration/Lab-Hours source (verified, not assumed): 
~/projects/ruvebal/scholar/udit/web-atelier-udit/web-foundations/docs/tracks/en/udit/2627-feii/index.md
§ "Session Sequence" table, and .../2627-feii/how-to-pass-this-track/data/content.json (Entrega 1
= Units 2-6, indicative Week 7; Mid-Term covers U1-U7). Formal split: 10h lección magistral (theory)
+ 30h laboratory + 14h individual exercises + 94h autonomous study + 2h assessment.
-->

# Phase V — Sprint & Session Chart, and the Theory → Team Meeting → Lab-Time Methodology

**Status:** PROPOSED — companion to Phase V, gates nothing on its own.

**Depends on:** `PHASE-V-FEII-COHORT-COLLABORATION-AND-ASSESSMENT.md` §2 (teams/modules), §8.5
(week-level calendar this chart subdivides into sessions), and
`PHASE-V-PRODUCT-BACKLOG-AND-JOURNEYS.md` §5 (the story backlog each session's lab time pulls
from).

---

## 1. The real session data this chart is built from

FE II's own public track page lists 12 sessions with **Duration** (total class time) and **Lab
Hours** (hands-on portion of that same session) — not assumed, read directly from the track's
Session Sequence table. Only U1–U7 fall inside this cohort's compressed five-week window
(`PHASE-V-...ASSESSMENT.md` §8.5); U8–U12 (3D/IoT/capstone) are out of scope for this backlog.

| Unit | Duration | Lab hours | Theory portion (Duration − Lab) | Topic |
| --- | --- | --- | --- | --- |
| U1 | 2h | 0h | 2h | Kickoff — distributed interface system framing (already spent) |
| U2 | 3h | 2h | ~1h | Astro fundamentals, content-first, SSR vs SSG, multi-framework |
| U3 | 3h | 2h | ~1h | Content collections, mandatory i18n routing, data fetching, micro-frontends |
| U4 | 2h | 2h | ~0h (folded intro) | Service workers, caching strategies, web app manifest |
| U5 | 3h | 3h | ~0h (folded intro) | Testing Trophy, flakiness, CI budgets, contract testing |
| U6 | 3h | 3h | ~0h (folded intro) | AI-assisted PR review, human-in-the-loop, accept/reject/escalate |
| U7 | 2h | 2h | ~0h (folded intro) | Core Web Vitals, performance budgets, bundle optimization |

**Reading this honestly:** U2/U3 are the only sessions with a real ~1-hour direct-teaching block —
new framework concepts (Astro islands, mandatory i18n routing) are genuinely load-bearing enough
to need it. From U4 onward the theory portion is a short (10–20 min) framing at the top of the
session, not a separate hour — the session *is* mostly lab time by the curriculum's own design.
This matches the professor's own description of the rhythm ("teach the lesson a little, theory —
team meeting — lab time"): brief, not absent.

## 1.5 The real cadence — resolved, not a projection

Confirmed directly, superseding the flat "4h/week" assumption this section originally worked
from: **tomorrow's session (2026-09-10) runs 2h; from the following week onward it's a strict one
session of 4h per week** — not two shorter meetings, not a flexible weekly pool. That single fact
(one session/week, no exceptions) rules out this document's earlier "Recommended: Week 4 runs two
meetings" resolution outright — there is no week that gets a second meeting.

Redoing §1's math against this real cadence: tomorrow's 2h session covers U2 (compressed from its
official 3h — theory trimmed further than §1's table assumed, lab time shortened correspondingly).
That leaves U3–U7 (3+2+3+3+2 = 13h of content) for the strictly-one-per-week weeks that follow.
Checked against the 4h cap, **every one of U3–U7 fits alone in a single week** (largest is 3h,
leaving 1h slack; smallest is 2h, leaving 2h slack) — the distribution conflict from the earlier
draft of this section is resolved *by not trying to fit two units in one week at all*, not by
picking one of the three options previously listed here. The honest cost: this takes **five more
weekly sessions after tomorrow (one per remaining unit), not four** — one week longer than
`PHASE-V-...ASSESSMENT.md` §8.5's original "five weeks, ending ~2026-10-15" framing. §3 below
gives the recalculated dates; §8.5 needs the same correction (flagged there directly).

**Unit 7 is explicitly the "measure the already-built app" session, followed by the defense** —
confirmed directly, not inferred: U7's Core Web Vitals work only makes sense once the six modules
actually exist and run, so it stays the last content session by construction, and the oral defense
(Phase V §6) is a distinct event after it, not folded into the same session.

## 2. The methodology, made explicit

Every TTOD project session (from Week 1 onward) runs the same three-part structure:

1. **Theory (brief).** A short block straight from that unit's curriculum lesson — ~1h for
   U2/U3, ~10–20 min for U4–U7 (per §1's real allocation). This is the FE II track's own
   "lección magistral" time, institutionally distinct from lab hours — keep it that short on
   purpose; the curriculum's own hour allocation is the argument against letting it run long.
2. **Team meeting (stand-up, ~10–15 min).** Six teams (Phase V §2's 2+1+2+1+2), each reports in
   under two minutes: **shipped since last session · blocked on · doing this lab block.**
   Professor facilitates, does not solve blockers live in front of the whole room — parks them
   for 1:1s during lab time. This is also where cross-team contract drift gets caught early (e.g.,
   does R4/R5 still match R3b's frozen route/locale contract? — the exact question TS1's freeze
   exists to make mechanical, Phase U §1).
3. **Lab time (the remainder).** Hands-on building. Teams pull stories for *this session* from the
   shared backlog (`PHASE-V-PRODUCT-BACKLOG-AND-JOURNEYS.md` §5) into a Kanban "This Session"
   column during the team meeting, not before it — that's what makes the meeting a real planning
   event instead of a formality (§4 below).

## 3. Sprint & session chart — tomorrow through the defense

Each row is one class session. "Pulls from backlog" cites the epic/story IDs from
`PHASE-V-PRODUCT-BACKLOG-AND-JOURNEYS.md` §5 so lab time has a concrete pull list, not a vague
"keep building."

### Session 1 — tomorrow, 2026-09-10 · U2 · **2h** (compressed from official 3h)

- **Theory (trimmed):** Astro fundamentals — content-first, SSR vs SSG, multi-framework
  integration, kept tighter than the official ~1h since the session itself is 2h, not 3h.
- **Team meeting:** confirm TS1's freeze is green (Phase U orchestration §5 gate) before any team
  branches off it; each team states their module's first concrete task.
- **Lab time (shortened accordingly):** open the first draft PR per team, against their own module
  skeleton. Pulls: **A1, A2, E1** (browse routes, quote page, login skeleton) — treat this as
  "started," not "finished," given the shorter session; anything unfinished carries into Session 2.
- **Due by end of session:** first draft PR per team open (Phase V §4 guardrail).

### Session 2 — week of 09-17 · U3 · 4h (1h theory + 3h lab)

- **Theory:** content collections, mandatory `es`+`en` i18n routing, data fetching, micro-frontends.
- **Team meeting:** cross-team contract check — R4 (graph) and R5 (oracle) confirm they still match
  R3b's frozen route/locale contract; close out anything Session 1's shorter lab time left open.
- **Lab time:** modules 01–03 push toward functional depth; module 05 gets login/logout working
  end to end. Pulls: **A3, B1, B2, C1, C2, E1 (finish)**.
- **Due by end of week:** modules 01–03 functionally working at assignment depth; login/logout
  live.

### Session 3 — week of 09-24 · U4 · 4h (~0h theory, mostly lab, 2h slack)

- **Theory (short):** Cache-First/Network-First policy, manifest — brief framing only; U4's
  official content is 2h against this week's 4h budget, leaving real slack (use it for cross-team
  contract check-ins or catching up anything still open from Session 1/2, not new content).
- **Team meeting:** module 04 reports offline-boundary scope; module 05 reports favorites-library
  and propose-form progress.
- **Lab time:** module 04 builds the offline boundary; module 05 builds the favorites library and
  propose form. Pulls: **D1, D2, E2, E3, F1**.
- **Due by end of week:** offline boundary observable; favorites library + propose form live.

### Session 4 — week of 10-01 · U5 · 4h (~0h theory, 3h content, 1h slack)

- **Theory (short):** Testing Trophy (not Pyramid), flakiness causes, CI budget under 5 minutes,
  contract testing, accessibility-in-the-suite.
- **Team meeting:** every team confirms their R7 test-coverage line (Phase V §5) is real, not
  stubbed — the point where "testing is everyone's job" (§2, backlog §3) gets checked, not assumed.
- **Lab time:** every team adds its unit/component/route/a11y test layer. Pulls: **H1 (a11y DoD
  clause) against every module's own stories.**
- **Due by end of week:** the a11y/testing Definition-of-Done clause satisfied by every module, not
  just claimed.

### Session 5 — week of 10-08 · U6 · 4h (~0h theory, 3h content, 1h slack)

- **Theory (short):** the GitHub PR AI-review workflow — AI comments, never approves or merges; a
  human approves.
- **Team meeting:** module 05 dry-runs the §2.7 CI proposal pipeline end to end in front of the
  class — propose → PR → approve → auto-accept.
- **Lab time:** close out remaining PRs. **This is the internal Entrega 1 checkpoint** — the
  curriculum's own U6 lesson states "Entrega 1 is due here" (Phase V §8).
- **Due by end of week:** Entrega 1 checkpoint — all six modules PR-complete; §2.7's pipeline
  demonstrated working end to end.

### Session 6 — week of 10-15 · U7 · 4h (~0h theory, 2h content, 2h slack) — measure the app

- **Theory (short):** Core Web Vitals, performance budgets — "measure before claiming" (Phase V
  §8). Confirmed explicitly: this session's purpose is to measure the app the cohort has already
  built, not to build anything new — hence the real slack, usable for final polish rather than new
  content.
- **Team meeting:** each team reports one measured performance change, before/after numbers — the
  Unit 7 requirement itself, not a suggestion.
- **Lab time:** Lighthouse passes, final polish, oral-defense slot booking. Pulls: **G1, G2, H2,
  H3**.
- **Due by end of week:** Lighthouse pass; PR rubric complete; oral defense scheduled.

### Defense — week of 10-22 (date TBD) · not a content session

Confirmed as a distinct event after U7, not folded into it: the oral "diff review" defense (Phase
V §6). No new backlog stories, no lab time — it is where each team defends the module they built.
Exact date is an open question (§6).

**Recalibration this revision:** this is **six weekly content sessions after tomorrow's shorter
one, plus the defense as a seventh touchpoint** — one week longer than
`PHASE-V-...ASSESSMENT.md` §8.5's original "five weeks, ending ~2026-10-15" framing, a direct
consequence of the confirmed cadence (2h tomorrow, then strictly one 4h session per week, never
two). §8.5 needs the same correction; it currently still describes the old five-week table.

## 4. What "sprint" means operationally here — the board, not the ceremony

Six teams, five weeks: full Scrum ceremony (separate planning/review/retro meetings) is more
process than the timeline affords. Use a single shared **GitHub Projects board** — zero new
tooling, since every other TTOD workflow already runs through GitHub PRs (Phase V §4, §2.7):

- **Columns:** Backlog (all of `PHASE-V-PRODUCT-BACKLOG-AND-JOURNEYS.md` §5's stories, by epic) →
  This Session → In Review (PR open) → Done.
- **Who moves cards:** each team, during their own two minutes of the team-meeting stand-up (§2
  item 2) — pulling into "This Session" is the planning act, not something decided beforehand by
  the professor. This is what keeps the meeting real instead of a status-only ritual.
- **Definition of Done, every card:** the PR merges against the guardrails already in Phase V §4,
  and inherits the accessibility clause from the backlog doc's §3 (keyboard-operable, one
  accessible name, no color-only meaning, respects reduced motion) — not re-litigated per card.

## 5. What this chart does not replace

Phase V §8.5's week-level exit criteria remain the authoritative grading gate — this chart
subdivides those weeks into sessions, it doesn't loosen them. Phase V §2's module/team table
remains authoritative for who owns what. `PHASE-V-PRODUCT-BACKLOG-AND-JOURNEYS.md` §5 remains the
single backlog — this document says *when* stories get pulled, never adds new ones of its own.

## 6. Open questions

**Resolved since the first pass:** the real cadence (tomorrow 2h, then strictly one 4h session per
week) is confirmed (§1.5) and fully resolves the earlier Week-4 distribution conflict — every
remaining unit now gets its own week, at the cost of one extra week of calendar versus the
original five-week framing.

1. **Exact weekday/time slot for the weekly session.** Still not confirmed — needed to replace
   "week of 10-01" style ranges with literal session dates.
2. **The defense date.** Named as "week of 10-22 (TBD)" in §3 — confirm the actual date once U7
   (Session 6) is scheduled; it should sit close enough after U7 that the measured-performance
   work is still fresh, but needs its own slot since it isn't a content session.
3. **Whether `PHASE-V-...ASSESSMENT.md` §8.5 should be corrected to match this six-plus-defense
   calendar**, or whether the professor has a way to reclaim the lost week elsewhere (e.g., trimming
   Unit 1's already-spent framing, or a slightly earlier true start date) — flagged in §8.5 itself
   for a direct answer.
4. **Board tool.** GitHub Projects is confirmed as the choice — justified (the backlog doc already
   has ~20 ready stories to seed it) but not yet built: the authenticated `gh` CLI here lacks the
   `project` scope, and `gh auth refresh -s project` is an interactive device-code flow only you
   can complete. Once refreshed, creating the board (`gh project create` + the four columns above)
   is quick.
