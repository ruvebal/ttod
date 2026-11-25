#!/usr/bin/env bash
# AA0 UX baseline: Lighthouse (mobile, 390 px) a11y + CLS + LCP on three views, and header
# screenshots at 390/768/1440 (F56). Later phases re-run this into their own folder and compare
# against ux-baseline.json here under the single "AA0 regression rule" in PHASE-AA0-REPORT.md §5.
# Run on Tanit only (LCP compares on the same host). Prerequisites: Google Chrome at CHROME_PATH,
# playwright installed in services/frontend (FE_PKG), npx with network access for lighthouse.
# Usage: baseline.sh <base-url> <out-dir>   (refuses to overwrite an existing ux-baseline.json)
set -euo pipefail
BASE="${1:?usage: baseline.sh <base-url> <out-dir>}"
OUT="${2:?usage: baseline.sh <base-url> <out-dir> (a new folder; the AA0 reference is never overwritten)}"
[ -e "$OUT/ux-baseline.json" ] && { echo "refusing to overwrite $OUT/ux-baseline.json" >&2; exit 1; }
export CHROME_PATH="${CHROME_PATH:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
FE_PKG="${FE_PKG:-$HOME/src/ttod/services/frontend/package.json}"   # where playwright is installed
LH="lighthouse@12.6.0"
mkdir -p "$OUT/lighthouse"

# VIEWS (space-separated) lets a later phase measure its own views; the default is the AA0 set.
read -r -a views <<< "${VIEWS:-/es/ /es/wisdom/ /es/graph/path}"
for v in "${views[@]}"; do
  slug="$(echo "$v" | tr '/' '-' | sed 's/^-//; s/-$//')"
  npx -y "$LH" "$BASE$v" --only-categories=accessibility,performance --form-factor=mobile \
    --screenEmulation.width=390 --screenEmulation.height=844 --screenEmulation.deviceScaleFactor=2 \
    --chrome-flags="--headless=new" --output=json --output-path="$OUT/lighthouse/$slug.json" --quiet
done

python3 - "$OUT" "$BASE" "${views[@]}" <<'PY'
import json, sys, datetime, platform
out, base, views = sys.argv[1], sys.argv[2], sys.argv[3:]
rows = []
for v in views:
    slug = v.strip("/").replace("/", "-")
    d = json.load(open(f"{out}/lighthouse/{slug}.json"))
    a = d["audits"]
    acc = d["categories"]["accessibility"]
    failing = [r["id"] for r in acc["auditRefs"]
               if r["weight"] > 0 and a[r["id"]]["score"] is not None and a[r["id"]]["score"] < 1]
    rows.append({
        "path": v,
        "lighthouse_a11y": round(acc["score"] * 100),
        "a11y_violations": len(failing),
        "a11y_failing_audits": failing,
        "performance": round(d["categories"]["performance"]["score"] * 100),
        "cls": round(a["cumulative-layout-shift"]["numericValue"], 4),
        "lcp_ms": round(a["largest-contentful-paint"]["numericValue"]),
        "tbt_ms": round(a["total-blocking-time"]["numericValue"]),
    })
doc = {
    "recorded": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "base": base,
    "tool": "lighthouse 12.6.0, mobile form factor, 390x844 @2x, simulated throttling",
    "host": platform.node(),
    "views": rows,
}
json.dump(doc, open(f"{out}/ux-baseline.json", "w"), indent=2, ensure_ascii=False)
import gzip, shutil, os
for v in views:
    slug = v.strip("/").replace("/", "-"); src = f"{out}/lighthouse/{slug}.json"
    with open(src, "rb") as fi, gzip.open(src + ".gz", "wb") as fo: shutil.copyfileobj(fi, fo)
    os.remove(src)
for r in rows:
    print(f'{r["path"]:16} a11y {r["lighthouse_a11y"]:3} ({r["a11y_violations"]} failing) '
          f'perf {r["performance"]:3} CLS {r["cls"]:.4f} LCP {r["lcp_ms"]} ms')
PY

node --input-type=module - "$BASE" "$OUT" "$FE_PKG" "${views[@]}" <<'JS'
import { createRequire } from "node:module";
const [base, out, pkg, ...paths] = process.argv.slice(2);
const { chromium } = createRequire(pkg)("playwright");
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH });
const views = paths.map((p) => [p.replace(/^\/|\/$/g, "").replace(/\//g, "-"), p]);
for (const w of [390, 768, 1440]) {
  const page = await browser.newPage({ viewport: { width: w, height: 900 }, deviceScaleFactor: 1 });
  for (const [slug, path] of views) {
    await page.goto(base + path, { waitUntil: "networkidle" });
    const header = page.locator("#ttod-site-header");
    if (await header.count()) await header.screenshot({ path: `${out}/header-${slug}-${w}.png` });
    if (w === 390) await page.screenshot({ path: `${out}/view-${slug}-390.png` });
  }
  await page.close();
}
await browser.close();
console.log("screenshots written");
JS
