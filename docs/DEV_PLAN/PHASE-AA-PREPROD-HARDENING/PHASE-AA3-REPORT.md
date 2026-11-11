<!--
AA3 report: classic header, account User section, library layout, 2D graph in Spanish, shell a11y hygiene.
Author: Rubén Vega Balbás PhD (agent-assisted). Status VERIFYING. The agent does not mark DONE.
-->

# PHASE-AA3 report: header, account, library, shell hygiene

**Status:** VERIFYING (2026-11-11) · cold review pending · **Branch:** `cascade/PHASE-AA-PREPROD-HARDENING-3` · **Exit gate:**
[`PHASES/AA3-nav-a11y-and-url-hygiene.exit-gate.sh`](PHASES/AA3-nav-a11y-and-url-hygiene.exit-gate.sh) plus
[`scripts/aa3-browser-check.mjs`](scripts/aa3-browser-check.mjs), both written before the code (commit `35385ed5`). The gate also
re-runs AA3b's browser check, so every locator must survive the new header.

## 1. What changed for a student

| Before | Now | Evidence |
| ------ | --- | -------- |
| A floating pill, with the language switch as its strongest element; hamburger already at 832 px | A full-width bar 56 px high (`--ttod-header-height: 3.5rem`) with four links, *Sabiduría · Grafo · Oráculo · Docs*, and a quiet `EN`/`ES` code. No hamburger until 40rem | [`header-*-{390,768,1440}.png`](baselines/aa3-2026-11-11/) |
| No account in the header; the footer always said "Log in" | Signed out: **Entrar**, which returns you to the page you were on. Signed in: **Biblioteca** and **Cuenta**, which shows your username once set | `header-{es,en}-{out,in}-*.png` |
| `/library` was bare HTML with raw section slugs | The same stele cards as wisdom, with a localized section, the saved date and a styled button; EmptyState when empty, and a 503 alert when the service fails | [`page-es-library-390.png`](baselines/aa3-2026-11-11/page-es-library-390.png) |
| `/account` showed only the email and roles | **Perfil** (username, editable), **Contraseña** (current, new, confirm, show/hide, "close my other sessions" on by default) and **Sesiones** ("sign out of this session" or "of every session") | [`page-es-account-390.png`](baselines/aa3-2026-11-11/page-es-account-390.png) |
| The 2D graph was English on `/es/`, with CLS 0.47 | Spanish on `/es/`; CLS **0.098** (two runs: 0.0984, 0.0983) | §3 |

## 2. Deliverables (findings → files)

- **Header (F56, A31; F7/A6, F10/A9, F38/A26):** `layouts/Page.astro`.
  - The bar reads the session once: from the page's `usuario` prop if the page already knows it, otherwise from
    `getSessionUser`, which only asks the backend when a session cookie exists.
  - Below 40rem it becomes a disclosure menu (WAI-ARIA APG): the panel opens below the bar and pushes content, with
    48 px rows and **no focus trap**. Escape and an outside tap close it and return focus to the button.
  - Hiding on scroll applies only below 40rem.
  - Kept from earlier phases: the server-side `data-collapsible`, the `<noscript>` fallback, the network status
    region, and AA3b's hooks (`cambioIdioma`, `data-cambio-idioma`, `#ttod-aviso`, and the module imports in the
    header script).
  - The 61 px band hack is gone (`--ttod-cabecera-flujo`, `--ttod-banda-arriba` and `overlayHeader`), because a
    solid bar needs no painted band behind it.
- **Sign-in link (F9/A8):** `lib/enlaces-cuenta.ts` serves header and footer alike. On the login or register page
  it keeps a safe incoming `next`, or asks for none; it never points at login itself.
- **Skip link (F11/A10):** every page's own `<main>` carries `id="ttod-main"`. The landing and the 3D graph wrap
  their hero or island inside that `<main>` (both already override the 48rem reading column), so skipping does not
  jump past content.
- **Reduced motion (F12/A11):** `cielo.ts` already stopped its loop. Verified in the browser: fewer than 10
  animation frames in 2 s on `/es/login/` under `prefers-reduced-motion`.
- **2D graph (F32/A20):** `GraphIsland` takes `lang`; its copy lives in `graphIslandCopy.ts`, and the Spanish
  section names come from Sabiduría's `rotuloSeccion`. Without `lang` it stays English, which is what the e2e
  specs expect.
- **F60:** the graph box keeps its 960:620 size from the first paint, and the legend, which grows with the data,
  now sits below the details panel.
- **Library (F53/A33):** `pages/[locale]/library.astro`. Each card is an `Estela` with `id={quote.id}`
  (LOCATORS `/{l}/library/#id`), newest first.
- **Account (F55/A35):** `pages/[locale]/account.astro` handles its own three forms server-side (`intent=profile |
  password | logout-all`) through new helpers in `lib/auth.server.ts` that call AA2's endpoints.
  - On success it redirects with a flash (`?ok=…#block`).
  - On failure it re-renders with a localized error: status 400, 401 for a wrong current password, 429 throttled.
  - A password change stores the **rotated** session cookie, so the caller stays signed in.
  - The show/hide buttons come from the server `hidden` and are switched on by `lib/verContrasena.ts` from the
    existing header script.
- **Shell polish (F33/A21, F34/A22, F35/A23):**
  - `quote.astro` shows EmptyState, or a 503, instead of throwing a 500;
  - `requireRole` returns a localized HTML 403;
  - the reviewer queue renders the full shell with the message;
  - account, library, quote and reviewer pages use the shell classes.
