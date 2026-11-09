---
name: ttod-influence-compose
purpose: Compose TTOD aphorisms under a named influence corpus (RAG + graph discovery → Ahmes cite → ttod-bridge propose-only).
surfaces: [skills, profiles]
landings: [.cursor/skills/ttod-influence-compose/SKILL.md]
mirrors: []
locks: []
external_readers: [Studio load path ~/src/.cursor/skills/ttod-influence-compose/SKILL.md is a thin stub to this pack]
status: tracked
---

# TTOD influence compose

Parameterised compose harness: pick an influence profile (first: Lao Tzu), discover via
DevIAC vectors / graph and Athanor, ground optionally with Ahmes cite, draft with local
Ollama, propose only through `ttod-bridge`. Never hand-edit `ttod.yml`.

| Surface | Purpose |
| --- | --- |
| `skills/ttod-influence-compose/SKILL.md` | Workflow: profile → discover → distill → propose |
| `profiles/lao-tzu.md` | Lao Tzu influence profile (points at locked pack `lao-tzu-tao-compose/`) |

**Related (do not absorb):** `~/src/.cursor/skills/ttod-bridge/` (write port),
`ground-with-athanor-ahmes`, `semantic-quote`, `grounding-graph`.

**Locked sibling pack:** `agentic/lao-tzu-tao-compose/` — path must not be renamed; holds
prompts, frozen queries, and Lao-specific rules consumed by profile `lao-tzu`.
