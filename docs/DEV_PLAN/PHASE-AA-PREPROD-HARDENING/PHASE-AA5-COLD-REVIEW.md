<!--
AA5 lane A cold review. Reviewer: cascade-cold-reviewer (agent), no implementation context.
Scope: lane A only (F25, F27, F28 · I7–I9). Lane B is BLOCKED and not reviewed. Not marked DONE.
-->

# PHASE-AA5 cold review: lane A (shore integrity)

**Commits reviewed:** `2aa93c0d` (implementation) and `0fac53e6` (verify log), compared against `40342a92`.
**Verdict: PASS-WITH-AMENDMENTS.** No P0. Three P1 findings to amend before DONE: all three are
documentation or message fixes, and the code behaviour is correct.

## What I ran (2026-11-10, on Tanit)

| Check | Command | Result |
| ----- | ------- | ------ |
| Backend suite | `.venv/bin/python -m unittest discover -s services/backend/tests -t . -p 'test_*.py'` | `Ran 99 tests … OK` |
| Root suite (`make test`) | `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` | `Ran 236 tests … OK` |
| New tests against the pre-change code | `git archive HEAD~2` to the scratchpad, add `test_aa5_shore_integrity.py`, run it | `FAILED (failures=4)`. Both `health_redis_down*` tests fail, and both `empty_secret_fails_boot` subtests fail. The other 3 pass either way (they are regression guards) |
| Exit gate, rerun by me | `bash PHASES/AA5-container-and-deploy-ops.exit-gate.sh` | `EXIT=0` in 71 s; `recreate kept aa5-gate-53253.txt; /health 503 with Redis down`. `ttod_oracle` was untouched (same uptimes before and after) |
| Bind target follows `.env` | `env TTOD_PROPOSAL_DIR=… docker compose config` | `/srv/drafts`: env and volume target both `/srv/drafts`. Empty: both fall back to the default. `TTOD_PROPOSAL_HOST_DIR=/tmp/elsewhere`: the source moves and the target stays. **The target always equals the backend's `TTOD_PROPOSAL_DIR`** |
| Data hidden by the mount | `docker exec ttod_oracle-backend-1 ls -la $TTOD_PROPOSAL_DIR`; Redis `--scan ttod:proposal:*`; `git ls-files services/backend/data` | 0 files in the container, 0 drafts in Redis, nothing baked into the image. Nothing is hidden |
| Fail-closed message | `env -i REDIS_URL=redis://redis:6379/0 TTOD_SESSION_SECRET= python -c "import services.backend.app.main"` | `RuntimeError: TTOD_SESSION_SECRET is empty while REDIS_URL is set; run \`make env-secrets\`` |
| Instructor `.env` | secret lengths only | `TTOD_SESSION_SECRET len=43`, `TTOD_PAT_SECRET len=43`, so the report's rollout step 1 holds |

## Acceptance (lane A boxes)

- [x] **1. Recreate keeps proposal files on a host bind.** I reran the gate live in an isolated project.
- [x] **2. With Redis stopped, the backend is no longer "healthy" through an HTTP 200-only check.**
  `/health` returns 503 live. The Compose healthcheck uses `urlopen`, which raises on 503, so the
  check exits non-zero.
- [ ] 3. Backend tests in CI/`make test`: **lane B**. `make test` still discovers only `tests/`
  (Makefile:116).
- [ ] 4. F2 / 8443: **lane B**, not applicable here.
- [ ] 5. Cold review: this document. Green once F1–F3 are amended.

## Findings

