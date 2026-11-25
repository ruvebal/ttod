<!--
AA3 cold review: classic header, account User section, library cards, Spanish 2D graph, shell a11y hygiene.
Reviewer: cascade cold reviewer (no implementation context). The reviewer does not mark DONE.
-->

# PHASE-AA3 cold review

**Verdict: PASS-WITH-AMENDMENTS.** No P0. One P1 blocks DONE, and the fix is small:

- **F1:** the header now depends on the session, but the service worker serves `/{l}/oracle/` **cache-first** from
  a copy fetched at install time. On the usual path, where the worker installs during an anonymous first visit, a
  signed-in student sees **Entrar** on the Oracle page for as long as that cache lives. If the worker installs while
  someone is signed in, the next person on that browser sees the **previous student's username and Biblioteca link**
  after logout. Without a username, the previous student's email sits in the link's `title`. Classroom machines are
  shared, so this matters.

Everything else in the account forms held up under direct testing:
- CSRF is refused for every form encoding.
- The rotated cookie keeps the caller signed in.
- `revoke_others` works both ways.
- logout-all and the cookie attributes are correct.
- `next` cannot be turned into an open redirect.

The header geometry stays one row at every width from 640 to 1440 px, signed in and out. axe finds nothing on nine
views at two widths.

The P2s are about resilience, the reduced-motion spec and gate evidence:
- a backend stall now hangs public pages for signed-in users;
- the header still slides away under reduced motion;
- the gate's two anchor spot-checks test nothing;
- the account link's accessible name is a bare username.

Base `origin/main` = `53855a59`, head `e5b01da0` (3 commits: gate before code `35385ed5`, implementation `f3f64dea`,
verify log `e5b01da0`).

## Evidence I ran (not taken from the report)

