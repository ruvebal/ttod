// AA3b browser checks (planner-written with the exit gate, 2026-11-11). What curl cannot prove:
// fragment → scroll mapping on sticky scenes, the scroll writer, <details> volumes, the language
// switch carrying search + hash, the 3D graph restoring ?from=&to=, copy-link, page errors, and the
// CSP inline-script report count against AA1.
// Usage: node aa3b-browser-check.mjs <base-url> <aa1 browser-smoke-after.json>
//        (CHROME_PATH, FE_PKG as in baselines/aa0-2026-11-10/baseline.sh)
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
const [base, aa1File] = process.argv.slice(2);
const pkg = process.env.FE_PKG || `${process.env.HOME}/src/ttod/services/frontend/package.json`;
const { chromium } = createRequire(pkg)("playwright");
const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" });
const errors = [];
const ok = (cond, msg) => { if (!cond) errors.push(msg); };
const corpus = await (await fetch(`${base}/api/v1/wisdom/sample`)).json();
const graph = await (await fetch(`${base}/api/v1/graph`)).json();
const es = corpus.filter((e) => e.lang === "es");
const sections = [...new Set(es.map((e) => e.section))];

async function open(path, { width = 1440, height = 900, reduced = false, slow = false } = {}) {
  const ctx = await browser.newContext({ viewport: { width, height }, reducedMotion: reduced ? "reduce" : "no-preference" });
  await ctx.grantPermissions(["clipboard-read", "clipboard-write"], { origin: base });
  const page = await ctx.newPage();
  const pageErrors = [];
  page.on("pageerror", (e) => pageErrors.push(String(e).slice(0, 200)));
  // Amended after the cold review (F2): a classroom phone, not a desktop on loopback.
  if (slow) {
    const cdp = await ctx.newCDPSession(page);
    await cdp.send("Network.emulateNetworkConditions", { offline: false, latency: 150, downloadThroughput: (1.6 * 1024 * 1024) / 8, uploadThroughput: (750 * 1024) / 8 });
    await cdp.send("Emulation.setCPUThrottlingRate", { rate: 4 });
  }
  await page.goto(base + path, { waitUntil: slow ? "load" : "networkidle", timeout: 120000 });
  await page.waitForTimeout(slow ? 6000 : 1800);
  return { ctx, page, pageErrors };
}
// The target is visible and the header does not cover it (header hidden, or its bottom above the target).
const unobscured = (page, selector) => page.evaluate((sel) => {
  const el = document.querySelector(sel); if (!el) return `missing ${sel}`;
  const r = el.getBoundingClientRect();
  if (r.bottom <= 0 || r.top >= innerHeight) return `${sel} off screen (top ${Math.round(r.top)})`;
  const h = document.getElementById("ttod-site-header");
  const hr = h?.getBoundingClientRect();
  const shown = h && hr.bottom > 0 && getComputedStyle(h).visibility !== "hidden" && Number(getComputedStyle(h).opacity) > 0.1;
  if (shown && hr.bottom > r.top + 1) return `${sel} under the header (header bottom ${Math.round(hr.bottom)} > target top ${Math.round(r.top)})`;
  return "";
}, selector);

