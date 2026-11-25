#!/usr/bin/env bash
# AA3 exit gate (F7, F9–F12, F32–F38, F53, F55 UI, F56, F58 · A6, A8–A11, A20–A26, A31, A33, A35), made
# runnable. Written by the planner before the phase code (2026-11-11). Any later amendment is disclosed
# in PHASE-AA3-REPORT.md.
#
# Frontend test-file contract (services/frontend, vitest):
#   src/layouts/header.test.ts                 header signed-out/in × en/es: 4 primary links (no Home), Entrar with
#                                              ?next= = this path (never login/register), Cuenta (display_name when
#                                              set) + Biblioteca only signed in, quiet EN/ES text link with hreflang
#                                              + lang, aria-current by prefix, skip link → main#ttod-main; footer
#                                              login never self-next (F7, F9, F10, F11, F38, F56)
#   src/tests/library-page.test.ts             stele cards with id, localized section, saved date; empty and 503 via
#                                              EmptyState (F53)
#   src/tests/account-user-section.test.ts     #profile #password #sessions; password POST rotates the cookie (Secure
#                                              per cookieSecure), PRG flash; wrong current → localized error, no
#                                              cookie; confirm mismatch → no backend call; profile POST → PATCH;
#                                              sign out everywhere → logout-all (F55 UI, A35)
#   src/components/graph/GraphIsland.i18n.test.ts   the 2D island speaks es on /es/ (F32, A20)
#   src/tests/shell-polish.test.ts             quote empty corpus → EmptyState not 500 (F34); localized Forbidden
#                                              (F35); register confirm (F36); logout deletes with the set attributes (F37)
#
# Live, isolated (scripts/isolated-stack.sh, project ttod_aa3gate): signed-out and signed-in HTML, the account
# forms end to end (profile name in the header, password change keeps the caller signed in and signs out a
# second session, wrong current refused), library cards for a saved quote, the Forbidden page, logout
# cookie attributes. Then scripts/aa3-browser-check.mjs (header geometry at 390/768/1440, disclosure menu,
# skip link, anchors below the header, CieloRuyi under reduced motion, Spanish 2D graph, CSP ≤ AA1), the
# AA3b browser check again (anchors must survive the new header, also throttled), and the AA0 UX rule.
#
# AA3_SKIP_LIVE=1 / AA3_SKIP_UX=1 are for quick local pre-checks only; the runner's verify runs all.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
pack="docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING"
fe="services/frontend"
tmp="${TMPDIR:-/tmp}"
fail() { echo "AA3 GATE FAIL: $*" >&2; exit 1; }
start="$(git log --format=%H -1 --diff-filter=A -- "$pack/PHASES/AA3-nav-a11y-and-url-hygiene.exit-gate.sh")"
[ -n "$start" ] || start="$(git merge-base HEAD origin/main)"

# 1. Contract tests, full suite, typecheck.
tests=(src/layouts/header.test.ts src/tests/library-page.test.ts src/tests/account-user-section.test.ts
       src/components/graph/GraphIsland.i18n.test.ts src/tests/shell-polish.test.ts
       src/tests/locators-registry.test.ts src/middleware.test.ts)
for t in "${tests[@]}"; do test -f "$fe/$t" || fail "missing $fe/$t (test-file contract above)"; done
[ -d "$fe/node_modules" ] || (cd "$fe" && npm ci --no-audit --no-fund >/dev/null 2>&1) || fail "npm ci failed"
(cd "$fe" && npx vitest run "${tests[@]}" >"$tmp/aa3-contract.log" 2>&1) || { tail -30 "$tmp/aa3-contract.log"; fail "contract tests red"; }
echo "contract tests: $(grep -Eo 'Tests +[0-9]+ passed' "$tmp/aa3-contract.log" | tail -1)"
(cd "$fe" && npx vitest run >"$tmp/aa3-suite.log" 2>&1) || { tail -30 "$tmp/aa3-suite.log"; fail "frontend suite red"; }
echo "frontend suite: $(grep -Eo 'Tests +[0-9]+ passed' "$tmp/aa3-suite.log" | tail -1)"
(cd "$fe" && npm run check >"$tmp/aa3-check.log" 2>&1) || { tail -30 "$tmp/aa3-check.log"; fail "astro check red"; }

