// AA1 browser smoke: load views through a proxy carrying the new headers; record console errors,
// failed requests (nosniff MIME blocks show up here) and CSP report-only violations.
// Usage: node browser-smoke.mjs <base-url> <out.json>   (CHROME_PATH, FE_PKG as in baseline.sh)
import { createRequire } from "node:module";
import { writeFileSync } from "node:fs";
const [base, out] = process.argv.slice(2);
const pkg = process.env.FE_PKG || `${process.env.HOME}/src/ttod/services/frontend/package.json`;
const { chromium } = createRequire(pkg)("playwright");
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" });
const views = ["/es/", "/es/wisdom/", "/es/wisdom/wis-034/", "/es/graph/", "/es/graph/path/", "/es/oracle/", "/es/login/", "/en/docs/"];
const results = [];
for (const path of views) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const r = { path, consoleErrors: [], failed: [], violations: [] };
  page.on("console", (m) => { if (m.type() === "error" && !/Content Security Policy/.test(m.text())) r.consoleErrors.push(m.text().slice(0, 200)); });
  page.on("requestfailed", (q) => r.failed.push(`${q.url()} ${q.failure()?.errorText}`));
  page.on("response", (s) => { if (s.status() >= 400) r.failed.push(`${s.url()} HTTP ${s.status()}`); });
  await page.exposeFunction("__csp", (v) => r.violations.push(v));
  await page.addInitScript(() => document.addEventListener("securitypolicyviolation", (e) =>
    window.__csp({ directive: e.effectiveDirective, blocked: e.blockedURI, sample: (e.sample || "").slice(0, 60), line: e.lineNumber })));
  const resp = await page.goto(base + path, { waitUntil: "networkidle" });
  r.status = resp.status();
  r.headers = { xfo: resp.headers()["x-frame-options"], cspro: !!resp.headers()["content-security-policy-report-only"] };
  r.swRegistered = await page.evaluate(async () => !!(navigator.serviceWorker && (await navigator.serviceWorker.getRegistration())));
  await page.waitForTimeout(800);
  results.push(r);
  await page.close();
}
await browser.close();
writeFileSync(out, JSON.stringify({ base, recorded: new Date().toISOString(), results }, null, 2));
for (const r of results) console.log(`${r.path.padEnd(22)} ${r.status} xfo=${r.headers.xfo} cspRO=${r.headers.cspro} sw=${r.swRegistered} errors=${r.consoleErrors.length} failed=${r.failed.length} csp-violations=${r.violations.length}`);
