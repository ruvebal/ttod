<!--
AA7 cold review. Reviewer: cascade-cold-reviewer (agent), no implementation context.
Scope: the Astro 5 → 7 upgrade (services/frontend), the Caddy @rutadoble guard, the exit-gate amendments and the
evidence in PHASE-AA7-REPORT.md. Not marked DONE.
-->

# PHASE-AA7 cold review: Astro 5 → 7

**Commits reviewed:** `5726a2e2` … `a51d9fa4` (`git diff 19a25609..HEAD`, 10 commits), compared against the AA5 tip
`19a25609`. Gate amendments compared against `1154caad`, where the gate and the phase file were written.
**Verdict: PASS-WITH-AMENDMENTS.** No P0. One P1 blocks DONE:

- **F1:** `.nvmrc` pins Node `22.12.0`, but Astro 7.4.11's own CLI refuses to start below **22.23.4**. A student
  who runs `nvm use` cannot run `astro dev` or `astro build`. The fix is one line.

The upgrade itself is sound, and I tested it directly:
- every version matches the report;
- the production audit numbers are exact, before and after;
- suite, `astro check`, build and the PWA guard are green;
- `BACKEND_URL` is read at runtime in the built server;
- cookies, the form origin check and the `Host` guard behave as on Astro 5;
- the Caddy guard stops every `//` and `/\` form I sent, including encoded, absolute-form and h2c requests.

Four P2s should be fixed inside AA7, because they concern AA7's own fix and gate:
- F2: `devalue` has the same packaging defect as `cookie`, and the new scan cannot see it;
- F3: dot-segment paths get past the Caddy guard (same-origin only, so not exploitable);
- F4: the scope-window guard matches patterns, so it would let a weakening edit through;
- F5: Caddy left the forbidden list as a whole, but AA1 is not re-run.

F6 is an older bug that AA7 touched without fixing: the propose form posts to `http://backend:8000` from the
browser.

## What I ran (2026-11-11, on Tanit)

I never ran a command against `ttod_oracle`. Every Compose call used `-p ttod_aa7review`, and the AA1 probe used
`LIVE_COMPOSE_NETWORK=ttod_aa7review_default`. My stack is down. Note: `ttod_oracle`'s containers show
`StartedAt 2026-11-11T18:48:35Z`. That restart came before my stack came up, and none of my commands caused it.

