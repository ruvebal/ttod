<!--
AA7 report: Astro 5 → 7 major upgrade of services/frontend.
Author: Rubén Vega Balbás PhD (agent-assisted). Status VERIFYING. The agent does not mark DONE.
-->

# PHASE-AA7 report: Astro 5 → 7

**Status:** VERIFYING (2026-11-11) · cold review pending · **Branch:** `cascade/PHASE-AA-PREPROD-HARDENING-7`, stacked on AA5
(PR #97). **Exit gate:** [`PHASES/AA7-astro-major-upgrade.exit-gate.sh`](PHASES/AA7-astro-major-upgrade.exit-gate.sh), written
with the phase file before any upgrade code. It re-runs the AA2, AA3b, AA3 and AA5 exit gates unchanged.

## 1. Result

| | Before (AA5 tip) | After |
| - | ---------------- | ----- |
| `astro` | 5.18 | **7.4.11** |
| `@astrojs/node` / `svelte` / `react` / `mdx` | 9 / 7 / 4 / 4 | **11.1.12 / 9.1.5 / 7.1.8 / 8.1.5** |
| `npm audit --omit=dev` | 13 (1 critical, 4 high, 2 moderate, 6 low) | **5 (0 critical, 0 high, 2 moderate, 3 low)** |
| Frontend suite / `astro check` / build / PWA guard | green | green (271 tests) |
| Docs heading ids (2 pages, 4 ids) | — | identical |
| Visible text of `/es/`, `/es/wisdom/`, `/es/graph/`, `/es/wisdom/wis-034/`, `/en/docs/` | — | identical |

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

## 4. Decisions

- **`compressHTML: true`, not v7's default `'jsx'`.** `'jsx'` strips whitespace between inline elements: the
  header's "Biblioteca Ada EN" or the stele foot would run together. With it pinned, the text snapshot is
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
- **Screenshots** (`before/` and `after/`, `strip.mjs`, 390 and 1440):
  - `quote` is 0 % different;
  - `landing` 0.1 %, `graph` 5–6 %, `wisdom` 11–17 %. All of it falls inside animated layers: the 3D
    constellation, and the slowly drifting painted backgrounds (`FondoEstudio`, the valley).
  - Side by side, the content layer is the same (checked by eye on `wisdom-1440` and `landing-1440`).
- **The earlier gates:** the runner's verify log re-runs AA2, AA3b, AA3 and AA5 unchanged:
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

## 7. Why the gate re-runs AA2, AA3b, AA3 and AA5

The upgrade replaces the compiler, the bundler, the server adapter and how env variables are read. Each earlier
gate holds a guarantee that lives exactly there:

| Gate | Guarantee the upgrade could silently break |
| ---- | ------------------------------------------ |
| AA2 | Cookie `Secure` rules, `security.allowedDomains` and the form origin check (adapter and core), the per-IP throttle through Astro |
| AA3b | The locator middleware (Astro 6 may hand it a partly decoded `pathname`), SSR ids, the hash/scroll scripts after a bundler change, CSP inline-script counts |
| AA3 | The session-aware header, the account forms and the cookie jar, the service worker, reduced motion, the AA0 Lighthouse rule |
| AA5 | The non-root frontend image and its health check, the Caddy `Host` guard against the adapter's known crash |

Unit tests mock the backend and render in a container; they cannot see the adapter, Caddy, real headers or a
browser. The earlier gates do. Running them unchanged (the gate refuses if any was edited on this branch) is
what lets this report say "nothing changed" with evidence. The `cookie` crash in §3 is the proof: every unit
test passed, and only a real stack found it.
