#!/usr/bin/env bash
# AA4 exit gate (F14, F15, F41–F44 · A12, A13, A27, A28), made runnable. Written by the planner before
# the phase code (2026-11-12). Any later amendment is disclosed in PHASE-AA4-REPORT.md.
#
# Decisions this gate encodes (the report records them, with the reasons):
# - D7 (a), owner: classroom hosts are noindex. Mechanism: `X-Robots-Tag: noindex` in Caddy's (seguridad)
#   snippet, so every response carries it, errors Caddy generates itself included. robots.txt exists,
#   has no `Disallow` and no `Sitemap` (no sitemap while noindex; a crawler that may not fetch a page
#   never reads its noindex).
# - Page level, independent of the host header (if indexing is ever reopened these stay out): a registry
#   row with `"index": false` or `"auth": true`, `?untranslated=`, and any non-200 page carry
#   `<meta name="robots" content="noindex">` and no canonical and no hreflang.
# - Every indexable page: one absolute canonical = its path (query dropped; `p` kept from 2 up), og:url
#   = canonical, hreflang en + es + x-default (= en), reciprocal. A quote's alternate is its
#   translation twin; a quote with no twin has no alternates.
# - Quote title and description come from the quote (text, teaches), never the id alone.
# - Manifest: `lang`, `dir`, maskable entries (the existing icons, measured inside the 40 % safe zone);
#   `start_url` stays `/`, and `/` now picks /es/ or /en/ from Accept-Language (F43), `Vary` set.
# - Offline honesty (F42): the public platform docs (en, es) name exactly the pages sw.js keeps offline.
# - No JSON-LD and no new inline scripts (AA1 CSP backlog).
#
# Frontend test-file contract (services/frontend, vitest):
#   src/lib/seo.test.ts                 canonical (query dropped, p kept), robots from the registry rows,
#                                       ?untranslated= noindex, alternates (none without a twin), quote
#                                       title/description trimmed at a word boundary, never the id alone
#   src/layouts/head-seo.test.ts        rendered Page: one canonical, en/es/x-default alternates, og:*,
#                                       noindex page → robots meta and no canonical/alternates; backend
#                                       down → noindex (amended after the cold review, F2)
#   src/lib/idioma.test.ts              preferred locale from Accept-Language (q values, regions, default en)
#   src/tests/locators-registry.test.ts the new rows render (login, register, propose)
#
# Live, isolated (scripts/isolated-stack.sh, project ttod_aa4gate): headers, robots.txt, head tags over
# the whole registry, quote twins, signed-in pages, a forged Host, root negotiation, manifest. Then the
# AA1, AA3b, AA3 and AA5 gates re-run unchanged (this phase edits the Caddyfile, Page.astro and the
# registry), with their CSP and UX lines kept in this log.
#
# AA4_SKIP_LIVE=1 / AA4_SKIP_GATES=1 are for quick local pre-checks only; the runner's verify runs all.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
pack="docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING"
fe="services/frontend"
reg="$fe/src/lib/locators.registry.json"
fail() { echo "AA4 GATE FAIL: $*" >&2; exit 1; }
start="$(git log --format=%H -1 --diff-filter=A -- "$pack/PHASES/AA4-seo-robots-and-meta.exit-gate.sh")"
[ -n "$start" ] || start="$(git merge-base HEAD origin/main)"
end="$(git log --format=%H -1 --grep='owner marks AA4 DONE')"; [ -n "$end" ] || end=HEAD

# 1. robots.txt and no sitemap (D7 (a)).
robots="$fe/public/robots.txt"
test -f "$robots" || fail "missing $robots (F14)"
grep -Eiq '^user-agent:[[:space:]]*\*' "$robots" || fail "robots.txt has no 'User-agent: *' group"
grep -Eiq '^disallow:[[:space:]]*[^[:space:]#]' "$robots" && fail "robots.txt disallows a path: a crawler that may not fetch a page never reads its noindex (D7 (a))"
grep -Eiq '^sitemap:' "$robots" && fail "robots.txt names a sitemap; no sitemap while noindex (D7 (a))"
ls "$fe"/public/sitemap* >/dev/null 2>&1 && fail "a sitemap file exists in public/ while the host is noindex"
grep -q '@astrojs/sitemap' "$fe/package.json" && fail "@astrojs/sitemap added while the host is noindex"