| Check | Command | Result |
| ----- | ------- | ------ |
| Frontend suite | `npx vitest run` | `Test Files 42 passed (42)`, `Tests 271 passed (271)` |
| Type check | `npm run check` | `149 files: 0 errors, 0 warnings, 5 hints` |
| Build, PWA guard | `npm run build`, `npm run pwa:guard` | `build exit 0`; `8 passed`, `[pwa-guard] PASS` |
| AA7 gate, its own checks | `AA7_SKIP_GATES=1 bash PHASES/AA7-…exit-gate.sh` | Passes; includes the earlier-gate edit guard and the externals scan |
| Installed versions | `node -p require(...).version` | astro 7.4.11, node 11.1.12, svelte 9.1.5, react 7.1.8, mdx 8.1.5, vite 8.3.8, vitest 5.1.0, cookie 2.0.2, @astrojs/check 0.9.10 |
| Production audit, now | `npm audit --omit=dev` | `5 vulnerabilities (3 low, 2 moderate)`: deepmerge via the Svelte Vite plugin, postcss-selector-parser via typography. Neither appears in `dist/server` (grep finds nothing) |
| Production audit, AA5 tip | `npm audit --omit=dev --package-lock-only` on `git show 19a25609:…/package-lock.json` | `low 6, moderate 2, high 4, critical 1, total 13` (astro critical; @astrojs/node, sharp, zod, zod-to-ts high). Matches the report |
| Audit fails closed | `{"error":…}` piped into the gate's parser | `KeyError: 'metadata'`, non-zero, so the gate fails. The `\|\| true` is safe |
| Runtime `BACKEND_URL` | grep `dist/server`, in the image too | Only `process.env.BACKEND_URL ?? ""` at runtime; nothing inlined |
| Externals scan, falsified | the gate's scan against a copy of the lock with `cookie` dev-only 1.1.1 and astro's 2.0.2 nested | `cookie: dev-only at top level`, exit 1. The report's claim holds |
| Externals vs nested copies | lock: each external with a divergent nested copy | `devalue top 5.9.4, nested astro 6.0.3` (F2), `cookie` (msw dev 1.1.1, harmless), `picomatch` (anymatch, harmless) |
| Isolated stack | `isolated-stack.sh up ttod_aa7review 28880` | Up on :28880 and :28881 |
| `@rutadoble`, positive | `curl --path-as-is` on `//`, `/\`, `///`, `%2F%2F`, `%2f/`, `%5C`, `%5C%5C`; `--request-target http://…//evil.example/x`; `--http2-prior-knowledge`; port 28881 | All **404**, no `Location`, AA1 headers present on the 404 |
| `@rutadoble`, gaps | `/.//evil.example/x`, `/%2e//…`, `/%2e%2e//…`, `/.\/…`, `/es/..//…`, `/%09/evil.example/x` | **301 `Location: /evil.example/x/`** (F3; same-origin) |
| Pages unaffected | `/`, `/es`, `/es/wisdom`, `/es/`, `/health`, `/api/v1/wisdom/sample`, `/es/account/` | 302 `/en/`; 301 `/es/`; 301 `/es/wisdom/`; 200; 200; 200; 302 to login with `next` |
| Node directly (inside the container) | raw `http.request` to :4321, with and without `X-Forwarded-Host` | Without it: `//`, `/\`, `///`, `/.//` give **404** (the middleware fix works). With it: all **301 `/evil.example/x/`**. Matches report §3b |
| Origin check, cookie | cross-origin form POST; spoofed `X-Forwarded-Proto: https`; real login | 403; 403; `303`, `Set-Cookie: ttod_session=…; Max-Age=3600; Path=/; HttpOnly; SameSite=Lax` |
| Malformed `Host` | `Host: localhost:abc` | 400 (AA5 guard holds) |
| AA1 headers on Astro 7 | `AA1_PROBE_PORT=28090 LIVE_COMPOSE_NETWORK=ttod_aa7review_default bash PHASES/AA1-…exit-gate.sh` | Every header and error-page check passes. The gate then stops at its own scope check (`AA1 changed files outside caddy/ and docs/: services/frontend/.nvmrc`), the same issue the AA3 and AA3b scope windows fix (F5) |
| Inline scripts served | count `<script>` without `src` | `/es/` 4, `/es/wisdom/` 4, `/es/graph/` 5, quote 3, login 3, docs 3. There is no Astro 5 stack to compare with, so I rely on the gate's browser checks (CSP ≤ AA1), which passed in the runner's third run |
| Screenshots | PIL `ImageChops.difference` on the 8 pairs | See F7 |
| Text and heading ids | `diff before/snapshot.json after/snapshot.json` | Identical. Docs coverage is complete: `src/content/docs` has 2 files with 2 headings each |
| Earlier gates and browser checks | `git diff 19a25609..HEAD` on the AA2/AA3b/AA3/AA5 gates and `scripts/` | Only the two scope-window hunks (AA3b `:122-125`, AA3 `:73-76`); `scripts/` unchanged |
| Scope-window end commits | `git log --grep='owner marks AA3b DONE'` / `AA3 DONE` | `55279677`, `4cac250d`. From `4cac250d` to `19a25609`, the backend diff is AA5's (`redis_client.py`, `test_aa5_lane_b.py`, …) |
| Verify log history | `git show dfb56d0f:` / `fcc04b52:` on `…VERIFY-LOG.md` | Two runs exit 1 on `off-site redirect: //evil.example/x → Location: /evil.example/x/`; the third, at `fcc04b52`, exits 0. Honest |

