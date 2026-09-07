---
name: public-artifact-privacy
description: Audit exact public, partner, student, or research-facing artifact candidates for leaked local paths, private network coordinates, internal hostnames, private machinery names, non-studio email identities, and internal roadmap language. Use before publishing, distributing, synchronizing, or claiming an artifact is sanitized.
---

# Public Artifact Privacy

Audit the exact artifact to be released, not merely its source branch or a nearby working tree.

## Workflow

1. Resolve the candidate's file list, generated output, archive contents, and reachable Git objects
   where relevant. A safe build source does not prove its rendered or packaged artifact is safe.
2. Run `../../scripts/check_public_privacy.py` over those files. For repository-wide checks, omit
   paths so the watcher reads `git ls-files`.
3. Supply private machinery terms through `TTOD_PRIVATE_TERMS_FILE`, pointing to a local untracked
   newline-delimited denylist. Never commit that denylist or repeat its values in a report.
4. Manually review findings. Replace local paths with repository-relative paths, private coordinates
   with role labels, personal identities with the approved `@crea-comm.net` studio domain, and
   internal phase identifiers with reader-facing capability or maturity language.
5. Rebuild or re-export, then rerun against the exact rendered or packaged candidate. Zero findings
   are required in source and output.

The tracked watcher covers common local home, mount, temporary and tilde paths; private IPv4 and
IPv6; internal hostname suffixes; and disallowed email domains. Bare machine or project names still
depend on the untracked denylist. The watcher is a deterministic gate, not proof that all sensitive
information has been found. Pair it with secret scanning, history inspection, rights review, and
human cold reading appropriate to the release risk. Do not suppress a real finding through broad
exclusions.

Within `docs/public` and rendered `_site-public` output, the watcher also rejects internal
development phase names and shorthand. Public readers should see what exists, what remains open,
and why it matters—not the private indexing system used to orchestrate implementation.
