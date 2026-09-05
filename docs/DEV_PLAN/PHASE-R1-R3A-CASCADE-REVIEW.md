# Phase R1/R2/R3a execution and downstream cascade review

**Date:** 2026-09-05  
**Outcome:** R1 DONE, R2 DONE, R3a DONE; cohort-start gate open on the declared macOS Docker
reference runtime.

## Evidence evaluated

- TTOD preconditions: strict validation clean, metadata check clean, 204 existing tests green.
- R1: six backend tests green; all six routes implemented; deterministic graph verified; proposal
  path remains proposed/blackbox; live FastMCP Streamable HTTP retrieval from R2 succeeded and
  fails closed when R2 is unavailable.
- R2: five focused tests green; 229 eligible records indexed through local `nomic-embed-text` in
  2.719 seconds; rights and graph-edge leakage findings fixed during review.
- R3a: Astro check/build clean; backend/MCP/frontend Docker images build; four-service host mode
  and five-service container profile run; `/health`, `/en/`, `/es/`, and the live quote route pass
  through Caddy; `llama3.2:1b` is present in the container tier; attribution is rendered.

## Structural findings propagated

1. The original plan specified R1 consuming R2 but omitted the FastMCP client transport. The
   frozen contract is now Streamable HTTP at `${MCP_SERVER_URL%/}/mcp`, with R2's
   `semantic_retrieval` envelope and fail-closed behavior. R7 must test the live link.
2. "All five containers" contradicted host mode, where Ollama is intentionally native and absent
   from Compose. The truthful topology is four host-mode services or five services with explicit
   `--profile container`; `OLLAMA_MODE` alone cannot activate a Compose profile.
3. Requiring physical proof on macOS, Linux/Podman, and Windows/WSL2 before cohort start made a
   single-host instructor gate impossible. R3a now requires one real reference-runtime smoke plus
   both Compose configurations. R6 adds Linux CI evidence; Windows/WSL2 remains an explicit,
   honestly reported onboarding check.
4. The existing `.env*` ignore rule also hid `.env.example`. The exception `!.env.example` is now
   present. Host mode defaults to the confirmed local `qwen3.8:27b`; container onboarding
   explicitly switches to `llama3.2:1b`.

## Review of R3b–R7

- **R3b, R4, and R5 may start in parallel.** Their touched-path budgets remain disjoint. They must
  consume the frozen `domain.ts` and the R3a report rather than reopening infrastructure files.
- **R3b:** retain strict locale filtering. The live corpus currently has English records only, so
  an `/es/` wisdom route must show an honest empty state until accepted Spanish records exist;
  it must not silently render an English quote. Translated editorial docs are separate from quote
  translations and do not mutate `ttod.yml`.
- **R4/R5:** the URL query is the only shared island channel. R5 should read `?tag=` at submit time
  (or on navigation) so parallel landing order does not create a hidden shared-store dependency.
  R5 owns the initial `src/lib/db.ts`; R6 extends it only after R5 is DONE.
- **R7 starts now, continuously.** Its first useful tests are R1 endpoint contracts, live R1→R2
  transport/fail-closed behavior, governance negative coverage, and threshold calibration. It
  must not wait for R3b/R4/R5 to finish.
- **R6 remains downstream of R3b/R4/R5.** It owns Linux Compose CI evidence and PWA/deployment
  integration. Scaleway staging remains instructor-gated and is not required for student local
  development.

## Remaining risks, not gate blockers

- Podman and Windows/WSL2 have not been executed yet; those claims remain open and assigned to
  R6/R7/onboarding evidence.
- The pre-existing Phase S blackbox proposal acceptance gap remains. R1 correctly stages inert
  proposals and does not bypass it; no report claims draft-to-accept works end to end.
- Retrieval threshold `0.575` is only a starting value until R7 lands its named empirical
  calibration fixture.

