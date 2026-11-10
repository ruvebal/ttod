#!/usr/bin/env bash
# AA1 exit gate: Caddy security headers (F1 / A1), made runnable. Written by the planner before
# the phase starts.
#
# The phase worktree's Caddyfile runs in a throwaway Caddy container joined to the live Compose
# network, so it proxies to the real frontend/backend. It listens on a scratch port and leaves the
# running stack untouched.
#
# Amended after the cold review (R1, R6): non-HTML and Caddy-generated error responses.
#
# Env: AA1_PROBE_PORT (default 28080), LIVE_COMPOSE_NETWORK (default ttod_oracle_default).
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
pack="docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING"
port="${AA1_PROBE_PORT:-28080}"
net="${LIVE_COMPOSE_NETWORK:-ttod_oracle_default}"
image="$(awk '/reverse-proxy:/{f=1} f && /image:/{print $2; exit}' docker-compose.yml)"
fail() { echo "AA1 GATE FAIL: $*" >&2; exit 1; }

[ -n "$image" ] || fail "could not read the reverse-proxy image from docker-compose.yml"
grep -q 'auto_https off' caddy/Caddyfile || fail "auto_https must stay off (no fake HTTPS; F2 is AA5)"

# 1. The Caddyfile is valid for the pinned image.
docker run --rm -v "$PWD/caddy/Caddyfile:/etc/caddy/Caddyfile:ro" "$image" \
  caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null 2>&1 \
  || fail "caddy validate failed for $image"

# 2. Serve it against the live services on a scratch port.
name="aa1-gate-$$"
docker run -d --rm --name "$name" --network "$net" -p "127.0.0.1:$port:8080" \
  -v "$PWD/caddy/Caddyfile:/etc/caddy/Caddyfile:ro" "$image" >/dev/null
trap 'docker rm -f "$name" >/dev/null 2>&1 || true' EXIT
for _ in $(seq 1 30); do curl -s -o /dev/null -m 2 "http://127.0.0.1:$port/health" && break; sleep 1; done

base="http://127.0.0.1:$port"
headers() { curl -sI -m 10 "$base$1" | tr -d '\r' | tr 'A-Z' 'a-z'; }
need() { printf '%s\n' "$1" | grep -Eq "$2" || fail "$3"; }

for page in /es/ /en/ /es/wisdom/; do
  h="$(headers "$page")"
  need "$h" '^http/1.1 200' "$page did not return 200 through the gate proxy"
  need "$h" '^x-frame-options: (deny|sameorigin)$' "$page lacks X-Frame-Options DENY|SAMEORIGIN (CSP report-only cannot deny framing)"
  need "$h" '^referrer-policy: (no-referrer|same-origin|strict-origin|strict-origin-when-cross-origin)$' "$page lacks a safe Referrer-Policy"
  need "$h" '^permissions-policy: .+' "$page lacks Permissions-Policy"
  need "$h" '^x-content-type-options: nosniff$' "$page lacks X-Content-Type-Options: nosniff"
  need "$h" '^content-security-policy-report-only: .+' "$page lacks CSP report-only"
  printf '%s\n' "$h" | grep -q '^content-security-policy:' \
    && fail "$page enforces CSP; AA0 did not authorize enforcement (report-only first)"
  printf '%s\n' "$h" | grep -q '^strict-transport-security:' \
    && fail "$page sends HSTS over plain HTTP (claims HTTPS the edge does not have)"
done

# 2b. Headers on non-HTML responses too, including errors Caddy generates itself (cold review
#     R1/R6, amended during AA1): API, health, an API 404 and a file_server 404.
for path in /health /api/v1/wisdom/sample /api/v1/__aa1-gate-missing /project-docs/__aa1-gate-missing; do
  h="$(headers "$path")"
  need "$h" '^x-frame-options: deny$' "$path lacks X-Frame-Options"
  need "$h" '^x-content-type-options: nosniff$' "$path lacks nosniff"
  need "$h" '^content-security-policy-report-only: .+' "$path lacks CSP report-only"
  printf '%s\n' "$h" | grep -q '^server:' && fail "$path still sends a Server header"
done

# 3. API JSON still usable; no CORS invented.
api="$(curl -s -m 15 -D - "$base/api/v1/wisdom/sample" -o /tmp/aa1-gate-sample.$$ | tr -d '\r' | tr 'A-Z' 'a-z')"
need "$api" '^http/1.1 200' "/api/v1/wisdom/sample not 200 through the proxy"
need "$api" '^content-type: application/json' "/api/v1/wisdom/sample is not JSON"
python3 -c "import json,sys; json.load(open(sys.argv[1]))" /tmp/aa1-gate-sample.$$ || fail "API body is not valid JSON"
rm -f /tmp/aa1-gate-sample.$$
printf '%s\n' "$api" | grep -q '^access-control-allow-origin:' && fail "a CORS header appeared (same-origin classroom; none invented)"
curl -s -m 5 "$base/health" | python3 -c "import json,sys; json.load(sys.stdin)" || fail "/health is not JSON"

# 4. Astro assets, service worker and existing cache rules still work.
asset="$(curl -s -m 10 "$base/es/" | grep -oE '/_astro/[A-Za-z0-9._-]+\.(css|js)' | head -1)"
[ -n "$asset" ] || fail "no /_astro asset referenced from /es/"
need "$(headers "$asset")" '^http/1.1 200' "$asset not 200"
sw="$(headers /sw.js)"
need "$sw" '^http/1.1 200' "/sw.js not 200"
need "$sw" '^cache-control: max-age=0, no-cache' "/sw.js lost its no-cache rule"

# 5. Evidence and scope.
report="$pack/PHASE-AA1-REPORT.md"
test -f "$report" || fail "missing $report"
grep -qi 'before' "$report" && grep -qi 'after' "$report" || fail "report lacks before/after curl evidence"
start="$(git merge-base HEAD origin/main)"
outside="$(git diff --name-only "$start" -- . ':(exclude)caddy/**' ':(exclude)docs/**' || true)"
[ -z "$outside" ] || fail "AA1 changed files outside caddy/ and docs/: $outside"
# Markdown is excluded: two trailing spaces are the pack's deliberate hard line breaks.
git diff --check "$start" -- . ':(exclude)*.md'
echo "AA1 exit gate passed: headers on HTML, CSP report-only, JSON/assets/SW intact, scope caddy+docs."
