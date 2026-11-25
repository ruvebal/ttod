<!--
Post-merge Redis completeness recovery after Equipo PRs #88–#92.
Author: Rubén Vega Balbás PhD · 2026-11-09
-->

# Redis shore completeness — 2026-11-09

**Recover from:** Phase Z pack (`INDEX.md`, cold review F2–F8) after student merges `#91 → #88 → #90 → #89 → #92`.

## Verdict

| Question | Answer |
| --- | --- |
| Compose Redis ready for permanence? | **Yes** — `redis:7-alpine`, tracked `redis/redis.conf` (AOF `everysec`, `noeviction`, **`protected-mode no`** on private network), bind `./data/redis:/data`, conf `:ro`, **no host ports**, backend `depends_on: service_healthy`. |
| Best-practice bar from Z1? | **Met** — Z1 exit-gate OK; AOF restart probe keeps key; host `data/redis/appendonlydir/` present. |
| After student contributions? | **Yes for shore domains** — #89 logout/revoke UI; #92 open register + Redis users + favorites require a real user. Graph/oracle PRs do not touch Redis. |
| Register always `student`? | **Yes — intentional.** Server forces `roles=("student",)`; client body cannot choose roles/id (`test_a_client_cannot_choose_its_own_roles_or_id`). Env admin seed remains `reviewer`+`instructor`. |

## Recovered against the plan

| Phase Z claim | Status now | Evidence |
| --- | --- | --- |
| Z1 AOF bind mount | **OK** | `./PHASES/Z1.exit-gate.sh` → OK; `SET/GET` across `docker compose restart redis` 2026-11-09 |
| Z2 favorites + shared client | **OK** | `redis_client.create_redis_client`; `_build_shore` one client |
| Z3 users + opaque sessions | **OK** | Memory/Redis stores; logout deletes sid |
| Z3 Compose session smoke (cold **F2**) | **Closed** | Unit: `#92` `SurvivesRestartTests`. **Live 2026-11-09:** admin login → favorite → `docker compose restart backend` → session+favorites OK; Redis AOF key survives `restart redis`; register always `student`; logout → 401. |
| Z4 proposals dual-write | **OK** (unchanged) | Disk-first; Redis failure → 503 |
| Z5 docs / #87 | **OK** | Shore docs; visual sync repaired 2026-11-09 (icons back into `shared/visual-system`) |
| Z6 hardening 1–4 | **OK** | Factory, 503 matrix tests, isolation, no KEYS/FLUSH |
| Open registration (beyond Z3 scope) | **Landed via #92** | `POST /api/v1/auth/register` + `/{locale}/register`; always student |

## Role contract (do not “fix” always-student)

```text
register()  → roles = ("student",)     # open classroom self-serve
ensure_admin() → ("reviewer", "instructor")  # env seed only
```

Promotion to reviewer/instructor is **not** an open API — out of band upsert / seed. That matches Z3 “never put roles from the client body into the session without server lookup.”

## Remaining follow-ups (not blocking classroom Redis)

| Item | Source | Note |
| --- | --- | --- |
| Stable `TTOD_SESSION_SECRET` / `TTOD_PAT_SECRET` / admin hash in `.env` | ops | **Fixed 2026-11-09:** `make env-secrets` (also run by `make up`) fills empty values idempotently; admin plaintext once in `.env.admin-password` (gitignored). |
| Live Compose login → restart backend → `/auth/session` | cold F2 residual | Run after secrets are set; Redis AOF already proven. |
| PAT revoke sidecar `ttod:pat:{jti}` | Z6 item 5 | Still deferred |
| Signed-session fallback | F7 | Legacy/test helpers; production login path is opaque sid |

## Commands re-run this session

```bash
./docs/DEV_PLAN/PHASE-Z-REDIS-RUNTIME-PERSISTENCE/PHASES/Z1.exit-gate.sh
docker compose up -d redis
docker compose exec -T redis redis-cli SET ttod:complete:probe …
docker compose restart redis   # GET still returns value
.venv/bin/python -m unittest \
  services.backend.tests.test_user_persistence \
  services.backend.tests.test_shore_stores \
  services.backend.tests.test_auth -v   # 29 OK
python3 scripts/sync_visual_system.py --check   # PASS after icon restore into shared/
```
