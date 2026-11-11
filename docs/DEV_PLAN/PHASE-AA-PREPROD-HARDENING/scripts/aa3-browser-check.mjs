// AA3 browser checks (planner-written with the exit gate, 2026-11-11): what curl cannot see about the
// header and the shell. Usage: node aa3-browser-check.mjs <base-url> <aa1 browser-smoke-after.json>
// (CHROME_PATH, FE_PKG as in baselines/aa0-2026-11-10/baseline.sh)
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
const [base, aa1File] = process.argv.slice(2);
const pkg = process.env.FE_PKG || `${process.env.HOME}/src/ttod/services/frontend/package.json`;
const { chromium } = createRequire(pkg)("playwright");
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" });
const errors = [];
const ok = (cond, msg) => { if (!cond) errors.push(msg); };

async function open(path, { width = 1440, height = 900, reduced = false } = {}) {
  const ctx = await browser.newContext({ viewport: { width, height }, reducedMotion: reduced ? "reduce" : "no-preference" });
  const page = await ctx.newPage();
  const pageErrors = [];
  page.on("pageerror", (e) => pageErrors.push(String(e).slice(0, 200)));
  await page.goto(base + path, { waitUntil: "networkidle" });
  await page.waitForTimeout(800);
  return { ctx, page, pageErrors };
}
const rem = (page) => page.evaluate(() => parseFloat(getComputedStyle(document.documentElement).fontSize));
const token = (page) => page.evaluate(() => getComputedStyle(document.documentElement).getPropertyValue("--ttod-header-height").trim());

