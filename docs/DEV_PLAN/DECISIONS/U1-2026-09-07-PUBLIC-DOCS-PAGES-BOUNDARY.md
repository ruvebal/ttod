# U1 decision — public documentation is independent from application deployment

**Status:** FROZEN (product-owner instruction, 2026-09-07)

## Decision

TTOD may publish a curated Jekyll documentation site whose exact source is `docs/public`. The site
may describe the project, the front-end reference, the teaching model, research preparation, public
guides, and role-oriented views for students, university partners, and research or venture
partners. It may be online while the application remains local.

The documentation workflow is a narrow exception to the earlier freeze on R6-owned application
workflows. It does **not** implement or assess application CI/CD, PWA behavior, cloud hosting,
student deployment, or a production environment. Those remain governed by the R6/Phase U gates.

## Publication boundary

- The Pages artifact is built from `docs/public` only, never the broader `docs` tree.
- Internal evidence reports, evaluations, local topology, and studio machinery are not copied into
  the publication source.
- Privacy checks run over both Jekyll source and rendered output.
- Exact private machinery terms remain in an untracked local denylist and a protected Actions
  secret; the values never enter Git history or workflow logs.
- Publishing Pages does not authorize changing repository visibility. A public repository exposes
  every tracked file and reachable history, so it requires the independent release cascade.

## Operational prerequisites

Before the first Pages deployment, configure GitHub Pages to use GitHub Actions and add the
newline-delimited `TTOD_PUBLIC_PRIVATE_TERMS` repository secret. Protect the `github-pages`
environment so only the intended default-branch workflow can deploy.

