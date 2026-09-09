---
title: Contributing
eyebrow: Governance before convenience
description: How to open a PR as a contributor, how a reviewer processes one, and the public contribution expectations behind both.
permalink: /guides/contributing/
---

# Make the evidence travel with the change

A contribution should identify what changed, why it belongs, how it was verified, and which
uncertainty remains. This page covers the mechanics — opening a PR, what happens to it, and how a
reviewer processes it — before the governance principles they both rest on.

## Opening a PR (module work)

1. Branch from the current teaching baseline: `git checkout -b <short-topic-name>`.
2. Make the change inside your module's own files — check your module's `ASSIGNMENT.md` for
   exactly which paths are yours.
3. Before pushing, run the same checks CI will run: `npm run check && npm run build` in
   `services/frontend` (or the equivalent for a backend change).
4. Open the PR. The repository's PR template fills in automatically — it mirrors the grading
   rubric directly: contract adherence, acceptance criteria, test coverage, the accessibility
   Definition of Done, and the AI Review Log (Unit 6's own template — what was AI-assisted, what
   you verified yourself).
5. The required `typecheck-and-build` check must pass and at least one approving review is
   required before merge — both are enforced automatically, not by convention.
6. A small PR that lands in stages defends better than one large PR that lands all at once — the
   [teaching model]({{ '/teaching/' | relative_url }}) explains why that's part of the design, not
   just a style preference.

**Cross-module contributions count too.** At least one PR into a module you don't own, and at
least one formal review of a PR outside your own module, are part of the assignment — see
[assignments and backlog]({{ '/teaching/assignments/' | relative_url }}) for why.

## Proposing a quote (content contribution)

Covered in full on [assignments and backlog]({{ '/teaching/assignments/#user-journeys' | relative_url }}) —
the short version: submit through the propose form (or `cli.py proposal create` directly) while
logged in, a human reviewer reads it and may ask for changes, and only a second, explicit approval
on the computed canonical diff actually publishes it. Two separate approvals, not one — the first
approves the idea, the second approves the exact change.

<figure class="diagram-teaser">
  <a class="diagram-teaser-link" href="{{ '/assets/diagrams/ttod-proposal-review.html' | relative_url }}">
    <img src="{{ '/assets/diagrams/ttod-proposal-review.png' | relative_url }}" alt="Workflow diagram: a contributor submits a proposal, a PR opens, a reviewer approves it, a bot computes and pushes the canonical diff which clears that approval, the reviewer approves again on the exact diff, and only then does the PR merge and ttod.yml update." loading="lazy">
  </a>
  <figcaption><a href="{{ '/assets/diagrams/ttod-proposal-review.html' | relative_url }}">Open the interactive review-pipeline diagram ↗</a> — the exact two-touchpoint gate this repository runs, not a simplified version of it.</figcaption>
</figure>

## For reviewers

- `make review-queue` lists open PRs waiting on you, proposal PRs specifically, and everything
  else open — read-only, it never approves or merges on your behalf.
- Review against the module's own `ASSIGNMENT.md` acceptance criteria and the PR template's
  checklist, not a generic impression of code quality.
- A PR missing its AI Review Log entry is incomplete, not merely under-documented.
- For a quote-proposal PR specifically: your approval on the *original* proposal is not the same
  event as your approval on the *computed diff* the bot pushes back afterward — branch protection
  intentionally clears the first approval so you look at the second. That's not a bug to route
  around.

## Canonical content

- Never append directly to the canonical YAML collection.
- Propose new material through the governed proposal path.
- Preserve stable IDs; deprecate rather than delete.
- Use the defined tag taxonomy, origin model, language policy, and rights fields.
- Do not cite pending proposals as accepted entries.

## Front-end work

- Preserve localization, semantic HTML, keyboard use, and explicit loading, empty, error, and recovery states.
- Keep framework islands bounded by a reason to hydrate.
- Test the risk at the cheapest layer that provides useful confidence.
- Measure bundle or runtime cost before claiming an optimization.

## Research and publication

- Separate design rationale from evidence of learning.
- Use authoritative sources for current legal or institutional requirements.
- Do not expose local paths, internal hosts, network coordinates, private infrastructure names, secrets, or private studio tooling.
- Use repository-relative references in public artifacts.
