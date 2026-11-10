#!/usr/bin/env bash
# AA0 live re-probe of FINDINGS-2026-11-10 against the local Compose stack.
# Read-only except the F27 check, which stops Redis for a few seconds and starts it again
# (instructor host only; never run it against a stack students use).
# Usage: probe.sh [base-url] [--with-redis-down]  > probe.log
set -uo pipefail
BASE="${1:-http://127.0.0.1:18080}"
ALT="${ALT:-http://127.0.0.1:18443}"
REDIS_DOWN="${2:-}"
repo="$(git rev-parse --show-toplevel)"
fe="$repo/services/frontend"
LIVE_COMPOSE="${LIVE_COMPOSE:-$HOME/src/ttod/docker-compose.yml}"

h() { printf '\n## %s\n' "$*"; }
code() { curl -s -o /dev/null -m 10 -w '%{http_code}' "$@"; }

echo "# probe run: $(date -u +%Y-%m-%dT%H:%M:%SZ) on $(hostname) · base $BASE · repo $(git -C "$repo" rev-parse --short HEAD)"

h "health"
curl -s -m 5 "$BASE/health"; echo

h "F1 security headers (curl -sI $BASE/es/)"
curl -sI -m 10 "$BASE/es/" | tr -d '\r'
for hd in content-security-policy x-frame-options referrer-policy permissions-policy x-content-type-options strict-transport-security; do
  if curl -sI -m 10 "$BASE/es/" | grep -qi "^$hd:"; then echo "PRESENT $hd"; else echo "ABSENT  $hd"; fi
done

h "F2 TLS on the alt port ($ALT)"
echo "https handshake: $(curl -sk -o /dev/null -m 5 -w '%{http_code}' "${ALT/http:/https:}/" 2>/dev/null || true) (000 = no TLS)"
echo "plain http on alt port: $(code "$ALT/es/")"

h "F22 cookie Secure source (code)"
grep -n "secure:" "$fe/src/pages/[locale]/login.astro" "$fe/src/pages/[locale]/register.astro"

h "F23 allowedDomains (code) + POST with a LAN Host header"
grep -n "allowedDomains" "$fe/astro.config.mjs"
echo "POST /es/login Host=localhost:        $(code -X POST -H 'Host: localhost' -H 'Origin: http://localhost' -d 'username=aa0-probe&password=x' "$BASE/es/login")"
echo "POST /es/login Host=$(hostname): $(code -X POST -H "Host: $(hostname)" -H "Origin: http://$(hostname)" -d 'username=aa0-probe&password=x' "$BASE/es/login")"

h "F25 proposal store mount (backend container)"
docker inspect "$(docker compose -p "${COMPOSE_PROJECT:-ttod_oracle}" -f "$LIVE_COMPOSE" ps -q backend)" \
  --format '{{len .Mounts}} mounts {{range .Mounts}}· {{.Type}} {{.Source}} -> {{.Destination}} {{end}}' 2>&1
grep -n "TTOD_PROPOSAL_DIR" "$LIVE_COMPOSE"

h "F27 /health with Redis down"
if [ "$REDIS_DOWN" = "--with-redis-down" ]; then
  docker compose -p "${COMPOSE_PROJECT:-ttod_oracle}" -f "$LIVE_COMPOSE" stop redis >/dev/null 2>&1
  sleep 2
  echo "redis stopped → /health: HTTP $(code "$BASE/health") body $(curl -s -m 5 "$BASE/health")"
  docker compose -p "${COMPOSE_PROJECT:-ttod_oracle}" -f "$LIVE_COMPOSE" start redis >/dev/null 2>&1
  for _ in $(seq 1 30); do
    curl -s -m 3 "$BASE/health" | grep -q '"redis":"ok"' && break; sleep 1
  done
  echo "redis restarted → /health: $(curl -s -m 5 "$BASE/health")"
else
  echo "skipped (pass --with-redis-down)"
fi

h "F3 open registration"
echo "GET /es/register: $(code "$BASE/es/register/")"
grep -rn "REGISTRATION_OPEN\|rate_limit\|ratelimit" "$repo/services/backend" --include='*.py' | head -5 || true
echo "(no matches above = no registration gate or limiter in backend code)"

h "F14 robots / sitemap"
echo "/robots.txt: $(code "$BASE/robots.txt") · /sitemap.xml: $(code "$BASE/sitemap.xml") · /sitemap-index.xml: $(code "$BASE/sitemap-index.xml")"

h "F32 graph locale"
curl -s -m 10 "$BASE/es/graph/path/" | grep -o '<html[^>]*lang="[^"]*"' | head -1
island="$fe/src/components/graph/GraphIsland.svelte"
echo "English UI strings hard-coded in GraphIsland.svelte (rendered on /es/ too):"
grep -noE '>(All tags|Loading live graph…|Select a node to view its details\.|Selected node|TTOD knowledge graph)<|aria-label="Section legend"' "$island" | sed 's/^/  /'

h "F8 slash duplicates (slashless vs slash)"
for p in /es/wisdom /es/library /es/graph /es/graph/path /es/oracle /es/login /es/docs /en/wisdom; do
  printf '%-18s no-slash %s · slash %s\n' "$p" "$(code "$BASE$p")" "$(code "$BASE$p/")"
done

h "F50/F51 id inventory"
for p in /es/ /es/wisdom/; do
  ids="$(curl -s -m 10 "$BASE$p" | grep -o ' id="[^"]*"' | sed 's/ id=//; s/"//g' | sort -u)"
  echo "$p: $(printf '%s\n' "$ids" | grep -c .) ids → $(printf '%s ' $ids)"
done

h "F57 language switch on /es/wisdom/wis-034/"
page="$(curl -s -m 10 "$BASE/es/wisdom/wis-034/")"
sw="$(printf '%s' "$page" | grep -oE 'href="/en/[^"]*"' | sort -u | head -5)"
echo "EN links on the page: $sw"
target="$(printf '%s' "$page" | grep -oE 'href="/en/wisdom/[^"]*wis-034[^"]*"' | head -1 | sed 's/href="//; s/"//')"
if [ -n "$target" ]; then
  echo "switch target $target → HTTP $(code "$BASE$target") · title: $(curl -s -m 10 "$BASE$target" | grep -o '<title>[^<]*' | head -1)"
else
  echo "no direct EN link to wis-034 found (switch is script-driven)"
fi
echo "/en/wisdom/wis-034/ → HTTP $(code "$BASE/en/wisdom/wis-034/") · title: $(curl -s -m 10 "$BASE/en/wisdom/wis-034/" | grep -o '<title>[^<]*' | head -1)"
echo "/es/no-such-page/ → HTTP $(code "$BASE/es/no-such-page/")"

h "end"
