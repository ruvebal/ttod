// AA7 screenshot strip: four views at 390 and 1440, for a before/after comparison.
// Usage: node strip.mjs <base-url> <out-dir>   (CHROME_PATH, FE_PKG as in baselines/aa0-2026-11-10/baseline.sh)
import { createRequire } from "node:module";
const [base, out] = process.argv.slice(2);
const { chromium } = createRequire(process.env.FE_PKG || `${process.env.HOME}/src/ttod/services/frontend/package.json`)("playwright");
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" });
for (const w of [390, 1440]) for (const [slug, path] of [["landing", "/es/"], ["wisdom", "/es/wisdom/"], ["graph", "/es/graph/"], ["quote", "/es/wisdom/wis-034/"]]) {
  const page = await browser.newPage({ viewport: { width: w, height: 900 } });
  await page.goto(base + path, { waitUntil: "networkidle" }); await page.waitForTimeout(1500);
  await page.screenshot({ path: `${out}/${slug}-${w}.png` }); await page.close();
}
await browser.close(); console.log("strip written");
