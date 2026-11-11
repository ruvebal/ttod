<!--
AA7 report: Astro 5 → 7 major upgrade of services/frontend.
Author: Rubén Vega Balbás PhD (agent-assisted). Status VERIFYING. The agent does not mark DONE.
-->

# PHASE-AA7 report: Astro 5 → 7

**Status:** VERIFYING (2026-11-11) · cold review **PASS-WITH-AMENDMENTS** ([PHASE-AA7-COLD-REVIEW.md](PHASE-AA7-COLD-REVIEW.md)), amended in the same session (§8) · **Branch:** `cascade/PHASE-AA-PREPROD-HARDENING-7`, stacked on AA5
(PR #97). **Exit gate:** [`PHASES/AA7-astro-major-upgrade.exit-gate.sh`](PHASES/AA7-astro-major-upgrade.exit-gate.sh), written
with the phase file before any upgrade code. It re-runs the AA1, AA2, AA3b, AA3 and AA5 exit gates. The only edit to them is one
scope window each in AA1, AA3b and AA3, pinned by file hash (§6).

## 1. Result

| | Before (AA5 tip) | After |
| - | ---------------- | ----- |
| `astro` | 5.18 | **7.4.11** |
| `@astrojs/node` / `svelte` / `react` / `mdx` | 9 / 7 / 4 / 4 | **11.1.12 / 9.1.5 / 7.1.8 / 8.1.5** |
| `npm audit --omit=dev` | 13 (1 critical, 4 high, 2 moderate, 6 low) | **5 (0 critical, 0 high, 2 moderate, 3 low)** |
| Frontend suite / `astro check` / build / PWA guard | green | green (271 tests) |
| Docs heading ids (2 pages, 4 ids) | — | identical |
| Visible text, header + main, uncut, of `/es/`, `/es/wisdom/` (16,118 characters), `/es/graph/`, `/es/wisdom/wis-034/`, `/en/docs/` | — | identical |

The 5 advisories left are build-time tooling only:
- `@tailwindcss/typography` → `postcss-selector-parser`, CSS processing at build time;
- the Svelte Vite plugin → `deepmerge`, dev and build only.

None of them ships in the server bundle.

## 2. How (two commits, one major each)

1. **Prep, still on Astro 5** (`refactor(aa7)`):
   - **Runtime `BACKEND_URL`.** `src/lib/backend.ts` reads `process.env.BACKEND_URL` on every call; it replaces 9
     `import.meta.env.BACKEND_URL` reads. Astro 6 inlines `import.meta.env` at build time, so a runtime-only
     setting would have frozen silently. A test proves the value is read per call.
   - **Zod import.** `z` comes from `astro/zod` (Zod 4 in Astro 6).
2. **Astro 6.4.8** with node 10, svelte 8, react 6, mdx **6.0.3**. mdx 7 already requires Astro 7. Everything was
   green on the first pass. `i18n.routing.redirectToDefaultLocale: false` is now explicit (Astro 6 changed the
   default; the root `/` redirects through `pages/index.astro`).
3. **Astro 7.4.11** with node 11, svelte 9, react 7, mdx 8:
   - `getContainerRenderer` imported from `@astrojs/react/container-renderer` (6 test files);
   - `compressHTML: true` pinned (see §4);
   - the Node floor set to `22.12.0` (`.nvmrc`, `engines`). The images and CI already resolve `22` to the latest 22.x.
   - The Rust compiler found no invalid HTML to reject.

## 3. The one real break, found live: `cookie`

The Astro 7 build passed locally, but the **Docker image crashed at startup** with `Cannot find package 'cookie'`.
- **What happened:** the built server imports `cookie` as a bare specifier. Astro's own `cookie@2` was installed
  nested under `node_modules/astro/`, and the top-level `cookie` was `msw`'s dev-only `1.x`. Locally the build
  silently used the wrong version (1.x); the image installs with `npm ci --omit=dev` and had none.
- **Fix:** `cookie@^2.0.2` as a direct dependency, so the top-level copy is Astro's version and present in
  production. It looks like an Astro 7 packaging quirk (an external import of a nested dependency). Worth an
  upstream issue if it survives the next minor.
- **Guard (a gate strengthening):** the AA7 gate now scans every bare import of the built server and requires each
  one to be a top-level, non-dev package in the lockfile. It was falsified against the broken lock layout
  (it names `cookie` and fails).

## 3b. The second break, found by re-running AA3b: `context.url` is normalized

The first full verify **failed** in the AA3b gate: on Astro 7, `GET //evil.example/x` answered `301 Location:
/evil.example/x/`, where Astro 5 gave 404.
- **Cause:** Astro 7 hands middleware a normalized `context.url` (`/evil.example/x`), while `context.request.url`
  keeps the path as sent (`//evil.example/x`; `/\…` arrives as `//…` too). The open-redirect guard in
  `lib/locators.ts` never saw the doubled slash, and the slash rule redirected.
- **Was it exploitable?** No: the target is a same-origin path. But it was a changed guarantee, and the gate is
  right to refuse it.
- **First fix, incomplete:** `src/middleware.ts` passes `new URL(context.request.url)`, the raw request, to
  `redireccionLocator`. Direct to the Node server that restored 404. The re-verify **still failed**, though,
  because through Caddy the request carries `X-Forwarded-Host`, and the adapter then rebuilds `request.url` from
  the forwarded headers, normalizing the path there too. Behind a proxy, the app cannot see `//host` at all.
- **Fix that holds:** the guard moved to the edge. `caddy/Caddyfile` `@rutadoble` matches the raw request line
  (`{http.request.orig_uri.path} ^/[/\\]`) and answers 404 before proxying. Probed through Caddy: `//`, `/\`
  and `///` hosts answer 404 with no `Location`; pages, redirects and the API are unchanged. The middleware change
  stays, for requests that reach Node directly. Caddy was out of AA7's scope; the phase file and the gate's scope
  check are amended accordingly.
- **The gate was not edited.** This is the case for re-running earlier gates as they are: no unit test could see
  it, because the normalization happens in the adapter.

## 4. Decisions

- **`compressHTML: true`, not v7's default `'jsx'`.** `'jsx'` applies JSX-style whitespace rules: a line break
  between two elements collapses to nothing, so text written across lines in a template can lose its space
  (corrected after the cold review, F8). With it pinned, the text snapshot is
  byte-identical. Moving to `'jsx'` is a separate, screenshot-checked decision, not part of an upgrade whose
  promise is "nothing changes".
- **Markdown pipeline left on the v7 default (Sätteri).** The heading-id diff shows the docs ids unchanged, even the
  accented `cómo-leer-el-corpus`, so `@astrojs/markdown-remark` was not needed.
- **`cookie` as a direct dependency** instead of `vite.ssr.noExternal`. It is explicit, visible in `package.json`,
  and the new gate check keeps the general case honest.

## 5. Evidence

- **Docs heading ids** (`baselines/aa7-2026-11-11/{before,after}/snapshot.json`, from `snapshot.py`): identical.
  - `/en/docs/introduction/`: `how-to-read-the-corpus`, `governance-before-convenience`.
  - `/es/docs/introduction/`: `cómo-leer-el-corpus`, `la-gobernanza-antes-que-la-comodidad`.
- **Visible text** of the five views: byte-identical before and after.
- **Screenshots** (`before/` from a stack of `main` on Astro 5, `after/` from this branch; `strip.mjs`, 390 and 1440;
  numbers from the committed `compare.py`):
  - `quote` is 0.00 % different;
  - `landing` is 0.05–0.09 %, `wisdom` 2.2–6.5 %, `graph` 3.9–6.4 %.
  - The differences fall in animated layers: the 3D constellation, the drifting painted backgrounds, and on
    `wisdom` the intro text's word-by-word reveal caught at a different instant.
  - The numbers vary from run to run with animation timing (the cold reviewer measured wisdom at 4.8–6.65 %).
    The text snapshot, which is byte-identical, is the evidence that the content is the same.
  - `/es/account/` is not in the strip: it needs a session. The AA3 gate's re-run covers it (header and account
    forms live).
