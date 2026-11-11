#!/usr/bin/env bash
# AA3b exit gate (F8, F49–F52, F54, F57 · LOCATORS §3–§8), made runnable. Written by the planner
# before the phase code (2026-11-11). Any later amendment is disclosed in PHASE-AA3b-REPORT.md.
#
# Single source: services/frontend/src/lib/locators.registry.json is LOCATORS §4 as data. The Vitest
# registry test and the live probe below both walk it; the gate also refuses a registry that lost a
# required row (REQUIRED_* below), so the contract cannot shrink to make the gate pass.
#
# Frontend test-file contract (services/frontend, vitest):
#   src/middleware.test.ts                slash 301 (query kept), endpoints/assets/non-GET exempt,
#                                         /graph/path → /graph/ (or /graph/code/ for ?s=), ?tag= → /graph/plano/
#   src/lib/buscar.test.ts                NFD + case fold, q capped at 100, combined filters, single-facet 301 target
#   src/lib/idioma.test.ts                translation twin both directions, no twin → other index + ?untranslated=,
#                                         search + hash carried
#   src/components/graph/senderoUrl.test.ts   ?from=&to=&node= parsed, validated, written back
#   src/tests/locators-registry.test.ts   every registry page: status, each registered id exactly once,
#                                         no duplicate ids, en/es structural id sets equal, quote 404s
#   src/tests/landing-figures.test.ts     F54: fixture corpus 3 quotes / 2 sections / 1 level → 3/2/1 in en
#                                         and es, <dt> label / <dd> number
# F54 is also mutation-checked: typing a literal count into ValleSigue or a landing page must turn
# landing-figures.test.ts red.
#
# Live, isolated (scripts/isolated-stack.sh, project ttod_aa3bgate): the registry probe in curl terms
# (status codes, Location headers, ids, en/es parity, internal hrefs all slash-terminated, search
# results equal to an independent Python fold over /api/v1/wisdom/sample, quote twins from
# /api/v1/graph), then scripts/aa3b-browser-check.mjs (system Chrome) for what only a browser can
# prove: hash → scroll on the sticky handscroll at 390 and 1440 with the header not covering the
# stop, #volume-{section}, the scroll writer (replaceState, no history growth), the language switch
# carrying search + hash, the 3D graph restoring ?from=&to= across reload, copy-link, no uncaught
# page errors, CSP inline-script reports not above the AA1 count.
# Then the AA0 UX regression rule (PHASE-AA0-REPORT §5) on /es/, /es/wisdom/ and /es/graph/ (against
# the AA0 /es/graph/path row), plus a recorded first baseline for /es/graph/plano/.
#
# AA3B_SKIP_LIVE=1 / AA3B_SKIP_UX=1 are for quick local pre-checks only; the runner's verify runs all.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
pack="docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING"
fe="services/frontend"
reg="$fe/src/lib/locators.registry.json"
fail() { echo "AA3b GATE FAIL: $*" >&2; exit 1; }
start="$(git log --format=%H -1 --diff-filter=A -- "$pack/PHASES/AA3b-locators-wisdom-and-graph-ia.exit-gate.sh")"
[ -n "$start" ] || start="$(git merge-base HEAD origin/main)"

# 1. The registry exists, is named by the frozen contract, and still carries every required row.
test -f "$reg" || fail "missing $reg (LOCATORS §4 as data)"
grep -q 'locators.registry.json' "$pack/LOCATORS.md" || fail "LOCATORS.md does not name the registry file"
python3 - "$reg" <<'PY' || fail "registry is missing required rows (see message above)"
import json, sys
r = json.load(open(sys.argv[1]))
pages = {p["path"]: p for p in r["pages"]}
REQUIRED_PAGES = {
    "/{l}/": {"start", "doors", "thesis", "map", "map-{section}", "close", "flagship-quote-heading", "sigue-tesis", "sigue-rollo"},
    "/{l}/wisdom/": {"search", "draw", "facets", "volume-{section}"},
    "/{l}/wisdom/{quote}/": set(),
    "/{l}/wisdom/sections/{section}/": {"{quote}"},
    "/{l}/wisdom/levels/{level}/": {"{quote}"},
    "/{l}/wisdom/tags/{tag}/": {"{quote}"},
    "/{l}/wisdom/?q={word}": {"search", "{quote}"},
    "/{l}/wisdom/?section={section}&level={level}": {"search", "{quote}"},
    "/{l}/graph/": set(), "/{l}/graph/plano/": set(), "/{l}/graph/code/": set(),
}
REQUIRED_REDIRECTS = {
    "/{l}/wisdom": "/{l}/wisdom/",
    "/{l}/graph": "/{l}/graph/",
    "/{l}/oracle?x=1": "/{l}/oracle/?x=1",
    "/{l}/graph/path": "/{l}/graph/",
    "/{l}/graph/path/?from={a}&to={b}": "/{l}/graph/?from={a}&to={b}",
    "/{l}/graph/path?from={a}&to={b}": "/{l}/graph/?from={a}&to={b}",
    "/{l}/wisdom/?section={section}": "/{l}/wisdom/sections/{section}/",
    "/{l}/wisdom/?level={level}&orden=nivel": "/{l}/wisdom/levels/{level}/?orden=nivel",
    "/{l}/wisdom/?tag={tag}": "/{l}/wisdom/tags/{tag}/",
}
missing = []
for path, ids in REQUIRED_PAGES.items():
    if path not in pages: missing.append(f"page {path}"); continue
    lost = ids - set(pages[path].get("ids", []))
    if lost: missing.append(f"ids {sorted(lost)} on {path}")