# 2. The noindex header lives in the (seguridad) snippet, which handle_errors also imports.
python3 - caddy/Caddyfile <<'PY' || fail "X-Robots-Tag noindex is not in the (seguridad) snippet (see message above)"
import re, sys
s = open(sys.argv[1]).read()
i = s.index("(seguridad) {"); depth = 0; j = i
for j in range(s.index("{", i), len(s)):
    depth += {"{": 1, "}": -1}.get(s[j], 0)
    if depth == 0: break
snippet = s[i:j]
if not re.search(r'^\s*X-Robots-Tag\s+"?noindex', snippet, re.M): print("no X-Robots-Tag noindex line inside (seguridad)"); sys.exit(1)
if s.count("import seguridad") < 2: print("(seguridad) is no longer imported by both the site and handle_errors"); sys.exit(1)
PY
image="$(awk '/reverse-proxy:/{f=1} f && /image:/{print $2; exit}' docker-compose.yml)"
docker run --rm -v "$PWD/caddy/Caddyfile:/etc/caddy/Caddyfile:ro" "$image" \
  caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null 2>&1 || fail "caddy validate failed for $image"

# 3. The registry decides which pages stay out (AA3b cold review: the five unregistered pages).
python3 - "$reg" <<'PY' || fail "registry rows or index flags (see message above)"
import json, sys
r = json.load(open(sys.argv[1])); pages = {p["path"]: p for p in r["pages"]}
NEW = ["/{l}/login/", "/{l}/register/", "/{l}/wisdom/propose/", "/{l}/quote/", "/{l}/account/reviewer/"]
NOINDEX = ["/{l}/library/", "/{l}/account/", "/{l}/account/reviewer/", "/{l}/wisdom/propose/", "/{l}/quote/"]
INDEX = ["/{l}/", "/{l}/wisdom/", "/{l}/wisdom/{quote}/", "/{l}/login/", "/{l}/register/", "/{l}/graph/", "/{l}/docs/"]
bad = [f"no row {p}" for p in NEW if p not in pages]
out = lambda p: pages[p].get("index") is False or pages[p].get("auth") is True
bad += [f"{p} must be noindex (index:false or auth:true)" for p in NOINDEX if p in pages and not out(p)]
bad += [f"{p} must stay indexable" for p in INDEX if p in pages and out(p)]
if bad: print("\n".join(bad)); sys.exit(1)
print(f"registry: {len(pages)} pages, noindex rows: {sorted(p for p in pages if out(p))}")
PY

