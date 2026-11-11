#!/usr/bin/env bash
# AA5 exit gate. Lane A (F25 / F27 / F28 · I7–I9) was written before lane A; lane B (F2, F6, F16–F19,
# F29–F31, F45–F48 · I1–I6, I10–I16) was appended by the planner before lane B code (2026-11-11).
# Lane A checks keep running. Amended for lane B: lane A's live part now runs on scripts/isolated-stack.sh
# (AA2 cold review F3), which uses temp Redis/drafts dirs instead of the checkout's ./data.
#
# Backend test-name contract (services/backend/tests, unittest -k):
#   lane A  *health_redis_down*      /health 503 when REDIS_URL is set and the ping fails (F27)
#           *empty_secret*           boot fails closed on an empty TTOD_*_SECRET with REDIS_URL (F28)
#   lane B  *health_body_sanitized*  a failing repository never puts exception text in the 503 body (F47)
#           *redis_pool_knobs*       timeouts, health_check_interval, max_connections reach the pool (F46)
#           *request_id*             X-Request-ID set or echoed (only if well formed) and one JSON access
#                                    log line per request with request_id, method, path, status, ms (F48)
#
# Live, isolated (project ttod_aa5gate): processes run as non-root and can still write proposal drafts
# to the host bind; frontend and mcp report healthy; Ollama publishes no host port; Redis has a
# maxmemory with noeviction; a request id flows Caddy → backend → JSON log; an https form login through
# an untrusted proxy is refused, and through a trusted proxy (TTOD_TRUSTED_PROXIES) succeeds with a
# Secure cookie; recreate keeps drafts and /health is 503 with Redis down (lane A).
# AA5_SKIP_LIVE=1 is for a quick local pre-check only; the runner's verify runs it in full.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
pack="docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING"
py="${PYTHON:-$HOME/src/ttod/.venv/bin/python}"
fail() { echo "AA5 GATE FAIL: $*" >&2; exit 1; }
laneb_start="$(git log --format=%H -1 -S'lane B (F2, F6' -- "$pack/PHASES/AA5-container-and-deploy-ops.exit-gate.sh")"
[ -n "$laneb_start" ] || laneb_start="$(git merge-base HEAD origin/main)"

# 1. Named tests exist and pass; backend suite green.
run_k() {
  out="$("$py" -m unittest discover -s services/backend/tests -t . -p 'test_*.py' -k "$1" -v 2>&1)" \
    || { printf '%s\n' "$out" | grep -q 'NO TESTS RAN' && fail "no test matches '$1' (test-name contract above)"
         printf '%s\n' "$out" | tail -20; fail "tests matching '$1' failed"; }
  n="$(printf '%s\n' "$out" | sed -n 's/^Ran \([0-9]*\) test.*/\1/p')"
  [ "${n:-0}" -ge 1 ] || fail "no test matches '$1' (test-name contract above)"
  echo "tests '$1': $n passed"
}
for k in health_redis_down empty_secret health_body_sanitized redis_pool_knobs request_id; do run_k "$k"; done
grep -rqs "503" $(grep -rls "health_redis_down" services/backend/tests) || fail "health_redis_down tests never assert 503"
"$py" -m unittest discover -s services/backend/tests -t . -p 'test_*.py' >/dev/null 2>&1 || fail "backend suite red"

# 2. F45: CI and `make test` run the backend suite.
make -n test 2>/dev/null | grep -q 'services/backend/tests' || fail "make test does not discover services/backend/tests (F45)"
grep -q 'services/backend/tests' .github/workflows/ci.yml || fail "CI has no backend test job (F45)"

