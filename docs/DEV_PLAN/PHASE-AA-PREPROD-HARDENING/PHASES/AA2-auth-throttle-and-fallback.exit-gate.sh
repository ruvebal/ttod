#!/usr/bin/env bash
# AA2 exit gate (F3–F5, F20, F22–F24, F26, F55 API), made runnable. Written by the planner before
# the phase starts.
#
# Backend test-name contract (services/backend/tests, unittest -k):
#   throttle_register  throttle_login  throttle_proposal   429 after the budget (F3/F20)
#   signed_fallback_off                                   signed blob refused by default (F4)
#   pat_denylist                                          revoked PAT → 401 before expiry (F5, D7 b)
#   oracle_requires_session                               stream + propose 401 without session (F24)
#   oracle_propose_dual_write                             propose goes through the proposal store (F26)
#   password_change                                       F55: old fails, new works, other sid 401,
#                                                         caller stays signed in, wrong current → 401
#   session_index                                         per-user SET, pruned on read
# Frontend contract (services/frontend, vitest):
#   src/lib/cookie-security.test.ts                       Secure from COOKIE_SECURE / X-Forwarded-Proto (F22)
#   src/lib/auth.server.test.ts                           forwards the client address to the backend
# Live, isolated (scripts/isolated-stack.sh, project ttod_aa2gate): LAN Host+Origin login is not 403
# (F23), HTTP login sets a non-Secure cookie and a forwarded-https one sets Secure (F22), a register
# burst hits 429 (F3), the oracle answers 401 without a session (F24).
# Set AA2_SKIP_LIVE=1 only for a quick local pre-check; the runner's verify runs it in full.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
pack="docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING"
py="${PYTHON:-$HOME/src/ttod/.venv/bin/python}"
fail() { echo "AA2 GATE FAIL: $*" >&2; exit 1; }

# 1. Backend contract tests exist and pass; full suite green.
run_k() {
  out="$("$py" -m unittest discover -s services/backend/tests -t . -p 'test_*.py' -k "$1" -v 2>&1)" || {
    printf '%s\n' "$out" | grep -q 'NO TESTS RAN' && fail "no test matches '$1' (test-name contract above)"
    printf '%s\n' "$out" | tail -25; fail "tests matching '$1' failed"; }
  echo "tests '$1': $(printf '%s\n' "$out" | sed -n 's/^Ran \([0-9]*\) test.*/\1/p') passed"
}
for k in throttle_register throttle_login throttle_proposal signed_fallback_off pat_denylist \
         oracle_requires_session oracle_propose_dual_write password_change session_index; do run_k "$k"; done
"$py" -m unittest discover -s services/backend/tests -t . -p 'test_*.py' >/dev/null 2>&1 || fail "backend suite red"
"$py" -m unittest discover -s tests -p 'test_*.py' >/dev/null 2>&1 || fail "root suite (make test) red"

# 2. Frontend contract tests and typecheck.
fe="services/frontend"
test -f "$fe/src/lib/cookie-security.test.ts" || fail "missing $fe/src/lib/cookie-security.test.ts"
grep -qi 'x-forwarded-for' "$fe/src/lib/auth.server.test.ts" || fail "auth.server.test.ts does not test client-address forwarding"
[ -d "$fe/node_modules" ] || (cd "$fe" && npm ci --no-audit --no-fund >/dev/null 2>&1) || fail "npm ci failed"
(cd "$fe" && npx vitest run src/lib/cookie-security.test.ts src/lib/auth.server.test.ts >/dev/null 2>&1) || fail "frontend contract tests red"
(cd "$fe" && npx vitest run >/dev/null 2>&1) || fail "frontend suite red"
grep -q 'import.meta.env.PROD' "$fe/src/pages/[locale]/login.astro" "$fe/src/pages/[locale]/register.astro" \
  && fail "cookie Secure still tied to import.meta.env.PROD"
grep -q 'TTOD_ALLOWED_HOSTS' "$fe/astro.config.mjs" || fail "allowedDomains is not read from TTOD_ALLOWED_HOSTS"

# 3. Live, isolated.
if [ "${AA2_SKIP_LIVE:-0}" != "1" ]; then
  stack="$pack/scripts/isolated-stack.sh"; project=ttod_aa2gate; port="${AA2_PORT:-28180}"
  lan="aa2-gate.lan"
  trap 'bash "$stack" down "$project"' EXIT
  bash "$stack" up "$project" "$port" "TTOD_ALLOWED_HOSTS=$lan" "COOKIE_SECURE=auto" >/dev/null
  base="http://127.0.0.1:$port"
  email="aa2-gate-$$@example.test"; pw="aa2-gate-password-$$"
  code=$(curl -s -o /dev/null -w '%{http_code}' -H 'content-type: application/json' \
    -d "{\"email\":\"$email\",\"password\":\"$pw\"}" "$base/api/v1/auth/register")
  [ "$code" = 201 ] || fail "isolated register returned $code"
  form="email=$email&password=$pw"
  lan_code=$(curl -s -o /dev/null -w '%{http_code}' -H "Host: $lan" -H "Origin: http://$lan" -d "$form" "$base/es/login/")
  [ "$lan_code" != 403 ] || fail "LAN Host+Origin login still 403 with TTOD_ALLOWED_HOSTS set (F23)"
  plain="$(curl -s -D - -o /dev/null -H 'Origin: http://localhost:'"$port" -H "Host: localhost:$port" -d "$form" "$base/es/login/" | tr -d '\r' | grep -i '^set-cookie: ttod_session=' || true)"
  [ -n "$plain" ] || fail "HTTP login set no session cookie"
  printf '%s' "$plain" | grep -qi '; *secure' && fail "plain-HTTP login set a Secure cookie (breaks LAN HTTP, F22)"
  https="$(curl -s -D - -o /dev/null -H 'X-Forwarded-Proto: https' -H 'Origin: http://localhost:'"$port" -H "Host: localhost:$port" -d "$form" "$base/es/login/" | tr -d '\r' | grep -i '^set-cookie: ttod_session=' || true)"
  printf '%s' "$https" | grep -qi '; *secure' || fail "forwarded-https login did not set Secure (F22)"
  oc=$(curl -s -o /dev/null -w '%{http_code}' -H 'content-type: application/json' -d '{"query":"x"}' "$base/api/v1/oracle/stream")
  [ "$oc" = 401 ] || fail "oracle stream without session answered $oc, expected 401 (F24)"
  got429=no
  for i in $(seq 1 40); do
    c=$(curl -s -o /dev/null -w '%{http_code}' -H 'content-type: application/json' \
      -d "{\"email\":\"burst-$i-$$@example.test\",\"password\":\"burst-password-$i\"}" "$base/api/v1/auth/register")
    [ "$c" = 429 ] && { got429=yes; break; }
  done
  [ "$got429" = yes ] || fail "40 rapid registrations never hit 429 (F3)"
  echo "live (isolated $project): LAN login $lan_code, cookie Secure only behind https, oracle 401, register burst 429"
fi

# 4. Evidence and scope.
test -f "$pack/PHASE-AA2-REPORT.md" || fail "missing PHASE-AA2-REPORT.md"
start="$(git merge-base HEAD origin/main)"
git diff --quiet "$start" -- ttod.yml proposals || fail "AA2 touched the canonical stores"
git diff --check "$start" -- . ':(exclude)*.md'
echo "AA2 exit gate passed: throttles, fallback off, PAT denylist, oracle auth + dual-write, password API, cookie/Host wiring."