| ID | Sev | Blocks DONE | Finding and evidence | Fix |
| -- | --- | ----------- | -------------------- | --- |
| **F1** | P1 | yes (amend) | **The second half of F25 is still open: the host CLI does not read `data/proposals`.** `data/proposals/README.md:5-6` and `docker-compose.yml:54` both say the instructor can review drafts, or `cli.py proposal accept` can read them, from the host. In fact `cli.py:53` hardcodes `DEFAULT_PROPOSALS = Path(__file__).parent / "proposals"`, and `proposal accept --help` offers only `--file` and `--allow-unknown-tags`. `accept <id>` therefore looks in the canonical `proposals/` folder and cannot find a web draft. The step that works is `cli.py proposal import data/proposals/<id>.json` (`cli.py:316-324`, which uses the same `ProposalStore` JSON format, `proposal_drafts.py:26`). It is followed by `accept`, or by the `proposals/*.json` PR flow (`.github/workflows/proposal-accept.yml`). Neither step is written down anywhere | Correct the README and the Compose comment, and add an "Accepting a web draft" step to the report's rollout: `import data/proposals/<id>.json`, then PR or `accept`. Also state that Redis and `data/proposals` keep the draft as `proposed` afterwards, so it stays in the web queue (this belongs with the F31 orphan note in lane B). If the host CLI must read the folder directly, adding a `--store` option or `TTOD_PROPOSAL_STORE` support to `_proposal_store()` is a lane A amendment |
| **F2** | P1 | yes (amend) | **The documented no-`make` boot paths now fail, and the error message assumes `make` is available.** The behaviour is intended (F28 names "raw compose"), but four guides still say `cp .env.example .env && docker compose up --build -d`: `docs/public/guides/local-setup.md:49-50` ("Without `make`", aimed at Windows), `docs/public/es/guides/local-setup.md:51-52`, `docs/research/STUDENT-DEVELOPER-GUIDE.md:28-30` and `docs/research/MAINTAINER-GUIDE.md:19-21`. `.env.example:29,32` ships both secrets empty, so in those paths the backend raises at import (`main.py:314` `app = create_app()`, then `config.py:23`). With `restart: unless-stopped` it then crash-loops, and `frontend` (`depends_on: service_healthy`) never starts. The report mentions this in one line (`PHASE-AA5-REPORT.md:62-63`), and its remedy is `make env-secrets`, which is exactly what this audience does not have | Add `python3 scripts/ensure_env_secrets.py` (PowerShell: `python scripts\ensure_env_secrets.py`) after `cp .env.example .env` in all four guides. Change the message to `run \`make env-secrets\` (or \`python3 scripts/ensure_env_secrets.py\`)`. A one-line test can assert that the message names the script |
| **F3** | P1 | yes (amend) | **The verification command in rollout step 3 is wrong.** `PHASE-AA5-REPORT.md:52` has `docker compose -p ttod_oracle exec backend ls "$TTOD_PROPOSAL_DIR"`. The host shell expands the variable, and it is unset on the host. The same expansion run against the live container gives `ls: cannot access '': No such file or directory`, so an instructor would read it as "the mount failed" | Use `docker compose -p ttod_oracle exec backend sh -c 'ls -la "$TTOD_PROPOSAL_DIR"'`. Also add a step 5: `curl -fsS http://localhost:8080/health` should report `"redis":"ok"`. Say that the commands run from `~/src/ttod` after the merge, and that `make rebuild` also recreates Redis (a short shore outage, with AOF data kept) |
| **F4** | P2 | no | **The API docs still promise 200.** `docs/public/guides/api.md:41` and `docs/public/es/guides/api.md:42` say "`200` with `{ status, ttod_version }`". Now it can be `503` `{status:"degraded", redis:"down", …}`. No code caller breaks: the frontend, Caddy (no `health_uri`) and CI never call `/health`, `tests/test_r7_platform.py:41` runs without Redis, and the guides' `curl -fsS` failing on 503 is the right outcome | Document the 503 and `redis` fields in both API tables |
| **F5** | P2 | no | **The "never leaks" test cannot fail for the reason in its name.** `redis_ping` swallows `RedisError` and returns `False` (`redis_client.py:19-23`), so no code path ever sends the exception text. Against the old code, `test_health_redis_down_never_leaks_the_exception` fails only on its `503` assert. The leak that does exist on `/health` is the repository branch, `detail=f"TTOD repository unavailable: {exc}"` (`main.py:132`). That is F47 / lane B | Keep the test as a guard and do not cite it as leak evidence. Lane B (F47) should add a test for the `main.py:132` path |
| **F6** | P2 | no | **The gate does not cover F28 or the override path live.** Its last line says "secrets fail closed", but F28 is proven only by unit tests. Step 3 renders config only for the default env. The `--env-file` amendment is **fair, not a weakening**: an isolated project with no `.env` must now refuse to boot, the throwaway secrets never touch the instructor's `.env`, the change is disclosed, and every F25/F27 check is unchanged | Optionally add a negative live probe: start the backend with an env file that has empty secrets, and expect the container to exit with `TTOD_SESSION_SECRET is empty` in its logs. Optionally rerun step 3 with `TTOD_PROPOSAL_DIR=/srv/x` |
| **F7** | P2 | no | **Small rough edges.** (a) `TTOD_PROPOSAL_HOST_DIR` is documented in the README but missing from `.env.example`. (b) A relative `TTOD_PROPOSAL_DIR` used to resolve against `/workspace` and is now an invalid mount target (confirmed with `docker compose config`, which accepts it, while `up` will reject it). (c) Because `main.py:314` builds the app at import, a shell that exports `REDIS_URL` without secrets makes every backend test fail at import. (d) On a Linux host (Lilith), drafts are owned by root until lane B (already noted in the report) | (a) Add a commented `TTOD_PROPOSAL_HOST_DIR=` to `.env.example`. (b) Note in `.env.example` that the value must be absolute. (c) and (d): no action now; lane B's F16 note stands |