# 4. Manifest (F43, F44) and offline honesty (F42).
python3 - "$fe/public" <<'PY' || fail "manifest (see message above)"
import json, math, struct, sys, zlib
pub = sys.argv[1]; m = json.load(open(f"{pub}/site.webmanifest")); bad = []
if m.get("lang") not in ("en", "es"): bad.append("manifest lang missing")
if m.get("dir") != "ltr": bad.append("manifest dir missing")
if m.get("start_url") != "/" or m.get("id") != "/" or m.get("scope") != "/": bad.append("id/start_url/scope must stay / (root picks the locale)")
mask = [i for i in m["icons"] if "maskable" in i.get("purpose", "").split()]
if {i.get("sizes") for i in mask} < {"192x192", "512x512"}: bad.append("no maskable 192 and 512 icons")
if not any("any" in i.get("purpose", "any").split() for i in m["icons"]): bad.append("no purpose any icon left")
def png(path):  # 8-bit RGB/RGBA, non-interlaced: enough for this repo's icons
    b = open(path, "rb").read(); i = 8; idat = b""
    while i < len(b):
        n, = struct.unpack(">I", b[i:i+4]); t = b[i+4:i+8]; d = b[i+8:i+8+n]; i += 12 + n
        if t == b"IHDR": w, h, bd, ct, _, _, il = struct.unpack(">IIBBBBB", d)
        elif t == b"IDAT": idat += d
    if bd != 8 or ct not in (2, 6) or il: raise ValueError(f"{path}: unsupported PNG layout")
    bpp = 3 if ct == 2 else 4; raw = zlib.decompress(idat); stride = w * bpp; rows = []; prev = bytearray(stride); p = 0
    for _ in range(h):
        f = raw[p]; line = bytearray(raw[p+1:p+1+stride]); p += 1 + stride
        for x in range(stride):
            a = line[x-bpp] if x >= bpp else 0; up = prev[x]; c = prev[x-bpp] if x >= bpp else 0
            if f == 1: line[x] = (line[x] + a) & 255
            elif f == 2: line[x] = (line[x] + up) & 255
            elif f == 3: line[x] = (line[x] + (a + up) // 2) & 255
            elif f == 4:
                pa, pb, pc = abs(up - c), abs(a - c), abs(a + up - 2 * c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else up if pb <= pc else c)) & 255
        rows.append(line); prev = line
    return w, h, bpp, rows
for i in mask:
    w, h, bpp, rows = png(f"{pub}/{i['src'].lstrip('/')}")
    if f"{w}x{h}" != i["sizes"]: bad.append(f"{i['src']}: {w}x{h}, declared {i['sizes']}")
    if bpp == 4 and any(rows[y][3 + 4 * x] < 255 for y in range(h) for x in range(w)): bad.append(f"{i['src']}: transparent pixels (a maskable icon fills its square)")
    bg = tuple(rows[0][0:3]); r = 0.0
    for y in range(h):
        for x in range(w):
            px = tuple(rows[y][bpp * x:bpp * x + 3])
            if max(abs(a - b) for a, b in zip(px, bg)) > 24: r = max(r, math.hypot(x + .5 - w / 2, y + .5 - h / 2))
    if r / w > 0.40: bad.append(f"{i['src']}: glyph reaches {r / w:.2f} of the width, outside the 0.40 maskable safe zone")
    else: print(f"maskable {i['src']}: glyph radius {r / w:.3f} of the width (safe zone 0.40)")
if bad: print("\n".join(bad)); sys.exit(1)
PY
python3 - "$fe/public/sw.js" docs/public/platform/index.md docs/public/es/platform/index.md <<'PY' || fail "offline claims do not match sw.js (F42, see message above)"
import re, sys
sw = open(sys.argv[1]).read()
pages = re.findall(r"'([^']+)'", re.search(r"OFFLINE_PAGES\s*=\s*\[([^\]]*)\]", sw).group(1))
bad = []
for doc, word in ((sys.argv[2], "offline"), (sys.argv[3], "sin conexión")):
    t = open(doc).read()
    for p in pages:
        if p not in t: bad.append(f"{doc} does not name the offline page {p}")
    if word not in t.lower(): bad.append(f"{doc} does not say '{word}'")
if bad: print("\n".join(bad)); sys.exit(1)
print(f"offline pages in sw.js and both platform docs: {pages}")
PY
if ! git diff --quiet "$start" -- "$fe/public/sw.js"; then
  [ "$(git show "$start:$fe/public/sw.js" | grep -o 'CACHE_PREFIX}v[0-9]*')" != "$(grep -o 'CACHE_PREFIX}v[0-9]*' "$fe/public/sw.js")" ] \
    || fail "sw.js changed without a cache version bump (next is v9)"
fi