## Acceptance

- [x] **`astro` ≥ 7, integrations on their Astro 7 majors, audit 0 critical / 0 high.** Re-measured.
- [~] **AA2, AA3b, AA3 and AA5 exit 0 "unchanged".** They exit 0 (runner log, third run). But two of them were
  edited: the scope window is a gate edit, made so that they pass. I judge it legitimate and not a weakening (see
  "Gate amendments" below), but the Acceptance line in the phase file (`AA7-astro-major-upgrade.md:73`) still says
  "no gate edits", and the report says "unchanged" three times (F8). Amend the wording; the guard itself needs F4.
- [x] **No server module reads `import.meta.env.BACKEND_URL`.** `git grep` finds none. In the built server it is
  `process.env`. One client island also reaches the reader (F6).
- [x] **Docs heading ids unchanged.** 4 of 4, and that is every heading in the docs collection.
- [x] **No UX regression; CSP at or below AA1.** The screenshots support "nothing visible changed" (F7 corrects the
  numbers). The CSP and Lighthouse checks ran inside the AA3b and AA3 gates; their counts are not in the committed log (F8).
- [ ] **Cold review green or amended.** This document.

## Findings

| ID | Sev | Blocks DONE | Finding and evidence | Fix |
| -- | --- | ----------- | -------------------- | --- |
| **F1** | P1 | yes (amend) | **The Node floor is below Astro 7's own floor, and Astro's CLI refuses to run on it.** `services/frontend/.nvmrc:1` is `22.12.0` and `package.json:56` is `"node": ">=22.12.0"` (report `:42`: "the Node floor set to `22.12.0`"). The installed packages need more: `astro` declares `"node": ">=22.23.4"` (`node_modules/astro/package.json:199`), and so do `@astrojs/mdx`, `react`, `svelte`, `prism` and `telemetry`; `undici` needs `>=22.19.0`. Astro enforces its floor: `node_modules/astro/bin/astro.mjs:31` `const engines = … '>=22.23.4'` calls `errorNodeUnsupported()` before any command runs. `satisfies("22.12.0", ">=22.23.4")` → `false`. Docker (`node:22-alpine`) and CI (`node-version: "22"`) pick the latest 22.x, so the gate and the images never saw it. Only a person who follows `.nvmrc` is hit, and that is a student's local setup | `.nvmrc` → `22.23.4` (or `22`, matching the images and CI). `engines.node` → `>=22.23.4`. Add one gate line: `node -e` checks that `.nvmrc` satisfies `require('astro/package.json').engines.node`. Correct report `:42` |
| **F2** | P2 | no (amend in AA7) | **`devalue` has the same packaging defect as `cookie`, and the new scan cannot see it.** The built server imports bare `"devalue"` from Astro's code (`dist/server/entry.mjs:10` `import { parse, stringify, unflatten } from "devalue"`, `chunks/_astro_content_*.mjs:6`). Astro declares `devalue ^6.0.3`, and npm placed that copy at `node_modules/astro/node_modules/devalue` (6.0.3). The top-level copy is Svelte's 5.9.4 (`npm ls devalue`). Svelte's own server runtime is also bundled, and also imports bare `"devalue"` (`chunks/index-server_*.mjs:1`, `devalue.uneval`, Svelte declares `^5.8.1`). So in production, **Astro 7 runs against devalue 5**. It works today: I serialized Date, Map, Set, URL, BigInt, RegExp, `-0`, `Infinity` and a typed array with v6 and parsed them with v5, and got back the same keys and types. But the guarantee the report draws from §3 ("the new gate check keeps the general case honest") is wrong: the scan (gate `:56-65`) checks that a package exists and is not dev-only, never which version. A direct dependency cannot fix this case, because two bundled runtimes need different majors of the same bare name. Smaller blind spots in the same scan: side-effect `import "x"`, single-quoted specifiers, and lock entries flagged `devOptional` | (a) In the gate, fail when an external has a nested copy under `astro`/`@astrojs/*` whose version differs from the top-level one. Even better, check the top-level version against the range each importing package declares. (b) Fix the cause: try `vite: { ssr: { noExternal: ['cookie', 'devalue'] } }`. Each import is then bundled from its importer's own copy (Astro's 6.x, Svelte's 5.x), and the `cookie` direct dependency is no longer needed. Rebuild, rerun the scan and the image boot. (c) Extend the regex to `import\s*["']…["']`, single quotes, and treat `devOptional` like `dev` |
| **F3** | P2 | no (amend in AA7) | **The Caddy guard misses dot segments and control characters.** `caddy/Caddyfile:56` matches `{http.request.orig_uri.path} ^/[/\\]`. Go has already decoded that path, so `%2F%2F` and `%5C` are caught (verified), and so are absolute-form and h2c requests. But the WHATWG URL parser in the adapter resolves `.` and `..` segments and strips tab and newline, and then Astro 7 collapses the result. Through Caddy on :28880: `/.//evil.example/x`, `/%2e//evil.example/x`, `/%2e%2e//evil.example/x`, `/.\/evil.example/x`, `/es/..//evil.example/x` and `/%09/evil.example/x` all give **`301 Location: /evil.example/x/`**. On Astro 5 the guard saw `//evil.example/x` and gave 404. The `Location` is same-origin in every case, so this is **not an open redirect**. It is the same kind of changed guarantee that the AA3b gate rightly refused in §3b. The AA3b probe only sends `//`, `/\` and `///`, so nothing would catch it. (Also, `/es//evil.example/x` now gives `/es/evil.example/x/` through Caddy but `/es//evil.example/x/` directly. That is harmless, but `middleware.test.ts:44` documents only the direct case) | Widen the matcher: `vars_regexp {http.request.orig_uri.path} ^/[/\\]\|(^\|[/\\])\.{1,2}([/\\]\|$)\|[\x00-\x1f]`. (The `\|` are Markdown table escapes; write a plain `|` in the Caddyfile.) TTOD has no legitimate URL with a dot segment or a control character. Add those six probes to the **AA7** gate (a strengthening, not an edit to AA3b), each expecting 404 with no `Location` |
| **F4** | P2 | no (amend in AA7) | **The scope-window guard checks patterns, not content, so a weakening edit to any earlier gate passes it.** Gate `:72-73` drops every changed line that contains `end=`, `"$end"`, `Scope window` or `later phase.s legitimate`, and it filters only lines whose second character is not `+` or `-`. I fed it four hostile added lines: `+end="$start"`, `+git diff --quiet "$start" "$end" -- ttod.yml \|\| fail "x"` (drops `proposals services/backend`), `+fail() { :; }  # Scope window` and `+-- a line starting with dashes`. **All four pass** (empty output). The filter is applied to AA2 and AA5 too, which were not meant to get any edit. The edit actually made (d94d58d4) is clean; the guard is what is loose | Pin the allowed edit by content: `git diff --quiet d94d58d4 -- <AA3b gate> <AA3 gate>` (nothing changed since the commit that added the window) and `git diff --quiet "$start" -- <AA2 gate> <AA5 gate>`. Or record `git diff "$start" -- <gate> \| sha256sum` and compare. Keep the browser-check line as it is |
| **F5** | P2 | no (amend in AA7) | **Caddy left the forbidden list completely, but the gate that guards Caddy (AA1) is not re-run.** Gate `:91` now checks only `ttod.yml proposals services/backend`. Any Caddy edit on this branch now passes AA7's own checks. The re-run gates cover `@hostmalo` (AA5) and count CSP violations (AA3b/AA3 browser checks), but a **removed** CSP header produces 0 violations, which is ≤ AA1, so it would pass. The actual Caddy diff is only the 8 `@rutadoble` lines (verified), and I ran AA1's header checks against my stack: all pass. AA1 itself cannot be re-run as it stands, because its scope check (`AA1-…exit-gate.sh:86-88`) fails on any later branch, the same issue AA3 and AA3b had | Allow exactly the `@rutadoble` hunk: compare `git diff -U0 "$start" -- caddy` with a recorded hash, or `git diff --quiet fcc04b52 -- caddy`. Re-run AA1 from the AA7 gate with `LIVE_COMPOSE_NETWORK` pointed at an isolated stack, and give AA1 the same scope window, in the same style and pinned the same way as F4 |
| **F6** | P2 | no (pre-existing; fix here or as its own task) | **A client island imports the server-only reader, and the propose form posts to `http://backend:8000` from the browser.** `ProposeForm.tsx:5,71` (`client:load`, `propose.astro:17`) → `lib/proposals.ts:2,14` `backendUrl()`. In the browser bundle Vite turns `process.env` into `{}`: `dist/client/_astro/ProposeForm.*.js` contains ``var c=`http://backend:8000`;function l(){return({}.BACKEND_URL??``)…||c}`` and then ``fetch(`${t}/api/v1/proposals`…)``. A browser cannot resolve `backend`, so a signed-in student's submit ends in the `network` error. On Astro 5 the result was the same (`import.meta.env.BACKEND_URL` is not exposed to the client), so **this is not an AA7 regression**. But AA7 rewrote this exact line, and `lib/backend.ts:2-5` says the reader is for server reads. I read this from the bundle; I did not click through it in a browser | In the browser, `submitProposal` should call the relative `/api/v1/proposals` (Caddy proxies `/api/*`; dev uses the Vite proxy, `astro.config.mjs:53-57`). Rename `lib/backend.ts` → `backend.server.ts`, or make it throw when `!import.meta.env.SSR`, so a future client import fails loudly. Add a test that `submitProposal` posts to a relative URL |
| **F7** | P3 | no | **The screenshot numbers cannot be reproduced, and no diff script is committed.** Report `:97-98`: "landing 0.1 %, graph 5–6 %, wisdom 11–17 %". My diff, counting any pixel that changed at all: landing 0.09 / 0.05 %, **wisdom 4.80 / 6.65 %**, graph 6.38 / 3.89 %, quote 0 / 0 (390 / 1440). With a threshold of more than 8 levels: landing 0, wisdom 0 / **0.02 %**, graph 5.77 / 1.10 %. The attribution holds in substance, with one correction. Graph: the diff map is exactly the 3D constellation; header, title and legend are identical. Wisdom-390: changes of at most 3 levels across the page (drift). Wisdom-1440: one 54×18 px box at (650,372) with a difference of up to 121 levels. Zoomed, it is the word "guarda." caught mid-way through the text-reveal animation, not the painted background. Every diff starts at y ≥ 56, so the header row is pixel-identical; that is the real evidence for the `compressHTML` claim. The text snapshot cannot be that evidence: it reads only `<main>` (`snapshot.py:16`), the header sits outside it (`Page.astro:238`), and `/es/wisdom/` hits the 4000-character cap. Deliverable 5 asked for `/es/account/`; the strip swapped it for the quote view without saying so | Commit the diff script next to `strip.mjs`, report its numbers and threshold, and attribute wisdom-1440 to the reveal animation. Say that the text snapshot covers `<main>` only and is capped. Either add `/es/account/` (signed in with a throwaway account on the isolated stack) or record that it was dropped |
| **F8** | P3 | no | **Wording that claims more than the evidence shows.** (a) "re-runs … unchanged" at report `:10`, `:101`, `:131` and the Acceptance at phase `:73`, against §6's disclosed edit. (b) Report `:103-104` says the verify log "include[s] the CSP inline-script counts against AA1 and the AA0 Lighthouse rule". The committed log has only each gate's last line; the counts were in the runner's `$TMPDIR/aa7-*.log`. (c) §4: "`'jsx'` strips whitespace between inline elements". Astro 7's own docs (`config.d.ts:486`) say `'jsx'` "preserves whitespace within a single line (e.g. a space between two inline elements)" and removes whitespace that contains line breaks. The claim is plausible for TTOD's multi-line markup, but no `'jsx'` build was compared. (d) With `AA7_SKIP_GATES=1` the gate still prints "the AA2/AA3b/AA3/AA5 guarantees re-proven" (`:93`) | (a) "re-runs them, with one disclosed scope-window edit"; amend phase `:73` to match. (b) Have the gate echo each gate's CSP and Lighthouse summary lines into the log, or drop the claim. (c) Write "would collapse the line-broken whitespace in …", or attach a one-off `'jsx'` text diff. (d) Print a different final line when the re-runs are skipped |
| **F9** | P3 | no | **The middleware change has no test, and it only matters without `X-Forwarded-Host`.** `middleware.ts:10` switched to `new URL(context.request.url)`. `middleware.test.ts` exercises `redireccionLocator` only, so it passes with either version. Live: directly to Node, `//evil.example/x` → 404; with `X-Forwarded-Host` → 301. Port 4321 is not published, so this is defence in depth for callers inside the Compose network | Add one `onRequest` test with a context whose `url` is normalized (`/evil.example/x`) and whose `request.url` is raw (`//evil.example/x`). It fails on the old line. In the comment, say that behind Caddy the edge is the guard |
| **F10** | P3 | no | **Stale Rollup pins.** `package.json:52-53` still pins `@rollup/rollup-linux-{arm64,x64}-musl` 4.63.1. Vite 8 bundles with Rolldown, and `rollup` is no longer installed at all (`node_modules/rollup` absent). The production image installs these two binaries for nothing | Remove them. If the old npm optional-dependency workaround is still wanted, pin `@rolldown/binding-linux-{arm64,x64}-musl` (already in the lock at 1.2.19) |

