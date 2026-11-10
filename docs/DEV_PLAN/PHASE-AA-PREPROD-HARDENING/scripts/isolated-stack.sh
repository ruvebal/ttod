#!/usr/bin/env bash
# Isolated TTOD stack for exit gates: reverse-proxy + frontend + backend + redis, built from the
# current checkout, in its own Compose project, on scratch ports. Never touches `ttod_oracle`.
# Ollama and the MCP server are not started (the oracle answers 5xx without them; auth runs first).
#
# Usage: isolated-stack.sh up <project> <http-port> [extra KEY=VALUE env ...]
#        isolated-stack.sh down <project>
# The env file (throwaway secrets + ports + extras) lives at ${TMPDIR:-/tmp}/<project>.env.
set -euo pipefail
cmd="${1:?up|down}"; project="${2:?project}"
repo="$(git rev-parse --show-toplevel)"; cd "$repo"
envf="${TMPDIR:-/tmp}/$project.env"
dc() { docker compose -p "$project" --env-file "$envf" -f docker-compose.yml "$@"; }
case "$cmd" in
  up)
    port="${3:?http-port}"; shift 3
    { echo "HTTP_PORT=$port"; echo "ALT_HTTP_PORT=$((port + 1))"
      echo "TTOD_SESSION_SECRET=$(openssl rand -hex 24)"; echo "TTOD_PAT_SECRET=$(openssl rand -hex 24)"
      for kv in "$@"; do echo "$kv"; done; } > "$envf"
    dc up -d redis >/dev/null 2>&1
    dc up -d --no-deps --build backend >/dev/null 2>&1
    for _ in $(seq 1 60); do [ "$(docker inspect -f '{{.State.Health.Status}}' "$(dc ps -q backend)" 2>/dev/null)" = healthy ] && break; sleep 2; done
    dc up -d --no-deps --build frontend >/dev/null 2>&1
    dc up -d --no-deps reverse-proxy >/dev/null 2>&1
    for _ in $(seq 1 60); do curl -fs -o /dev/null "http://127.0.0.1:$port/es/" && break; sleep 2; done
    curl -fs -o /dev/null "http://127.0.0.1:$port/es/" || { echo "isolated stack not serving on :$port" >&2; exit 1; }
    echo "isolated stack $project up on http://127.0.0.1:$port"
    ;;
  down) dc down -v --remove-orphans >/dev/null 2>&1 || true; rm -f "$envf" ;;
  *) echo "usage: $0 up|down <project> ..." >&2; exit 2 ;;
esac