red = {x["from"]: x["to"] for x in r["redirects"]}
for a, b in REQUIRED_REDIRECTS.items():
    if red.get(a) != b: missing.append(f"redirect {a} -> {b}")
for k in ("notFound", "exempt", "values"):
    if not r.get(k): missing.append(k)
if missing: print("\n".join(missing)); sys.exit(1)
print(f"registry: {len(pages)} pages, {len(red)} redirects, {len(r['notFound'])} not-found, {len(r['exempt'])} exempt")
PY

# 2. Frontend contract tests, full suite, typecheck.
tests=(src/middleware.test.ts src/lib/buscar.test.ts src/lib/idioma.test.ts src/components/graph/senderoUrl.test.ts
       src/tests/locators-registry.test.ts src/tests/landing-figures.test.ts)
for t in "${tests[@]}"; do test -f "$fe/$t" || fail "missing $fe/$t (test-file contract above)"; done
[ -d "$fe/node_modules" ] || (cd "$fe" && npm ci --no-audit --no-fund >/dev/null 2>&1) || fail "npm ci failed"
(cd "$fe" && npx vitest run "${tests[@]}" >"${TMPDIR:-/tmp}"/aa3b-contract.log 2>&1) || { tail -30 "${TMPDIR:-/tmp}"/aa3b-contract.log; fail "contract tests red"; }
echo "contract tests: $(grep -Eo 'Tests +[0-9]+ passed' "${TMPDIR:-/tmp}"/aa3b-contract.log | tail -1)"
(cd "$fe" && npx vitest run >"${TMPDIR:-/tmp}"/aa3b-suite.log 2>&1) || { tail -30 "${TMPDIR:-/tmp}"/aa3b-suite.log; fail "frontend suite red"; }
echo "frontend suite: $(grep -Eo 'Tests +[0-9]+ passed' "${TMPDIR:-/tmp}"/aa3b-suite.log | tail -1)"
(cd "$fe" && npm run check >"${TMPDIR:-/tmp}"/aa3b-check.log 2>&1) || { tail -30 "${TMPDIR:-/tmp}"/aa3b-check.log; fail "astro check red"; }
grep -q "'dt'" "$fe/src/tests/landing-figures.test.ts" && grep -q "'dd'" "$fe/src/tests/landing-figures.test.ts" \
  || fail "landing-figures.test.ts does not query <dt>/<dd>"

# 3. F54 mutation: a literal count must turn the fixture test red (then restore).
mutate() { # file, python regex, replacement
  local f="$1"; cp "$f" "$f.aa3b-orig"
  python3 - "$f" "$2" "$3" <<'PY' || { mv "$f.aa3b-orig" "$f"; fail "F54 mutation target not found in $1 (update the gate, disclose it)"; }
import re, sys
f, pat, rep = sys.argv[1:]
s = open(f).read(); t, n = re.subn(pat, rep, s, count=1)
if n == 0: sys.exit(1)
open(f, "w").write(t)
PY
  if (cd "$fe" && npx vitest run src/tests/landing-figures.test.ts >/dev/null 2>&1); then
    mv "$f.aa3b-orig" "$f"; fail "F54: a literal count in $1 did not fail landing-figures.test.ts"; fi
  mv "$f.aa3b-orig" "$f"
}
mutate "$fe/src/components/ValleSigue.astro" 'n: totalCitas' 'n: 230'
mutate "$fe/src/pages/es/index.astro" 'totalCitas=\{[^}]+\}' 'totalCitas={230}'
mutate "$fe/src/pages/en/index.astro" 'totalCitas=\{[^}]+\}' 'totalCitas={230}'
echo "F54 mutation: literal counts in ValleSigue, /es/ and /en/ each fail the fixture test"