## Answers to the brief's specific questions

**Completeness of the upgrade.**
- **Versions and majors:** correct (table above). `@astrojs/check` 0.9.10 type-checks Astro 7 with 0 errors.
- **i18n:** `redirectToDefaultLocale: false` is explicit, and `/` → 302 `/en/` through `pages/index.astro`.
- **Content layer:** the Zod import comes from `astro/zod`. The docs route uses `render(entry)`, and nothing uses
  `entry.slug` or `Astro.glob`.
- **Vitest:** 5.1.0, peer `vite ^6 || ^7 || ^8`; `getViteConfig` works and 271 tests pass.
- **Svelte, Tailwind:** the Svelte plugin is 7.3.1 and `@tailwindcss/vite` 4.3.3; both build on Vite 8.
- **PWA guard:** passes, 8 of 8.
- **Node adapter:** standalone mode, `HOST`/`PORT` honoured in the image, the health check is green.
- **`security.allowedDomains` and `checkOrigin`:** unchanged in behaviour. Cross-origin POST → 403, spoofed https
  → 403, same-origin login → 303 with the same cookie attributes.
- **Missed:** the Node floor (F1) and the stale Rollup pins (F10). `TTOD_ALLOWED_HOSTS` is still read at build
  time, by design (AA2, F23); the upgrade does not change that.

