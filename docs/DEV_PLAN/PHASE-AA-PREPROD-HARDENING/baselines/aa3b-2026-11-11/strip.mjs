// AA3b screenshot strip (390 px): the five deep links PHASE-AA3b deliverable 9 names.
// Usage: node strip.mjs <base-url> <out-dir>   (CHROME_PATH, FE_PKG as in baselines/aa0-2026-11-10/baseline.sh)
import { createRequire } from "node:module";
const [base, out] = process.argv.slice(2);
const { chromium } = createRequire(process.env.FE_PKG || `${process.env.HOME}/src/ttod/services/frontend/package.json`)("playwright");
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" });
const page = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
const shot = async (name, path, wait = 2200) => {
  await page.goto(base + path, { waitUntil: "networkidle" }); await page.waitForTimeout(wait);
  await page.screenshot({ path: `${out}/${name}.png` });
  console.log(`${name}.png  ${new URL(page.url()).pathname}${new URL(page.url()).search}${new URL(page.url()).hash}`);
};
await shot("1-landing-map-architecture", "/es/#map-architecture");
await shot("2-wisdom-q-diseno", "/es/wisdom/?q=diseno");
await shot("3-wisdom-volume-architecture", "/es/wisdom/#volume-architecture");
await shot("4-graph-from-to", "/es/graph/?from=a11y-001&to=img-038", 4500);
await shot("5a-quote-wis-034", "/es/wisdom/wis-034/");
await page.evaluate(() => window.scrollTo(0, 0));
await page.click(".ttod-lang-switch"); await page.waitForLoadState("networkidle"); await page.waitForTimeout(1200);
await page.screenshot({ path: `${out}/5b-after-switch.png` });
console.log(`5b-after-switch.png  ${new URL(page.url()).pathname}`);
await browser.close();
