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
| `backend` | built from `services/backend` | none | **your** uid:gid under `make` (else 10001) |
| `mcp-server` | built from `services/mcp` | none | **your** uid:gid under `make` (else 10001) |
| `redis` | `redis:7-alpine` | **none** | **your** uid:gid under `make` (else the image's `redis`) |
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

Use `make` (`make rebuild`, `make up`). It exports your uid and gid (`TTOD_UID`, `TTOD_GID`,
`TTOD_REDIS_USER`), so the backend writes `data/proposals` and Redis writes `data/redis` **as you**. There is
no `chown`, `git pull` keeps working (the tracked `data/proposals/README.md` stays yours), and backups need no
`sudo`. As root, `make` falls back to uid 10001.

Plain `docker compose` on Linux uses uid 10001 and the Redis image's own user, so set the same three
variables in `.env` first (see `.env.example`). If the drafts folder is not writable, the backend logs it at
startup: `Proposal drafts folder … is not writable by uid …`.

## 4. TLS in front of Caddy (Traefik on Lilith)

1. Traefik terminates TLS and reaches Caddy **over the Docker network** (`reverse-proxy:8080`), so Caddy sees
   Traefik's own container address. Do not route Traefik through the published `HTTP_PORT` on Docker Desktop:
   there, every client (LAN included) arrives from the host gateway `192.168.65.x`, and trusting it would trust
   everyone.
2. Set `TTOD_TRUSTED_PROXIES` to Traefik's address or its network's CIDR, and **only** that. Separate several
   entries with spaces; a comma stops Caddy from starting. Never `private_ranges`, never the classroom LAN.
3. **Traefik must not pass on forwarded headers that clients send.** Keep `forwardedHeaders.insecure` off
   (the default) and do not list the LAN in `forwardedHeaders.trustedIPs`. Otherwise a student's own
   `X-Forwarded-For` would reach the backend, which keys its per-IP throttles on the left-most address (AA2, F3).
4. Add the public hostname to `TTOD_ALLOWED_HOSTS` and rebuild the frontend.
5. Check: an `https://` login answers 303 and sets the session cookie with `Secure`. Over plain HTTP the cookie
   has no `Secure`, and a client-sent `X-Forwarded-Proto: https` changes nothing.

## 5. Bring-up

```bash
make rebuild                 # ensure secrets, build, recreate
make ollama-pull             # first run on an empty Ollama volume: chat + embed models
docker compose ps            # backend, frontend, mcp-server, redis report "healthy"
```

**Ollama from the host**, loopback only, never on the LAN (F30). Only needed when a host tool should use
the *stack's* Ollama: `make review-pr` defaults to a native Ollama on `:11434`.

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
curl -s -D - -o /dev/null http://localhost:8080/health | grep -i x-request-id  # AA5: request id (GET; HEAD is 405)
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
- **`npm audit --omit=dev` (2026-11-11, after AA5's non-breaking fixes):** 13 production advisories
  (1 critical, 4 high, 2 moderate, 6 low), all needing major upgrades (Astro 5 → 7). Most cannot be reached in
  TTOD: it uses no `define:vars`, spread props, `transition:` directives, server islands or `astro:assets`, and
  `zod` and `esbuild` run at build time. The reachable one, `@astrojs/node` crashing on a malformed `Host`
  port, is blocked at Caddy (a strict `Host` matcher answers 400). **Guard:** the Astro major upgrade comes
  before any public exposure. Student stacks publish `HTTP_PORT` on every interface, so on a shared classroom
  LAN the site is reachable by classmates. That is the intended teaching setup, but it is exposure.
- `caddy:2.10-alpine` and `redis:7-alpine` still float within their minor or major line. Pin by digest before
  making reproducibility claims (only Ollama is pinned today, F6).
- The frontend image excludes `.env*`; inspecting the built image must find no `.env` file.

## 8. Backups

`data/redis/` (AOF: users, sessions, favorites, draft index) and `data/proposals/` (draft files) are the
shore. Under `make` both belong to you (§3), so a plain `cp -a` or `tar` backs them up. `ttod.yml` and `proposals/` are the governed corpus, in git.

## 9. Close condition

Lilith validation is DONE only after §5–§6 run on Lilith itself, with outputs filed, including the §4 https
check if Traefik is in front. Tanit evidence is a release-candidate check, not Linux-host proof.
