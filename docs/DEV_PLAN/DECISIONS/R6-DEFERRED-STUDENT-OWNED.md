# R6 decision — deferred and reserved for student ownership, not implemented

> **2026-09-07 refinement:**
> [`U0-2026-09-07-TEACHING-SKELETON-BOUNDARY.md`](U0-2026-09-07-TEACHING-SKELETON-BOUNDARY.md)
> preserves student ownership of R6's assessed depth while permitting Phase U to plan a minimal,
> instructor-provided hello-world seam. This historical decision remains authoritative for the
> rich reference build and full R6 scope; read both records together for the future teaching
> baseline.

> **Documentation-only exception:**
> [`U1-2026-09-07-PUBLIC-DOCS-PAGES-BOUNDARY.md`](U1-2026-09-07-PUBLIC-DOCS-PAGES-BOUNDARY.md)
> permits a Jekyll Pages workflow rooted only at `docs/public`. It is not application CI/CD, PWA,
> cloud application deployment, or assessed R6 work.

**Status:** FROZEN (product-owner instruction, 2026-09-05)
**Decider:** Rubén Vega Balbás (TTOD product owner)
**Cascade:** Phase R §6 — see [`../PHASE-R-TTOD-ORACLE-PLATFORM-CASCADE-PROMPT.md`](../PHASE-R-TTOD-ORACLE-PLATFORM-CASCADE-PROMPT.md)
**Does not mutate:** `ttod.yml`, `schema/*.json`, `ttod_core/`, or any deployment target — this
record freezes a scope boundary; it does not implement anything.

## Decision

**R6 is not implemented in the reference build on `main`, and must not be implemented by an
agent or continued cascade momentum.** R3b, R4, R5, and R7's current work landed as a reference/
architectural-validation build — proof the plan is buildable, not the graded student artifact.
R1, R2, and R3a are the only phases students inherit directly (via the generated
`cohort-starter` branch, see `scripts/generate-cohort-starter.sh` and the closure report). R6
begins only when the actual cohort takes ownership of it as their own work.

**R6's full scope, so "deferred" cannot quietly shrink to mean "the easy half is done, only
deployment is left":**

- PWA service worker (`public/sw.js`, Cache-First static / Network-First API) and the durable
  offline-queue integration that extends R5's `src/lib/db.ts`.
- CI/CD workflow files (`.github/workflows/*.yml`) — typecheck/unit gate, sharded Chromium E2E,
  measured wall-clock time.
- **Linux CI evidence** — R3a's own report explicitly left this as an R6/R7 target, not something
  claimed from a macOS Docker run. GitHub Actions' own hosted Linux runners are the intended
  mechanism (already correctly named in `PHASES/R6-pwa-cicd-audit.md`) — not Lilith, which is
  private studio infrastructure students cannot reach (see the 2026-09-05 Lilith/Tanit correction
  in the master document, commit `41eb1d51`).
- Windows/WSL2 onboarding evidence, honestly reported, not inferred from any other platform.
- Lighthouse performance budgets.
- Any Scaleway `stg` deployment integration (itself separately gated on the §0.1.3 deploy decision
  being signed — R6 does not reopen that decision, only implements against it once it exists).

## Why this needed a written decision, not just a status line

Phase R's own §6.1 cold-review discipline and the cascade's own momentum (R0 through R5, plus R7
continuing) make it easy for an implementing session to read "R6 is next in the dependency graph"
and just build it — nothing in the mechanical gates alone stops that. This record exists so that
never happens by inertia: **an open dependency slot is not authorization.** Only an explicit,
separate instruction from the product owner reopens R6, the same discipline already established
for the Scaleway deploy decision (§0.1.3) and for Phase S's translate-draft backfill scope.

## What this does not do

- It does **not** say R6 will never happen — it happens when the cohort owns it, which is the
  original design (§6's ownership column always marked R6 "student, 1 owner").
- It does **not** retroactively invalidate R7's existing reference-build test work — R7 stays
  PARTIAL, correctly gated on R6-shaped closing work (assembled Chromium E2E, measured CI timing)
  that only makes sense once R6 exists. See the updated `PHASE-R7-REPORT.md`.
- It does **not** touch the reference build's own R3b/R4/R5 source — those stay on `main` as a
  validated reference, per their own decision (`PHASE-R1-R3A-CASCADE-REVIEW.md`), untouched by
  this record.
- It does **not** authorize deleting or rewriting anything — R6's absence is enforced by simply
  not having built it, not by a lock file or a check that blocks a future session mechanically.
  The mechanical enforcement is this document plus the master doc's updated status line; a future
  session must still read them.

## Consequence for future sessions

Any agent or session reading Phase R's dependency graph and finding R3b/R4/R5/R7 all in a DONE-or-
PARTIAL state, with nothing obviously blocking R6, must treat that as a **prompt to check this
record**, not as a green light. If R6 work is ever wanted before the cohort starts (e.g. the
product owner decides a full end-to-end reference including deployment is worth building for a
department pitch or demo), that is a new, explicit decision — record it the same way this one was
recorded, do not silently start building `.github/workflows/` files because the gate table has a
row for them.
