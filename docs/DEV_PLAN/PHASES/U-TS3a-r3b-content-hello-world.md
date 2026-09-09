<!--
Self-contained runbook. Derived from PHASE-U-FEII-TEACHING-SKELETON-CASCADE.md §2, §5 TS3 and
PHASE-U-WEEK0-ORCHESTRATION.md — that orchestration document is normative; regenerate this one if
it changes. Generated as part of the Week-0 skeleton-generator pass.
-->

# Phase U · TS3a — R3b content/i18n hello-world reduction

**Mode:** student lane (or instructor-built if executed before cohort start), 1 owner
**Entry:** TS1 `DONE` — subtraction table published, `domain.ts` confirmed frozen
**Exit:** localized (`es`+`en`) index + one detail page, one real `WisdomEntry`, semantic HTML,
an `ASSIGNMENT.md` naming what students add — no facet-browse routes, no taxonomy

---

## 0. What this phase actually is

R3b is the *first* of the three TS3 lanes to land, because R4 and R5 both consume content this
lane's route/locale contract establishes (Phase U §5 TS3: "R3b owns localized route/content
primitives and one real content example" comes before R4/R5's own steps). This is not a rewrite —
it is subtraction from an already-working reference: the wisdom pages already fetch real data from
the backend (`GET /api/v1/wisdom/sample`) and already render it with full i18n and semantic markup.
The job is to keep the *one index/detail journey* and remove the *faceted browse* routes, which
become the student assignment instead.

## 1. Required reading

- `PHASE-U-FEII-TEACHING-SKELETON-CASCADE.md` §2 (R3b's own row: instructor-provided vs.
  deliberately-absent), §3 (teaching journey).
- This repo's live files (read before editing, not from memory): `services/frontend/src/pages/[locale]/wisdom/index.astro`,
  `[slug].astro`, `sections/[section].astro`, `tags/[tag].astro`, `levels/[level].astro`,
  `services/frontend/src/content/wisdom.ts`, `services/frontend/src/content.config.ts`.
- `docs/DEV_PLAN/PHASES/U-TS1-subtraction-and-contracts.md`'s published subtraction table for the
  exact keep/cut lines confirmed for this seam.

## 2. Non-negotiable boundaries

- **Work on `skeleton/ts3a-r3b`, forked from `skeleton/ts1-contracts` (not `main`).**
- **Do not touch the backend.** `services/backend/app/main.py`'s `/api/v1/wisdom/sample` endpoint
  is out of scope — R3b consumes it, does not modify it. If the hello-world reduction needs a
  smaller response, filter client-side or request a backend change through TS1's owner, don't
  edit `services/backend/**` directly (forbidden path, §7).
- **Mandatory `es`+`en` routing stays even at hello-world depth.** Phase U's hello-world contract
  keeps localization in the *instructor-provided* column for every lane — this is one concept
  that must never be cut, only the amount of content behind it.
- **No content-collection invention.** `content.config.ts` today defines one `docs` collection for
  markdown documentation — wisdom entries are fetched live from the backend, not stored as an
  Astro content collection. Do not introduce a parallel local YAML/markdown wisdom source; that
  would contradict `ttod.yml` being the single source of truth (`AGENTS.md` non-negotiable rule 3).

## 3. Domain contract slice

```typescript
// services/frontend/src/types/domain.ts — already frozen by TS1, read-only here
export interface WisdomEntry {
  id: string;
  section: string;
  subsection?: string;
  level: 'beginner' | 'intermediate' | 'advanced' | 'master';
  text: string;
  teaches: string;
  tags: string[];
  related: string[];
  origin: 'human' | 'studio' | 'blackbox' | 'mixed' | 'legacy-unknown';
  lang: string;
  rights: { license: string; holder?: string };
}
```

`services/frontend/src/content/wisdom.ts` already implements `fetchWisdom(locale)` against this
shape, plus `labels` (en/es UI strings) and `frequencies()` (used by the facet routes being cut —
keep the function, since a future student assignment may reintroduce faceted browsing using it;
just stop calling it from any hello-world route).

## 4. Scope — exact keep/cut

| File (today) | Keep for hello-world | Cut → becomes assignment |
| --- | --- | --- |
| `wisdom/index.astro` | Fetch + render list of entries, `es`/`en` locale switch, empty-state message | — (this stays largely as-is; it is already close to hello-world depth) |
| `wisdom/[slug].astro` (19 lines) | One detail page: fetch by id, render `text`/`teaches`/`section`/`level`, semantic HTML, back link | — (already compact; confirm it stays, do not add facet cross-links here) |
| `wisdom/sections/[section].astro` (10 lines) | — | **Remove from hello-world branch entirely.** Document in `ASSIGNMENT.md` as "section browse" — a named deliverable, not a bug |
| `wisdom/tags/[tag].astro` (10 lines) | — | **Remove.** Becomes "tag browse" assignment line |
| `wisdom/levels/[level].astro` (10 lines) | — | **Remove.** Becomes "level browse" assignment line |
| `content/wisdom.ts`'s `frequencies()` | Keep the function (unused by any route, but not deleted — students' facet routes will call it) | — |

