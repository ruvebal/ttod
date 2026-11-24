#!/usr/bin/env bash
# AA7 exit gate (Astro 5 → 7), made runnable. Written by the planner with the phase file (2026-11-11), before
# any upgrade code. The point of the phase is that nothing earlier breaks, so after its own checks it re-runs
# the AA1, AA2, AA3b, AA3 and AA5 exit gates (only a pinned scope-window edit allowed; see §4). A guarantee that held on Astro 5 must hold on Astro 7.
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
// Amended during AA7: @astrojs/react declares no Astro peer, so check the first major built for Astro 7
// (npm peer data, 2026-11-11: node 11, svelte 9, mdx 8 need astro ^7; react 7 shipped alongside).
for (const [p, min] of [["@astrojs/node", 11], ["@astrojs/svelte", 9], ["@astrojs/react", 7], ["@astrojs/mdx", 8]]) {
  if (major(p) < min) bad.push(`${p} ${v(p)} < ${min} (the major built for Astro 7)`);
}
if (bad.length) { console.error(bad.join("\n")); process.exit(1); }
console.log(`astro ${v("astro")}, @astrojs/node ${v("@astrojs/node")}`);
') || fail "Astro 7 and matching integrations not installed"

# 2. The production audit: no critical, no high.
# Amended during AA7: npm audit exits non-zero on any advisory (even low); only the verdict below counts.
(cd "$fe" && npm audit --omit=dev --json 2>/dev/null || true) | python3 -c '
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
# Amended during AA7 (strengthening): the production image installs with --omit=dev, so every bare
# import the built server makes must resolve to a top-level, non-dev package in the lockfile. Astro 7
# emitted `import "cookie"` while its cookie@2 sat nested under astro/ and the top-level cookie was a
# dev-only 1.x: fine locally (wrong version), a crash in the image.
(cd "$fe" && grep -rhoE 'from "[a-z@][^"]*"|import\("[a-z@][^"]*"\)' dist/server 2>/dev/null \
  | sed -E 's/.*"([^"]+)".*/\1/' | grep -v '^node:\|^astro:' | sed -E 's#^(@[^/]+/[^/]+|[^/@][^/]*).*#\1#' | sort -u \
  | python3 -c '
import json, sys
lock = json.load(open("package-lock.json"))["packages"]; bad = []
externals = sys.stdin.read().split()
# Amended after the cold review (F2): presence is not enough. If a package that the server code comes
# from (astro, @astrojs/node, or another external) has its OWN nested copy of X, its bare `import "X"`
# gets the top-level copy instead (devalue: Astro wants 6, the top level is the Svelte copy, 5). Such an X
# must be bundled (vite.ssr.noExternal in astro.config.mjs).
owners = set(externals) | {"astro", "@astrojs/node"}
for pkg in externals:
    top = lock.get(f"node_modules/{pkg}")
    why = "missing" if not top else ("dev-only" if top.get("dev") else "")
    if why: bad.append(pkg + ": " + why + " at top level")
    for owner in owners:
        nested = lock.get(f"node_modules/{owner}/node_modules/{pkg}")
        if nested and top and nested.get("version") != top.get("version"):
            bad.append(f"{pkg}: {owner} needs its nested {nested.get('version')}, the bundle would import the top-level {top.get('version')}")
if bad: print("\n".join(bad)); sys.exit(1)') || fail "the built server imports a package the production image will not have"

# 4. Earlier gates. Amended after the cold review (F4/F5): the allowed edit is pinned by content, not by text
# patterns. AA1, AA3b and AA3 got one scope window each (their own diff ends at their DONE commit); each of
# those three files must be byte-identical to the blob pinned here. Every other earlier gate and browser
# check must be unchanged since this gate was written. Re-pinning a hash is a reviewed change, never routine.
declare -A pinned=(
  [AA1-caddy-security-headers]=c133ae2319fa1cfb682ea2b73f8e441a64542bb2
  [AA3b-locators-wisdom-and-graph-ia]=16da05b5e54da0ddd82a1814ecbd481120ca848a
  [AA3-nav-a11y-and-url-hygiene]=5e2e658e97cfe2632756390536c4826c12099004
)
gates=(AA1-caddy-security-headers AA2-auth-throttle-and-fallback AA3b-locators-wisdom-and-graph-ia AA3-nav-a11y-and-url-hygiene AA5-container-and-deploy-ops)
for g in "${gates[@]}"; do
  f="$pack/PHASES/$g.exit-gate.sh"
  if [ -n "${pinned[$g]:-}" ]; then
    [ "$(git hash-object "$f")" = "${pinned[$g]}" ] || fail "$g exit gate differs from its pinned scope-window version"
  else
    git diff --quiet "$start" -- "$f" || fail "$g exit gate was edited on the AA7 branch"
  fi
done
git diff --quiet "$start" -- "$pack/scripts/aa3b-browser-check.mjs" "$pack/scripts/aa3-browser-check.mjs" \
  || fail "an earlier browser check was edited on the AA7 branch"
if [ "${AA7_SKIP_GATES:-0}" != "1" ]; then
  for g in "${gates[@]}"; do
    echo "--- re-running $g"
    log="${TMPDIR:-/tmp}/aa7-$g.log"
    bash "$pack/PHASES/$g.exit-gate.sh" >"$log" 2>&1 || { tail -15 "$log"; fail "$g exit gate fails on Astro 7"; }
    # Keep each gate's CSP counts and UX numbers in this log, not only its last line (cold review F8).
    grep -E '^csp |a11y [0-9]+ CLS|live|contract tests|frontend suite' "$log" || true
    tail -1 "$log"
  done
  gates_note="and the AA1/AA2/AA3b/AA3/AA5 guarantees re-proven"
else
  gates_note="(earlier gates SKIPPED: AA7_SKIP_GATES=1, not a verify)"
fi

# 5. Evidence and scope.
test -f "$pack/PHASE-AA7-REPORT.md" || fail "missing PHASE-AA7-REPORT.md"
grep -q "heading" "$pack/PHASE-AA7-REPORT.md" || fail "report has no docs heading-id diff"
# Amended during AA7: Caddy left the forbidden list. Astro 7 normalizes `//host` paths behind a proxy, so
# the open-redirect guard moved to the edge (caddy/Caddyfile @rutadoble); see PHASE-AA7-REPORT §3b.
git diff --quiet "$start" -- ttod.yml proposals services/backend || fail "AA7 touched the corpus or the backend"
git diff --check "$start" -- . ':(exclude)*.md' || fail "whitespace errors"
echo "AA7 exit gate passed: Astro 7, clean production audit, $gates_note."