**Runtime `BACKEND_URL`.** All 9 server reads are covered, and the built server reads `process.env` per call. The
unit test proves only that the helper reads per call. The build grep is the real proof that nothing is inlined.
Add it to the gate: assert that `process.env.BACKEND_URL` appears in `dist/server`. One client island uses the
reader wrongly (F6).

**`cookie`.** The diagnosis in §3 is right, and so is the falsification. A direct dependency fixes `cookie` only
while the top-level 2.x satisfies Astro's range. It cannot fix the same defect for `devalue` (F2), where two
runtimes need different majors. I recommend `ssr.noExternal` for both, with the gate checking versions, not only
presence.

**Security.**
- **Caddy:** solid for `//`, `/\`, `///`, `%2F%2F`, `%2f/`, `%5C`, `%5C%5C`, absolute-form and h2c, on both ports.
  The 404 carries the AA1 headers. It is open to dot segments and control characters, same-origin only (F3).
- **Middleware:** meaningful only for direct-to-Node callers (F9).
- **Cookies and sessions:** `HttpOnly; SameSite=Lax; Max-Age=3600; Path=/`, with no `Secure` on plain HTTP, as
  `COOKIE_SECURE` intends.
- **Origin check:** intact.
- **Inline scripts:** the source count (`is:inline`) is unchanged. The served counts are listed above; the
  per-view ≤ AA1 check ran in the gates.

