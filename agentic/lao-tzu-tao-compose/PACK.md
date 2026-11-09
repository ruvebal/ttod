---
name: lao-tzu-tao-compose
purpose: Lao Tzu influence profile data for ttod-influence-compose (prompts, rules, frozen queries); path locked.
surfaces: [skills, rules, queries, prompts]
landings: []
mirrors: []
locks: []
external_readers: [ttod-influence-compose profile lao-tzu; a sibling repo skill (provenance-layer profiles) names queries/ as an output directory]
status: tracked
---

# Lao Tzu → Tao of Development (influence profile pack)

**Do not rename this directory.** Compose workflow lives in
[`ttod-influence-compose`](../ttod-influence-compose/) with profile `lao-tzu`. This pack holds
Lao-specific prompts, rules, and frozen discovery harvests.

| Surface | Purpose |
| --- | --- |
| `skills/tao-compose/SKILL.md` | Thin redirect → `ttod-influence-compose` + profile `lao-tzu` |
| `rules/tao-compose.md` | Lao / cathedral hard gates |
| `queries/` | Frozen discovery harvests (vectors · Athanor · graph) |
| `prompts/compose-system.md` | Generative system prompt for local Ollama |

**Corpus:** Ahmes vaults under `~/ahmes-library/scholar/documents/` from
`~/projects/.../bibliographies/lao_tzu`. **Project slug:** `scholar-lao-tzu`.

**Authority ladder:** see `ttod-influence-compose` skill (vectors/graph → Athanor → Ahmes cite →
ttod-bridge propose).
