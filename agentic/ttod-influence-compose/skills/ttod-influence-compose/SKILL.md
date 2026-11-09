---
name: ttod-influence-compose
description: >-
  Compose TTOD aphorisms under a named influence corpus (e.g. Lao Tzu scholar-lao-tzu)
  via DevIAC vectors/graph → Athanor → optional Ahmes cite → local Ollama draft →
  ttod-bridge propose only. Use when drafting Tao of Development quotes that need an
  influence voice without treating RAG snippets as citation authority or hand-editing
  ttod.yml. Do not use for verbatim scholarly quotation (semantic-quote) or claim
  grounding in curriculum prose (ground-with-athanor-ahmes).
---

# TTOD influence compose

**Canonical pack:** `~/src/ttod/agentic/ttod-influence-compose/`  
**Write port:** `~/src/.cursor/skills/ttod-bridge/` only  
**First profile:** [`profiles/lao-tzu.md`](../../profiles/lao-tzu.md)

## When to use

- Draft a new TTOD aphorism whose *voice* is informed by an ingested influence corpus.
- Re-run discovery against a live Athanor/DevIAC project after a bibliography pipeline completes.

## When not to use

- Accepting or merging proposals (human `proposal accept` only).
- Quoting scripture/scholarship verbatim into lessons (`semantic-quote` + Ahmes cite).
- Proving studio product claims from Lao Tzu (or any influence) as independent evidence.

## Authority ladder (non-negotiable)

1. DevIAC vectors / graph — **discovery only** (`authority_level: derived`)
2. Athanor search — **canonical pointers** (`node_id`, coat, project_slug)
3. `ahmes query --cite "$DB:$NODE"` — **only** cite-grade evidence when needed for notes
4. `ttod-bridge` `propose_quote` — **staging only**; human accepts into `ttod.yml`

## 0. Load the influence profile

Read `agentic/ttod-influence-compose/profiles/<influence_id>.md`. Required fields:
`project_slug`, `library`, `knowledge_scope`, path to system prompt / rules / frozen queries.

If the profile is missing, stop and ask the owner to add one — do not invent slugs.

## 1. Preflight

```bash
curl -sf http://localhost:11434/api/tags >/dev/null
curl -sf http://localhost:8100/health >/dev/null
# Profile-specific: INJECT_DONE or equivalent when the profile names one
test -f "$INJECT_DONE_PATH"   # from profile, when present
```

Export Athanor env without printing secrets:

```bash
set -a; source ~/src/athanor/.env; set +a
ATHANOR=~/src/athanor/.venv/bin/athanor
AHMES=~/src/ahmes/.venv/bin/ahmes
```

## 2. Discover (DERIVED)

Prefer frozen harvests under the profile’s `queries/` when re-running the same theme; otherwise:

**Vectors** (scoped to profile `project_slug` + `knowledge_scope`):

```bash
curl -s -X POST http://localhost:8100/vectors/search \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"<theme>\",\"project_slug\":\"$PROJECT_SLUG\",\"knowledge_scope\":\"$KNOWLEDGE_SCOPE\",\"n_results\":5}"
```

**Graph** (optional enrichment — still DERIVED): neighbors / semantic anchors for the theme via
the studio graph MCP or documented graph harvest JSON; label every edge/snippet DERIVED.

**Athanor**:

```bash
$ATHANOR search "<theme>" --project-slug "$PROJECT_SLUG" --library "$LIBRARY"
```

Never paste `content_preview` or vector chunks into the aphorism text.

## 3. Ground (optional notes only)

If teaching notes need a cite-safe pointer:

```bash
$AHMES query --cite "$DB:<node_id>" --style chicago-author-date
```

Keep `[BIBLIO-GAP]` when not evaluator-safe. TTOD quotes themselves are pedagogical, not evidence.

## 4. Draft

Feed the profile’s compose system prompt + theme + 2–3 DERIVED discovery snippets (labeled) to
**local** Ollama only (`localhost:11434`). Prefer one or two sentences; image-bearing; section/
tags as humble suggestions for human taxonomy mapping.

## 5. Propose

```bash
# via ~/src/.cursor/skills/ttod-bridge adapter only
adapter.propose_quote(..., origin="blackbox")
```

Never hand-append YAML to `ttod.yml`. Never cite a pending proposal ID as canonical.

## 6. Stop

Hand the pending proposal to a human. Do not `proposal accept` from this skill.

## Adding an influence

1. Ensure bibliography → Ahmes → Athanor/DevIAC inject for a stable `project_slug`.
2. Add `profiles/<id>.md` with slug, library, scope, prompt/rules/query paths.
3. Prefer a locked pack under `agentic/` for large query harvests (see `lao-tzu-tao-compose/`).
4. Do not rename locked packs listed in `agentic/README.md`.
