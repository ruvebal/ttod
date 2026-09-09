# Evidence-State Reporting Pack

Maintained by `@crea-comm.net` for reusable, agent-oriented engineering reports.

| Surface | Purpose |
| --- | --- |
| `agent/report-steward.md` | bounded role and operating contract |
| `skills/evidence-state-report/SKILL.md` | reusable report workflow |
| `skills/public-artifact-privacy/SKILL.md` | public/student artifact privacy gate |
| `skills/evidence-state-report/references/report-contract.md` | report schema and claim tests |
| `rules/evidence-reporting.md` | concise repository rule |
| `rules/public-privacy.md` | public-output privacy boundary |
| `scripts/check_public_privacy.py` | deterministic tracked-text watcher (paths, hosts, phases, empty `<a>`) |

The pack is source material, not an automatic installation. A host studio may map the agent,
skill, and rules into its own discovery directories. Keep the files together so the privacy
watcher and reporting contract evolve as one governed method.

CI (`public-docs-pages.yml`) runs the same watcher on `_site-public` before htmlproofer. Agents
must clear the watcher locally on `docs/public` (and diagram assets) before pushing — see
`skills/public-artifact-privacy/SKILL.md` defect catalog.