- **The earlier gates:** the runner verify re-runs AA1, AA2, AA3b, AA3 and AA5. The log keeps each gate's live
  summary, CSP counts and Lighthouse numbers (not only its last line, cold review F8). Earlier runs failed on
  the §3b break and are in the git history of the log:
  [`PHASES/AA7-astro-major-upgrade-VERIFY-LOG.md`](PHASES/AA7-astro-major-upgrade-VERIFY-LOG.md). They include the CSP
  inline-script counts against AA1 and the AA0 Lighthouse rule.

## 6. Gate amendments (disclosed)

- **Strengthening:** the build-externals scan (§3), falsified against the broken lock layout.
- **Earlier gates, one allowed edit:** the AA3b and AA3 scope checks ("no backend change since my gate was written")
  compared against HEAD, so AA5's legitimate backend work counted as theirs. Their window now ends at their own
  DONE commit (`55279677`, `4cac250d`). The AA7 guard allows exactly those lines and fails on any other edit to
  an earlier gate or browser check.
- **Bugs in my own gate:** the integration check assumed every integration declares an Astro peer
  (`@astrojs/react` declares none), so it now checks the first majors built for Astro 7: node 11, svelte 9,
  react 7, mdx 8. Also, `npm audit` exits non-zero on any advisory, even low, so only the critical/high verdict
  counts now.