// 1. Landing: #map-{section} on the sticky handscroll, cold, at 390 and 1440 (+ reduced motion).
const target = sections.includes("architecture") ? "architecture" : sections[1];
for (const width of [390, 1440]) {
  const { ctx, page, pageErrors } = await open(`/es/#map-${target}`, { width, height: width === 390 ? 844 : 900 });
  const cur = await page.evaluate(() => document.querySelector("[data-parada][data-actual]")?.id ?? "");
  ok(cur === `map-${target}`, `${width}px /es/#map-${target}: current stop is "${cur}"`);
  const kept = await page.evaluate(() => location.hash);
  ok(kept === `#map-${target}`, `${width}px /es/#map-${target}: the reader's fragment became "${kept}"`);
  const u = await unobscured(page, "[data-contador]"); ok(!u, `${width}px /es/#map-${target}: ${u}`);
  ok(!pageErrors.length, `${width}px /es/: page errors ${pageErrors.join(" | ")}`);
  await ctx.close();
}
// Amended after the cold review (F2): the same deep links on a throttled network (150 ms RTT,
// 1.6 Mb/s, 4× CPU) must land, and must not rewrite the reader's fragment while the page loads.
for (const [hash, check] of [[`#map-${target}`, "stop"], ["#doors", "doors"]]) {
  for (const width of [390, 1440]) {
    const { ctx, page } = await open(`/es/${hash}`, { width, height: width === 390 ? 844 : 900, slow: true });
    const kept = await page.evaluate(() => location.hash);
    ok(kept === hash, `slow ${width}px /es/${hash}: the fragment became "${kept}"`);
    if (check === "stop") {
      const cur = await page.evaluate(() => document.querySelector("[data-parada][data-actual]")?.id ?? "");
      ok(cur === hash.slice(1), `slow ${width}px /es/${hash}: current stop is "${cur}"`);
    } else {
      const op = await page.evaluate(() => Number(getComputedStyle(document.getElementById("doors")).opacity));
      ok(op > 0.5, `slow ${width}px /es/#doors: doors chapter opacity ${op} (scrollY ${await page.evaluate(() => scrollY)})`);
    }
    await ctx.close();
  }
}
{
  const { ctx, page } = await open(`/es/#map-${target}`, { width: 390, height: 844, reduced: true });
  const u = await unobscured(page, `#map-${target}`); ok(!u, `reduced motion /es/#map-${target}: ${u}`);
  await ctx.close();
}
for (const [hash, sel] of [["#thesis", "#sigue-tesis"], ["#close", "#close h2"], ["#map", "#sigue-rollo"]]) {
  const { ctx, page } = await open(`/es/${hash}`, { width: 390, height: 844 });
  const u = await unobscured(page, sel); ok(!u, `/es/${hash}: ${u}`);
  await ctx.close();
}
{
  const { ctx, page } = await open("/es/#doors");
  const op = await page.evaluate(() => Number(getComputedStyle(document.getElementById("doors")).opacity));
  ok(op > 0.5, `/es/#doors: doors chapter opacity ${op}`);
  await ctx.close();
}
// 2. Scroll writer: › updates the hash with replaceState; the first viewport stays clean.
{
  const { ctx, page } = await open("/es/");
  ok((await page.evaluate(() => location.hash)) === "", "/es/ cold load wrote a hash");
  await page.goto(`${base}/es/#map-${(await page.evaluate(() => document.querySelector("[data-parada]")?.id.replace(/^map-/, "")))}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(1800);
  const len = await page.evaluate(() => history.length);
  await page.click('[data-ir="1"]'); await page.waitForTimeout(2200);
  const next = await page.evaluate(() => document.querySelectorAll("[data-parada]")[1]?.id);
  ok((await page.evaluate(() => location.hash)) === `#${next}`, `› did not write #${next} (hash ${await page.evaluate(() => location.hash)})`);
  ok((await page.evaluate(() => history.length)) === len, "scroll writer grew history (must be replaceState)");
  await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(800);
  ok((await page.evaluate(() => location.hash)) === "", "back in the first viewport the chapter hash stayed");
  await ctx.close();
}
// 3. Wisdom: #volume-{section} opens and lands; toggling writes the hash without history.
{
  const { ctx, page, pageErrors } = await open(`/es/wisdom/#volume-${target}`, { width: 390, height: 844 });
  ok(await page.evaluate((t) => document.getElementById(`volume-${t}`)?.open === true, target), `#volume-${target} not open`);
  const u = await unobscured(page, `#volume-${target}`); ok(!u, `/es/wisdom/#volume-${target}: ${u}`);
  const len = await page.evaluate(() => history.length);
  const another = sections.find((s) => s !== target);
  await page.click(`#volume-${another} > summary`); await page.waitForTimeout(500);
  ok((await page.evaluate(() => location.hash)) === `#volume-${another}`, `toggling #volume-${another} did not write its hash`);
  ok((await page.evaluate(() => history.length)) === len, "volume toggle grew history");
  ok(!pageErrors.length, `/es/wisdom/: page errors ${pageErrors.join(" | ")}`);
  await ctx.close();
}
// 4. A quote inside a paged facet list.
{
  const html = await (await fetch(`${base}/es/wisdom/sections/${target}/?p=2`)).text();
  const ids = new Set(es.map((e) => e.id));
  const onPage = [...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]).filter((i) => ids.has(i));
  const q = onPage[Math.min(5, onPage.length - 1)];
  ok(Boolean(q), `/es/wisdom/sections/${target}/?p=2 renders no quote ids`);
  if (q) {
    const { ctx, page } = await open(`/es/wisdom/sections/${target}/?p=2#${q}`, { width: 390, height: 844 });
    const u = await unobscured(page, `#${CSS_escape(q)}`); ok(!u, `?p=2#${q}: ${u}`);
    // copy-link on that quote: absolute URL in the clipboard, announced politely
    const link = page.locator(`#${CSS_escape(q)} a[data-copiar]`).first();
    if (await link.count()) {
      await link.click(); await page.waitForTimeout(300);
      const clip = await page.evaluate(() => navigator.clipboard.readText());
      ok(clip === `${base}/es/wisdom/sections/${target}/?p=2#${q}`, `copy-link copied "${clip}"`);
      const said = await page.evaluate(() => [...document.querySelectorAll('[aria-live="polite"],[role="status"]')].map((n) => n.textContent.trim()).join("|"));
      ok(/copiado|copied/i.test(said), "copy-link not announced in a polite live region");
    } else ok(false, `#${q} has no a[data-copiar] copy-link`);
    await ctx.close();
  }
}
// 5. Language switch carries search + hash; quote twin.
{
  const { ctx, page } = await open("/es/wisdom/?q=diseno#search");
  // Amended during AA3b: after the jump to #search the header has hidden itself (it hides on any
  // downward scroll past 200 px), so the reader scrolls up to reach it, as a person would.
  await page.evaluate(() => window.scrollTo(0, 0)); await page.waitForTimeout(400);
  await page.click(".ttod-lang-switch"); await page.waitForLoadState("networkidle");
  const u = new URL(page.url());
  ok(u.pathname === "/en/wisdom/" && u.search === "?q=diseno" && u.hash === "#search", `switch from ?q=diseno#search landed on ${u.pathname}${u.search}${u.hash}`);
  await page.goto(`${base}/es/wisdom/wis-034/`, { waitUntil: "networkidle" });
  await page.click(".ttod-lang-switch"); await page.waitForLoadState("networkidle");
  ok(new URL(page.url()).pathname === "/en/wisdom/wis-033/", `switch on wis-034 landed on ${page.url()}`);
  await ctx.close();
}
// 6. Graph: ?from=&to= restored and kept across reload; ?node= opens the card.
{
  const deg = new Map();
  for (const e of graph.edges) if (e.rel === "related") for (const n of [e.source, e.target]) deg.set(n, (deg.get(n) ?? 0) + 1);
  // Amended during AA3b: the es corpus has no `related` edges, so 3D nodes carry the related (en)
  // quote's id and show its es twin. The URL keeps the node id (identical in both locales); the page
  // shows the twin. A path end counts as shown if either id is on screen.
  const linked = graph.edges.find((e) => e.rel === "related");
  const [a, b] = [linked.source, linked.target];
  const twin = new Map();
  for (const e of graph.edges) if (e.rel === "translation_of") { twin.set(e.source, e.target); twin.set(e.target, e.source); }
  // innerText returns the rendered case and the meta line is `text-transform: uppercase`.
  const shown = (text, id) => { const t = text.toLowerCase(); return t.includes(id) || (twin.has(id) && t.includes(twin.get(id))); };
  const { ctx, page, pageErrors } = await open(`/es/graph/?from=${a}&to=${b}`);
  await page.waitForTimeout(2500);
  const keep = async (when) => {
    const s = new URL(page.url()).searchParams;
    ok(s.get("from") === a && s.get("to") === b, `${when}: /es/graph/ URL lost from/to (${page.url()})`);
    const text = await page.evaluate(() => document.body.innerText);
    ok(shown(text, a) && shown(text, b), `${when}: path ends ${a}/${b} (or their twins) not shown`);
  };
  await keep("cold");
  await page.reload({ waitUntil: "networkidle" }); await page.waitForTimeout(3000);
  await keep("reload");
  ok(!pageErrors.length, `/es/graph/: page errors ${pageErrors.join(" | ")}`);
  await page.goto(`${base}/es/graph/?node=${a}`, { waitUntil: "networkidle" }); await page.waitForTimeout(3000);
  ok(new URL(page.url()).searchParams.get("node") === a, `/es/graph/?node=${a} dropped node`);
  await ctx.close();
}
// 7. CSP inline-script reports must not exceed AA1 (old page → its successor).
{
  const aa1 = Object.fromEntries(JSON.parse(readFileSync(aa1File, "utf8")).results.map((r) => [r.path, r.violations.length]));
  const map = { "/es/": "/es/", "/es/wisdom/": "/es/wisdom/", "/es/wisdom/wis-034/": "/es/wisdom/wis-034/",
    "/es/graph/": "/es/graph/path/", "/es/graph/plano/": "/es/graph/", "/es/graph/code/": "/es/graph/path/" };
  for (const [now, then] of Object.entries(map)) {
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await ctx.newPage(); const v = [];
    await page.exposeFunction("__csp", (x) => v.push(x));
    await page.addInitScript(() => document.addEventListener("securitypolicyviolation", (e) => window.__csp(e.effectiveDirective)));
    await page.goto(base + now, { waitUntil: "networkidle" }); await page.waitForTimeout(800);
    ok(v.length <= aa1[then], `${now}: ${v.length} CSP reports > AA1 ${then} ${aa1[then]}`);
    console.log(`csp ${now.padEnd(22)} ${v.length} (AA1 ${then}: ${aa1[then]})`);
    await ctx.close();
  }
}
function CSS_escape(s) { return s.replace(/[^a-zA-Z0-9_-]/g, (c) => `\\${c}`); }
await browser.close();
if (errors.length) { console.error(errors.join("\n")); process.exit(1); }
console.log("browser checks passed: handscroll hash at 390/1440 (+reduced motion), chapters, scroll writer, volumes, paged quote, copy-link, language switch, graph from/to/node, CSP ≤ AA1");