# 3. Static config.
make -n rebuild 2>/dev/null | grep -q 'ensure_env_secrets.py' || fail "make rebuild does not call ensure_env_secrets.py (F28)"
# Amended during lane B: the config goes through a file; piping it would collide with the heredoc on stdin.
cfgf="$(mktemp)"; docker compose -p ttod_aa5cfg -f docker-compose.yml config --format json > "$cfgf" 2>/dev/null
python3 - "$cfgf" <<'PY' || fail "compose config (see message above)"
import json, sys
c = json.load(open(sys.argv[1]))["services"]; bad = []
b = c["backend"]; target = b["environment"]["TTOD_PROPOSAL_DIR"]
if not any(v.get("type") == "bind" and v.get("target") == target for v in b.get("volumes", [])): bad.append("backend: no bind at TTOD_PROPOSAL_DIR (F25)")
if c["redis"].get("ports"): bad.append("redis publishes a host port")
if c["ollama"].get("ports"): bad.append("ollama publishes a host port by default (F30)")
if "@sha256:" not in c["ollama"]["image"]: bad.append(f"ollama image not pinned by digest: {c['ollama']['image']} (F6)")
for svc in ("frontend", "mcp-server"):
    if not c[svc].get("healthcheck"): bad.append(f"{svc} has no healthcheck (F17)")
if bad: print("\n".join(bad)); sys.exit(1)
PY
git check-ignore -q data/proposals/aa5-probe.yml || fail "data/proposals/ contents are not gitignored"
test -f docker-compose.ollama-port.yml && grep -q '127.0.0.1:' docker-compose.ollama-port.yml \
  || fail "no opt-in override publishing Ollama on loopback only (F30)"
grep -Eq '^maxmemory [0-9]+(mb|gb)' redis/redis.conf && grep -q '^maxmemory-policy noeviction' redis/redis.conf \
  || fail "redis.conf lacks maxmemory or noeviction (F29)"
for f in services/backend/Dockerfile services/frontend/Dockerfile services/mcp/Dockerfile; do
  grep -Eq '^USER +[^r0 ][^ ]*' "$f" || fail "$f does not drop to a non-root USER (F16)"; done
grep -q 'trusted_proxies' caddy/Caddyfile && grep -q 'TTOD_TRUSTED_PROXIES' caddy/Caddyfile .env.example \
  || fail "Caddy trusted_proxies not wired to TTOD_TRUSTED_PROXIES (F2 / AA2 carry)"
grep -qi 'not TLS\|no es TLS' caddy/Caddyfile || fail "Caddyfile does not say plainly that :8443 is not TLS (F2)"
lil="docs/DEV_PLAN/LILITH-VALIDATION-CHECKLIST.md"
for k in TTOD_ALLOWED_HOSTS COOKIE_SECURE TTOD_TRUSTED_PROXIES ensure_env_secrets maxmemory chown docker-compose.ollama-port.yml; do
  grep -q "$k" "$lil" || fail "Lilith checklist does not mention $k (F18)"; done
grep -qi 'orphan\|huérfan' data/proposals/README.md || fail "no orphan-file note for the dual-write (F31)"