## Startup ordering and Redis blips (checklist item 2)

Docker does not restart a container for being unhealthy, and `restart: unless-stopped` acts only
when the process exits. So a Redis blip cannot cause a restart loop. The backend is marked unhealthy
only after 6 failed checks 10 s apart, which is about 60 s, so short blips never show up. Caddy runs
no active health checks, so pages keep being served and only `/health` reports 503. The one new
coupling is `frontend` `depends_on: backend: service_healthy`: if someone runs `make up`/`rebuild`
while Redis is down, the frontend will not start. That is acceptable and correct. The 503 body is
the old payload plus `status`/`redis`, with no host or exception text in it (`main.py:134-139`).

## Downstream

No downstream phase file is invalidated. Lane B should pick up two items: F5 (the repository-branch
leak at `main.py:132`, under F47), and the `data/proposals` UID/chown step when it adds a non-root
`USER` (F16, already noted in the report).

---

<!--
AA5 lane B cold review. Reviewer: cascade-cold-reviewer (agent), no implementation context.
Scope: lane B (F2, F6, F16–F19, F29–F31, F45–F48 · I1–I6, I10–I16) plus the lane A and AA2 carries. Not marked DONE.
-->

# PHASE-AA5 cold review: lane B (container and deploy ops)

**Commits reviewed:** `4f529de6` (gate before code), `4681e11c` (implementation) and `123ed4eb` (verify log),
compared against `fd2f8278`.
**Verdict: PASS-WITH-AMENDMENTS.** No P0. One P1 blocks DONE:

- **F1:** on any Linux host running Docker Engine, the non-root backend (uid 10001) cannot write drafts into
  `data/proposals`, and every web proposal answers **500**. Only the instructor's Lilith checklist mentions the
  `chown`. The student guides say nothing, `/health` stays green, and the gate cannot catch it because Docker
  Desktop maps ownership.

The rest of the code is sound. I tested each of these directly:
- the request-id path (a client cannot choose the logged id, and log injection is closed);
- the sanitized 503;
- Caddy's trust default;
- the Redis cap;
- the pinned digest;
- the health checks;
- the CI job, in a clean Python 3.12 venv.

Every new test fails against the old code. The P2s are about the Lilith checklist: the TLS-proxy topology on
Docker Desktop, and Linux file ownership breaking `git pull` and backups. The npm deferral needs a narrower
justification and the owner's explicit sign-off.

## What I ran (2026-11-11, on Tanit; `ttod_oracle` untouched, uptimes continuous before and after)