# 4. Static scope.
git diff --quiet "$start" -- ttod.yml proposals services/backend || fail "AA3b touched ttod.yml, proposals or the backend"
inl_before=$(git grep -c 'is:inline' "$start" -- "$fe/src" | awk -F: '{s+=$NF} END {print s+0}')
inl_now=$(git grep -c 'is:inline' -- "$fe/src" | awk -F: '{s+=$NF} END {print s+0}')
[ "$inl_now" -le "$inl_before" ] || fail "is:inline scripts grew $inl_before → $inl_now (AA1 CSP backlog)"
grep -q "searchParams.get('orden')" "$fe/src/components/wisdom/Bosque.astro" || fail "shipped key 'orden' no longer read"
grep -q "searchParams.get('p')" "$fe/src/components/wisdom/Bosque.astro" || fail "shipped key 'p' no longer read"
grep -q "'tag', 'node'" "$fe/src/components/graph/urlState.ts" || fail "shipped GraphIsland keys tag/node changed"
grep -Eq "get\('s'\)|\.s\b|'s'" "$fe/src/components/graph/CodigoGrafo.svelte" || fail "shipped CodigoGrafo key 's' not found"
test ! -e "$fe/src/pages/[locale]/graph/path.astro" || fail "/graph/path still a page (must be a 301)"
test -f "$pack/PHASE-AA3b-REPORT.md" || fail "missing PHASE-AA3b-REPORT.md"
git diff --check "$start" -- . ':(exclude)*.md' || fail "whitespace errors"

# 5. Live, isolated.
if [ "${AA3B_SKIP_LIVE:-0}" != "1" ]; then
  stack="$pack/scripts/isolated-stack.sh"; project=ttod_aa3bgate; port="${AA3B_PORT:-28280}"
  trap 'bash "$stack" down "$project"' EXIT
  bash "$stack" up "$project" "$port" >/dev/null
  base="http://127.0.0.1:$port"
  python3 - "$base" "$reg" <<'PY' || fail "live registry probe (see message above)"
import json, re, sys, unicodedata, urllib.request, urllib.error, urllib.parse, http.client
base, regf = sys.argv[1], sys.argv[2]
R = json.load(open(regf)); V = R["values"]
host = urllib.parse.urlsplit(base)
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
op = urllib.request.build_opener(NoRedirect)
def get(path, method="GET", data=None):
    req = urllib.request.Request(base + path, method=method, data=data)
    try: r = op.open(req, timeout=60); return r.status, dict(r.headers), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e: return e.code, dict(e.headers), e.read().decode("utf-8", "replace")
corpus = json.loads(urllib.request.urlopen(base + "/api/v1/wisdom/sample", timeout=60).read())
graph = json.loads(urllib.request.urlopen(base + "/api/v1/graph", timeout=60).read())
fold = lambda s: "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()
twins = {}
for e in graph["edges"]:
    if e.get("rel") == "translation_of": twins[e["source"]] = e["target"]; twins[e["target"]] = e["source"]
errs = []
def check(ok, msg):
    if not ok: errs.append(msg)
