# PHASE-AA5: Container, permanence, health, and deploy ops

> **Track:** ops / shore integrity — F2, F6, F16–F19, F25, F27–F31, F45–F48 · I1–I16.  
> **Status:** two lanes (amended 2026-11-10, since the old gate contradicted its own "prefer early" note).  
> **Lane A (shore integrity: F25, F27, F28 / I7–I9): READY after AA0.** It has no dependency on Caddy headers.  
> **Lane B (everything else): VERIFYING 2026-11-11** (AA1 DONE; owner chose lane B before AA4). One report, two VERIFYING passes.
> Lane B checks are appended to the exit gate, and lane A's live part moved onto `scripts/isolated-stack.sh` (AA2 cold review F3).

**Exit gate:** [`AA5-container-and-deploy-ops.exit-gate.sh`](AA5-container-and-deploy-ops.exit-gate.sh) (lane A now; lane B is appended when AA1 is DONE). Read it before you start: it names the backend tests it runs (`*health_redis_down*`, `*empty_secret*`) and smoke-tests recreate + Redis-down in an isolated Compose project.

**Lane A DONE (2026-11-10):** F25 bind mount, F27 health 503, F28 fail-closed secrets ([PHASE-AA5-REPORT](../PHASE-AA5-REPORT.md)). Carried into lane B by the lane A cold review:
- **F47, concretely:** `/health` puts the repository exception text in its 503 body (`main.py` health handler, `detail=f"TTOD repository unavailable: {exc}"`). Sanitize it and add a test that fails on today's body.
- **Non-root `USER` (F16)** must own the `data/proposals` bind (and `data/redis` if touched): set the UID/GID and document a `chown` on Linux hosts (Lilith), or the backend can no longer write drafts.
- `make rebuild` is now safe for drafts (bind mount live), but rollouts of one service should still recreate only that service.

**Carried from AA2 (cold review F3, 2026-11-10):**
- Move the AA5 lane A gate's live part onto `scripts/isolated-stack.sh` (temp Redis/drafts dirs). It is safe today only because the harness runs it in a worktree.
- **F2 / TLS story:** a TLS proxy in front of Caddy (Traefik on Lilith) needs Caddy `servers { trusted_proxies static <proxy-cidr> }` so `X-Forwarded-Proto`/`-For` survive. Re-test an `https://` form login (it is 403 today) and `COOKIE_SECURE=auto` producing Secure. Never trust the classroom LAN ranges: a student could then spoof `X-Forwarded-For` past the per-IP throttle.
- **Non-root `USER`** must own `data/proposals` **and** the Redis dir (`TTOD_REDIS_HOST_DIR`, default `data/redis`).
- **Lilith checklist** names `TTOD_ALLOWED_HOSTS` (build-time) and `COOKIE_SECURE`.

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