| Command | Result |
| ------- | ------ |
| `cd services/frontend && npx vitest run` | `Test Files 41 passed (41) · Tests 269 passed (269)` |
| `npm run check` | `0 errors · 0 warnings · 5 hints` |
| Runner verify log | exit 0 at `f3f64dea`. I did not re-run Lighthouse; the UX numbers are from that log and `baselines/aa3-2026-11-11/ux/ux-baseline.json` (plano CLS 0.0984) |
| Isolated stack `ttod_aa3review` :28580 (up, used, **down**; `ttod_oracle` untouched) | |
| `aa3-browser-check.mjs` and `aa3b-browser-check.mjs`, my run | both **pass**; the CSP counts equal the runner's (`/es/` 4, `/es/oracle/` 5, `/es/graph/code/` 6 …) |
| CSRF, `curl` with the session cookie | form POST to `/es/account/` from `Origin: http://evil.example` → **403**; no `Origin` → 403; `text/plain` → 403; `multipart` → 403; foreign `logout-all` → 403. The session was still valid afterwards (`/api/v1/auth/session` 200) |
| Non-form body | `content-type: application/json` POST to `/es/account/` → **500** (`formData()` throws); `/es/login/` behaves the same on `main` (F9) |
| Password change with `revoke_others` **off**, live | 303 `Location: /es/account/?ok=password#password`, `Set-Cookie: ttod_session=…; Max-Age=3600; Path=/; HttpOnly; SameSite=Lax` (no `Secure` over HTTP). Caller 200, caller's old token **401**, second browser **200** (kept) |
| logout-all, live | 303 `Location: /es/`, `Set-Cookie: ttod_session=deleted; Path=/; Expires=Thu, 01 Jan 1970 …; HttpOnly; SameSite=Lax`. Caller 401, second browser 401 |
| `next` safety (browser) | `/es/login/?next=%2F%2Fevil.example`: header Entrar `href="/es/login/"`, form `next` = `/es/account/`. `enlaceEntrar` re-validates with `safeNextPath` and requires the incoming value to come back unchanged (`enlaces-cuenta.ts:14-16`) |
| Localized 403 | `paginaProhibida` interpolates only `PROHIBIDO` constants and `localeOf()` ∈ {en, es} (`auth.server.ts:191-202`), so nothing user-controlled is injected. Live: the student on `/es/account/reviewer/` gets 403 with the full shell, and axe is clean |
| `scratchpad/probe/p2.mjs` (service worker) | see F1 |
| Session cost, `curl` ×3 | `/es/wisdom/`: anonymous 8 ms, signed in 9–10 ms (one `/auth/session` round-trip). **`docker pause` backend**: anonymous **200 in 7 ms**; signed in, **no response within 20 s** (F2) |
| Header geometry, signed in (username "Ada Lovelace Byron") and signed out, en/es, 640/700/768/820/900/1024/1440 | height 56 px, one row, no horizontal overflow at every width |
| Menu at 390 | Escape closes it and returns focus (gate). An outside tap closes it, but focus goes to `<body>`, not the button (F8a) |
| Accessible names (390, signed in) | `TTOD · Inicio`, `Inicio`, `Sabiduría`, `Grafo`, `Oráculo`, `Docs`, `Biblioteca`, **`Ada Lovelace Byron`**, `English (EN)` |
| Skip link, Tab → Enter → Tab | `/es/`: next stop is `Sabiduría` in `main` (the hero); `/es/graph/`: `Girar` in `main` (the 3D island); `/es/library/`: `Mi cuenta` breadcrumb in `main`. Every page under `src/pages` has exactly one `<main id="ttod-main">` (grep), and nothing references the removed wrapper div |
| axe-core 4.x (wcag2a/aa, 21aa, 22aa, best-practice) | clean at 390 and 1280 on `/es/account/`, `/en/account/`, `/es/library/`, `/es/account/reviewer/` (403), `/es/`, `/es/quote/`, `/es/graph/plano/`, `/es/register/`, `/es/login/?next=//evil` |
| Reduced motion, 390, after scrolling | `data-oculta` set, `transition: transform 0.3s …`, `transform: matrix(1,0,0,1,0,-56)` (F3) |
| Docs anchors, my own probe | `/es/docs/introduction/#la-gobernanza-antes-que-la-comodidad` and the en twin: the target lands at **72 px** (56 + 16) at 390 and 1440 |
| What the gate's anchor step actually picked | `/es/docs/`: **no target** (step skipped); `/es/oracle/`: `#ttod-aviso` (F4) |
| Landing and 3D graph under the 56 px bar | `.valle` top 0 behind the solid bar, title clear of it (screenshot checked). `/es/graph/` scene ends 5 px short of the viewport at 390 (`--sendero-nav: 61px`, F8d) |
| e2e graph specs (`graph-island`, `graph-keyboard`, `graph-url-state`, `graph-performance`) on the stack with system Chrome | **16/17 pass**. `graph-keyboard.spec.ts:65` (ArrowDown on a `<select>`) fails, and it fails the same way against a `git archive` of `53855a59`, so it predates AA3 (macOS Chrome opens the picker) |
| Scope | `git diff 53855a59 -- ttod.yml proposals services/backend` is empty; `is:inline` 1 → 1; `banda-arriba`, `cabecera-flujo` and `overlayHeader` are gone from `src` |

## Findings

