<!--
AA5 report. Lane A (shore integrity) only; lane B is appended when AA1 is DONE.
Author: Rubén Vega Balbás PhD (agent-assisted). Status VERIFYING. The agent does not mark DONE.
-->

# PHASE-AA5 report: container, permanence, health and deploy ops

## Lane A: shore integrity (F25, F27, F28 · I7–I9)

**Status:** VERIFYING · **Opened by:** the owner, 2026-11-10 ("permanent data needed"), ahead of
AA0 DONE · **Branch:** `cascade/PHASE-AA-PREPROD-HARDENING-5` · **Exit gate:**
[`PHASES/AA5-container-and-deploy-ops.exit-gate.sh`](PHASES/AA5-container-and-deploy-ops.exit-gate.sh)

### What changed

| Finding | Change | Where |
| ------- | ------ | ----- |
| **F25 / I7** proposals lost on recreate | The backend mounts the host folder `./data/proposals` at `TTOD_PROPOSAL_DIR`. The host path can be overridden with `TTOD_PROPOSAL_HOST_DIR`. Contents are gitignored, and a README explains the folder | `docker-compose.yml` (backend `volumes`), `.gitignore`, `data/proposals/README.md` |
| **F27 / I8** health 200 with Redis down | With Redis configured and the ping failing, `/health` answers **503** `{"status":"degraded","redis":"down",…}`, without the exception text. Compose's healthcheck (`urlopen` raises on 503) now marks the backend unhealthy | `services/backend/app/main.py` |
| **F28 / I9** empty secrets regenerate per process | `Settings.from_env` refuses to boot when `REDIS_URL` is set and `TTOD_SESSION_SECRET` or `TTOD_PAT_SECRET` is empty: "run `make env-secrets`". Without Redis (dev, tests) a throwaway secret is still generated. `make rebuild` now runs `ensure_env_secrets.py` first, as `make up` already did | `services/backend/app/config.py`, `Makefile` |

### Evidence

- **Before (AA0 probe, 2026-11-10):** the backend container had 0 mounts, and with Redis stopped
  `/health` returned **HTTP 200** `redis: down`
  ([`baselines/aa0-2026-11-10/probe.log`](baselines/aa0-2026-11-10/probe.log)).
- **Tests:** `services/backend/tests/test_aa5_shore_integrity.py`, 6 tests, all passing:
  - 503 when Redis is down, with no exception text leaked;
  - 200 when Redis is up;
  - boot fails for each empty secret when Redis is set;
  - a throwaway secret is generated without Redis;
  - secrets that are set are used verbatim.

  The full backend suite stays green.
- **After, live but isolated:** the exit gate builds this worktree's backend in its own Compose
  project, `ttod_aa5gate`, with only Redis and the backend and no host ports.
  - It writes a file into `data/proposals/` and force-recreates the backend; the file is still
    visible at `TTOD_PROPOSAL_DIR`.
  - It stops that project's Redis; `/health` answers **503**.

  The project is removed afterwards. The instructor stack (`ttod_oracle`) was never touched.

### Rolling it out to the instructor stack (after the owner merges)

Run from `~/src/ttod` on `main` after the merge. `make rebuild` recreates every service, Redis
included; its AOF keeps the data.

1. `make rebuild` on Tanit. It runs `ensure_env_secrets.py`; `.env` already has both secrets, so
   the boot check passes.
2. **No migration is needed today.** On 2026-11-10 the running container's proposal folder held
   **0 files**, so the bind mount hides nothing.
   - If drafts appear before the rebuild, copy them out first:
     `docker cp ttod_oracle-backend-1:/workspace/services/backend/data/proposals/. data/proposals/`.
   - Drafts also live in Redis (dual-write), so the copy is a belt-and-braces step.
3. Check the mount: `docker compose -p ttod_oracle exec backend sh -c 'ls -la "$TTOD_PROPOSAL_DIR"'`
   lists the same files as `ls -la data/proposals`. The single quotes matter: the variable only
   exists inside the container. Check health: `curl -fsS http://127.0.0.1:18080/health` shows
   `"redis":"ok"`.
4. Back up `data/proposals/` together with `data/redis/`.
5. **Accepting a web draft** (F25's second half): `cli.py proposal accept` reads `proposals/`, so
   run `.venv/bin/python cli.py proposal import data/proposals/<id>.json` first, then review and
   accept as usual. The Redis copy stays `proposed` in the web queue until it is resolved there.

### Notes for lane B and later phases

- **File ownership.** The backend still runs as root (F16 is lane B), so drafts on a Linux host
  such as Lilith are owned by root. When lane B adds a non-root `USER`, it must give the host folder
  the matching UID, or the backend stops being able to write drafts.
- **A stricter boot.** A raw `docker compose up` without `.env` secrets now fails on purpose, with
  a clear message. Before, it silently produced sessions that died on every restart. Students who
  run Compose directly need `make env-secrets` once.

### Cold review amendments (PASS-WITH-AMENDMENTS, [PHASE-AA5-COLD-REVIEW.md](PHASE-AA5-COLD-REVIEW.md))

| Finding | Amendment |
| ------- | --------- |
| F1 (P1) | The README and the Compose comment no longer claim `accept` reads the folder; rollout step 5 documents `proposal import`. No CLI change was needed |
| F2 (P1) | The four `cp .env.example .env` guides (local setup EN/ES, student and maintainer guides) add `python3 scripts/ensure_env_secrets.py`; the boot error names the script, not only `make` |
| F3 (P1) | Rollout step 3 uses `sh -c '…"$TTOD_PROPOSAL_DIR"'`, adds a health check, and says where the commands run |
| F4 (P2) | The API guides (EN/ES) document the 503 and the `redis` field |
| F5 (P2) | The test is renamed `…body_is_sanitized` and marked a regression guard; the real leak is F47 (lane B) |
| F7 (P2) | `.env.example` gains `TTOD_PROPOSAL_HOST_DIR`, notes that `TTOD_PROPOSAL_DIR` must be absolute, and its stale "random secret if empty" comment now states the F28 rule |
| F6 (P2) | Not taken: a live empty-secret boot probe adds a build for a rule the unit tests already prove |

Handed to lane B: the `main.py` repository-exception leak (F47), and giving `data/proposals` the
non-root UID when F16 lands.

### Gate amendment made during the phase

The gate's isolated stack had no `.env`. After F28 its backend correctly refused to boot, so the
gate now writes throwaway secrets (`openssl rand`) to a temporary env file, passes it with
`--env-file`, and deletes it on exit. It never reads the instructor's `.env`. Every other check is
unchanged.

### Out of lane A (open)

Lane B covers F2, F6, F16–F19, F29–F31 and F45–F48. It stays BLOCKED until AA1 is DONE.