# 2. Static scope and the shipped lessons.
page="$fe/src/layouts/Page.astro"
grep -q 'border-radius: 999px' <(sed -n '/\.ttod-site-header {/,/}/p' "$page") && fail "header is still a pill (border-radius 999px)"
grep -Eq -- '--ttod-header-height: *[0-9.]+rem' "$page" || fail "--ttod-header-height token missing"
grep -q 'scroll-padding-top: calc(var(--ttod-header-height)' "$page" || fail "global scroll-padding-top rule lost"
grep -q 'data-collapsible' "$page" || fail "server-side data-collapsible lost (CLS 0.19 lesson)"
grep -q '<noscript>' "$page" || fail "<noscript> no-JS navigation lost"
grep -q 'ttod-network-boundary' "$page" || fail "network status live region lost"
for keep in 'cambioIdioma' 'data-cambio-idioma' 'id="ttod-aviso"' 'enlazarCambioIdioma' 'enlazarCopiarEnlace'; do
  grep -q "$keep" "$page" || fail "AA3b hook '$keep' lost from Page.astro"; done
! git grep -q -e 'banda-arriba' -e 'cabecera-flujo' -e 'overlayHeader' -- "$fe/src" || fail "the 61 px band hack is still there"
python3 - "$fe/src/lib/locators.registry.json" <<'PY' || fail "account registry row still owned by AA3 or missing its ids"
import json, sys
rows = [p for p in json.load(open(sys.argv[1]))["pages"] if p["path"] == "/{l}/account/"]
ok = rows and not rows[0].get("owner") and {"profile", "password", "sessions"} <= set(rows[0]["ids"])
sys.exit(0 if ok else 1)
PY
inl_before=$(git grep -c 'is:inline' "$start" -- "$fe/src" | awk -F: '{s+=$NF} END {print s+0}')
inl_now=$(git grep -c 'is:inline' -- "$fe/src" | awk -F: '{s+=$NF} END {print s+0}')
[ "$inl_now" -le "$inl_before" ] || fail "is:inline scripts grew $inl_before → $inl_now (AA1 CSP backlog)"
# Scope window (amended in AA7): this phase's own diff ends at its DONE commit. Re-run on a later branch,
# a later phase's legitimate backend change (AA5) must not count as AA3's.
end="$(git log --format=%H -1 --grep='owner marks AA3 DONE')"; [ -n "$end" ] || end=HEAD
git diff --quiet "$start" "$end" -- ttod.yml proposals services/backend || fail "AA3 touched ttod.yml, proposals or the backend"
test -f "$pack/PHASE-AA3-REPORT.md" || fail "missing PHASE-AA3-REPORT.md"
git diff --check "$start" -- . ':(exclude)*.md' || fail "whitespace errors"

# 3. Live, isolated.
if [ "${AA3_SKIP_LIVE:-0}" != "1" ]; then
  stack="$pack/scripts/isolated-stack.sh"; project=ttod_aa3gate; port="${AA3_PORT:-28480}"
  trap 'bash "$stack" down "$project"' EXIT
  bash "$stack" up "$project" "$port" >/dev/null
  base="http://127.0.0.1:$port"
  python3 - "$base" "$port" <<'PY' || fail "live signed-out/signed-in checks (see message above)"
import http.cookiejar, json, re, sys, urllib.error, urllib.parse, urllib.request
base, port = sys.argv[1], sys.argv[2]
errs = []
def check(ok, msg):
    if not ok: errs.append(msg)
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
def client():
    jar = http.cookiejar.CookieJar()
    return jar, urllib.request.build_opener(NoRedirect, urllib.request.HTTPCookieProcessor(jar))
def req(op, path, data=None, method=None, json_body=None, headers=None):
    h = {"Origin": f"http://localhost:{port}", "Host": f"localhost:{port}", **(headers or {})}
    body = None
    if json_body is not None: body = json.dumps(json_body).encode(); h["content-type"] = "application/json"
    elif data is not None: body = urllib.parse.urlencode(data).encode(); h["content-type"] = "application/x-www-form-urlencoded"
    r = urllib.request.Request(base + path, data=body, method=method, headers=h)
    try: resp = op.open(r, timeout=60); return resp.status, resp.headers, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e: return e.code, e.headers, e.read().decode("utf-8", "replace")
