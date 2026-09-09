# 道 THE TAO OF THE DEVELOPMENT (TTOD) — FE II teaching baseline

This is the **hello-world teaching skeleton**, not the instructor's rich reference. Every seam
(content, graph, oracle, PWA, auth, testing) is present end to end but deliberately incomplete —
your assignment is the gap between what runs and what a finished feature would do. Each module
names its own acceptance criteria in its `ASSIGNMENT.md`:

- `services/frontend/src/pages/[locale]/wisdom/ASSIGNMENT.md` — content, i18n, proposals UI
- `services/frontend/src/components/graph/ASSIGNMENT.md` — knowledge graph
- `services/frontend/src/components/oracle/ASSIGNMENT.md` — Oracle terminal
- `services/frontend/public/ASSIGNMENT.md` — PWA & local operations
- `services/frontend/src/auth/ASSIGNMENT.md` — auth, favorites library, public API
- `services/frontend/ASSIGNMENT-testing.md` — testing strategy

## Start here

- [`docs/public/teaching/index.md`](docs/public/teaching/index.md) — how this maps to FE II
  Units 1–7, and how a class session runs (theory → team meeting → lab time)
- [`docs/public/audiences/students.md`](docs/public/audiences/students.md) — what you're expected
  to build and defend
- [`AGENTS.md`](AGENTS.md) — the governed-data contract: how quote proposals get reviewed and
  accepted, and the one rule that never changes — only a named human accepts a proposal into
  `ttod.yml`

## Run it locally

```bash
cp .env.example .env   # fill in required values
make up                # starts backend, MCP, frontend, and the app's own Ollama
```

See `Makefile` (`make help`) for the full command list — validation, tests, local dev servers.

## Contributing

Every PR follows [`.github/pull_request_template.md`](.github/pull_request_template.md) — it's
your module's grading rubric as a checklist, not a separate hoop. `.github/workflows/ci.yml` is
the required check your PRs run against.