| # | Sev | Blocks DONE | Finding and evidence | Fix |
| - | --- | ----------- | -------------------- | --- |
| F1 | **P1** | yes | **The service worker freezes the session-aware header on the Oracle pages.** `public/sw.js:9` lists `/en/oracle/` and `/es/oracle/` as `OFFLINE_PAGES`; `:53` precaches them with a credentialed `fetch` at install time; `:142-151` serves them `cacheFirst` forever. Before AA3 that HTML did not depend on the session. Now `Page.astro:23` and `:256-259` put `Entrar`, or the username + `Biblioteca`, into it. Probe `p2.mjs`: (1) the worker installs on the anonymous login page (the normal first visit), the student signs in, and `/es/oracle/` shows **`Entrar EN`** while `/es/wisdom/` shows `Biblioteca Ada Lovelace Byron EN`. (2) The worker installs while signed in (any future `CACHE_NAME` bump does this for every signed-in student), the student logs out (session 401), and `/es/oracle/` shows **`Biblioteca Ada Lovelace Byron EN`**, with `title="Ada Lovelace Byron"`. Without a username the `title` is the **email** (`Page.astro:258`). This breaks Acceptance item 2 on one of the four primary views. It also leaks personal data to the next person on a shared lab browser. It contradicts the AA2 carry that the Oracle's sign-in notice should agree with the header | In `sw.js`: precache `OFFLINE_PAGES` with `fetch(url, { cache: 'no-store', credentials: 'omit' })`; serve navigations to them **network-first**, with the cache only as the offline fallback; bump `CACHE_NAME` to `v8` so that caches already holding a name are purged. Optionally send `Clear-Site-Data: "storage"` from `/{l}/logout` and logout-all. Add a browser-check step that signs in, visits `/es/oracle/`, and asserts the header shows the account; then logs out and asserts no username or email in the HTML. `sw.js` is in AA4's PWA lane, so see "Downstream" below |
| F2 | P2 | no | **A backend stall now hangs every public page for signed-in users.** `getSessionUser` (`auth.server.ts:113-129`) calls `fetch` with no timeout, and the layout now calls it on every page that does not pass `usuario` (`Page.astro:23`). With the backend container paused, anonymous `/es/wisdom/` answered 200 in 7 ms, but a signed-in request got nothing in 20 s (undici waits about 300 s). Before AA3, wisdom, the landing and docs never waited on the backend. The reviewer 403 path also asks twice: `requireRole`, then `Page` again (`reviewer/index.astro:50`, `usuario={reviewer ?? undefined}`). Normal cost is fine (+1–2 ms) | Give the session lookup a short `signal: AbortSignal.timeout(1500)` (precedent: `grafo.server.ts:37`). If it times out, render the signed-out header. Pass the user from `requireRole` to `Page` on the 403 path, or return it with the 403 |
| F3 | P2 | no | **The header still slides away, animated, under reduced motion.** The spec row "Hide-on-scroll … none under reduced motion" (phase `:30`) is not met. `.ttod-site-header[data-oculta]:not([data-open]):not(:focus-within)` (`Page.astro:206-209`, specificity 0,4,0) sets its own `transition` and beats `.ttod-site-header { transition: none }` (`:124-126`, 0,1,0). Measured at 390 with `reducedMotion: 'reduce'`: `transition: transform 0.3s …`, `transform: translateY(-56px)`. This predates AA3 (base `Page.astro:121-131`), but AA3 rewrote the block, and its Acceptance says "reduced-motion verified". The browser check only counts the login sky's frames | Wrap the hide rule in `@media (prefers-reduced-motion: no-preference)` (no hiding at all), or skip setting `data-oculta` in JS when `matchMedia('(prefers-reduced-motion: reduce)')` matches. Add a step to `aa3-browser-check.mjs`: scroll at 390 with reduced motion and assert the header stays visible |
| F4 | P2 | no | **The gate's anchor spot-checks prove nothing, and the report says they passed.** `aa3-browser-check.mjs` step 4 takes the first id below 900 px, wrapped in `if (id)`. On `/es/docs/` the selector `h2[id], h3[id]` finds **no** target, so the step is skipped. On `/es/oracle/` it picks `#ttod-aviso`, the 1 px visually hidden live region after the footer. The `/es/account/reviewer/` entry is dead (`sel = null`). Report §3 ("Anchors on `/es/docs/` and `/es/oracle/` land below the header") is an overclaim. The behaviour itself is right: my probe on `/es/docs/introduction/#…` lands at 72 px at both widths | Point the step at `/es/docs/introduction/` (last `h2[id]`) and a real in-`main` id on the Oracle page, and **fail** when no target is found. Correct report §3 |
| F5 | P2 | no | **The account link's accessible name is the bare username.** `Page.astro:258` renders `{usuario.display_name ?? nav.account}`, so screen readers announce "Biblioteca, Ada Lovelace Byron, English (EN)" and nothing says the link is the account (WCAG 2.4.4 / 2.4.6). The group label "Tu cuenta e idioma" is only read on entry to the group. Report §5 raises this. On a related point, `.ttod-cuenta` (`:155`) uses `inline-block; line-height: 44px` while its neighbours use `inline-flex; align-items: center`, so the name sits about 2 px low (visible in `header-es-in-768.png`) | `<span class="ttod-sr-only">{nav.account}: </span>{name}`. This keeps the visible text inside the name (2.5.3) and drops the need for `title`. Give `.ttod-cuenta` the same `inline-flex` alignment, and truncate an inner `<span>` |
| F6 | P3 | no | **Account show/hide toggles.** The a11y tree shows three buttons that are all named **"Mostrar"**. After a press, it reads **`button "Ocultar" [pressed]`**: the name flips *and* `aria-pressed` flips, which is a double negative (`verContrasena.ts:15-16`). Login and register already do this right, with a fixed `aria-label` plus `aria-pressed` (`register.astro:141-144`, `acceso.ts`). So two helpers now do the same job. The comment at `Page.astro:301` says `enlazarVerContrasena` serves "la cuenta y del registro", but register uses `acceso.ts` | Use one helper. Give each button a stable name that says which field it controls ("Mostrar la contraseña actual"), and let `aria-pressed` carry the state. Correct the comment |
| F7 | P3 | no | **The account form has no client-side mismatch check.** The spec asks for one (phase `:52`, "client and server reject mismatch, same rule as A24"). The form is `novalidate` (`account.astro:166`) and the confirm field has no `data-igual-que`, so only the server checks. The two pages also answer a mismatch differently: register 200, account 400 | Move the `data-igual-que` check out of `acceso.ts` into a shared module, wire it from the layout script, and add `data-igual-que="cuenta-nueva"` to the confirm field. Pick one status for both pages |
| F8 | P3 | no | **Legibility and overclaims.** (a) Report §2: "Escape and an outside tap close it and return focus to the button". An outside tap calls `cerrar(false)` (`Page.astro:337-342`); my probe shows focus on `<body>`. That behaviour is reasonable, but the sentence is wrong (the spec row at `:29` asked for it too). (b) The comments at `cookie-security.ts:32-33` and `logout.ts:20` say a cookie deleted with different attributes "is treated as another cookie and not deleted". Browsers identify a cookie by name + domain + path; `HttpOnly` and `SameSite` play no part, and `main`'s `{ path: '/' }` already deleted it. Students will learn a myth. The F37 unit test (`shell-polish.test.ts`, last block) only asserts the helper's own return value, so it would pass either way. (c) `Page.astro:359-360` still says "la pastilla vuelve" (the pill is gone). (d) `SenderoAforismos.svelte:1940-1944`: `--sendero-nav: 61px`, "61 px es lo que mide la barra". The bar is now 56, and `/es/graph/` leaves a 5 px strip at 390. (e) `paginaProhibida`'s HTML is never served in production: its only caller, the reviewer page, discards the body and renders its own shell. Say so at `auth.server.ts:186-190`. (f) AA3b's carry asked AA3 to decide whether a deep link should land with the header hidden at 390. It does (docs probe: header bottom 0 after the jump), and neither the report nor the phase records the decision | (a) Correct the report, or return focus on outside taps only when focus was inside the panel. (b) Reword: "name, Path and Domain identify the cookie; reusing the set attributes keeps the delete header identical to the set". Make the test assert that `logout.ts` and the `logout-all` branch call `cookies.delete` with `atributosSesion(request)`. (c) "la barra". (d) `height: calc(100svh - var(--ttod-header-height))` and delete the constant. (e) One comment line. (f) One line in the report |
| F9 | P3 | no | **A non-form POST returns 500.** `account.astro:39` calls `await Astro.request.formData()` unguarded, so `application/json` throws (live: 500 with a stack trace in the log). This cannot be exploited: nothing changes state, and a cross-site JSON request needs a preflight. `login.astro:32` already did the same on `main` | `try { form = await Astro.request.formData() } catch { return new Response(null, { status: 415 }) }` on both pages |
| F10 | P3 | no | **Deliverables and small targets.** The phase's deliverables (`:68`) include a "live HTML inventory (en + es), signed-in and signed-out; keyboard smoke note". Neither is in `baselines/aa3-2026-11-11/` or the report; the gate's Python run covers part of it, but nothing is filed. The `EN`/`ES` switch is **19 × 44 px**. That passes WCAG 2.5.8 through the spacing exception, but it is far below the 44 px habit the rest of the bar follows | File the inventory (the gate's signed-in and signed-out HTML, saved) and a five-line keyboard note, or record that the gate replaces them. Give the language switch `padding-inline: .75rem` |

## Checklist answers

1. **Acceptance and the header spec.**
   - Holds:
     - full width, no radius, 56 px token, no hamburger at 768, the language switch quiet (my run of the check and
       the screenshots);
     - Entrar never self-`next`;
     - Cuenta and Biblioteca when signed in, en and es, on SSR pages;
     - `#id` lands below the bar (my docs probe);
     - library cards with `id` and localized sections (live, gate);
     - the password change end to end, wrong current refused, other browser signed out (live, both `revoke_others`
       modes);
     - the graph bilingual (check step 6, unit test);
     - the skip link reaches `main` on every page.
   - Does not hold:
     - item 2 on `/{l}/oracle/` once the service worker is installed (F1);
     - "reduced-motion verified" covers the sky only (F3);
     - the spec rows for an outside tap returning focus (F8a) and client-side mismatch (F7);
     - deliverable "HTML inventory / keyboard note" (F10).
   - The UX rule comes from the runner log, not re-measured.
2. **Auth and security.**
   - CSRF: Astro 5.18 `checkOrigin` (default on) refuses every form encoding without a same-origin `Origin`.
     `SameSite=Lax` also keeps the cookie off cross-site POSTs.
   - Rotation: the caller keeps a fresh cookie, and the old token dies.
   - `revoke_others`: correct both ways. Unchecked sends `false`, and the backend then revokes only the caller's
     old sid.
   - Error paths: they leak nothing. `401` and `403` from the backend both read as "wrong current password", which
     fits because `requireUser` ran first. There is no lock-out path beyond the backend's `account` throttle (429,
     localized).
   - logout-all: deletes with matching attributes and goes home.
   - `next`: cannot become an open redirect.
   - The 403 page: nothing injectable.
   - The session lookup costs one Redis-backed round-trip per signed-in view, cheap when healthy. Without a timeout
     it couples every public page to the backend (F2).
   - The real hole is outside the BFF: the service worker cache (F1).