header = lambda html: (re.search(r'<header[^>]*id="ttod-site-header".*?</header>', html, re.S) or [""])[0]
# Signed out.
_, anon = client()
for path, lang in (("/es/", "es"), ("/en/wisdom/sections/architecture/", "en"), ("/es/login/", "es")):
    st, _, html = req(anon, path); h = header(html)
    check(st == 200, f"{path} → {st}")
    entrar = re.search(r'href="(/%s/login/[^"]*)"' % lang, h)
    check(bool(entrar), f"{path}: no sign-in link in the header (F7)")
    if entrar: check("login" not in urllib.parse.unquote(entrar.group(1).split("next=", 1)[-1]) if "next=" in entrar.group(1) else True, f"{path}: sign-in next points at login (F9)")
    check(f'/{lang}/library/' not in h, f"{path}: Library shown signed out (F10)")
    check(len(re.findall(r'<main[\s>]', html)) == 1 and 'id="ttod-main"' in re.search(r'<main[^>]*>', html).group(0), f"{path}: not exactly one main#ttod-main (F11)")
st, _, html = req(anon, "/en/wisdom/sections/architecture/")
check(re.search(r'<a[^>]*href="/en/wisdom/"[^>]*aria-current="page"|<a[^>]*aria-current="page"[^>]*href="/en/wisdom/"', header(html)), "nested wisdom route does not mark Wisdom current (F38)")
# A student: register, sign in through the form, twice (two browsers).
email, pw, pw2 = f"aa3-{port}@example.test", "aa3-gate-password-1", "aa3-gate-password-2"
st, _, _ = req(anon, "/api/v1/auth/register", json_body={"email": email, "password": pw}); check(st == 201, f"register → {st}")
jar_a, a = client(); jar_b, b = client()
for op in (a, b):
    st, hd, _ = req(op, "/es/login/", data={"email": email, "password": pw}); check(st == 303, f"form login → {st}")
st, _, html = req(a, "/es/wisdom/"); h = header(html)
check("/es/account/" in h and "/es/library/" in h and "/es/login/" not in h, "signed-in header lacks Cuenta/Biblioteca or still shows Entrar (F7)")
# Profile name shows in the header.
st, hd, _ = req(a, "/es/account/", data={"intent": "profile", "display_name": "Ada Gate"}); check(st == 303, f"profile POST → {st}")
st, _, html = req(a, "/es/account/")
check(st == 200 and "Ada Gate" in header(html), "display_name not shown in the header after the profile form (F55)")
for anchor in ("profile", "password", "sessions"): check(f'id="{anchor}"' in html, f"/es/account/ lacks #{anchor}")
# Wrong current password is refused, nothing changes.
st, hd, html = req(a, "/es/account/", data={"intent": "password", "current_password": "wrong-one-xx", "new_password": pw2, "confirm_password": pw2, "revoke_others": "on"})
check(st in (400, 401, 422) and "ttod_session=" not in (hd.get("Set-Cookie") or ""), f"wrong current password → {st}, cookie set: {'ttod_session=' in (hd.get('Set-Cookie') or '')}")
# Confirm mismatch is refused.
st, hd, html = req(a, "/es/account/", data={"intent": "password", "current_password": pw, "new_password": pw2, "confirm_password": pw2 + "x", "revoke_others": "on"})
check(st in (400, 422), f"confirm mismatch → {st}")
# The real change: caller stays signed in with a rotated cookie, the second browser is out, old password dead.
st, hd, _ = req(a, "/es/account/", data={"intent": "password", "current_password": pw, "new_password": pw2, "confirm_password": pw2, "revoke_others": "on"})
check(st == 303 and "ttod_session=" in (hd.get("Set-Cookie") or ""), f"password change → {st}, rotated cookie: {'ttod_session=' in (hd.get('Set-Cookie') or '')}")
check("Secure" not in (hd.get("Set-Cookie") or ""), "rotated cookie is Secure over plain HTTP (AA2 F22)")
st, _, html = req(a, "/es/account/"); check(st == 200, f"caller signed out after changing password ({st})")
st, _, _ = req(b, "/api/v1/auth/session"); check(st == 401, f"other session still alive after revoke_others ({st})")
st, _, _ = req(anon, "/api/v1/auth/login", json_body={"email": email, "password": pw}); check(st == 401, f"old password still works ({st})")
# Library: a saved quote renders as a stele card with a localized section and its id.
corpus = json.loads(urllib.request.urlopen(base + "/api/v1/wisdom/sample").read())
q = next(e for e in corpus if e["lang"] == "es" and e["section"] == "architecture")
st, _, _ = req(a, "/api/v1/favorites", json_body={"quoteId": q["id"]}); check(st in (200, 201), f"save favorite → {st}")
st, _, html = req(a, "/es/library/")
check(st == 200 and re.search(r'<article[^>]*class="[^"]*piedra[^"]*"[^>]*id="%s"|<article[^>]*id="%s"[^>]*class="[^"]*piedra' % (q["id"], q["id"]), html) and "Arquitectura" in html,
      f"/es/library/: no stele card #{q['id']} with 'Arquitectura' (F53)")