// 1. Geometry: full width, the token's height, no pill, no hamburger at 768, the language switch quiet.
for (const [width, lang] of [[390, "es"], [768, "es"], [1440, "en"], [768, "en"]]) {
  const { ctx, page, pageErrors } = await open(`/${lang}/wisdom/`, { width });
  const g = await page.evaluate(() => {
    const h = document.getElementById("ttod-site-header"); const r = h.getBoundingClientRect(); const cs = getComputedStyle(h);
    const toggle = h.querySelector(".ttod-nav-toggle"); const nav = h.querySelector(".ttod-site-nav");
    const sw = h.querySelector(".ttod-lang-switch"); const link = nav.querySelector("a");
    return { left: r.left, width: r.width, height: r.height, radius: parseFloat(cs.borderTopLeftRadius),
      toggleShown: toggle && getComputedStyle(toggle).display !== "none", navShown: getComputedStyle(nav).display !== "none" && nav.getBoundingClientRect().height > 0,
      swBg: getComputedStyle(sw).backgroundColor, swSize: parseFloat(getComputedStyle(sw).fontSize), linkSize: parseFloat(getComputedStyle(link).fontSize),
      swHreflang: sw.getAttribute("hreflang"), swLang: sw.getAttribute("lang"), vw: document.documentElement.clientWidth };
  });
  const t = await token(page); const px = parseFloat(t) * (t.endsWith("rem") ? await rem(page) : 1);
  ok(g.left <= 0.5 && Math.abs(g.width - g.vw) <= 1, `${width}px: header not full width (${g.left}, ${g.width}/${g.vw})`);
  ok(Math.abs(g.height - px) <= 1, `${width}px: header height ${g.height} ≠ --ttod-header-height ${t}`);
  ok(g.radius < 2, `${width}px: header has a ${g.radius}px radius (pill)`);
  ok(/rgba\(0, 0, 0, 0\)|transparent/.test(g.swBg) && g.swSize <= g.linkSize + 0.5, `${width}px: language switch is not quiet (bg ${g.swBg}, ${g.swSize}px vs links ${g.linkSize}px)`);
  ok(g.swHreflang && g.swLang, `${width}px: language switch lacks hreflang/lang`);
  if (width >= 640) ok(!g.toggleShown && g.navShown, `${width}px: hamburger shown or primary nav hidden (no hamburger at ≥ 40rem)`);
  else ok(g.toggleShown && !g.navShown, `${width}px: no Menu button, or the nav is open by default`);
  ok(!pageErrors.length, `${width}px /${lang}/wisdom/: page errors ${pageErrors.join(" | ")}`);
  await ctx.close();
}
// 2. Disclosure menu at 390: opens below the bar and pushes content, no focus trap, Escape returns focus.
{
  const { ctx, page } = await open("/es/wisdom/", { width: 390, height: 844 });
  const before = await page.evaluate(() => document.querySelector("main").getBoundingClientRect().top);
  await page.click(".ttod-nav-toggle");
  const s = await page.evaluate(() => ({ exp: document.querySelector(".ttod-nav-toggle").getAttribute("aria-expanded"),
    rows: [...document.querySelectorAll(".ttod-site-nav a")].map((a) => a.getBoundingClientRect().height),
    mainTop: document.querySelector("main").getBoundingClientRect().top }));
  ok(s.exp === "true", "390px: Menu did not set aria-expanded=true");
  ok(s.rows.length >= 4 && s.rows.every((h) => h >= 44), `390px: menu rows below 44px (${s.rows.join(",")})`);
  ok(s.mainTop > before + 40, `390px: open panel does not push content (main ${before} → ${s.mainTop})`);
  // Tab through every focusable in the header; one more Tab must leave it (no trap).
  const n = await page.evaluate(() => [...document.querySelectorAll("#ttod-site-header a[href], #ttod-site-header button")].filter((e) => e.getClientRects().length).length);
  await page.focus(".ttod-nav-toggle");
  for (let i = 0; i < n + 1; i += 1) await page.keyboard.press("Tab");
  ok(await page.evaluate(() => !document.getElementById("ttod-site-header").contains(document.activeElement)), "390px: focus is trapped inside the open menu");
  await page.click(".ttod-nav-toggle"); await page.focus(".ttod-site-nav a"); await page.keyboard.press("Escape");
  ok(await page.evaluate(() => document.activeElement?.classList.contains("ttod-nav-toggle") && document.querySelector(".ttod-nav-toggle").getAttribute("aria-expanded") === "false"), "390px: Escape did not close and return focus to Menu");
  await ctx.close();
}
// 3. Skip link lands on the main landmark.
{
  const { ctx, page } = await open("/es/docs/");
  await page.keyboard.press("Tab");
  ok(await page.evaluate(() => document.activeElement?.classList.contains("ttod-skip-link")), "first Tab is not the skip link");
  await page.keyboard.press("Enter"); await page.waitForTimeout(300);
  ok(await page.evaluate(() => location.hash === "#ttod-main" && document.querySelector("main#ttod-main") !== null), "skip link does not target main#ttod-main");
  await ctx.close();
}
// 4. Anchors below the header on views AA3 owns (AA3b checks the landing and wisdom).
for (const [path, sel] of [["/es/account/reviewer/", null], ["/es/docs/", "h2[id], h3[id]"], ["/es/oracle/", "[id]:not(script):not(#ttod-site-header *)"]]) {
  if (!sel) continue;
  const { ctx, page } = await open(path, { width: 390, height: 844 });
  const id = await page.evaluate((s) => [...document.querySelectorAll(s)].map((e) => e.id).find((i) => i && document.getElementById(i).getBoundingClientRect().top > 900) ?? "", sel);
  if (id) {
    await page.goto(`${base}${path}#${id}`, { waitUntil: "networkidle" }); await page.waitForTimeout(600);
    const r = await page.evaluate((i) => {
      const t = document.getElementById(i).getBoundingClientRect(); const h = document.getElementById("ttod-site-header");
      const hr = h.getBoundingClientRect(); const shown = getComputedStyle(h).visibility !== "hidden" && hr.bottom > 0;
      return { top: t.top, hb: shown ? hr.bottom : 0 };
    }, id);
    ok(r.top >= r.hb - 1 && r.top < 844, `${path}#${id}: target top ${Math.round(r.top)} vs header bottom ${Math.round(r.hb)}`);
  }
  await ctx.close();
}
// 5. Reduced motion: the auth sky (CieloRuyi) runs no continuous animation loop (F12).
{
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, reducedMotion: "reduce" });
  const page = await ctx.newPage();
  await page.addInitScript(() => { const raf = window.requestAnimationFrame.bind(window); window.__raf = 0; window.requestAnimationFrame = (f) => { window.__raf += 1; return raf(f); }; });
  await page.goto(`${base}/es/login/`, { waitUntil: "networkidle" }); await page.waitForTimeout(500);
  const a = await page.evaluate(() => window.__raf); await page.waitForTimeout(2000); const b = await page.evaluate(() => window.__raf);
  ok(b - a < 10, `reduced motion /es/login/: ${b - a} animation frames in 2 s (continuous loop)`);
  await ctx.close();
}
// 6. The 2D graph speaks Spanish on /es/ (F32).
{
  const { ctx, page } = await open("/es/graph/plano/");
  await page.waitForTimeout(1500);
  const text = await page.evaluate(() => document.querySelector("main").innerText + " " + [...document.querySelectorAll("main [aria-label]")].map((e) => e.getAttribute("aria-label")).join(" "));
  for (const en of ["All tags", "Selected node", "Select a node", "Knowledge graph with", "Section legend", "Loading live graph", "Showing all tags"])
    ok(!text.includes(en), `/es/graph/plano/: English UI string "${en}"`);
  await ctx.close();
}
// 7. CSP inline-script reports must not exceed AA1.
{
  const aa1 = Object.fromEntries(JSON.parse(readFileSync(aa1File, "utf8")).results.map((r) => [r.path, r.violations.length]));
  for (const [now, then] of [["/es/", "/es/"], ["/es/wisdom/", "/es/wisdom/"], ["/es/login/", "/es/login/"], ["/es/oracle/", "/es/oracle/"], ["/en/docs/", "/en/docs/"], ["/es/graph/plano/", "/es/graph/"]]) {
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await ctx.newPage(); const v = [];
    await page.exposeFunction("__csp", (x) => v.push(x));
    await page.addInitScript(() => document.addEventListener("securitypolicyviolation", (e) => window.__csp(e.effectiveDirective)));
    await page.goto(base + now, { waitUntil: "networkidle" }); await page.waitForTimeout(800);
    ok(v.length <= aa1[then], `${now}: ${v.length} CSP reports > AA1 ${then} ${aa1[then]}`);
    console.log(`csp ${now.padEnd(18)} ${v.length} (AA1 ${then}: ${aa1[then]})`);
    await ctx.close();
  }
}
await browser.close();
if (errors.length) { console.error(errors.join("\n")); process.exit(1); }
console.log("AA3 browser checks passed: header geometry 390/768/1440, disclosure menu, skip link, anchors, reduced motion, Spanish 2D graph, CSP ≤ AA1");