# 5. Tests, typecheck, PWA guard.
tests=(src/lib/seo.test.ts src/layouts/head-seo.test.ts src/lib/idioma.test.ts src/tests/locators-registry.test.ts)
for t in "${tests[@]}"; do test -f "$fe/$t" || fail "missing $fe/$t (test-file contract above)"; done
grep -q 'Accept-Language\|accept-language' "$fe/src/lib/idioma.test.ts" || fail "idioma.test.ts does not cover Accept-Language"
[ -d "$fe/node_modules" ] || (cd "$fe" && npm ci --no-audit --no-fund >/dev/null 2>&1) || fail "npm ci failed"
(cd "$fe" && npx vitest run "${tests[@]}" >"${TMPDIR:-/tmp}"/aa4-contract.log 2>&1) || { tail -30 "${TMPDIR:-/tmp}"/aa4-contract.log; fail "contract tests red"; }
echo "contract tests: $(grep -Eo 'Tests +[0-9]+ passed' "${TMPDIR:-/tmp}"/aa4-contract.log | tail -1)"
(cd "$fe" && npx vitest run >"${TMPDIR:-/tmp}"/aa4-suite.log 2>&1) || { tail -30 "${TMPDIR:-/tmp}"/aa4-suite.log; fail "frontend suite red"; }
echo "frontend suite: $(grep -Eo 'Tests +[0-9]+ passed' "${TMPDIR:-/tmp}"/aa4-suite.log | tail -1)"
(cd "$fe" && npm run check >"${TMPDIR:-/tmp}"/aa4-check.log 2>&1) || { tail -30 "${TMPDIR:-/tmp}"/aa4-check.log; fail "astro check red"; }
(cd "$fe" && npm run pwa:guard >"${TMPDIR:-/tmp}"/aa4-pwa.log 2>&1) || { tail -20 "${TMPDIR:-/tmp}"/aa4-pwa.log; fail "PWA guard red"; }
echo "frontend: suite, check, PWA guard green"

# 6. Static scope and the CSP backlog.
git diff --quiet "$start" "$end" -- ttod.yml proposals services/backend || fail "AA4 touched ttod.yml, proposals or the backend"
inl_before=$(git grep -c 'is:inline' "$start" -- "$fe/src" | awk -F: '{s+=$NF} END {print s+0}')
inl_now=$(git grep -c 'is:inline' -- "$fe/src" | awk -F: '{s+=$NF} END {print s+0}')
[ "$inl_now" -le "$inl_before" ] || fail "is:inline scripts grew $inl_before → $inl_now (AA1 CSP backlog)"
scr_before=$(git show "$start:$fe/src/layouts/Page.astro" | grep -c '<script')
scr_now=$(grep -c '<script' "$fe/src/layouts/Page.astro")
[ "$scr_now" -le "$scr_before" ] || fail "Page.astro gained a <script> ($scr_before → $scr_now)"
git grep -q 'application/ld+json' -- "$fe/src" && fail "JSON-LD is an inline script (CSP report-only backlog); not in AA4"
for g in AA1-caddy-security-headers AA3b-locators-wisdom-and-graph-ia AA3-nav-a11y-and-url-hygiene AA5-container-and-deploy-ops; do
  git diff --quiet "$start" -- "$pack/PHASES/$g.exit-gate.sh" || fail "$g exit gate was edited on the AA4 branch"
done
git diff --quiet "$start" -- "$pack/scripts/aa3b-browser-check.mjs" "$pack/scripts/aa3-browser-check.mjs" \
  || fail "an earlier browser check was edited on the AA4 branch"
test -f "$pack/PHASE-AA4-REPORT.md" || fail "missing PHASE-AA4-REPORT.md"
git diff --check "$start" -- . ':(exclude)*.md' || fail "whitespace errors"

# 7. Live, isolated.
if [ "${AA4_SKIP_LIVE:-0}" != "1" ]; then
  stack="$pack/scripts/isolated-stack.sh"; project=ttod_aa4gate; port="${AA4_PORT:-28880}"
  trap 'bash "$stack" down "$project"' EXIT
  bash "$stack" up "$project" "$port" >/dev/null
  base="http://127.0.0.1:$port"
  python3 - "$base" "$port" "$reg" "$fe/public/robots.txt" <<'PY' || fail "live checks (see message above)"