**Net effect:** the hello-world branch has exactly one index route and one detail route, both
localized, both real (not mocked) data from the live backend. The three facet routes disappear
from the branch's route tree entirely — Astro's file-based routing means their removal is just
deleting the three files, no route-config change needed elsewhere.

**`ASSIGNMENT.md`** (new, `services/frontend/src/pages/[locale]/wisdom/ASSIGNMENT.md`): learning
outcomes (content collections/dynamic routes, i18n routing, semantic HTML for humanities content),
constraints (must use `fetchWisdom`/`WisdomEntry` as-is, must keep both locales), acceptance
criteria (section/tag/level browse routes exist, breadcrumbs present, one accessibility check per
route), prohibited shortcuts (do not hardcode a locale, do not bypass the backend fetch with a
static JSON dump).

## 5. Mechanical gates

| Gate | Required proof |
| --- | --- |
| Both locales render | `/en/wisdom/` and `/es/wisdom/` both return real content, not an empty state, against the live backend |
| One detail page works | `/en/wisdom/<real-id>/` renders the entry's `text`, `teaches`, `section`, `level` |
| Facet routes absent | `sections/`, `tags/`, `levels/` directories do not exist on this branch |
| `ASSIGNMENT.md` present | learning outcomes, constraints, acceptance criteria, prohibited shortcuts all named |
| No backend edits | `git diff main -- services/backend/` on this branch is empty |

## 6. Rollback and mutation law

- Never fetches or writes `ttod.yml` directly — all data comes through `/api/v1/wisdom/sample`.
- If the backend endpoint is unreachable during this work, that is a signal to fix the local dev
  stack (`make up`), not to fabricate a static fixture that silently becomes the "real" data path.

## 7. Touched-path budget

**Allowed:** `services/frontend/src/pages/[locale]/wisdom/**`, a new `ASSIGNMENT.md` in that
directory, `services/frontend/src/content/wisdom.ts` (read/reference only — no edit expected).

**Forbidden:** `services/backend/**`, `services/mcp/**`, `ttod_core/**`, `ttod.yml`, any file
under `components/graph/`, `components/oracle/`, `lib/db.ts` (other lanes' territory).

## 8. Post-phase review

A second reader confirms the three removed routes are genuinely absent (not just unlinked) and
that the kept index/detail journey still round-trips through the real backend, not a hardcoded
fixture introduced during subtraction.

## 9. Phase report status enum

- **DONE** — both locales render real content, facet routes absent, `ASSIGNMENT.md` filed, no
  backend edits.
- **PARTIAL** — name exactly which gate in §5 is unmet.
- **BLOCKED** — TS1 has not filed `DONE`.

## 10. Exact commands

```bash
cd /Users/ruvebal/src/ttod
git worktree add ../ttod-skeleton-ts3a -b skeleton/ts3a-r3b skeleton/ts1-contracts
cd ../ttod-skeleton-ts3a/services/frontend
npm run dev
# visit http://localhost:4321/en/wisdom/ and /es/wisdom/, click into one entry
```

## 11. Report requirements

File `docs/DEV_PLAN/PHASE-U-TS3a-REPORT.md`: status (§9), which routes were removed and
where their `ASSIGNMENT.md` line lives, a real screenshot or curl transcript of both locales
rendering live backend data, confirmation the three facet-route files no longer exist.

## 12. Agent prompt — paste this into a fresh agent session with no other file open

```text
Act as TTOD Phase U TS3a engineer. Work only inside a new git worktree on branch skeleton/ts3a-r3b,
forked from skeleton/ts1-contracts (never main). This runbook
(docs/DEV_PLAN/PHASES/U-TS3a-r3b-content-hello-world.md) is self-contained.

Read services/frontend/src/pages/[locale]/wisdom/index.astro, [slug].astro,
sections/[section].astro, tags/[tag].astro, levels/[level].astro, and
services/frontend/src/content/wisdom.ts before changing anything.

Keep index.astro and [slug].astro close to as-is — they already fetch real WisdomEntry data from
the live backend (/api/v1/wisdom/sample) and render both es and en locales. Delete
sections/[section].astro, tags/[tag].astro, and levels/[level].astro entirely from this branch —
do not comment them out, remove the files. Do not touch content/wisdom.ts's frequencies()
function; leave it unused but present.

Write services/frontend/src/pages/[locale]/wisdom/ASSIGNMENT.md: learning outcomes (content
collections/dynamic routes, mandatory i18n routing, semantic HTML), constraints (must reuse
fetchWisdom and the WisdomEntry type from src/types/domain.ts exactly, must keep both locales
working), acceptance criteria (section/tag/level browse routes exist and are accessible,
breadcrumbs present), and prohibited shortcuts (no hardcoded locale, no static JSON replacing the
live backend fetch).

Do not edit anything under services/backend/, services/mcp/, ttod_core/, or ttod.yml — you consume
the wisdom API, you do not change it.

Verify both /en/wisdom/ and /es/wisdom/ render real entries against the live local stack (run
`make up` at the repo root first if the backend is not already running), and that one detail page
renders correctly.

File docs/DEV_PLAN/PHASE-U-TS3a-REPORT.md with status (DONE/PARTIAL/BLOCKED per this
runbook's §9), exactly which files were removed, the ASSIGNMENT.md content, and evidence (a real
screenshot or curl output) that both locales render live backend data.
```