**Evidence honesty.** The verify-log history, the audit numbers, the text and heading-id diffs and the versions
are all accurate. The screenshot percentages are not reproducible, but the "animated layers" conclusion survives
inspection, with one correction (F7). Three sentences claim more than the evidence shows (F8).

## Gate amendments

| Amendment | Judgement |
| --------- | --------- |
| Scope window in AA3b and AA3 (`d94d58d4`) | **Legitimate; not a weakening.** The check's own message is "AA3 touched …"; once AA3 is DONE, its window ends at `4cac250d`. `end=HEAD` is the fallback when the DONE commit is missing, which is the old behaviour. Every other AA3/AA3b check still runs against HEAD. But the guard that allows it is loose (F4), and the "unchanged" wording must go (F8a) |
| Caddy leaves the forbidden list | Justified by §3b, but too broad: allow the hunk, not the directory, and re-run AA1 (F5) |
| Integration-major check | **Acceptable.** `@astrojs/react` declares no Astro peer (I checked the installed `package.json`). Fixed minimum majors plus `npm ci`'s peer resolution are enough |
| `npm audit … \|\| true` | **Acceptable, and it fails closed:** an audit that cannot run yields JSON without `metadata`, so the parser raises and the gate fails |
| Externals scan (strengthening) | Good, and falsified as claimed. It checks presence, not version (F2) |