- **Register confirm (F36/A24):** a confirm field. The server refuses a mismatch before calling the backend, and the
  client warns early through `setCustomValidity` in the existing `acceso.ts`.
- **Logout attributes (F37/A25):** `lib/cookie-security.ts atributosSesion()` is the single definition used by
  login, register, the password change, logout and logout-all, both to set and to delete.
- **Registry:** the account row (`#profile #password #sessions`) moved from `owner: AA3` to `auth: true`, and the
  registry test now renders it with a session.

## 3. Evidence

- **Contract tests** (the five files named in the gate, plus the registry and middleware tests), the full suite
  (**269 tests, 41 files**), and `astro check` with 0 errors. The runner's log is
  [`PHASES/AA3-nav-a11y-and-url-hygiene-VERIFY-LOG.md`](PHASES/AA3-nav-a11y-and-url-hygiene-VERIFY-LOG.md).
- **Live, isolated stack** (the gate's Python run, from a fresh stack):
  - Signed out: the header shows Entrar with `next` and no Library; the nested route is marked current; each page
    has exactly one `main#ttod-main`.
  - A real student signs in through the form in two "browsers". Setting the username shows it in the header.
  - A wrong current password is refused with no cookie set, and a confirm mismatch is refused.
  - The real change answers 303 with a rotated cookie, which is not `Secure` over HTTP. The caller stays signed in,
    the second browser gets 401, and the old password gets 401.
  - The saved quote renders as a stele card in `/es/library/`.
  - A student on the reviewer queue gets a 403 HTML page with `lang="es"`.
  - Logout deletes the cookie with `Path=/`, `HttpOnly` and `SameSite=Lax`.
- **Browser** (`aa3-browser-check.mjs`):
  - **Header:** full width, height equal to the token (±1 px), no radius, at 390/768/1440 in en and es; the
    language switch is transparent and no larger than the links; no hamburger and exactly 4 visible links from
    40rem; a menu button below that.
  - **Menu:** rows of at least 44 px, the panel pushes `main` down, Tab leaves the panel (no trap), Escape returns
    focus to the button.
  - **Skip link:** it is the first Tab stop and lands on `main#ttod-main`.
  - **Anchors** on `/es/docs/` and `/es/oracle/` land below the header.
  - **Reduced motion:** the login sky does not animate.
  - **2D graph:** `/es/graph/plano/` has no English UI strings.
  - **CSP:** reports no higher than AA1 on 6 views.
- **AA3b browser check, re-run:** every anchor and locator check still passes, including the throttled deep links.
- **AA0 UX rule** (Lighthouse 12.6.0, 390, on Tanit; [`baselines/aa3-2026-11-11/ux/`](baselines/aa3-2026-11-11/ux/ux-baseline.json)):

  | View | a11y | CLS | LCP | AA0 reference (a11y / CLS / LCP) |
  | ---- | ---- | --- | --- | -------------------------------- |
  | `/es/` | 100 | 0.0130 | 5119 ms | 100 / 0.0130 / 5047 |
  | `/es/wisdom/` | 100 | 0.0000 | 2409 ms | 100 / 0.0000 / 2330 |
  | `/es/graph/` | 100 | 0.0003 | 2405 ms | `/es/graph/path` 100 / 0.0003 / 4959 |
  | `/es/graph/plano/` | 100 | **0.0984** | 2257 ms | AA3b baseline: CLS 0.4702 |

  Taking the band hack away did not move CLS on `/es/graph/`, the dark view the phase asked about.

## 4. Amendments (disclosed)

- **Browser check, strengthened during AA3:** it now asserts that exactly 4 primary links are *visible* from 40rem.
  - Why: my own screenshot strip showed "Inicio" still visible in the desktop bar. A more specific
    `display: inline-flex` rule beat the class that should hide it, and the unit test excluded that link by class
    instead of checking what renders.
  - Fixed in `Page.astro`.
- **Account `dl` stacks below 30rem:** found in the same screenshot pass (the email wrapped letter by letter at 390).
- **Account test harness:** the test reads the cookie jar the Node adapter reads (`Symbol.for('astro.cookies')`),
  because the Astro container does not write `Set-Cookie` itself. Live, the gate checks the real header.
- **Tests updated to the new markup, not weakened:**
  - register tests send the confirm field;
  - the logout delete check matches on the shared attributes;
  - the library test reads the stele card.

## 5. Decisions taken while implementing (for the reviewer to challenge)

- **`Page.astro` asks for the session itself when a page does not pass `usuario`.** That costs one backend call per
  signed-in page view (none for anonymous visitors). The account, library and reviewer pages pass the user they
  already have.
- **The username replaces "Cuenta" in the bar** (truncated at 12ch, full name in `title`). The account link's
  accessible name is therefore the username. Read with the Biblioteca link next to it, that seemed clear enough.
- **The account forms post to the page itself** rather than to API routes, following the login page's pattern
  (PRG, server-side validation, JS optional).
- **"Sign out of every session"** uses `logout-all`, which also signs the caller out (AA2 carry), so it redirects home.

## 6. New findings

- **F62 (P3):** in `Breadcrumbs`, the current (last) item sits a few px higher than the links (visible in the
  library and quote shots). It predates AA3; a style fix belongs to AA4's polish or a student task.

## 7. Rollout (owner)

Run `make rebuild` on Tanit; there is no backend change. Signed-in students see **Cuenta** and **Biblioteca**
right away. The username shows once they set it under `Mi cuenta → Perfil`.
