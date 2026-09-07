---
name: evidence-state-report
description: Create or review auditable engineering phase reports that distinguish observations, decisions, verification, residual risk, and safe continuation. Use for release gates, cold audits, handoffs, incident closeouts, migration reports, or any claimed state transition.
---

# Evidence-State Report

Treat the report as evidence for a state transition, not a narrative of activity.

## Workflow

1. Read the governing plan, phase/runbook, repository instructions, and prior report that defines
   the incoming state.
2. Capture commit, branch, worktree status, environment/tool versions when material, and protected
   artifact digests before edits.
3. Execute the named verification gates. Retain exact commands, exits, measurements, and meaningful
   warnings. A failed attempt that reveals a constraint belongs in the report.
4. Classify statements as observations, decisions, inferences, or unresolved risks. Never make one
   category impersonate another.
5. Compare actual work with scope and non-scope. Record files changed and any authorized boundary
   decision.
6. Recheck protected digests and repository status after work.
7. Stop at the state the evidence supports. If independent review is required, use `VERIFYING`, not
   `DONE`.
8. End with one exact next action and a safe resume point that a fresh agent can follow.

Read [the report contract](references/report-contract.md) when designing a new report family,
reviewing a disputed completion claim, or reporting a high-risk release/migration.

## Non-negotiable quality tests

- A reader can reproduce the central claims without private conversation history.
- Current measurements live in dated evidence, not evergreen prose.
- Missing evidence is named as missing.
- Failure, warning, and limitation language is as precise as success language.
- Publication, deployment, destructive cleanup, and external communication remain separately
  authorized actions.
- Public/student artifacts contain no local absolute paths, private network coordinates, internal
  hostnames, or personal email domains outside `@crea-comm.net`.
