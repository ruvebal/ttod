# CLAUDE.md — The Tao of Development

> *"Name your variables as if you were baptising stars."*

**Author:** Rubén Vega Balbás PhD — Creative Technologist & Developer — ruvebal@crea-comm.net
**License:** CC BY-SA 4.0
**Status:** Standalone — extracted from Web Atelier (UDIT)

---

## What This Is

A pedagogical wisdom database — a dynamically counted collection of aphorisms for developers walking
the path. Taoist-style koans, paradoxes, and hard-won insights are organized by section (images,
CSS, architecture, debugging, wisdom...) and mastery level (beginner → master). Never embed a
current quote count in prose; derive it from the canonical snapshot with the CLI.

TTOD is the **teaching layer** of the crea-comm.net studio. After every development iteration, the blackbox studio bounces pedagogical insights back into this database. The padawans learn; so does the master.

## Architecture

- `ttod.yml` — Single source of truth. YAML database; `meta` counts are generated projections,
  not hand-maintained facts.
- `schema/` — versioned schema surface planned by Phase Q; do not claim a schema exists until the
  corresponding file and executable gate are present.
- `cli.py` — Typer CLI: validate, stats, export, add.
- `exports/` — Generated outputs (JSON, graph data). Gitignored.
- `.cursor/rules/ttod-editing.mdc` — **Strict editing checklist** (IDs, tags, collections, validation).
- `sources/tao-of-ai-development/` — Full *Tao of AI Development* chapter (EN+ES), moved 2026-08-13 from Web Atelier. **Not yet merged** into `ttod.yml`. See that folder's README before extracting IDs.

## Quote Schema (per entry)

```yaml
- id: arch-001                    # {section_prefix}-{number}
  text: 'The aphorism itself.'
  section: architecture           # One of 16 sections
  subsection: boundaries          # Subsection within section
  level: advanced                 # beginner | intermediate | advanced | master
  tags: [boundaries, coupling]    # From controlled tag_taxonomy
  teaches: 'What the student learns'
  show_when: 'When to surface this quote'
  related: [arch-002, cc-001]     # Graph edges to other quotes
  lesson: lesson-slug             # Link to a teaching unit
  chapter: 'Chapter Name'         # Source chapter
  source: source-slug             # Origin document
  origin: human                   # human | studio | blackbox (NEW)
  created_at: 2025-12-06          # When added (NEW for new entries)
```

## Origin Tracking (blackbox integration)

When the studio generates a new teaching from a dev session:

- `origin: studio` — distilled by the developer during work
- `origin: blackbox` — proposed by AI, validated by human
- `origin: human` — original authorship (core quotes; merged DevIAC koans note `source: deviac/docs/tao/ttod.yaml (merged)`)

Every quote with `origin: blackbox` MUST have `validated_by: human` before merging.

## CLI

```bash
python cli.py validate           # Schema validation
python cli.py stats              # Dynamically derived section/level/origin breakdown
python cli.py export --format json --output exports/ttod.json
python cli.py add --section architecture --level advanced --text "..."
python cli.py graph --output exports/graph.json  # For 3D visualization
```

## Integration Points

- **DevIAC MCP**: `ingest_knowledge.py` can ingest `exports/ttod.json` into pgvector
- **Fine-tuning**: `prepare_data.py` reads ttod.yml as pedagogical exemplars
- **Web Atelier**: Jekyll consumes ttod.yml via `site.data.ttod`
- **Arkadia**: Future RAG source for teaching-mode chat
- **3D Portfolio**: Visualization schema drives force-directed knowledge graph

## Rules

1. Never delete quotes — mark as `deprecated: true` if outdated.
2. Every blackbox-origin quote needs human validation.
3. IDs are immutable — once assigned, never reused. Prefix must match section (`arch` ≠ `devops`).
4. The YAML is the source of truth. JSON exports are derived.
5. Tags must come from `tag_taxonomy` or be explicitly added to it.
6. After any accepted edit: never hand-edit `meta.total_quotes`, section counts, coverage, or
   collection totals. Run the dynamic stats/check command and validator; the acceptance path must
   recompute projections atomically. If the command cannot do so, stop and record a contract
   blocker rather than patching a number manually.
