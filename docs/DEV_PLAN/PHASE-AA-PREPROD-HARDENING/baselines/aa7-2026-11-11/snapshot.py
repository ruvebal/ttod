#!/usr/bin/env python3
"""AA7 snapshot: every docs page's heading ids (en, es) and the visible text of key views (header + main,
uncut; amended after the cold review, F7), as JSON.
Run before and after the upgrade against an isolated stack; diff the two files.
Usage: snapshot.py <base-url> <out.json>"""
import json, re, sys, urllib.request
base, out = sys.argv[1], sys.argv[2]
get = lambda p: urllib.request.urlopen(base + p, timeout=60).read().decode("utf-8", "replace")
snap = {"docs": {}, "text": {}}
for lang in ("en", "es"):
    index = get(f"/{lang}/docs/")
    for slug in sorted(set(re.findall(rf'href="(/{lang}/docs/[^"#?]+/)"', index))):
        html = get(slug)
        snap["docs"][slug] = re.findall(r'<h[1-6][^>]*\sid="([^"]+)"', html)
for path in ("/es/", "/es/wisdom/", "/es/graph/", "/es/wisdom/wis-034/", "/en/docs/"):
    html = get(path)
    parts = [m.group(0) for m in (re.search(r'<header[^>]*id="ttod-site-header"[\s\S]*?</header>', html),
                                  re.search(r"<main[\s\S]*?</main>", html)) if m]
    text = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", " ".join(parts) or html)
    text = re.sub(r"<[^>]+>", " ", text)
    snap["text"][path] = re.sub(r"\s+", " ", text).strip()
json.dump(snap, open(out, "w"), indent=1, ensure_ascii=False)
print(f"{len(snap['docs'])} docs pages, {sum(len(v) for v in snap['docs'].values())} heading ids, {len(snap['text'])} views")
