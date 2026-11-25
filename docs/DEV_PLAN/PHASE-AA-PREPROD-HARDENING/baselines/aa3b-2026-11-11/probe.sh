#!/usr/bin/env bash
# AA3b live curl probe: every row of services/frontend/src/lib/locators.registry.json, filled with real
# corpus ids, as plain curl status lines (the exit gate runs the stricter Python probe over the same file).
# Usage: probe.sh <base-url>   (run from the repo root, against scripts/isolated-stack.sh, not the instructor stack)
set -euo pipefail
base="${1:?usage: probe.sh <base-url>}"
python3 - "$base" services/frontend/src/lib/locators.registry.json <<'PY'
import json, re, subprocess, sys, urllib.request
base, reg = sys.argv[1], json.load(open(sys.argv[2]))
corpus = json.loads(urllib.request.urlopen(base + "/api/v1/wisdom/sample").read())
V = reg["values"]
def curl(path, method="GET"):
    out = subprocess.run(["curl", "-s", "-o", "/dev/null", "-X", method, "-w", "%{http_code} %{redirect_url}", base + path], capture_output=True, text=True).stdout
    return out.replace(base, "").rstrip()  # no redirect → curl leaves a trailing space
for L in ("es", "en"):
    other = "en" if L == "es" else "es"
    ids = sorted(e["id"] for e in corpus if e["lang"] == L)
    oth = sorted(e["id"] for e in corpus if e["lang"] == other and e["id"] not in set(ids))
    vals = {"l": L, "section": V["section"], "level": V["level"], "tag": V["tag"], "word": V["word"][L],
            "quote": ids[0], "a": ids[0], "b": ids[1], "other-quote": oth[0]}
    fill = lambda s: re.sub(r"\{([a-z-]+)\}", lambda m: vals.get(m.group(1), m.group(0)), s)
    print(f"## {L}")
    for p in reg["pages"]:
        tag = " (signed-in page: redirects to login)" if p.get("auth") else " (AA3 owns its ids)" if p.get("owner") else ""
        print(f"page      {fill(p['path']):58} {curl(fill(p['path']))}{tag}".rstrip())
    for r in reg["redirects"]:
        print(f"redirect  {fill(r['from']):58} {curl(fill(r['from']))}".rstrip())
    for n in reg["notFound"]:
        print(f"notfound  {fill(n):58} {curl(fill(n))}".rstrip())
    for x in reg["exempt"]:
        print(f"exempt    {fill(x):58} {curl(fill(x))}".rstrip())
    print(f"post      {'/' + L + '/login':58} {curl('/' + L + '/login', 'POST')}".rstrip())
PY
