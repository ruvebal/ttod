# Lilith deployment-validation checklist

**Audience:** the TTOD maintainer (instructor only).
**Scope:** private instructor-only Linux validation of current `main`. This is not a student distribution,
and not a public cloud.
**Rewritten 2026-11-11 (Phase AA5 lane B, F18).** It replaces the 2026-09-05 version, which predates the
Redis shore, fail-closed secrets, AA1 headers, AA2 auth hardening and AA5 ops.

## 1. What runs

Compose project `ttod_oracle` has six services:

| Service | Image | Host port | Runs as |
| ------- | ----- | --------- | ------- |
| `reverse-proxy` | `caddy:2.10-alpine` | `HTTP_PORT` (8080) and `ALT_HTTP_PORT` (8443), **both plain HTTP** | root (Caddy image default) |
| `frontend` | built from `services/frontend` | none | `node` (uid 1000) |
| `backend` | built from `services/backend` | none | `ttod` (uid 10001) |
| `mcp-server` | built from `services/mcp` | none | `ttod` (uid 10001) |
| `redis` | `redis:7-alpine` | **none** | `redis` |
| `ollama` | `ollama/ollama@sha256:3293…` (0.33.3, pinned) | **none by default** | root (Ollama image default) |

**TLS:** `:8443` is NOT TLS. HTTPS, when you want it, ends at a proxy in front of Caddy (Traefik on
Lilith); see §4.

## 2. Configuration (`.env`)

```bash
cp .env.example .env
python3 scripts/ensure_env_secrets.py     # fills TTOD_SESSION_SECRET / TTOD_PAT_SECRET; idempotent
```

Without those secrets the backend **refuses to boot** while `REDIS_URL` is set (F28). `make rebuild` runs
`ensure_env_secrets.py` for you. Then set:

```dotenv
COMPOSE_PROJECT_NAME=ttod_oracle
HTTP_PORT=8080
ALT_HTTP_PORT=8443
OLLAMA_MODE=container
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2:1b
OLLAMA_EMBED_MODEL=nomic-embed-text
# Hostnames the class uses (build-time: rebuild the frontend after changing). Without an entry,
# Astro refuses form POSTs (login, register) from that Host with 403 (F23).
TTOD_ALLOWED_HOSTS=lilith.example.lan
# Cookie Secure flag: auto = Secure only when the request reached the edge over HTTPS (F22).
COOKIE_SECURE=auto
# The TLS proxy in front, if any (one address or CIDR). Never the classroom LAN (§4).
# TTOD_TRUSTED_PROXIES=172.30.0.0/24
```

## 3. Host folders and permissions (non-root containers, F16)

The backend runs as uid **10001** and writes proposal drafts to the host bind `data/proposals`. On Linux the
folder must belong to that uid; Docker Desktop on macOS maps ownership itself.

```bash
mkdir -p data/proposals data/redis
sudo chown -R 10001:10001 data/proposals        # backend drafts (F25 bind)
# data/redis: the Redis image's entrypoint takes ownership of /data itself, so no chown is needed.
```

A different uid is possible: build with `--build-arg TTOD_UID=<uid>` and chown to it.

## 4. TLS in front of Caddy (Traefik on Lilith)

1. Traefik terminates TLS and forwards to `reverse-proxy:8080` (same Docker network) or to `HTTP_PORT`.
2. Set `TTOD_TRUSTED_PROXIES` to Traefik's address or network CIDR, and **only** that. Caddy then keeps
   Traefik's `X-Forwarded-Proto: https` and `X-Forwarded-For`. From anyone else it replaces them, so a
   student cannot fake https or dodge the per-IP throttles (AA2, F3).
3. Add the public hostname to `TTOD_ALLOWED_HOSTS` and rebuild the frontend.
4. Check: an `https://` login answers 303 and sets the session cookie with `Secure`. Over plain HTTP the
   cookie has no `Secure`.
5. Never trust the classroom LAN range. Doing so lets any student spoof `X-Forwarded-For`.

## 5. Bring-up

```bash
make rebuild                 # ensure secrets, build, recreate
make ollama-pull             # first run on an empty Ollama volume: chat + embed models
docker compose ps            # backend, frontend, mcp-server, redis report "healthy"
```

**Ollama from the host** (e.g. `make review-pr`), loopback only, never on the LAN (F30):

```bash
docker compose -f docker-compose.yml -f docker-compose.ollama-port.yml up -d ollama   # 127.0.0.1:11435
```

## 6. Acceptance probes

```bash
curl -fsS http://localhost:8080/health                       # {"status":"ok",...,"redis":"ok"}
curl -fsSL http://localhost:8080/es/ | grep -F 'wis-034'     # governed flagship quote
curl -fsSI http://localhost:8080/es/ | grep -i 'x-frame-options: DENY'         # AA1 headers
curl -sI http://localhost:8080/es/graph/path | head -1                        # 301 (AA3b locators)
curl -s -o /dev/null -w '%{http_code}\n' -X POST -H 'content-type: application/json' \
  -d '{"query":"x"}' http://localhost:8080/api/v1/oracle/stream               # 401 (AA2: session required)
curl -sI http://localhost:8080/health | grep -i x-request-id                  # AA5: request id
docker compose logs --no-color --tail=20 backend                             # one JSON line per request
docker compose exec redis redis-cli config get maxmemory                    # 268435456 (256 MB, F29)
```

- **Redis down** (`docker compose stop redis`): `/health` answers **503** `{"status":"degraded","redis":"down"}`
  (F27). Start Redis again afterwards.
- **Recreate:** `docker compose up -d --force-recreate backend` keeps the files in `data/proposals` (F25).

## 7. Security boundary

- Firewall the host ports to the studio network. This is not approved for public exposure.
- **Redis** has no host port; `protected-mode no` is safe only because of that. Never publish 6379.
- **Ollama** has no host port by default. The loopback override (§5) is the only supported exposure.
- **`npm audit --omit=dev` (2026-11-11):** 18 production advisories (1 critical, 8 high, 3 moderate, 6 low).
  The critical one and most of the highs come from Astro 5 and need the Astro 7 major upgrade. Five
  (`devalue`, `source-map-js`, `undici`, `vite`, `smol-toml`) have non-breaking fixes. Both are deliberately
  deferred to a separate, tested dependency PR (PHASE-AA5-REPORT §lane B). Do not expose the site
  publicly before that PR lands.
- `caddy:2.10-alpine` and `redis:7-alpine` still float within their minor or major line. Pin by digest before
  making reproducibility claims (only Ollama is pinned today, F6).
- The frontend image excludes `.env*`; inspecting the built image must find no `.env` file.

## 8. Backups

`data/redis/` (AOF: users, sessions, favorites, draft index) and `data/proposals/` (draft files) are the
shore. `ttod.yml` and `proposals/` are the governed corpus, in git.

## 9. Close condition

Lilith validation is DONE only after §5–§6 run on Lilith itself, with outputs filed, including the §4 https
check if Traefik is in front. Tanit evidence is a release-candidate check, not Linux-host proof.
