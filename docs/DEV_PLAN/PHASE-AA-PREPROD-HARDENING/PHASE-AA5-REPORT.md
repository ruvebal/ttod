<!--
AA5 report. Lane A (shore integrity, DONE 2026-11-10) and lane B (ops, 2026-11-11).
Author: Rubén Vega Balbás PhD (agent-assisted). Status VERIFYING. The agent does not mark DONE.
-->

# PHASE-AA5 report: container, permanence, health and deploy ops

## Lane A: shore integrity (F25, F27, F28 · I7–I9)

**Status:** DONE (owner, 2026-11-10; cold review PASS-WITH-AMENDMENTS, amended) · **Opened by:** the owner, 2026-11-10 ("permanent data needed"), ahead of
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

## Lane B: ops (F2, F6, F16–F19, F29–F31, F45–F48 · I1–I6, I10–I16)

**Status:** DONE (owner, 2026-11-11: "AA5 done") · cold review **PASS-WITH-AMENDMENTS** ([PHASE-AA5-COLD-REVIEW.md](PHASE-AA5-COLD-REVIEW.md) § Lane B), amended in the same session (§ Cold review amendments) · **Branch:** `cascade/PHASE-AA-PREPROD-HARDENING-5` (reopened from `main` at
`fd2f8278`). **Exit gate:** the same file. The lane B checks were appended before any code (commit `4f529de6`),
lane A's checks keep running, and lane A's live part moved onto `scripts/isolated-stack.sh` (AA2 cold review F3).

### What changed

| Finding | Change | Where |
| ------- | ------ | ----- |
| **F2** TLS honesty (I1) | Caddy says in plain words that `:8443` is NOT TLS. `servers { trusted_proxies static {$TTOD_TRUSTED_PROXIES:127.0.0.1/32} }`: only the TLS proxy in front (Traefik on Lilith) may pass `X-Forwarded-Proto`/`-For`. The default trusts nobody | `caddy/Caddyfile`, compose `reverse-proxy.environment`, `.env.example` |
| **F6** pins (I4) | Ollama is pinned by digest (`ollama/ollama@sha256:3293…`, 0.33.3, the image Tanit runs). Caddy and Redis still float within a minor or major line (recorded in the Lilith checklist) | `docker-compose.yml` |
| **F16** non-root (I2) | backend and mcp run as `ttod` (uid 10001, build arg `TTOD_UID`); frontend runs as `node`. The backend image owns its drafts folder, and the Lilith checklist gives the one `chown` a Linux host needs for the bind | three Dockerfiles |
| **F17** health checks (I3) | frontend: a `fetch` of `/site.webmanifest` (no backend involved). mcp: a TCP connect to 3001. The backend still needs mcp only `started`, so the site never waits on the Oracle's retrieval | `docker-compose.yml` |
| **F18** Lilith checklist (I5) | Rewritten for current `main`: services and users, `.env` with `TTOD_ALLOWED_HOSTS` / `COOKIE_SECURE` / `TTOD_TRUSTED_PROXIES`, `ensure_env_secrets`, `chown`, the TLS proxy steps, current probes (`wis-034`, headers, 301, 401, request id, maxmemory), and the security boundary | `docs/DEV_PLAN/LILITH-VALIDATION-CHECKLIST.md` |
| **F19** npm audit (I6) | Re-measured below; fixes deliberately deferred | this report |
| **F29** Redis memory (I10) | `maxmemory 256mb` with `noeviction` kept: a runaway client now gets a clean error, not an OOM kill | `redis/redis.conf` |
| **F30** Ollama port (I11) | No host port by default. `docker-compose.ollama-port.yml` is the opt-in, publishing on `127.0.0.1` only. It is needed only when a host tool should use the *stack's* Ollama; `make review-pr` defaults to a native one on `:11434`. The docs that named `:11435` say so | compose, override, guide, `review-local.sh` |
| **F31** orphans (I13) | A note on why a draft can be orphaned (disk write, then Redis fails) and how to sweep it | `data/proposals/README.md` |
| **F45** backend tests (I12) | `make test` now also runs `services/backend/tests`, and CI gains a `backend-tests` job (Python 3.12, the `make venv` installs). The push trigger now includes `services/backend/**` and `ttod_core/**` | `Makefile`, `.github/workflows/ci.yml` |
| **F46** Redis pool (I14) | `socket_timeout` 2 s, `socket_connect_timeout` 2 s, `health_check_interval` 30 s, `max_connections` 50, each overridable by env | `app/redis_client.py`, compose |
| **F47** sanitized bodies (I15) | `/health`'s 503 says only "TTOD repository unavailable"; the reason goes to the log. The Oracle stream never put exception text in a response (errors inside the stream are logged), so nothing changed there | `app/main.py` |
| **F48** structured logs (I16) | One JSON line per request (`ts, event, request_id, method, path, status, ms`); only the path, never the query or headers. Caddy stamps its own UUID (`header_up X-Request-ID {http.request.uuid}`), so a client cannot choose the logged id. The backend echoes the id and mints one for direct calls; uvicorn's text access log is off | `app/access_log.py`, `caddy/Caddyfile`, backend Dockerfile |