## Decisions

- **`compressHTML: true`.** Agreed. It is the conservative choice for an upgrade that promises "nothing changes",
  and the pixel-identical header row supports it. Correct the description of `'jsx'` (F8c).
- **Sätteri kept.** Agreed. All 4 heading ids are identical, including the accented `cómo-leer-el-corpus`, and the
  2 docs files hold every heading in the collection. Revisit if the docs grow headings that end in punctuation
  or contain repeated text.
- **`cookie` as a direct dependency.** Challenged (F2). It works for `cookie` today, but the version is copied by
  hand from Astro's range, and the same approach cannot fix `devalue`. `vite.ssr.noExternal` addresses the cause.

## Legibility for a student

Sections 3 and 3b are the strongest teaching in the pack so far: a real break, a wrong first fix, and the reason
an end-to-end gate found what unit tests could not. Keep them. For a student, three things blur the lesson:
- "unchanged" next to a disclosed gate edit (F8a);
- screenshot percentages they cannot reproduce (F7);
- a `.nvmrc` that stops `astro dev` on the first try (F1).

A two-line glossary in §3 would also help a first-year reader: "a bare import is `from "cookie"`, without `./`;
it is resolved from `node_modules` next to `dist/`, not next to the package that wrote it."

## Downstream

- **AA4** (rebases onto AA7): no assumption is broken. If AA4 adds probes for canonical or hreflang URLs, reuse
  F3's dot-segment list.
- **AA6** (close-out, Phase T handoff): its checklist should carry F1's Node floor (`22.23.4`) for any host that
  runs the frontend outside Docker. F6 belongs in AA6's disposition list if it is not fixed in AA7.
- **This phase file:** amend `AA7-astro-major-upgrade.md:73` (Acceptance wording) in the same commit as the F4 and
  F8 fixes.