| Check | Command | Result |
| ----- | ------- | ------ |
| Backend suite | `~/src/ttod/.venv/bin/python -m unittest discover -s services/backend/tests -t . -p 'test_*.py'` | `Ran 134 tests … OK` |
| `make test` | `make test PYTHON=~/src/ttod/.venv/bin/python` | `Ran 236 tests … OK`, then `Ran 134 tests … OK`. Both suites run. The `FAIL: 2 public-privacy finding(s)` and `OSError: disk full` lines come from negative fixtures that already existed |
| CI job on a clean runner (simulated) | `git archive HEAD` → fresh `python3.12 -m venv`, the job's two `pip install` lines, then `env -i PATH=/usr/bin:/bin` and the job's `unittest` line | `Ran 134 tests in 70.4s OK`. No Redis, no Ollama and no extra packages needed |
| New tests against the pre-change code | `git archive fd2f8278`, add `test_aa5_lane_b.py`, run it | `FAILED (failures=4, errors=2)`: all 6 fail. Each test proves its fix |
| Exit gate, my own run | `bash PHASES/AA5-container-and-deploy-ops.exit-gate.sh` | `EXIT=0` in 111 s, the same final line as the runner log. `ttod_aa5gate` was removed afterwards |
| Gate amendments | `git diff 4f529de6 HEAD -- …exit-gate.sh` | Three changes: a stdin collision (JSON piped into `python3 -` while the heredoc also used stdin, a real bug); the JSON login returns its token in the body (true, `/api/v1/auth/login` → `session_token`); a stronger request-id check (Caddy's UUID required, a spoofed id must not come back). **None of them weakens the gate** |
| Isolated stack `ttod_aa5review` :28780 (up, used, **down**; 0 containers and 0 volumes left) | `isolated-stack.sh up … TTOD_ALLOWED_HOSTS=aa5-review.lan COOKIE_SECURE=auto` + `mcp-server --no-deps` | all five services up, four `healthy` (Caddy has no health check) |
| Users | `dc exec <svc> id`; `dc exec redis ps -o user,comm` | backend `10001(ttod)`, mcp `10001(ttod)`, frontend `1000(node)`; `redis-server` runs as `redis`; Caddy runs as root (image default) |
| Writable paths | `dc exec backend sh -c 'echo $HOME; ls -ld …'` | `HOME=/home/ttod` (exists, 0700, owned by ttod); `/tmp` writable; the image's drafts dir is owned by ttod. The mcp writes nothing (`server.py` has no file writes). The backend writes only `TTOD_PROPOSAL_DIR` and `tempfile` under `/tmp` (`storage.py:73`). `FileLock` (`repository.py:99`) is used only by `ttod.yml` transactions, which the backend never runs |
| **Linux ownership, simulated** | named volume owned `1000:1000` 0755 (a clone owned by the host user) mounted at the drafts dir of the built backend image, then `write_text` | `PermissionError: [Errno 13] Permission denied: '/workspace/services/backend/data/proposals/draft.json'` (F1) |
| Git after the documented `chown` (Linux container) | repo with a tracked `data/proposals/README.md`, `chown -R 10001:10001 data/proposals`, then `git checkout` as uid 1000 | `error: unable to unlink old 'data/proposals/README.md': Permission denied`, and the worktree is left dirty (F3) |
| Redis file modes | `dc exec redis ls -ln /data /data/appendonlydir`; image `docker-entrypoint.sh` | the dir is `drwx------`, the files `-rw-------`. The entrypoint runs `find . \! -user redis -exec chown redis` and sets umask `0077` (F3) |
| Client source address on Docker Desktop | hold connections from `127.0.0.1:28780` and from the LAN address `10.0.0.11:28780`, then `netstat -tn` in Caddy | **both** arrive from `192.168.65.1`, which is outside the compose subnet `172.20.0.0/16` (F2) |
| https spoof, untrusted (default) | form login from the host with `X-Forwarded-Proto: https`, `Origin: https://aa5-review.lan` | `403`. Plain-HTTP login: `303`, cookie with no `Secure` |
| https spoof, trusted = compose subnet | same request from the LAN address | `403`: the host forwarder is not in the subnet |
| https spoof, trusted = `192.168.65.1/32` | same request from the LAN address | **`303`, `Secure`**. On Docker Desktop, trusting the address a host-port proxy arrives from trusts every LAN client (F2) |
| `trusted_proxies` env forms | `caddy adapt` / `caddy validate` on `caddy:2.10-alpine` (v2.10.2) | empty → `127.0.0.1/32`; `"10.0.0.0/8 172.20.0.0/16"` → **two ranges**; `"10.0.0.0/8,172.20.0.0/16"` → `Error: … parsing CIDR expression` (Caddy will not start); `private_ranges` → **accepted**, `192.168.0.0/16, 172.16.0.0/12, 10.0.0.0/8 …` |
| Request id through Caddy | `curl -D -` with and without `X-Request-ID: client-chosen-id-12345` | a Caddy UUID each time; the client id never comes back. The backend's JSON line carries the same UUID |
| Log content | `curl '/api/v1/wisdom/sample?q=secret-search-term&email=a@b.c'`, then the backend logs | the line has the path only (no query, no IP, no headers). uvicorn's text access lines are gone. There are no path parameters other than `favorites/{quote_id}` |
| Request-id regex | `_WELL_FORMED.match('abcdefgh\n')` | `True` (F7) |
| SSE through the middleware | a minimal app with `install_access_log` and a 3-chunk stream 0.5 s apart, under uvicorn | chunks at 0.05 / 0.56 / 1.06 s, so streaming is preserved; the logged `ms` is `1.2` (F7) |
| Redis cap | `config get maxmemory` / `maxmemory-policy` | `268435456`, `noeviction` |
| At the cap | `config set maxmemory 1mb`, then a redis-py `SET` from the backend, a login and `/health` | `OutOfMemoryError` (a `RedisError`), reads still work, login **503** `Session store unavailable`, `/health` **200 `"redis":"ok"`** (F6). Cap restored afterwards |
| Pool vs threads | `_build_shore` (`main.py:64-66`) | one shared client for all stores and the throttle, so one pool of 50. AnyIO's default thread limiter is 40, plus the event loop. 50 is enough |
| Pinned digest | `docker buildx imagetools inspect ollama/ollama@sha256:3293…` | `application/vnd.oci.image.index.v1+json`, with `linux/amd64` and `linux/arm64`. `ttod_oracle-ollama-1` runs image `sha256:32931b46…`, the same digest. `ollama --version` → `0.33.3` |
| Ollama override | `docker compose -f docker-compose.yml -f docker-compose.ollama-port.yml config` | `host_ip 127.0.0.1, published 11435`; with no override, `ports: None` |
| Health checks | `docker inspect … .State.Health.Log`; backend log tally | frontend exit 0 ×5; mcp healthy. Over the run the backend log holds `GET /health` 56 times, all from the backend's own 10 s check, and **no request from the frontend's check** |
| Lilith §6 probes on the stack | each command | `wis-034` found, `X-Frame-Options: DENY`, `301` on `/es/graph/path`, oracle `401`, maxmemory as stated. **`curl -sI /health` → `405 Method Not Allowed`**, yet the grep for `x-request-id` still passes (F5) |
| npm audit | `npm audit --omit=dev --json` in `services/frontend` | `{low 6, moderate 3, high 8, critical 1, total 18}`. Every package in the report's table matches |
| Non-breaking npm fixes (lockfile copy in the scratchpad) | `npm audit fix --package-lock-only` on a **copy**, then re-audit | 18 → **13** (high 8 → 4, moderate 3 → 2). The worktree is untouched (F4) |
| Required checks | `gh api repos/{owner}/{repo}/branches/main/protection/required_status_checks` | `["typecheck-and-build"]` only (F8) |
| Scope | `git diff --stat fd2f8278 HEAD -- ttod.yml proposals services/frontend/src` | empty |

## Acceptance (lane B, plus the boxes lane A left open)

- [x] **1. `--force-recreate` keeps proposal files on the host bind.** My gate run passed it, and the gate now uses
  temp dirs.
- [x] **2. With Redis stopped, the backend is not "healthy".** The gate run returned `503`.
- [x] **3. Backend unit tests run in CI and `make test`.** `make test` runs both suites, and the CI job passed in my
  clean venv. It is not a required check yet (F8).
- [x] **4. F2 cannot be misread as "8443 is TLS".** The Caddyfile (`:2-4`), compose (`:7`), `.env.example` (`:5`)
  and the checklist (`:15,22`) all say plain HTTP. The 8443 mentions left outside `DEV_PLAN` also say "no es TLS".
- [ ] **5. Cold review green or amended:** this document. It goes green once F1 is amended, or once the owner scopes
  Linux hosts out of student use in writing.

**Deliverables and carries.**

Done:
- `maxmemory` set; Ollama no longer published; non-root `USER`; frontend and mcp health checks; Redis pool knobs;
  sanitized 503; JSON logs; orphan note; recreate smoke; npm audit excerpt; TLS note.
- **Lane A carry, F47:** done, and the test fails on the old body (verified).
- **Lane A carry, one-service rollouts:** lane B touches every image, the Caddyfile and `redis.conf`, so the
  report's full `make rebuild` is justified here.
- **AA2 carries:** gate moved to `isolated-stack.sh`; `trusted_proxies`; https login re-tested (`403`/`303 secure`);
  `TTOD_ALLOWED_HOSTS` and `COOKIE_SECURE` named in the checklist.

Partial:
- **Non-root owns the drafts bind:** documented for Lilith only (F1).
- **Non-root owns the Redis dir:** the checklist's "no chown is needed" holds for Redis itself, but it hides the
  backup and git consequences (F3).

Deviation:
- F17's suggested fix was to gate the Oracle on a healthy mcp. Lane B deliberately keeps `service_started`, so the
  site never waits on retrieval. I accept that: the report discloses it, and the site must not depend on the Oracle.

## Findings

| ID | Sev | Blocks DONE | Finding and evidence | Fix |
| -- | --- | ----------- | -------------------- | --- |
| **F1** | P1 | yes (amend, or owner scopes it out) | **On Linux, the non-root backend cannot write drafts unless someone runs a manual `chown` that only the Lilith checklist mentions.** `data/proposals/` is tracked (`git ls-files data/` → `data/proposals/README.md`), so every clone creates it owned by the user who cloned, mode 0755. The backend runs as 10001 (`services/backend/Dockerfile:18-23`). Simulated with Linux semantics: `PermissionError … draft.json`. The API maps `OSError` to **500 `Unable to save proposal`** (`main.py:417-419`; `tests/test_api.py:88-96`). The container still starts, because `ProposalStore.__init__` only calls `mkdir(exist_ok=True)`, and `/health` stays 200. Three things make it worse: (a) neither `docs/public/guides/local-setup.md` nor the ES guide has a Linux note (`git grep -i chown docs/public` → nothing), and every student runs their own stack; (b) the gate's "non-root backend writes a draft" check runs on Docker Desktop, which maps ownership, so it **cannot fail** for this cause; (c) the escape hatch in checklist `:63`, "build with `--build-arg TTOD_UID`", is undone by the next `make rebuild` (`up --build`), because compose does not pass `TTOD_UID` and the default 10001 comes back. This answers the report's "uid 10001, not 1000" challenge: that choice is what produces F1 and the proposals half of F3 | Wire the uid through Compose and default it to the host user on Linux. Add `build.args: { TTOD_UID: ${TTOD_UID:-10001} }` to **backend and mcp-server**, and `# TTOD_UID=1000  # Linux: $(id -u), so the drafts folder needs no chown` to `.env.example`. Better still, have `scripts/ensure_env_secrets.py` (or `make up`) write `TTOD_UID=$(id -u)` on Linux hosts. Add a Linux note to both local-setup guides. In `lifespan`, check that `TTOD_PROPOSAL_DIR` is writable and log an ERROR that names the fix; optionally add `"proposals":"read-only"` to `/health`. Gate: assert that `docker compose config` shows `TTOD_UID` among the backend build args. With the uid matched, the Lilith `chown` (checklist `:59`, report `:177`) is no longer needed |
| **F2** | P2 | no | **The checklist's TLS-proxy guidance allows an unsafe topology and does not say what Traefik itself must do.** The default (`127.0.0.1/32`) is safe; I verified it. But checklist `:67` allows Traefik to forward "to `reverse-proxy:8080` … **or to `HTTP_PORT`**". On Docker Desktop, every client of a published port, loopback and LAN alike, reaches Caddy from **`192.168.65.1`** (netstat). So the only value that makes a host-port Traefik work also trusts every LAN client. With `TTOD_TRUSTED_PROXIES=192.168.65.1/32`, a plain-HTTP request from `10.0.0.11` carrying `X-Forwarded-Proto: https` got **`303` with a `Secure` cookie**. Second gap: the backend (`main.py:132-133`) and the frontend (`auth.server.ts:60`) both take the **left-most** `X-Forwarded-For` hop. Through a trusted Traefik that hop is whatever Traefik forwards, so Traefik must strip client-sent `X-Forwarded-*` (no `forwardedHeaders.insecure`, and no `trustedIPs` covering the LAN), or students can choose their throttle key again. Third, syntax: the Caddyfile (`:9`) says "one entry". In fact space-separated values work (`10.0.0.0/8 172.20.0.0/16` → two ranges). A comma-separated value stops Caddy from starting (`parsing CIDR expression`). `private_ranges` is accepted and trusts all of 10/8, 172.16/12 and 192.168/16 | Rewrite checklist §4.1: Traefik joins the stack's Docker network (or a shared external network); `TTOD_TRUSTED_PROXIES` is Traefik's container address (`/32`) or that network's CIDR; **never a published-port path**, and on Docker Desktop never `192.168.65.x`. Add a §4 step: Traefik's entrypoint must not trust forwarded headers from clients. Make the probe concrete: an https login through Traefik gives `303` + `Secure`, and the same request sent straight to `HTTP_PORT` with `X-Forwarded-Proto: https` gives `403`. In the Caddyfile, `.env.example` and the checklist, write "one or more CIDRs, **space-separated**; never `private_ranges`" |
| **F3** | P2 | no | **On Linux, ownership changes inside the two bind folders break `git pull` and plain-user backups, and the checklist does not say so.** (a) Checklist `:59` `sudo chown -R 10001:10001 data/proposals` also changes the owner of the tracked `README.md` and of the folder. The next pull that touches the README (lane B itself edited it) fails with `unable to unlink old 'data/proposals/README.md': Permission denied` (reproduced), and the worktree is left dirty. (b) Checklist `:60` says that for `data/redis` "no chown is needed". That is true for Redis, but the image entrypoint chowns the whole bind, `README.md` included, to uid 999, and sets umask `0077` (`drwx------`, `-rw-------`, observed). So the same git failure applies to `data/redis/README.md`, and the §8 backup (`:122-125`) cannot read the AOF without `sudo` | Move both READMEs out of the bind folders (for example `data/README.md`) and create the folders with `mkdir -p` in `make up`/`rebuild` (or keep an empty `.gitkeep` that never changes). In §8, give a working command: `sudo tar -C data -czf ttod-shore-$(date +%F).tgz redis proposals`. In §3, explain the 999/0700 ownership. F1's uid fix removes the proposals half |
| **F4** | P2 | no | **The numbers are right, but the deferral reaches further than its authority, and the checklist's guard is drawn at the wrong boundary.** I re-measured exactly 18 (1/8/3/6), and every package and fix kind in the report table (`:139-148`) matches. Deferring the **majors** is what I6 says ("defer majors intentionally"). The report then cites I6 for "**both** kinds" (`:150`). The non-breaking half is a lockfile-only `npm audit fix` that takes 18 → 13 and removes half the highs (`devalue`, `source-map-js`, `undici`, `vite`) on my lockfile copy; I6 does not cover deferring that. The guard ("before any public exposure", report `:153`; checklist `:116-117`) misses that every student stack publishes `HTTP_PORT` on **all interfaces** (`docker-compose.yml:6`) of a shared classroom LAN. Reachability is not analysed either. The critical advisory is "RCE through AVIF image optimization": `/_image` is live, but remote sources are refused (`/_image?href=https://…` → 403), so it looks unreachable without a crafted local asset. The node-adapter "malformed Host port crash" (high) did not trigger with three malformed `Host` values I sent through Caddy; that is inconclusive | Either land the non-breaking lockfile fix in AA5 (it is lockfile-only; run `npm test`, the build and the AA3/AA3b browser checks), or record the owner's explicit acceptance of deferring it. Add two reachability lines to the report. Widen the guard to "before public exposure, **and before students run stacks on a shared LAN**", or bind student stacks to loopback by default (`127.0.0.1:${HTTP_PORT}`) |
| **F5** | P3 | no | **Two documented commands mislead.** (a) Report rollout `:181` and checklist `:99` use `curl -sI …/health \| grep -i x-request-id`. `-I` sends HEAD, `/health` answers **405** (`Allow: GET`), and the grep passes anyway because the middleware stamps the 405 too. (b) Report `:180`: "use the override for `make review-pr`". `review-local.sh` defaults to the **native** Ollama on `:11434`; the override is only needed for the compose path | (a) `curl -s -D - -o /dev/null http://127.0.0.1:18080/health \| grep -i x-request-id` (the same fix at `:8080` in the checklist). (b) "…only if you point `make review-pr` at the compose Ollama" |
| **F6** | P3 | no | **Ops visibility.** (a) At the memory cap, `/health` says `200 "redis":"ok"` while every login answers 503, because PING still works. (b) The backend's own 10 s check produces 8,640 `/health` lines a day, 56 of the 67 lines in my run, which buries real traffic. (c) Not lane B's doing, but worth knowing: `/health` costs about 350 ms each time (`ms` 346–387), against 7 ms for `/wisdom/sample` | (a) Add `docker compose exec redis redis-cli info memory \| grep -E 'used_memory_human\|maxmemory_human'` to checklist §6. Optionally make `/health` report degraded once `used_memory` passes 90% of `maxmemory`. (b) Skip logging `GET /health` 200s from the in-container check, or document `grep -v '"/health"'`. (c) A note for AA6 |
| **F7** | P3 | no | **Access-log details.** (a) For the Oracle's SSE stream, `ms` is the time to response headers, not to the end of the stream: a 1.5 s stream was logged as `1.2` ms. (b) `_WELL_FORMED.match` with `$` (`access_log.py:27,40`) accepts a trailing `\n`. HTTP parsers do not deliver a raw LF inside a header value, and `json.dumps` escapes it, so this is not exploitable; it is a correctness nit | (a) Document `ms` as "time to first byte" (report `:121`, module docstring), or rename it `ttfb_ms`. (b) Use `_WELL_FORMED.fullmatch(incoming)` |
| **F8** | P3 | no | **The CI job cannot block a merge yet.** Branch protection requires only `typecheck-and-build`. The new `backend-tests` job runs on every PR (`pull_request` has no paths filter), but a red result does not block. The workflow is still named "Frontend — typecheck and build" (`ci.yml:1`). The push paths (`:11-17`) omit `ttod.yml`, `schema/**`, `pyproject.toml` and `cli.py`, which the backend tests read (PRs are unaffected) | Owner action: add `backend-tests` to the required checks. Rename the workflow, for example "CI — frontend and backend". Add the four paths to the push filter |

## Answers to the brief's specific questions

**Security.**
- **Caddy trust.** The default `127.0.0.1/32` trusts nothing that reaches the container, and an empty `.env` value
  falls back to it, both in compose (`:-`) and in Caddy. From an untrusted client, Caddy replaces
  `X-Forwarded-For`/`-Proto`/`-Host`; a spoofed https login gets `403`. Several CIDRs work space-separated; a comma
  breaks startup (F2).
- **X-Request-ID.** On `/api/*` and `/health`, Caddy overwrites the header with its own UUID (`Caddyfile:66-68`), so
  a client cannot choose the logged id (verified). The frontend does not forward the header (it only sets `cookie`
  and `x-forwarded-for`). Log injection is closed twice over: the id regex, and `json.dumps` (F7b is a nit).
- **What the log records.** `ts, event, request_id, method, path, status, ms`. No query, no headers, no IP, no
  cookies; the only path parameter is a quote id.
- **The 503.** `{"detail":"TTOD repository unavailable"}`, with the reason in the log; the test fails on the old
  body. The Oracle never echoes `{exc}`. `oracle.py:159` builds an internal `RuntimeError`, which surfaces as
  Starlette's plain 500 (`propose`) or as a cut stream.
- **Ollama.** It has no host port by default; the override publishes on `127.0.0.1` only.
- **Non-root.** Nothing the backend or mcp writes at runtime fails on Docker Desktop: HOME exists, `/tmp` is
  writable, and no caches are written. On Linux it fails on the drafts bind (F1).

**Operations.**
- **Health checks.** They are correct and cheap: one `node -e fetch` every 15 s on a static file (no backend call),
  and a TCP connect every 15 s.
- **Digest.** A multi-arch OCI index, identical to the image Tanit runs, so `make rebuild` pulls nothing. The
  container is recreated and keeps the named volume `ttod_ollama_data`.
- **`maxmemory`.** With `noeviction`, writes are refused cleanly with `OutOfMemoryError`, which the shore maps to
  503. Reads keep working. Sessions carry TTLs, so memory recovers. AOF buffers are not counted against the cap.
- **Pool.** 50 against at most 41 concurrent users of one shared client, so there is room. Exhaustion would raise
  `ConnectionError`, which also maps to 503.
- **Tanit.** No action is needed (`.env` has `OLLAMA_BASE_URL=http://ollama:11434`, and nothing uses `:11435`).
- **Lilith.** See F1–F3.
- **CI.** It passes on a clean runner (simulated), and `make test` passes.

**npm.** Covered in F4.

**Scope.** Nothing in `ttod.yml`, `proposals/` or `services/frontend/src`. The frontend change is the Dockerfile
`USER` only.

## Downstream

No later phase file is invalidated. If F1 is fixed with a host-matched `TTOD_UID`, amend the Lilith checklist §3 and
the report's rollout step 1 in the same commit, because the `chown` disappears. F6(c), the 350 ms `/health`, is
input for AA6 if it touches health or quota.