# 4. Live, isolated.
if [ "${AA5_SKIP_LIVE:-0}" != "1" ]; then
  stack="$pack/scripts/isolated-stack.sh"; project=ttod_aa5gate; port="${AA5_PORT:-28680}"; lan="aa5-gate.lan"
  envf="${TMPDIR:-/tmp}/$project.env"; datadir="${TMPDIR:-/tmp}/$project.data"
  dc() { docker compose -p "$project" --env-file "$envf" -f docker-compose.yml "$@"; }
  trap 'bash "$stack" down "$project"' EXIT
  # Amended after the cold review (F1, strengthening): run as `make` does, with the host's uid/gid, and
  # check below that the containers which write host folders really run as that user. Docker Desktop maps
  # bind ownership, so a write test alone cannot catch the Linux failure; the uid check can.
  host_uid="$(id -u)"; host_gid="$(id -g)"
  export TTOD_UID="$host_uid" TTOD_GID="$host_gid" TTOD_REDIS_USER="$host_uid:$host_gid"
  bash "$stack" up "$project" "$port" "TTOD_ALLOWED_HOSTS=$lan" "COOKIE_SECURE=auto" >/dev/null
  dc up -d --no-deps --build mcp-server >/dev/null 2>&1 || fail "isolated mcp-server did not start"
  base="http://127.0.0.1:$port"
  # F16: nothing of ours runs as root.
  for svc in backend frontend mcp-server; do
    uid="$(dc exec -T "$svc" id -u | tr -d '\r')"; [ "$uid" != 0 ] || fail "$svc runs as root (F16)"; done
  for svc in backend redis; do
    uid="$(dc exec -T "$svc" id -u | tr -d '\r')"; [ "$uid" = "$host_uid" ] || fail "$svc runs as uid $uid, not the host user $host_uid (F16/F1)"; done
  # Amended after the cold review (F4): a malformed Host port (an open @astrojs/node crash) stops at Caddy.
  hc="$(curl -s -o /dev/null -w '%{http_code}' -H 'Host: localhost:8x8x' "$base/es/")"
  [ "$hc" = 400 ] || fail "malformed Host port reached the frontend (HTTP $hc), want 400 at Caddy"
  # F17: frontend and mcp become healthy.
  for svc in frontend mcp-server; do
    st=""; for _ in $(seq 1 45); do st="$(docker inspect -f '{{.State.Health.Status}}' "$(dc ps -q "$svc")" 2>/dev/null)"; [ "$st" = healthy ] && break; sleep 2; done
    [ "$st" = healthy ] || fail "$svc health is '$st' (F17)"; done
  # F29: Redis memory cap with clean rejects.
  mm="$(dc exec -T redis redis-cli config get maxmemory | tail -1 | tr -d '\r')"; pol="$(dc exec -T redis redis-cli config get maxmemory-policy | tail -1 | tr -d '\r')"
  [ "${mm:-0}" -gt 0 ] && [ "$pol" = noeviction ] || fail "redis maxmemory=$mm policy=$pol (F29)"
  # F16 + F25: the non-root backend still writes drafts to the host bind.
  email="aa5-$$@example.test"; pw="aa5-gate-password-1"
  curl -s -o /dev/null -H 'content-type: application/json' -d "{\"email\":\"$email\",\"password\":\"$pw\"}" "$base/api/v1/auth/register"
  # Amended during lane B: the JSON login returns the token in its body (only the form login sets a cookie).
  token="$(curl -s -H 'content-type: application/json' -d "{\"email\":\"$email\",\"password\":\"$pw\"}" "$base/api/v1/auth/login" \
    | python3 -c 'import json, sys; print(json.load(sys.stdin).get("session_token", ""))')"
  [ -n "$token" ] || fail "isolated login returned no session token"
  before="$(ls "$datadir/proposals" | wc -l | tr -d ' ')"
  code="$(curl -s -o /dev/null -w '%{http_code}' -H "cookie: ttod_session=$token" -H 'content-type: application/json' \
    -d '{"text":"Una cita de prueba del gate AA5.","teaches":"Que el borrador llega al disco.","section":"wisdom","level":"beginner","tags":["aa5"]}' "$base/api/v1/proposals")"
  after="$(ls "$datadir/proposals" | wc -l | tr -d ' ')"
  [ "$code" = 201 ] && [ "$after" -gt "$before" ] || fail "non-root backend could not write a draft to the bind (HTTP $code, files $before → $after)"
  # F48: one request id from Caddy to the backend log, echoed to the client.
  rid="$(curl -s -D - -o /dev/null "$base/health" | tr -d '\r' | sed -n 's/^[Xx]-[Rr]equest-[Ii][Dd]: //p')"
  [ -n "$rid" ] || fail "no X-Request-ID on /health through Caddy (F48)"
  # Amended during lane B (strengthening): the id must be Caddy's UUID, not one the backend minted (32 hex,
  # no dashes), and a client-chosen id must not survive the proxy.
  printf '%s' "$rid" | grep -Eq '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' || fail "X-Request-ID $rid is not Caddy's UUID (F48)"
  spoof="$(curl -s -D - -o /dev/null -H 'X-Request-ID: client-chosen-id-12345' "$base/health" | tr -d '\r' | sed -n 's/^[Xx]-[Rr]equest-[Ii][Dd]: //p')"
  [ "$spoof" != "client-chosen-id-12345" ] || fail "a client-chosen X-Request-ID reached the backend (F48)"
  sleep 1; dc logs --no-log-prefix backend 2>/dev/null | grep -F "\"request_id\": \"$rid\"" | grep -q '"path": "/health"' \
    || dc logs --no-log-prefix backend 2>/dev/null | grep -F "\"request_id\":\"$rid\"" | grep -q '"path":"/health"' \
    || fail "backend log has no JSON line for request $rid (F48)"
  # F2: an https login through a proxy Caddy does not trust is refused; through a trusted one it works.
  login_via_proxy() { dc exec -T backend python - "$lan" "$email" "$pw" <<'PY'
import sys, urllib.request, urllib.error, urllib.parse
lan, email, pw = sys.argv[1:]
req = urllib.request.Request("http://reverse-proxy:8080/es/login/", method="POST",
    data=urllib.parse.urlencode({"email": email, "password": pw}).encode(),
    headers={"Host": lan, "Origin": f"https://{lan}", "X-Forwarded-Proto": "https", "X-Forwarded-Host": lan,
             "content-type": "application/x-www-form-urlencoded"})
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
try: r = urllib.request.build_opener(NoRedirect).open(req, timeout=20); code, h = r.status, r.headers
except urllib.error.HTTPError as e: code, h = e.code, e.headers
print(code, "secure" if "secure" in (h.get("Set-Cookie") or "").lower() else "plain")
PY
  }
  untrusted="$(login_via_proxy)"
  case "$untrusted" in "303 secure") fail "an untrusted client's X-Forwarded-Proto was honoured ($untrusted) (F2)";; esac
  subnet="$(docker network inspect "${project}_default" -f '{{(index .IPAM.Config 0).Subnet}}')"
  echo "TTOD_TRUSTED_PROXIES=$subnet" >> "$envf"
  dc up -d --no-deps --force-recreate reverse-proxy >/dev/null 2>&1; sleep 3
  trusted="$(login_via_proxy)"
  [ "$trusted" = "303 secure" ] || fail "https login through a trusted proxy answered '$trusted', want '303 secure' (F2)"
  # Lane A: recreate keeps drafts; /health 503 with Redis down.
  marker="aa5-gate-$$.txt"; echo "recreate probe" > "$datadir/proposals/$marker"
  dc up -d --no-deps --force-recreate backend >/dev/null 2>&1
  for _ in $(seq 1 40); do [ "$(curl -s -o /dev/null -w '%{http_code}' "$base/health")" = 200 ] && break; sleep 2; done
  dir="$(dc exec -T backend printenv TTOD_PROPOSAL_DIR | tr -d '\r')"
  dc exec -T backend test -f "$dir/$marker" || fail "proposal file lost on backend recreate (F25)"
  dc stop redis >/dev/null 2>&1; sleep 3
  code="$(curl -s -o /dev/null -w '%{http_code}' "$base/health")"
  [ "$code" = 503 ] || fail "/health answered $code with Redis down, expected 503 (F27)"
  echo "live (isolated $project): non-root (backend/frontend/mcp), drafts written, frontend+mcp healthy, maxmemory+noeviction, request id end to end, https login untrusted='$untrusted' trusted='$trusted', recreate kept drafts, health 503 on Redis down"
fi

# 5. Evidence and scope.
test -f "$pack/PHASE-AA5-REPORT.md" || fail "missing PHASE-AA5-REPORT.md"
grep -qi 'lane a' "$pack/PHASE-AA5-REPORT.md" && grep -qi 'lane b' "$pack/PHASE-AA5-REPORT.md" || fail "report lacks a lane A or lane B section"
grep -q 'npm audit --omit=dev' "$pack/PHASE-AA5-REPORT.md" || fail "report has no npm audit --omit=dev excerpt (F19)"
git diff --quiet "$laneb_start" -- ttod.yml proposals || fail "AA5 touched the canonical stores"
git diff --check "$laneb_start" -- . ':(exclude)*.md' || fail "whitespace errors"
echo "AA5 exit gate passed: lane A (bind, health 503, secrets) and lane B (non-root, health checks, pins, maxmemory, CI backend suite, request ids, TLS proxy trust, docs)."