import http.cookiejar, json, re, sys, urllib.error, urllib.parse, urllib.request, socket
from html.parser import HTMLParser
base, port, regf, robotsf = sys.argv[1:5]
R = json.load(open(regf)); V = R["values"]
errs = []
def check(ok, msg):
    if not ok: errs.append(msg)
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k): return None
def client():
    return urllib.request.build_opener(NoRedirect, urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
anon = client()
def get(path, op=anon, data=None, json_body=None, headers=None):
    h = dict(headers or {}); body = None
    if json_body is not None: body = json.dumps(json_body).encode(); h["content-type"] = "application/json"
    elif data is not None: body = urllib.parse.urlencode(data).encode(); h["content-type"] = "application/x-www-form-urlencoded"; h.setdefault("Origin", base)
    r = urllib.request.Request(base + path, data=body, headers=h)
    try: resp = op.open(r, timeout=60); return resp.status, resp.headers, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e: return e.code, e.headers, e.read().decode("utf-8", "replace")
def raw(request_bytes):  # what a browser or curl --path-as-is would send, Host included
    s = socket.create_connection(("127.0.0.1", int(port)), timeout=30); s.sendall(request_bytes); out = b""
    while True:
        c = s.recv(65536)
        if not c: break
        out += c
    s.close(); head, _, body = out.partition(b"\r\n\r\n")
    return head.decode("latin-1").lower(), body.decode("utf-8", "replace")
class Head(HTMLParser):
    def __init__(self):
        super().__init__(); self.links = []; self.metas = []; self.title = ""; self._t = False
    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "link": self.links.append(a)
        elif tag == "meta": self.metas.append(a)
        elif tag == "title": self._t = True
    def handle_endtag(self, tag):
        if tag == "title": self._t = False
    def handle_data(self, d):
        if self._t: self.title += d
def head(html):
    p = Head(); p.feed(html.split("</head>", 1)[0]); return p
canon = lambda h: [l.get("href") for l in h.links if l.get("rel") == "canonical"]
alts = lambda h: {l.get("hreflang"): l.get("href") for l in h.links if l.get("rel") == "alternate" and l.get("hreflang")}
altcount = lambda h: sum(1 for l in h.links if l.get("rel") == "alternate" and l.get("hreflang"))
meta = lambda h, k: [m.get("content") for m in h.metas if m.get("property") == k or m.get("name") == k]
robots_noindex = lambda h: any("noindex" in (c or "") for c in meta(h, "robots"))

# Headers: every response, Caddy's own included.
st, hd, body = get("/robots.txt")
check(st == 200 and hd.get("content-type", "").startswith("text/plain"), f"/robots.txt → {st} {hd.get('content-type')}")
check(body.strip() == open(robotsf).read().strip(), "/robots.txt served differs from public/robots.txt")
check(get("/sitemap.xml")[0] == 404, "/sitemap.xml exists while noindex")
for path in ("/es/", "/en/wisdom/", "/robots.txt", "/site.webmanifest", "/sw.js", "/api/v1/wisdom/sample", "/health",
             "/es/wisdom/zz-999/", "/project-docs/__aa4-missing"):
    st, hd, _ = get(path)
    check("noindex" in (hd.get("x-robots-tag") or ""), f"{path} ({st}) lacks X-Robots-Tag noindex")
for req, why in ((b"GET //evil.example/x HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n", "Caddy 404 (@rutadoble)"),
                 (b"GET /es/ HTTP/1.1\r\nHost: bad_host.example\r\nConnection: close\r\n\r\n", "Caddy 400 (@hostmalo; Go itself refuses a Host with a space, so an underscore)")):
    h, _ = raw(req); check("x-robots-tag: noindex" in h, f"{why} lacks X-Robots-Tag noindex: {h.splitlines()[0] if h else 'no answer'}")

# Head tags over the registry (anonymous rows; signed-in rows below).
corpus = json.loads(get("/api/v1/wisdom/sample")[2]); graph = json.loads(get("/api/v1/graph")[2])
twins = {}
for e in graph["edges"]:
    if e.get("rel") == "translation_of": twins[e["source"]] = e["target"]; twins[e["target"]] = e["source"]
abs_ = lambda p: base + p
def common(path, h, lang):
    check(h.title.strip() != "", f"{path}: empty <title>")
    check(len(meta(h, "description")) == 1 and meta(h, "description")[0], f"{path}: not exactly one meta description")
    for k in ("og:title", "og:description", "og:site_name", "og:type", "og:locale"):
        check(len(meta(h, k)) == 1 and meta(h, k)[0], f"{path}: not exactly one {k}")
    check(meta(h, "og:locale")[:1] == [{"en": "en_US", "es": "es_ES"}[lang]], f"{path}: og:locale {meta(h, 'og:locale')}")
def indexable(path, h, want_canon, want_alts):
    check(not robots_noindex(h), f"{path}: robots noindex on an indexable page")
    check(canon(h) == [abs_(want_canon)], f"{path}: canonical {canon(h)} (want [{abs_(want_canon)}])")
    check(meta(h, "og:url") == [abs_(want_canon)], f"{path}: og:url {meta(h, 'og:url')}")
    want = {k: abs_(v) for k, v in want_alts.items()}
    check(alts(h) == want and altcount(h) == len(want), f"{path}: alternates {alts(h)} (want {want})")
def noindex(path, h):
    check(robots_noindex(h), f"{path}: no robots noindex")
    check(canon(h) == [] and altcount(h) == 0, f"{path}: noindex page carries canonical {canon(h)} or alternates {alts(h)}")
for L in ("en", "es"):
    O = "es" if L == "en" else "en"
    E = [e for e in corpus if e["lang"] == L]; qids = sorted(e["id"] for e in E)
    vals = {"l": L, "section": V["section"], "level": V["level"], "tag": V["tag"], "word": V["word"][L], "quote": next(q for q in qids if q in twins)}
    fill = lambda s: re.sub(r"\{([a-z-]+)\}", lambda m: vals.get(m.group(1), m.group(0)), s)
    for p in R["pages"]:
        if p.get("auth") or p.get("owner"): continue
        path = fill(p["path"]); st, _, html = get(path); h = head(html)
        if st != 200: check(p["path"] == "/{l}/quote/" and st == 503, f"{path} → {st}"); continue
        common(path, h, L)
        clean = urllib.parse.urlsplit(path).path
        if p.get("index") is False: noindex(path, h); continue
        if p["path"] == "/{l}/wisdom/{quote}/":
            t = twins[vals["quote"]]; want = {L: clean, O: f"/{O}/wisdom/{t}/"}; want["x-default"] = want["en"]
        else:
            other = f"/{O}" + clean[3:]; want = {L: clean, O: other}; want["x-default"] = want["en"]
        indexable(path, h, clean, want)
    # Query variants (AA3b carry): canonical drops the query; ?untranslated= is noindex.
    for path, c in ((f"/{L}/wisdom/?q={V['word'][L]}", f"/{L}/wisdom/"),
                    (f"/{L}/wisdom/?section={V['section']}&level={V['level']}", f"/{L}/wisdom/"),
                    (f"/{L}/graph/?from={qids[0]}&to={qids[1]}", f"/{L}/graph/"),
                    (f"/{L}/graph/plano/?tag={V['tag']}", f"/{L}/graph/plano/"),
                    (f"/{L}/graph/code/?s=services/backend/app/main.py", f"/{L}/graph/code/"),
                    (f"/{L}/login/?next=%2F{L}%2Fwisdom%2F", f"/{L}/login/")):
        st, _, html = get(path); h = head(html)
        check(st == 200 and canon(h) == [abs_(c)], f"{path} → {st}, canonical {canon(h)} (want {abs_(c)})")
    # Amended after the cold review (F1/F9, a strengthening): ?p= counts only on a facet list, clamped to the pages
    # it really has; search, filters and the home page drop it.
    for path, c in ((f"/{L}/wisdom/?q={V['word'][L]}&p=2", f"/{L}/wisdom/"), (f"/{L}/?p=7", f"/{L}/")):
        st, _, html = get(path); check(canon(head(html)) == [abs_(c)], f"{path}: canonical {canon(head(html))} (want {abs_(c)})")
    n = sum(1 for e in E if V["tag"] in e["tags"]); last = max(1, -(-n // 20))
    for p, want in (("2", min(2, last)), ("999", last), ("1e1", 1)):
        path = f"/{L}/wisdom/tags/{V['tag']}/?p={p}"; c = f"/{L}/wisdom/tags/{V['tag']}/" + (f"?p={want}" if want >= 2 else "")
        st, _, html = get(path); check(canon(head(html)) == [abs_(c)], f"{path} ({n} quotes, {last} pages): canonical {canon(head(html))} (want {abs_(c)})")
    st, _, html = get(f"/{L}/wisdom/?untranslated={qids[0]}"); noindex(f"/{L}/wisdom/?untranslated=", head(html))
    st, _, html = get(f"/{L}/wisdom/zz-999/"); check(st == 404, f"/{L}/wisdom/zz-999/ → {st}"); noindex(f"/{L}/wisdom/zz-999/ (404)", head(html))
    st, _, html = get(f"/{L}/wisdom/sections/zz-none/"); noindex(f"/{L}/wisdom/sections/zz-none/ ({st})", head(html))
    # Quotes (F41): title and description from the quote; twin alternates, reciprocal; no twin, no alternates.
    with_twin = [q for q in qids if q in twins][:8]; without = [q for q in qids if q not in twins][:2]
    check(len(with_twin) == 8, f"{L}: fewer than 8 twins")
    norm = lambda s: re.sub(r"\s+", " ", s).strip()
    for q in with_twin + without:
        e = next(x for x in E if x["id"] == q); st, _, html = get(f"/{L}/wisdom/{q}/"); h = head(html)
        words = " ".join(norm(e["text"]).split()[:3])
        check(words in norm(h.title), f"/{L}/wisdom/{q}/: title {h.title!r} lacks the quote's first words {words!r}")
        check(not re.fullmatch(rf"\s*{re.escape(q)}\b.*", h.title) , f"/{L}/wisdom/{q}/: title starts with the id: {h.title!r}")
        d = norm((meta(h, "description") or [""])[0]); src = norm(e.get("teaches") or e["text"])
        check(d[:30] == src[:30], f"/{L}/wisdom/{q}/: description {d[:40]!r} does not start like teaches {src[:40]!r}")
        check(meta(h, "og:type") == ["article"], f"/{L}/wisdom/{q}/: og:type {meta(h, 'og:type')}")
        if q in twins:
            t = twins[q]; a = alts(h)
            check(a.get(O) == abs_(f"/{O}/wisdom/{t}/"), f"/{L}/wisdom/{q}/: {O} alternate {a.get(O)} (want twin {t})")
            back = alts(head(get(f"/{O}/wisdom/{t}/")[2]))
            check(back.get(L) == abs_(f"/{L}/wisdom/{q}/"), f"/{O}/wisdom/{t}/ does not point back to {q}: {back.get(L)}")
        else:
            check(altcount(h) == 0 and canon(h) == [abs_(f"/{L}/wisdom/{q}/")], f"/{L}/wisdom/{q}/ (no twin): alternates {alts(h)}, canonical {canon(h)}")

# Signed in: account, library, reviewer are noindex with no canonical.
email, pw = f"aa4-{port}@example.test", "aa4-gate-password-1"
st, _, _ = get("/api/v1/auth/register", json_body={"email": email, "password": pw}); check(st == 201, f"register → {st}")
me = client(); st, _, _ = get("/es/login/", op=me, data={"email": email, "password": pw}); check(st == 303, f"form login → {st}")
for L in ("en", "es"):
    for path in (f"/{L}/account/", f"/{L}/library/", f"/{L}/account/reviewer/"):
        st, _, html = get(path, op=me); h = head(html)
        check(st in (200, 403), f"{path} signed in → {st}"); noindex(f"{path} (signed in, {st})", h)
    st, hd, _ = get(f"/{L}/library/"); check(st == 302 and "/login/" in (hd.get("location") or ""), f"anonymous /{L}/library/ → {st}")

# A forged Host must not reach canonical, og:url or hreflang.
# Amended during AA4 (a strengthening, PHASE-AA4-REPORT §6): with a Host Astro does not trust (a forged one,
# or a classroom IP nobody added to TTOD_ALLOWED_HOSTS) its URL falls back to the container's own
# http://localhost:4321. Neither that nor the forged host may appear; canonical and alternates go
# root-relative and og:url/og:image are left out.
for host in ("evil.example", "192.168.77.7:8080"):
    for path in ("/es/", "/en/wisdom/"):
        h, body = raw(f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode())
        tags = head(body); headtxt = body.split("</head>", 1)[0]
        check(host not in headtxt and "localhost:4321" not in headtxt, f"{path} with Host {host}: forged or internal address in the head")
        check(canon(tags) == [path] and meta(tags, "og:url") == [] and meta(tags, "og:image") == [], f"{path} with Host {host}: canonical {canon(tags)}, og:url {meta(tags, 'og:url')}")

# Root picks the locale (F43).
for al, want in (("es-ES,es;q=0.9,en;q=0.5", "/es/"), ("es", "/es/"), ("en-US,en;q=0.9", "/en/"), ("fr-FR,fr", "/en/"),
                 (None, "/en/"), ("es;q=0.1, en;q=0.9", "/en/"), ("fr, es;q=0.5", "/es/")):
    st, hd, _ = get("/", headers={"Accept-Language": al} if al else {})
    loc = urllib.parse.urlsplit(urllib.parse.urljoin(base + "/", hd.get("location") or "")).path
    check(st in (302, 307) and loc == want, f"/ with Accept-Language {al!r} → {st} {loc} (want {want})")
    check("accept-language" in (hd.get("vary") or "").lower(), f"/ redirect lacks Vary: Accept-Language")

# Manifest as served.
st, hd, body = get("/site.webmanifest"); m = json.loads(body)
for i in m["icons"]:
    s, h2, _ = get("/" + i["src"].lstrip("/")); check(s == 200 and (h2.get("content-type") or "").startswith(i["type"]), f"icon {i['src']} → {s} {h2.get('content-type')}")
check(m.get("lang") and any("maskable" in i.get("purpose", "") for i in m["icons"]), "served manifest lacks lang or maskable icons")
if errs: print("\n".join(errs[:50])); print(f"({len(errs)} failures)"); sys.exit(1)
print("live: X-Robots-Tag on every response (Caddy errors too), robots.txt, registry head tags, query canonicals, quote meta + twins, signed-in noindex, forged Host, root locale, manifest")
PY
  bash "$stack" down "$project"; trap - EXIT
fi

# 8. Earlier gates, unchanged (checked in step 6), re-run.
if [ "${AA4_SKIP_GATES:-0}" != "1" ]; then
  for g in AA1-caddy-security-headers AA3b-locators-wisdom-and-graph-ia AA3-nav-a11y-and-url-hygiene AA5-container-and-deploy-ops; do
    echo "--- re-running $g"
    log="${TMPDIR:-/tmp}/aa4-$g.log"
    bash "$pack/PHASES/$g.exit-gate.sh" >"$log" 2>&1 || { tail -15 "$log"; fail "$g exit gate fails on the AA4 branch"; }
    grep -E '^csp |a11y [0-9]+ CLS|live|contract tests|frontend suite' "$log" || true
    tail -1 "$log"
  done
  gates_note="AA1/AA3b/AA3/AA5 gates re-run green"
else
  gates_note="earlier gates SKIPPED (AA4_SKIP_GATES=1, not a verify)"
fi
echo "AA4 exit gate passed: noindex on every response, robots.txt without Disallow, canonical/hreflang/og from the registry, quote meta, maskable manifest, offline docs honest; $gates_note."
