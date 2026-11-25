// AA3 screenshot strip: the header at 390/768/1440 × en/es × signed out/in (PHASE-AA3 "Proof"), plus the
// account and library pages signed in at 390. Signs up a throwaway user on the target (an isolated stack).
// Usage: node strip.mjs <base-url> <out-dir>   (CHROME_PATH, FE_PKG as in baselines/aa0-2026-11-10/baseline.sh)
import { createRequire } from "node:module";
const [base, out] = process.argv.slice(2);
const { chromium } = createRequire(process.env.FE_PKG || `${process.env.HOME}/src/ttod/services/frontend/package.json`)("playwright");
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" });
const email = `strip-${Date.now()}@example.test`, password = "strip-password-1";
await fetch(`${base}/api/v1/auth/register`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ email, password }) });
const signedIn = await browser.newContext();
{
  const page = await signedIn.newPage();
  await page.goto(`${base}/es/login/`); await page.fill("#email", email); await page.fill("#password", password);
  await Promise.all([page.waitForNavigation(), page.click('button[type="submit"]')]);
  await page.goto(`${base}/es/account/`);
  await page.fill("#cuenta-nombre", "Ada"); await Promise.all([page.waitForNavigation(), page.click('#profile button[type="submit"]')]);
  const corpus = await (await fetch(`${base}/api/v1/wisdom/sample`)).json();
  for (const q of corpus.filter((e) => e.lang === "es").slice(0, 2)) await page.request.post(`${base}/api/v1/favorites`, { data: { quoteId: q.id } });
  await page.close();
}
const anon = await browser.newContext();
for (const [who, ctx] of [["out", anon], ["in", signedIn]]) {
  for (const lang of ["es", "en"]) {
    for (const w of [390, 768, 1440]) {
      const page = await ctx.newPage(); await page.setViewportSize({ width: w, height: 900 });
      await page.goto(`${base}/${lang}/wisdom/`, { waitUntil: "networkidle" });
      await page.locator("#ttod-site-header").screenshot({ path: `${out}/header-${lang}-${who}-${w}.png` });
      if (w === 390) { await page.click(".ttod-nav-toggle"); await page.screenshot({ path: `${out}/menu-${lang}-${who}-390.png` }); }
      await page.close();
    }
  }
}
for (const path of ["/es/account/", "/es/library/", "/en/account/"]) {
  const page = await signedIn.newPage(); await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(base + path, { waitUntil: "networkidle" }); await page.waitForTimeout(600);
  await page.screenshot({ path: `${out}/page${path.replaceAll("/", "-").replace(/-$/, "")}-390.png`, fullPage: true });
  await page.close();
}
await browser.close();
console.log("strip written");
