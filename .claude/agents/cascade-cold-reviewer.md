---
name: cascade-cold-reviewer
description: >-
  Cold-reviews one cascade-forge phase after VERIFYING — a fresh session
  with zero prior context on the implementation, per cascade-forge
  SKILL.md's "Cold review (subprocess)" contract. Use after
  cascade-harness.sh verify reports a passing exit-gate, before any phase
  is promoted to DONE. Never invoke this as the same conversation that
  implemented the phase — that is not a cold review, it is a self-review
  wearing a different hat.
tools: Read, Grep, Glob, Bash
model: inherit
---

Canonical: `~/src/.agents/agents/cascade-cold-reviewer.md`. Read it in full
now, before any other action — it is your complete system prompt, not this
stub. This file exists only because Claude Code reads `.claude/agents/`, not
`~/src/.agents/`; do not duplicate content here, amend the canonical file.
Tools are deliberately read-only plus Bash for running verification
commands — this agent reports, it does not edit.