ids_of = lambda html: re.findall(r'\sid="([^"]+)"', html)
loc_path = lambda h: (lambda u: u.path + (("?" + u.query) if u.query else ""))(urllib.parse.urlsplit(urllib.parse.urljoin(base + "/", h.get("Location") or h.get("location") or "")))
structural = {}
for L in ("en", "es"):
    other = "es" if L == "en" else "en"
    E = [e for e in corpus if e["lang"] == L]; qids = {e["id"] for e in E}
    secs = sorted({e["section"] for e in E})
    vals = {"l": L, "section": V["section"], "level": V["level"], "tag": V["tag"], "word": V["word"][L],
            "quote": sorted(qids)[0], "a": sorted(qids)[0], "b": sorted(qids)[1],
            "other-quote": sorted(e["id"] for e in corpus if e["lang"] == other and e["id"] not in qids)[0]}
    fill = lambda s: re.sub(r"\{([a-z-]+)\}", lambda m: vals.get(m.group(1), m.group(0)), s)
    for p in R["pages"]:
        if p.get("auth") or p.get("owner"): continue
        path = fill(p["path"]); st, h, html = get(path)
        check(st == p.get("status", 200), f"{path} → {st}")
        found = ids_of(html)
        dup = sorted({i for i in found if found.count(i) > 1})
        check(not dup, f"{path}: duplicate ids {dup[:5]}")
        for want in p.get("ids", []):
            if want == "{quote}":
                check(any(i in qids for i in found), f"{path}: no quote id rendered")
            elif "{section}" in want:
                for s in secs: check(found.count(want.replace("{section}", s)) == 1, f"{path}: #{want.replace('{section}', s)} not exactly once")
            else:
                check(found.count(fill(want)) == 1, f"{path}: #{fill(want)} not exactly once")
        structural.setdefault(p["path"], {})[L] = {i for i in found if i not in qids and not re.match(r"^volume-|^map-", i)}
        # every internal page href is slash-terminated (F8)
        for href in re.findall(r'href="(/[^"#?]*)', html):
            last = href.rsplit("/", 1)[-1]
            if href.startswith(("/api/", "/_astro/", "/visual-system/", "/project-docs/", "/data/")) or "." in last or href.endswith("/logout"): continue
            check(href.endswith("/"), f"{path}: slashless internal href {href}")
        # slashless form 301s to this page, query kept
        u = urllib.parse.urlsplit(path)
        if u.path != "/" and u.path.endswith("/"):
            slashless = u.path.rstrip("/") + (("?" + u.query) if u.query else "")
            st2, h2, _ = get(slashless)
            check(st2 == 301 and loc_path(h2) == path, f"{slashless} → {st2} {loc_path(h2)} (want 301 {path})")
    for x in R["redirects"]:
        a, b = fill(x["from"]), fill(x["to"]); st, h, _ = get(a)
        check(st == 301 and loc_path(h) == b, f"{a} → {st} {loc_path(h)} (want 301 {b})")
    for x in R["notFound"]:
        a = fill(x); st, _, _ = get(a); check(st == 404, f"{a} → {st} (want 404)")
    for x in R["exempt"]:
        a = fill(x); st, h, _ = get(a)
        check(not (st == 301 and loc_path(h) == urllib.parse.urlsplit(a).path + "/"), f"exempt {a} was slash-redirected")
    st, h, _ = get(f"/{L}/login", method="POST", data=b"email=x&password=y")
    check(st != 301, f"POST /{L}/login was 301-redirected (would drop the body)")
    st, h, _ = get(f"/{L}/library/")
    check(st != 302 or loc_path(h).startswith(f"/{L}/login/"), f"library sign-in redirect is slashless: {loc_path(h)}")
    # search (F49): rendered ids equal an independent fold over the corpus
    def expect(q=None, section=None, level=None, tag=None):
        out = []
        for e in E:
            hay = fold(" ".join([e["text"], e["teaches"], " ".join(e["tags"]), e["id"]]))
            if q and not all(w in hay for w in fold(q[:100]).split()): continue
            if section and e["section"] != section: continue
            if level and e["level"] != level: continue
            if tag and tag not in e["tags"]: continue
            out.append(e["id"])
        return set(out)
    for q in V["search"][L]:
        want = expect(q=q); st, _, html = get(f"/{L}/wisdom/?q=" + urllib.parse.quote(q))
        got = {i for i in ids_of(html) if i in qids}
        check(st == 200, f"?q={q} → {st}")
        if len(want) <= 20: check(got == want, f"?q={q}: rendered {sorted(got)[:6]} ≠ expected {sorted(want)[:6]}")
        else: check(got <= want and len(got) == 20 and str(len(want)) in html, f"?q={q}: page 1 not 20 of {len(want)}")
    st, _, html = get(f"/{L}/wisdom/?q=" + "x" * 300); check(st == 200, f"long q → {st}")
    st, _, html = get(f"/{L}/wisdom/?q=zzqqxxnomatch")
    check(st == 200 and not {i for i in ids_of(html) if i in qids} and f"/{L}/wisdom/sections/" in html, "no-match search: not an empty state with the section index")
    want = expect(section=V["section"], level=V["level"]); st, _, html = get(f"/{L}/wisdom/?section={V['section']}&level={V['level']}")
    got = {i for i in ids_of(html) if i in qids}
    check(got == want if len(want) <= 20 else got <= want, f"combined filter: {sorted(got)[:5]} vs {sorted(want)[:5]}")
    # language switch (F57): quote pages point at the translation twin, both directions
    pairs = [(q, twins[q]) for q in sorted(qids) if q in twins][:8]
    check(len(pairs) >= 8, f"{L}: fewer than 8 twins in /api/v1/graph")
    for q, t in pairs:
        st, _, html = get(f"/{L}/wisdom/{q}/")
        sw = re.search(r'class="ttod-lang-switch"[^>]*href="([^"]+)"|href="([^"]+)"[^>]*class="ttod-lang-switch"', html)
        href = sw and (sw.group(1) or sw.group(2))
        check(href == f"/{other}/wisdom/{t}/", f"/{L}/wisdom/{q}/ switch → {href} (want /{other}/wisdom/{t}/)")
    # graph IA (F52): the header link, the islands, nothing still pointing at /graph/path
    st, _, html = get(f"/{L}/")
    check(f'href="/{L}/graph/"' in html and "/graph/path" not in html, f"/{L}/: header/doors not on /{L}/graph/")
    for path, comp in ((f"/{L}/graph/", "SenderoAforismos"), (f"/{L}/graph/plano/", "GraphIsland"), (f"/{L}/graph/code/", "CodigoGrafo")):
        st, _, html = get(path); check(st == 200 and comp in html, f"{path}: {st}, island {comp} {'present' if comp in html else 'missing'}")