## 7. Why the gate re-runs AA1, AA2, AA3b, AA3 and AA5

The upgrade replaces the compiler, the bundler, the server adapter and how env variables are read. Each earlier
gate holds a guarantee that lives exactly there:

| Gate | Guarantee the upgrade could silently break |
| ---- | ------------------------------------------ |
| AA1 | The security headers and report-only CSP on every response, now that the Caddyfile changed (§3b) |
| AA2 | Cookie `Secure` rules, `security.allowedDomains` and the form origin check (adapter and core), the per-IP throttle through Astro |
| AA3b | The locator middleware (Astro 6 may hand it a partly decoded `pathname`), SSR ids, the hash/scroll scripts after a bundler change, CSP inline-script counts |
| AA3 | The session-aware header, the account forms and the cookie jar, the service worker, reduced motion, the AA0 Lighthouse rule |
| AA5 | The non-root frontend image and its health check, the Caddy `Host` guard against the adapter's known crash |

Unit tests mock the backend and render in a container; they cannot see the adapter, Caddy, real headers or a
browser. The earlier gates do. Running them unchanged (the gate refuses if any was edited on this branch) is
what lets this report say "nothing changed" with evidence. The `cookie` crash in §3 is the proof: every unit
test passed, and only a real stack found it.

## 8. Cold review amendments (2026-11-11)

The verdict was PASS-WITH-AMENDMENTS, with one P1 ([review](PHASE-AA7-COLD-REVIEW.md)). Every finding was handled:

| # | Fix | Proof |
| - | --- | ----- |
| F1 (P1): `.nvmrc` 22.12 below Astro 7.4.11's own CLI floor (22.23.4) | `.nvmrc` `22.23.4`, `engines` `>=22.23.4` | — |
| F2: `devalue` had the `cookie` defect, invisible to a presence-only scan | `vite.ssr.noExternal: ['cookie', 'devalue']`: both are bundled from Astro's own folder, so the right major ships. The `cookie` direct dependency is gone. The externals scan now also fails when the code's owner (astro, `@astrojs/node`, another external) carries its own nested copy that differs from the top-level one | Falsified: with `devalue` external, the scan reports "astro needs its nested 6.0.3, the bundle would import the top-level 5.9.4" |
| F3: `@rutadoble` missed dot segments and control characters | The guard rejects a doubled slash or backslash anywhere, dot segments, encoded dot/slash/backslash, and control characters. The placeholder holds the decoded path, so raw control characters are matched too | Through Caddy: `/.//`, `/%2e//`, `/%2e%2e//`, `/.\/`, `/es/..//`, `/%09/`, `/%0a/`, `/%7f/`, `//`, `/\`, `%2F%2F`, `%5C` all 404; pages, accented queries, docs, hyphenated sections and the API unchanged |
| F4: the allowed-edit guard matched text, not content | AA1, AA3b and AA3 gates are pinned by git blob hash; every other earlier gate and both browser checks must be byte-identical | Falsified: a one-line edit dropping the backend path fails |
| F5: AA1 not re-run although Caddy changed | AA1 joins the re-run, with the same scope window (its own diff, `9d748fb8..5a915b3d`, stayed inside `caddy/` and `docs/`; checked) | verify log |
| F6: `ProposeForm` posted to `http://backend:8000` from the browser (older bug) | In the browser the island posts to its own origin (`/api/v1/proposals`, routed by Caddy) | `proposals.test.ts` browser case |
| F7: screenshot numbers not reproducible; snapshot partial; `/es/account/` silently dropped | `compare.py` committed; the snapshot reads header + main, uncut; before/after re-captured; the account page's absence is stated (§5) | `compare.py` output above |
| F8: overclaims | "unchanged" now says "only a pinned scope window"; the log keeps each gate's CSP/UX lines; the `compressHTML` description is corrected; a skipped run no longer says "re-proven" | — |
| F9: no test for the middleware change | `destinoDe(request)` in `lib/locators.ts`, tested with a raw `//host` request (and the normalized form shown to fire) | `middleware.test.ts` |
| F10: dead `@rollup/*-musl` pins | Removed (Vite 8 bundles with Rolldown); the image still builds | isolated stack |