# Forbidden is a localized page.
st, hd, html = req(a, "/es/account/reviewer/")
check(st == 403 and 'lang="es"' in html and "text/html" in (hd.get("content-type") or ""), f"student on reviewer queue → {st}, not a localized HTML page (F35)")
# Logout deletes with the attributes it was set with.
st, hd, _ = req(a, "/es/logout", data={})
sc = hd.get("Set-Cookie") or ""
check(st == 303 and "ttod_session=" in sc and "Path=/" in sc and "HttpOnly" in sc and re.search(r"SameSite=Lax", sc, re.I), f"logout cookie delete attrs: {sc!r} (F37)")
if errs: print("\n".join(errs)); sys.exit(1)
print("live: signed-out header (Entrar, no Library, prefix current, one main#ttod-main), signed-in header, profile name, password change e2e, library card, localized 403, logout attrs")
PY
  FE_PKG="$repo_root/$fe/package.json" node "$pack/scripts/aa3-browser-check.mjs" "$base" "$pack/baselines/aa1-2026-11-10/browser-smoke-after.json" \
    || fail "AA3 browser checks (see messages above)"
  FE_PKG="$repo_root/$fe/package.json" node "$pack/scripts/aa3b-browser-check.mjs" "$base" "$pack/baselines/aa1-2026-11-10/browser-smoke-after.json" \
    || fail "AA3b anchor/locator checks no longer pass with the new header"
  if [ "${AA3_SKIP_UX:-0}" != "1" ]; then
    ux="$(mktemp -d)/ux"
    for v in /es/ /es/wisdom/ /es/graph/; do curl -fs -o /dev/null "$base$v"; curl -fs -o /dev/null "$base$v"; done
    FE_PKG="$repo_root/$fe/package.json" VIEWS="/es/ /es/wisdom/ /es/graph/" \
      bash "$pack/baselines/aa0-2026-11-10/baseline.sh" "$base" "$ux" >/dev/null || fail "baseline.sh failed"
    python3 - "$pack/baselines/aa0-2026-11-10/ux-baseline.json" "$ux/ux-baseline.json" <<'PY' || fail "AA0 UX regression rule"
import json, sys
a = {v["path"]: v for v in json.load(open(sys.argv[1]))["views"]}
b = {v["path"]: v for v in json.load(open(sys.argv[2]))["views"]}
bad = []
for new, old in {"/es/": "/es/", "/es/wisdom/": "/es/wisdom/", "/es/graph/": "/es/graph/path"}.items():
    n, o = b[new], a[old]
    if n["lighthouse_a11y"] < o["lighthouse_a11y"]: bad.append(f"{new}: a11y {n['lighthouse_a11y']} < {o['lighthouse_a11y']}")
    extra = set(n["a11y_failing_audits"]) - set(o["a11y_failing_audits"])
    if extra: bad.append(f"{new}: new failing a11y audits {sorted(extra)}")
    if n["cls"] > min(0.1, o["cls"] + 0.02): bad.append(f"{new}: CLS {n['cls']} > {min(0.1, o['cls'] + 0.02)}")
    if n["lcp_ms"] > o["lcp_ms"] * 1.2: bad.append(f"{new}: LCP {n['lcp_ms']} > {round(o['lcp_ms'] * 1.2)}")
    print(f"{new:14} a11y {n['lighthouse_a11y']} CLS {n['cls']:.4f} LCP {n['lcp_ms']} (AA0 {old}: {o['lighthouse_a11y']} / {o['cls']:.4f} / {o['lcp_ms']})")
if bad: print("\n".join(bad)); sys.exit(1)
PY
  fi
  echo "live (isolated $project): signed-out/in HTML, account e2e, browser checks, AA3b anchors${AA3_SKIP_UX:+ (UX skipped)}, AA0 UX rule"
fi

echo "AA3 exit gate passed: classic header, account and library UX, Spanish 2D graph, shell a11y hygiene."
