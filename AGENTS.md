# AGENTS.md — 道 The Tao of Development (TTOD)

> *"Name your variables as if you were baptising stars."*

**Repository:** the repository root
**Author:** Rubén Vega Balbás PhD — `ruvebal@crea-comm.net`
**Format:** [AGENTS.md open standard](https://github.com/agentsmd/agents.md) (Agentic AI Foundation / Linux Foundation)
**Licenses:** code MIT ([`LICENSE-CODE`](LICENSE-CODE)); content CC BY-NC-SA 4.0 ([`LICENSE-CONTENT`](LICENSE-CONTENT))

Read this file before editing quotes, running the CLI, or proposing new aphorisms.

---

## Mission

TTOD is the studio **pedagogical wisdom database** — aphorisms for developers walking the path,
organized by section (images, CSS, architecture, wisdom, …) and level (beginner → master). Never
embed a current quote count in prose; derive counts from the canonical snapshot with the CLI.

---

## Dev environment

```bash
cd <repository root>
make help                                        # root task surface (Compose · CLI · Astro)
make venv                                        # once — .venv + editable install
make validate                                    # or: .venv/bin/python cli.py validate
make stats
```

Legacy one-liner (same corpus tools without Make):

```bash
python3 -m venv .venv && . .venv/bin/activate   # once
pip install -e .                                 # if pyproject present; else: pip install typer pyyaml
. .venv/bin/activate && python cli.py validate
. .venv/bin/activate && python cli.py stats
```

**Running the stack (`make up`):** starts the full application, including its own Ollama
container — nothing to install first, no host dependency. This is the one supported path,
and what students use. Borrowing an Ollama you already run yourself (e.g. for Metal GPU
speed outside Docker on macOS) is a personal, manual override, not a `make` target — set
`OLLAMA_MODE=host` and `OLLAMA_BASE_URL` in your own `.env` if you want it. See the `ollama`
service in `docker-compose.yml` and the comments in `.env.example` for both paths.

| Path | Role |
| --- | --- |
| `ttod.yml` | Canonical quote database (human-governed) |
| `cli.py` | validate · stats · snapshot · export · migrate · proposal · bridge · add · deprecate · erase |
| `.cursor/rules/ttod-editing.mdc` | Strict YAML editing checklist |
| `schema/` | v3 schema surface (Phase Q complete) |
| `exports/` | Derived JSON/graph (gitignored) |

**Do not** hand-append YAML to `ttod.yml`. Mutations go through `proposal accept`, `add`
(requires `--reviewer-id`), or `migrate apply --approve` (one-time v2→v3 only) via
`ttod_core/repository.py` atomic transactions. Use disposable copies (`--file`) for bridge
self-tests and experiments.

---

## Editing workflow

### Read or search

```bash
python cli.py export --format json          # full corpus as JSON
python cli.py stats                          # section/level/tag breakdown
```

Never parse `ttod.yml` ad hoc — go through `cli.py` or `ttod_core` so schema and digest logic stay
in one place.

### Propose a new quote (never merge)

1. Distill only from a **citable source** (a lesson, grounded research, your own session notes).
2. `python cli.py proposal create --section <id> --text "..." --proposer-id <you>` — or, once
   logged in, the web propose form, which calls the same primitive.
3. Either opens/updates a PR under `proposals/` for a human reviewer. On approval,
   `.github/workflows/proposal-accept.yml` computes the `ttod.yml` diff — a second human approval
   and merge is what actually lands it (see that workflow's own comments for why).
4. Every `origin: blackbox` entry needs a human-reviewed acceptance before it counts.

### Edit existing quotes (human, post-Q3)

1. Read `.cursor/rules/ttod-editing.mdc`.
2. Pick section + next free ID prefix (`meta.last_id_by_section`).
3. Tags only from `tag_taxonomy` (extend taxonomy first if needed).
4. Run `python cli.py validate` — **zero errors** before finishing.
5. Never hand-edit `meta.total_quotes`, section counts, or collection totals.

---

## Quote record (v3 shape)

```yaml
- id: arch-001
  schema_version: '3.1.0'
  content_digest: '<sha256 via TTOD-C14N-v1>'
  text: 'The aphorism itself.'
  section: architecture
  subsection: boundaries
  level: advanced                 # beginner | intermediate | advanced | master
  lang: en                        # ISO 639-1; required. Translations are separate IDs.
  tags: [boundaries, coupling]    # from tag_taxonomy
  teaches: 'What the student learns'
  related: [arch-002, cc-001]
  relation_edges:                 # optional typed edges
    - {target: arch-060, relation_type: translation_of}  # Spanish twin points here; never arch-001-es
  lesson: lesson-slug
  source: source-slug
  origin: human                   # human | studio | blackbox | legacy-unknown
  rights:
    access: public
    license: CC-BY-NC-SA-4.0
    holder: ruvebal@crea-comm.net
    permission_basis: rights-holder-relicense-2026-08-18
  created_at: '2025-12-06'
```

**ID / language policy:** IDs stay `{section_prefix}-{number}` — never locale suffixes
(`arch-001-es` is invalid). A Spanish twin of `arch-001` is the next free `arch-NNN`, linked via
`relation_edges: [{target: arch-001, relation_type: translation_of}]` with `lang: es`.

**Origin contract**

| `origin` | Meaning |
| --- | --- |
| `human` | Original authorship |
| `studio` | Distilled by the developer during work |
| `blackbox` | Proposed by AI — requires validated human review block |
| `legacy-unknown` | Pre-v3 records with no recorded origin (not human-by-default) |

---

## Verification before claiming done

```bash
make check                                                  # validate --strict + stats --check + unittest
# or without Make:
. .venv/bin/activate && python cli.py validate --strict --json  # must exit 0
. .venv/bin/activate && python cli.py stats --check             # meta must match recomputed
python -m unittest discover -s tests -p 'test_*.py'            # full suite must be green (count grows — do not hardcode it)
```

If you only staged a proposal, confirm `ttod.yml` hash unchanged and `pending/*.yaml` exists with
`origin: blackbox` and **no** `validated_by`.

---

## Non-negotiable rules

1. Never delete quotes — set `deprecated: true`.
2. IDs are immutable; prefix must match section (`arch-*` → `architecture`).
3. YAML is source of truth; JSON exports are derived.
4. NC content default: unresolved/new quotes default to `rights.license: CC-BY-NC-SA-4.0`. Do not silently relicense.
5. TTOD quotes are **pedagogical**, not independent evidence for Athanor/WPL claims.
6. Cite quotes in lessons **by ID** only — never cite a pending proposal's suggested id.

---

## Related docs

| Doc | When |
| --- | --- |
| [`README.md`](README.md) | Start here — how to run the app locally, where each module's assignment lives |
| [`docs/public/teaching/index.md`](docs/public/teaching/index.md) | How this maps to FE II Units 1–7 |
| [`docs/public/audiences/students.md`](docs/public/audiences/students.md) | What you're expected to build and defend |
| [`.cursor/rules/ttod-editing.mdc`](.cursor/rules/ttod-editing.mdc) | YAML editing gate |
