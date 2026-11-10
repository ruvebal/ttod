# PHASE-AA5: Container, permanence, health, and deploy ops

> **Track:** ops / shore integrity — F2, F6, F16–F19, F25, F27–F31, F45–F48 · I1–I16.  
> **Status:** two lanes (amended 2026-11-10, since the old gate contradicted its own "prefer early" note).  
> **Lane A (shore integrity: F25, F27, F28 / I7–I9): READY after AA0.** It has no dependency on Caddy headers.  
> **Lane B (everything else): BLOCKED until AA1 DONE.** One report, two VERIFYING passes.

## Goal

Bind-mount proposal dual-write disk; make `/health` fail when Redis is down; fail-closed secrets + `ensure_env_secrets` on rebuild; Redis `maxmemory`; stop publishing Ollama by default; non-root USER; healthchecks; CI/backend tests; honest TLS story; Lilith rewrite; npm audit.

## Deliverables

- Compose volume `./data/proposals` (+ gitignore) for `TTOD_PROPOSAL_DIR`.
- `/health` → 503 (or ready split) when Redis down under `REDIS_URL`.
- Secrets boot policy + Makefile `rebuild` calls ensure.
- `maxmemory` in `redis.conf`; Ollama host publish off by default.
- Dockerfile USER + frontend/mcp healthchecks.
- CI + `make test` discover `services/backend/tests`.
- Lilith checklist + TLS note + npm audit excerpt.
- Redis pool knobs: timeouts, `health_check_interval`, `max_connections` (F46 / I14); sanitized 503 bodies on health/oracle (F47 / I15); JSON access logs with request id, or an explicit AA0-accepted deferral (F48 / I16).
- Orphan-file note for disk-first dual-write (F31 / I13).
- Recreate smoke: proposal file survives backend recreate.
- Cold review.

## Scope

**In:** Compose, Dockerfiles, redis.conf, Makefile, CI, ops docs, health handler.  
**Out:** Cloud registry; issuing real public certs on student laptops.

## Prompt (Implementation Agent)

```text
Implement PHASE-AA5 per
docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING/PHASES/AA5-container-and-deploy-ops.md.

## Deliver
1. Bind-mount proposal dir; prove recreate keeps dual-write files.
2. Health 503 (or ready) when Redis down; Compose notices.
3. ensure_env_secrets on rebuild; fail boot on empty secrets when REDIS_URL set.
4. Redis maxmemory; unpublish Ollama host port by default.
5. Non-root USER; frontend (+ mcp) HEALTHCHECK.
6. CI + make test run backend suite.
7. Lilith checklist + TLS honesty + npm audit note.
7b. Redis pool knobs (F46); sanitize error bodies (F47); structured logs or deferral (F48); orphan note (F31).
8. Cold review. Do not self-certify DONE.

## Constraints
- Do not publish Redis ports. No secrets in git. No commit unless asked.
```

## Acceptance

- [ ] `docker compose up --force-recreate` backend keeps proposal files on host bind.
- [ ] Redis stop → backend not “healthy” via HTTP 200-only check.
- [ ] Backend unit tests run in CI/`make test`.
- [ ] F2 cannot be misread as “8443 is TLS.”
- [ ] Cold review green or amended.

## Risks

- Non-root + bind mounts permission surprises — test on Tanit before Lilith.
