---
title: "Formally review one PR outside your own module"
seam: graph
team_number: 2
team_name: "Knowledge Graph"
task_number: 9
area: "Cross-module"
verb: contribute
layout: default
lang: en
---

# Assignment — Team 2, Task 9: Formally review one PR outside your own module

**Seam:** graph · **Team:** 2 · **Task:** 9 of ~10
**Area(s):** Cross-module · **Verb served:** contribute

As the Knowledge Graph team, your module’s `ASSIGNMENT.md` defines strict constraints on node identity, edge semantics, and data integrity. When reviewing a PR from a sibling team—such as **Content** (who might be adding new wisdom nodes) or **Oracle** (who might be querying graph relationships)—you are not just checking syntax. You are verifying that their changes respect the graph’s structural invariants. For example, if the Content team adds a new node, does it correctly reference existing edges? If the Oracle team adds a query, does it handle missing relations gracefully? Your review checklist is the Graph module’s own `ASSIGNMENT.md`: does the PR violate the "Prohibited shortcuts" section? Does it maintain the "Acceptance criteria" for data consistency? This is not about judging their code style, but ensuring their contribution does not corrupt the graph’s integrity.

See the shared explanation: docs/public/teaching/tasks.md#the-three-recurring-tasks

> "Before changing a domain entity, check for side effects in application use cases. Before trusting LLM output, parse it into a value object. The guard is not distrust — it is respect for the boundary."
> — TTOD `arch-051`, *architecture*

This is a formal review, not a courtesy skim: the same discipline that guards a domain entity from an unchecked side effect is what you owe a sibling module's PR. Checking it against their own `ASSIGNMENT.md` is not distrust of their work — it is respect for the boundary their module depends on.