### Evidence

- **Backend tests:** `health_body_sanitized`, `redis_pool_knobs` (2) and `request_id` (3) in
  `tests/test_aa5_lane_b.py`. The full backend suite runs 134 tests, OK, and `make test` runs both suites.
- **Live, isolated stack** (`ttod_aa5gate`, from the gate):
  - backend, frontend and mcp run with a non-zero uid;
  - the non-root backend writes a draft into the host bind (201, one more file);
  - frontend and mcp report `healthy`;
  - Redis reports `maxmemory` > 0 with `noeviction`;
  - `/health` through Caddy carries a UUID `X-Request-ID`, and the backend log has a JSON line with that id and
    path. A client-chosen id does not survive the proxy;
  - **https login through a proxy Caddy does not trust: `403 plain`. Through a trusted one
    (`TTOD_TRUSTED_PROXIES` = the stack's subnet): `303 secure`.** The same request in both runs; only the trust
    setting differs, so the pair falsifies itself;
  - lane A still holds: drafts survive a recreate, and `/health` answers 503 with Redis down.
- **`npm audit --omit=dev`** (services/frontend, 2026-11-11): **18** production advisories (1 critical, 8 high,
  3 moderate, 6 low).

  | Severity | Package (direct?) | Fix |
  | -------- | ----------------- | --- |
  | critical | `astro` (direct) | major: astro 7.4.10 |
  | high | `@astrojs/node` (direct), `sharp`, `zod`, `zod-to-ts` | major: @astrojs/node 11, astro 7 |
  | high | `devalue`, `source-map-js`, `undici`, `vite` | non-breaking |
  | moderate | `@tailwindcss/typography` (direct), `postcss-selector-parser` | major |
  | moderate | `smol-toml` | non-breaking |
  | low | `@astrojs/mdx`, `@astrojs/svelte` (direct), `esbuild`, three svelte-plugin packages, `deepmerge` | major |

  **Both kinds of fix are deferred deliberately** (I6: "defer majors intentionally"). The Astro 5 → 7 upgrade
  rebuilds the whole frontend and needs the AA3/AA3b browser checks. The non-breaking fixes change the
  lockfile under the same frontend. Both belong in one dependency PR with its own tests, not in an ops phase.
  **Recommendation:** do that PR before any public exposure. The Lilith checklist §7 says the same.

### Amendments (disclosed)

- **Gate bugs fixed while running it** (they don't weaken anything):
  - the compose-config check piped JSON into a script that was itself on stdin (now a temp file);
  - the draft check assumed the JSON login sets a cookie, but it returns the token in its body.
- **Gate strengthened:** the request id must be Caddy's UUID (a backend-minted id has no dashes), and a
  client-chosen id must not come back. Without this, the check passed even with Caddy out of the picture.
- **mcp health is a TCP connect, not an HTTP probe.** fastmcp's HTTP transport has no plain health route, and
  a JSON-RPC probe would test the Oracle's dependencies, not whether the server is up.

### Decisions for the reviewer to challenge

- **uid 10001, not 1000.** It matches no typical host user, so the chown is explicit and documented. 1000
  would "just work" on many laptops by accident.
- **The trusted-proxy default is `127.0.0.1/32`.** That is a value Caddy accepts which trusts nothing reachable
  from outside its container. There is no "trust the LAN" option.
- **Request ids for API requests only.** Caddy stamps the backend route; frontend page renders call the
  backend server-to-server without one (they get a backend-minted id). Correlating page views was not asked
  for.

### Rollout (owner)

1. Run `make rebuild`. It builds the backend and mcp images with your uid, and runs Redis as you (no `chown`
   anywhere). Ollama is recreated with the pinned image, the same one already running, and keeps its model
   volume. Its host port `11435` disappears; the override restores it on loopback if a host tool needs the
   stack's Ollama.
2. Check: `curl -s -D - -o /dev/null http://127.0.0.1:18080/health | grep -i x-request-id` (a GET; HEAD answers
   405) and `docker compose logs --tail=5 backend` (JSON lines).
3. **Optional, GitHub settings:** make `backend-tests` a required check next to `typecheck-and-build`. Today a
   red backend run would not block a merge.

### Cold review amendments (lane B, 2026-11-11)

The verdict was PASS-WITH-AMENDMENTS, with one P1. Every finding was handled in this session:

| # | Fix | Proof |
| - | --- | ----- |
| F1 (P1): on Linux the non-root backend could not write `data/proposals` (every proposal a 500) | `make` exports your uid/gid (`TTOD_UID`, `TTOD_GID`). Compose passes them as build args to backend and mcp, whose Dockerfiles create that user (numeric `USER`, root → 10001). Plain `docker compose` keeps 10001, and the setup guides (en, es) now show Linux users the one `.env` line. The backend logs a clear startup error when the drafts folder is not writable | The gate now runs the live stack with the host uid and checks that the backend **and Redis** run as that uid (the structural proof; Docker Desktop's ownership mapping hides the write failure itself) |
| F2: the trusted-proxy story had holes | The checklist §4: Traefik must reach Caddy over the Docker network, not the published port (on Docker Desktop every client comes from `192.168.65.x`); Traefik must not forward client `X-Forwarded-*` (keep `forwardedHeaders.insecure` off); several CIDRs are space-separated, never comma; never `private_ranges`. The same rules are in the Caddyfile comment and `.env.example` | — |
| F3: `chown -R` broke `git pull`; Redis files needed sudo | Gone with F1: under `make`, Redis runs as you too (`TTOD_REDIS_USER`), so `data/` stays yours | gate: Redis uid = host uid |
| F4: non-breaking npm fixes not covered by I6; no reachability | `npm audit fix` (lockfile only): **18 → 13** (4 highs, 1 moderate gone). The frontend suite (269), `astro check`, the build, and the AA3 + AA3b browser checks pass on a stack built from the new lockfile. **Reachability** of the 13 left (all need Astro 7): the Astro XSS advisories need `define:vars`, spread props, `transition:` directives or server islands, and TTOD uses none (every `transition:` in the code is CSS); `sharp` needs `astro:assets` (unused); `zod` and `esbuild` run at build time. The one reachable, `@astrojs/node` crashing on a malformed `Host` port, is now blocked at Caddy (strict `Host` matcher → 400). The checklist guard now also says that student stacks are reachable by classmates on a shared LAN | gate: `Host: localhost:8x8x` → 400 at Caddy |
| F5: `curl -sI` sends HEAD (405); the `make review-pr` claim was wrong | Both corrected here and in the checklist | — |
| F6: `/health` said `redis: ok` at the memory cap; probe log noise | `redis: "full"` and 503 within 5 % of `maxmemory`. Docker's internal `/health` probe (no request id, status 200) is no longer logged; one through Caddy, or any failure, still is. The ~350 ms cost of `/health` predates AA5 and stays recorded | `health_redis_full…`, `request_id_health_probe…` tests |
| F7: `ms` for streams; `match` + `$` | `ms` is documented as time until the response starts; the request id uses `fullmatch` | `request_id_trailing_newline…` test |
| F8: CI job not required; trigger paths | The push trigger adds `ttod.yml`, `schema/**`, `pyproject.toml`, `cli.py`. Making `backend-tests` required is a GitHub setting for the owner (rollout step 3). The workflow keeps its name, because renaming it changes nothing about required checks and only adds noise | — |

**Also found while amending:** the first draft of the probe-skip used `return` inside `finally`, which replaced
the response with `None` (caught by the existing health tests). It now logs from `finally` and never returns
from it.
