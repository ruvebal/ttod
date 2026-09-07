# Evidence-state report contract

## Required sections

Adapt headings to the project, but preserve these information classes:

1. **Identity:** phase, state, date, implementer, independent verifier, governing contract.
2. **Outcome:** what state is justified now, in the first paragraph.
3. **Scope:** what changed and what was explicitly excluded.
4. **Baseline:** commit, worktree, relevant versions, input identities and digests.
5. **Evidence:** commands, exits, tests, measurements, artifacts, warnings.
6. **Failures:** failed attempts that exposed a constraint, with recovery and side effects.
7. **Decisions:** chosen policy plus consequence; do not disguise a preference as observation.
8. **Residual risk:** severity, affected audience, owner, and release consequence.
9. **Integrity:** protected data before/after; mutation statement.
10. **Continuation:** dependency state, exact next action, safe resume point.

## Claim test

For every material sentence, ask:

- Is it directly observed? Name the evidence.
- Is it a decision? Name the decider or pending approval.
- Is it inferred? State the inference and inputs.
- Is it historical? Date it rather than presenting it as current.
- Is it outside the reporter's authority? Stop at a recommendation or blocker.

## State discipline

- `BLOCKED`: required authority, input, environment, or decision is unavailable.
- `READY`: prerequisites are evidenced and work may begin.
- `IN_PROGRESS`: scoped work is underway.
- `VERIFYING`: implementation is complete enough for the required independent check.
- `DONE`: every exit condition is evidenced and the authorized promoter has accepted it.

Near-complete is not `DONE`. A green unit suite is not a release decision. A public repository is
not a public deployment. A branch with deleted files is not a history-isolated artifact.

## Evidence compression

Do not paste noisy logs when a command, exit, summary, and retained artifact are sufficient. Do
retain anomalous warnings, failed attempts, security-negative results, and measurements that govern
the next decision. Prefer tables where multiple gates map to exact results.