for path, by in structural.items():
    if len(by) == 2: check(by["en"] == by["es"], f"{path}: en/es structural ids differ: {sorted(by['en'] ^ by['es'])[:8]}")
if errs: print("\n".join(errs[:40])); print(f"({len(errs)} failures)"); sys.exit(1)
print("live registry probe: statuses, 301 Locations, ids, en/es parity, slash hrefs, search = corpus fold, twins, graph IA")
PY
  FE_PKG="$repo_root/$fe/package.json" node "$pack/scripts/aa3b-browser-check.mjs" "$base" "$pack/baselines/aa1-2026-11-10/browser-smoke-after.json" \
    || fail "browser checks (see messages above)"
  if [ "${AA3B_SKIP_UX:-0}" != "1" ]; then
    ux="$(mktemp -d)/ux"
    for v in /es/ /es/wisdom/ /es/graph/ /es/graph/plano/; do curl -fs -o /dev/null "$base$v"; curl -fs -o /dev/null "$base$v"; done
    FE_PKG="$repo_root/$fe/package.json" VIEWS="/es/ /es/wisdom/ /es/graph/ /es/graph/plano/" \
      bash "$pack/baselines/aa0-2026-11-10/baseline.sh" "$base" "$ux" >/dev/null || fail "baseline.sh failed"
    python3 - "$pack/baselines/aa0-2026-11-10/ux-baseline.json" "$ux/ux-baseline.json" <<'PY' || fail "AA0 UX regression rule"
import json, sys
a = {v["path"]: v for v in json.load(open(sys.argv[1]))["views"]}
b = {v["path"]: v for v in json.load(open(sys.argv[2]))["views"]}
pairs = {"/es/": "/es/", "/es/wisdom/": "/es/wisdom/", "/es/graph/": "/es/graph/path"}
bad = []
for new, old in pairs.items():
    n, o = b[new], a[old]
    if n["lighthouse_a11y"] < o["lighthouse_a11y"]: bad.append(f"{new}: a11y {n['lighthouse_a11y']} < {o['lighthouse_a11y']}")
    extra = set(n["a11y_failing_audits"]) - set(o["a11y_failing_audits"])
    if extra: bad.append(f"{new}: new failing a11y audits {sorted(extra)}")
    if n["cls"] > min(0.1, o["cls"] + 0.02): bad.append(f"{new}: CLS {n['cls']} > {min(0.1, o['cls'] + 0.02)}")
    if n["lcp_ms"] > o["lcp_ms"] * 1.2: bad.append(f"{new}: LCP {n['lcp_ms']} > {round(o['lcp_ms'] * 1.2)}")
    print(f"{new:16} a11y {n['lighthouse_a11y']} CLS {n['cls']:.4f} LCP {n['lcp_ms']} (AA0 {old}: {o['lighthouse_a11y']} / {o['cls']:.4f} / {o['lcp_ms']})")
p = b["/es/graph/plano/"]; print(f"/es/graph/plano/ (new baseline) a11y {p['lighthouse_a11y']} CLS {p['cls']:.4f} LCP {p['lcp_ms']}")
if bad: print("\n".join(bad)); sys.exit(1)
PY
  fi
  echo "live (isolated $project): registry probe, browser checks${AA3B_SKIP_UX:+ (UX skipped)}, AA0 UX rule"
fi

echo "AA3b exit gate passed: slash policy, wisdom ids/search/filters, landing chapters, graph IA, language switch, F54 guard."
