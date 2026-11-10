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