3. **Accessibility.**
   - The disclosure pattern is right: a button with `aria-expanded` and `aria-controls`, a `display:none` panel, no
     trap, Escape returns focus.
   - The focus order is skip → brand → Menú/links → utility.
   - The language switch: its `aria-label` "English (EN)" contains the visible "EN", and `lang`/`hreflang` are
     correct.
   - Open issues: the account name (F5), the toggles (F6), reduced motion (F3), the 19 px switch (F10).
4. **Regressions.**
   - AA3b locators and hooks: its browser check passes on my stack.
   - The landing's pinned scenes: they sit under a solid 56 px bar with the title clear.
   - CSP: unchanged.
   - The e2e graph specs: 16/17, and the one failure predates AA3.
   - GraphIsland: the stage box and the moved legend pass the English e2e selectors.
   - The removed wrapper: nothing depends on it.
   - Leftovers: the stale `61px` and "pastilla" (F8).
5. **Legibility.**
   - The header and account code read well cold: `enlaces-cuenta.ts` is twenty lines with its rule in the comment,
     and the account page's `intent` dispatch is linear.
   - What would mislead a student: the cookie-identity myth (F8b), the two password-toggle helpers (F6), and three
     report sentences (F4, F8a, and §2's reduced-motion claim).
6. **Scope.** Clean.

## Downstream phases to amend (I edited no file but this one; the orchestrator should commit these with it)

- **AA4** (`PHASES/AA4-seo-robots-and-meta.md`, item 3 "PWA: document Oracle-only offline OR add shell"): every
  page's HTML now carries per-user header state. Any offline page or shell must be fetched with
  `credentials: 'omit'` and served network-first. The `CACHE_NAME` bump that F1 needs belongs to whichever phase
  ships the fix (AA3 amendment preferred, because AA3 caused it).
- **AA3** (this phase file): record the outcome of F3 (reduced motion) and F8f (header hidden after a deep link at
  390) under the Header spec.
