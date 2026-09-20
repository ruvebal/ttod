# Y1 decision — agentic layout: flat packs, promote `public-docs-i18n`

**Status:** FROZEN 2026-09-20 on the evidence below. The checklist rows were pre-filled with the
plan's recommended defaults; the one place this decision departs from them is called out.
**Owner:** `ruvebal@crea-comm.net` — may overturn any row.
**Implementation authority:** Y2 only; no file moved by this record.

## Decisions

| # | Question | Decision | Basis |
| --- | --- | --- | --- |
| 1 | Packs flat under `agentic/`, or nested under `agentic/packs/`? | **Flat siblings** (recommended default adopted) | The legibility test passed on the flat tree (Y0). Nesting would add a level to solve a problem the test does not show. "Worse is better." |
| 2 | `public-docs-i18n`: leaf skill or pack? | **Promote to pack** — *departs from the "keep leaf" default* | See below |
| 3 | Collection id | **`dear_tree`** (recommended default adopted) | Names an affection for structure; readable aloud |
| 4 | `report-steward/` path | **Frozen** | CI runs `report-steward/scripts/check_public_privacy.py` at that path |

## Why promote `public-docs-i18n` (row 2)

The pack criterion written in Y0 says a pack is ≥2 surfaces that must move together, and names
"skill + script" as the example. Checked live: the skill's step 2 calls
`scripts/translate_public_docs.py`, and **that call is the only reference to the script anywhere
outside DEV_PLAN history** (`git grep`; no Makefile, no CI). So the skill already has a second
surface — it lives in the repo-level `scripts/` directory, outside `agentic/`. The leaf-skill
definition says "one surface"; the leaf-rule definition says "no companion scripts". Keeping it a
leaf would make the criterion decorative, and would leave the tree with a workflow whose
executable half is invisible from `agentic/README.md`.

Consequences Y2 must handle: the script derives the repo root as `parents[1]` of its own path,
so moving it changes that constant; the `.cursor` landing must be retargeted; `agentic/skills/`
would then hold nothing (it stays a documented placement rule for future leaf skills, and
disappears from git while empty).

## Evidence that "no other structural change" is right

Legibility test, negative control: a naive reader was given `main`'s pre-Y0 README with the same
listing. It found three real contradictions (README says `ide-mcp/` is "not yet created" while it
exists; the "deliberately absent" section is misleading about the cascade subagents; `agents/` is
"reserved, currently empty" but ambiguous) and misfiled `.cursor/mcp.json`. The same reader given
the Y0 README found nothing. So the test can fail, the old README failed it, the new one passes —
the tree's problem was the legend, which Y0 already fixed, not the shape of the directories.

## Non-authorization

No move, no `ttod.yml` change, no `proposal accept`, no rename of `report-steward/`.
