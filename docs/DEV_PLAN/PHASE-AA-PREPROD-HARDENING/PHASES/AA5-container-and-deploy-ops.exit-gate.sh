#!/usr/bin/env bash
# AA5 exit gate. Lane A section (F25 / F27 / F28 · I7–I9), made runnable. Written by the planner before
# the phase starts. Lane B checks are appended to this same file when AA1 is DONE (the harness
# looks for exactly one <phase>.exit-gate.sh); lane A checks then keep running.
#
# Test-name contract (the implementer adds these to services/backend/tests):
#   *health_redis_down*   F27: /health answers 503 (or the ready probe does) when REDIS_URL is set
#                         and the ping fails
#   *empty_secret*        F28: boot fails closed when REDIS_URL is set and a TTOD_*_SECRET is empty
#
# The live part runs in an isolated Compose project (default ttod_aa5gate: redis + backend only,
# no host ports) built from this worktree, so the instructor stack is never touched.
# Set AA5_SKIP_LIVE=1 only for a quick local pre-check; the runner's verify must run it in full.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
pack="docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING"
py="${PYTHON:-$HOME/src/ttod/.venv/bin/python}"
project="${AA5_GATE_PROJECT:-ttod_aa5gate}"
fail() { echo "AA5-A GATE FAIL: $*" >&2; exit 1; }

# 1. Named tests exist and pass, and the backend suite stays green.
run_k() {
  out="$("$py" -m unittest discover -s services/backend/tests -t . -p 'test_*.py' -k "$1" -v 2>&1)" \
    || { printf '%s\n' "$out" | grep -q 'NO TESTS RAN' \
           && fail "no test matches '$1' (see the test-name contract at the top of this gate)"
         printf '%s\n' "$out" | tail -20; fail "tests matching '$1' failed"; }
  n="$(printf '%s\n' "$out" | sed -n 's/^Ran \([0-9]*\) test.*/\1/p')"
  [ "${n:-0}" -ge 1 ] || fail "no test matches '$1' (see the test-name contract at the top of this gate)"
  echo "tests '$1': $n passed"
}
run_k health_redis_down
run_k empty_secret
grep -rqs "503" $(grep -rls "health_redis_down" services/backend/tests) || fail "health_redis_down tests never assert 503"
"$py" -m unittest discover -s services/backend/tests -t . -p 'test_*.py' >/dev/null 2>&1 || fail "backend suite red"

# 2. F28: rebuild runs ensure_env_secrets.
make -n rebuild 2>/dev/null | grep -q 'ensure_env_secrets.py' || fail "make rebuild does not call ensure_env_secrets.py"

# 3. F25: the proposal dir is a host bind at TTOD_PROPOSAL_DIR, and its contents are gitignored.
cfg="$(docker compose -p "$project" -f docker-compose.yml config --format json 2>/dev/null)"
bind_src="$(printf '%s' "$cfg" | python3 -c '
import json, sys
c = json.load(sys.stdin)["services"]["backend"]
target = c["environment"]["TTOD_PROPOSAL_DIR"]
for v in c.get("volumes", []):
    if v.get("type") == "bind" and v.get("target") == target:
        print(v["source"]); break
')"
[ -n "$bind_src" ] || fail "backend has no bind mount whose target equals TTOD_PROPOSAL_DIR"
case "$bind_src" in "$repo_root"/*) ;; *) fail "proposal bind source $bind_src is outside the repo checkout";; esac
rel="${bind_src#"$repo_root"/}"
git check-ignore -q "$rel/aa5-probe.yml" || fail "$rel/ contents are not gitignored"
printf '%s' "$cfg" | python3 -c '
import json, sys
s = json.load(sys.stdin)["services"]["redis"]
sys.exit(1 if s.get("ports") else 0)' || fail "redis publishes a host port"

# 4. Live, isolated: recreate keeps proposal files; /health answers 503 with Redis down.
if [ "${AA5_SKIP_LIVE:-0}" != "1" ]; then
  dc() { docker compose -p "$project" -f docker-compose.yml "$@"; }
  trap 'dc down -v --remove-orphans >/dev/null 2>&1 || true' EXIT
  mkdir -p "$bind_src"
  marker="aa5-gate-$$.txt"; echo "recreate probe" > "$bind_src/$marker"
  dc up -d redis >/dev/null 2>&1
  dc up -d --no-deps --build backend >/dev/null 2>&1 || fail "isolated backend did not start"
  in_backend() { dc exec -T backend python -c "$1"; }
  status() { in_backend "
import urllib.request, urllib.error
try: print(urllib.request.urlopen('http://localhost:8000/health', timeout=3).status)
except urllib.error.HTTPError as e: print(e.code)
except Exception: print(0)"; }
  for _ in $(seq 1 40); do [ "$(status 2>/dev/null)" = "200" ] && break; sleep 2; done
  [ "$(status)" = "200" ] || fail "isolated backend never became healthy with Redis up"
  dc up -d --no-deps --force-recreate backend >/dev/null 2>&1
  for _ in $(seq 1 40); do [ "$(status 2>/dev/null)" = "200" ] && break; sleep 2; done
  dir="$(dc exec -T backend printenv TTOD_PROPOSAL_DIR | tr -d '\r')"
  dc exec -T backend test -f "$dir/$marker" || fail "proposal file lost on backend recreate (F25)"
  rm -f "$bind_src/$marker"
  dc stop redis >/dev/null 2>&1; sleep 3
  code="$(status)"
  [ "$code" = "503" ] || fail "/health answered $code with Redis down, expected 503 (F27)"
  echo "live (isolated $project): recreate kept $marker; /health 503 with Redis down"
fi

# 5. Evidence and scope.
test -f "$pack/PHASE-AA5-REPORT.md" || fail "missing PHASE-AA5-REPORT.md"
grep -qi 'lane a' "$pack/PHASE-AA5-REPORT.md" || fail "report has no lane A section"
start="$(git merge-base HEAD origin/main)"
git diff --quiet "$start" -- ttod.yml proposals || fail "lane A touched the canonical stores"
# Markdown is excluded: two trailing spaces are the pack's deliberate hard line breaks.
git diff --check "$start" -- . ':(exclude)*.md'
echo "AA5 lane A exit gate passed: proposal bind survives recreate, health 503 on Redis down, secrets fail closed."
