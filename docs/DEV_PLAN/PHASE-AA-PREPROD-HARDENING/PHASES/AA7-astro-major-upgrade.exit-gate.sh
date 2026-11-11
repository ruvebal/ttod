#!/usr/bin/env bash
# AA7 exit gate (Astro 5 → 7), made runnable. Written by the planner with the phase file (2026-11-11), before
# any upgrade code. The point of the phase is that nothing earlier breaks, so after its own checks it re-runs
# the AA2, AA3b, AA3 and AA5 exit gates as they are. A guarantee that held on Astro 5 must hold on Astro 7.
# Each re-run gate brings up and tears down its own isolated stack (they run one after another).
# AA7_SKIP_GATES=1 runs only AA7's own checks (a quick local pre-check); the runner's verify runs all.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
pack="docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING"
fe="services/frontend"
fail() { echo "AA7 GATE FAIL: $*" >&2; exit 1; }
start="$(git log --format=%H -1 --diff-filter=A -- "$pack/PHASES/AA7-astro-major-upgrade.exit-gate.sh")"
[ -n "$start" ] || start="$(git merge-base HEAD origin/main)"

# 1. Versions: Astro 7 and the official integrations it supports.
[ -d "$fe/node_modules" ] || (cd "$fe" && npm ci --no-audit --no-fund >/dev/null 2>&1) || fail "npm ci failed"
(cd "$fe" && node -e '
const v = (p) => require(p + "/package.json").version;
const major = (p) => Number(v(p).split(".")[0]);
const bad = [];
if (major("astro") < 7) bad.push(`astro ${v("astro")} < 7`);
for (const p of ["@astrojs/node", "@astrojs/svelte", "@astrojs/react", "@astrojs/mdx"]) {
  const peer = require(p + "/package.json").peerDependencies?.astro ?? "";
  if (!/\b7\b|\^7|>=\s*7/.test(peer)) bad.push(`${p} ${v(p)} does not declare Astro 7 support (peer "${peer}")`);
}
if (bad.length) { console.error(bad.join("\n")); process.exit(1); }
console.log(`astro ${v("astro")}, @astrojs/node ${v("@astrojs/node")}`);
') || fail "Astro 7 and matching integrations not installed"

# 2. The production audit: no critical, no high.
(cd "$fe" && npm audit --omit=dev --json 2>/dev/null) | python3 -c '
import json, sys
m = json.load(sys.stdin)["metadata"]["vulnerabilities"]
print(f"npm audit --omit=dev: {m}")
sys.exit(1 if m.get("critical", 0) or m.get("high", 0) else 0)' || fail "production npm audit still has critical or high advisories"

# 3. The migration's own invariants.
! git grep -n "import.meta.env.BACKEND_URL" -- "$fe/src" ':!*.test.*' || fail "server code still reads import.meta.env.BACKEND_URL (build-time in Astro 6+)"
test -f "$fe/src/lib/backend.ts" || fail "missing src/lib/backend.ts (runtime BACKEND_URL reader)"
grep -q "compressHTML" "$fe/astro.config.mjs" || fail "compressHTML not decided explicitly in astro.config.mjs"
grep -q "redirectToDefaultLocale" "$fe/astro.config.mjs" || fail "i18n redirectToDefaultLocale not set explicitly"
! git grep -n "from '@astrojs/react'" -- "$fe/src/**/*.test.*" | grep -q getContainerRenderer || fail "container renderer still imported from the package root"
(cd "$fe" && npx vitest run >"${TMPDIR:-/tmp}/aa7-suite.log" 2>&1) || { tail -30 "${TMPDIR:-/tmp}/aa7-suite.log"; fail "frontend suite red"; }
(cd "$fe" && npm run check >"${TMPDIR:-/tmp}/aa7-check.log" 2>&1) || { tail -30 "${TMPDIR:-/tmp}/aa7-check.log"; fail "astro check red"; }
(cd "$fe" && npm run build >"${TMPDIR:-/tmp}/aa7-build.log" 2>&1) || { tail -30 "${TMPDIR:-/tmp}/aa7-build.log"; fail "build red"; }
(cd "$fe" && npm run pwa:guard >"${TMPDIR:-/tmp}/aa7-pwa.log" 2>&1) || { tail -20 "${TMPDIR:-/tmp}/aa7-pwa.log"; fail "PWA guard red"; }
echo "frontend: suite, check, build, PWA guard green"

# 4. Earlier gates, unchanged: they must not have been edited on this branch to pass.
for g in AA2-auth-throttle-and-fallback AA3b-locators-wisdom-and-graph-ia AA3-nav-a11y-and-url-hygiene AA5-container-and-deploy-ops; do
  git diff --quiet "$start" -- "$pack/PHASES/$g.exit-gate.sh" || fail "$g exit gate was edited on the AA7 branch"
done
git diff --quiet "$start" -- "$pack/scripts/aa3b-browser-check.mjs" "$pack/scripts/aa3-browser-check.mjs" \
  || fail "an earlier browser check was edited on the AA7 branch"
if [ "${AA7_SKIP_GATES:-0}" != "1" ]; then
  for g in AA2-auth-throttle-and-fallback AA3b-locators-wisdom-and-graph-ia AA3-nav-a11y-and-url-hygiene AA5-container-and-deploy-ops; do
    echo "--- re-running $g"
    bash "$pack/PHASES/$g.exit-gate.sh" >"${TMPDIR:-/tmp}/aa7-$g.log" 2>&1 || { tail -15 "${TMPDIR:-/tmp}/aa7-$g.log"; fail "$g exit gate fails on Astro 7"; }
    tail -1 "${TMPDIR:-/tmp}/aa7-$g.log"
  done
fi

# 5. Evidence and scope.
test -f "$pack/PHASE-AA7-REPORT.md" || fail "missing PHASE-AA7-REPORT.md"
grep -q "heading" "$pack/PHASE-AA7-REPORT.md" || fail "report has no docs heading-id diff"
git diff --quiet "$start" -- ttod.yml proposals services/backend caddy || fail "AA7 touched the corpus, backend or Caddy"
git diff --check "$start" -- . ':(exclude)*.md' || fail "whitespace errors"
echo "AA7 exit gate passed: Astro 7, clean production audit, and the AA2/AA3b/AA3/AA5 guarantees re-proven."
