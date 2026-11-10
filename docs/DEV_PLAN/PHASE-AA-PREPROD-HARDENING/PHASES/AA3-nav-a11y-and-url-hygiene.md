# PHASE-AA3: Header, a11y, graph i18n, account and library UX

> **Track:** Astro shell — F7, F9–F12, F32–F38, F53, F55 (UI), F56, F58 · A6, A8–A11, A20–A26, A31, A33, A35.  
> **Status:** BLOCKED until AA0 DONE · **may run parallel to AA1/AA2 and AA3b**  
> **Amended 2026-11-10:** URL/locator work (F8, F49–F52, F54, F57) moved to [AA3b](AA3b-locators-wisdom-and-graph-ia.md).
> Header redesign, library layout, User section and anchor offset added here.

## Goal

Replace the floating pill with a classic, minimal, responsive header that carries account
state. Fix the broken `/library` layout. Give `/account` a User section (username + change
password). Localize GraphIsland. Finish account/quote shell polish and a11y hygiene.

## Header spec (F56)

The current pill is a centred floating capsule whose strongest element is the language switch.
Target: the conventional pattern that public-sector and editorial design systems have converged
on, because readers already know it (see References).

| Aspect | Spec |
| ------ | ---- |
| Container | Full-width `position: sticky; top: 0`. Solid paper background, 1 px hairline bottom border (`--ttod-color-line-subtle`), **no radius, no floating shadow** (a faint shadow only once `data-scrolled`). Inner row aligned to the page measure (`max-width` token), 16–24 px gutters |
| Height | Fixed **`--ttod-header-height: 3.5rem`** (56 px; tune in AA3, keep it a token). SSR'd height so there is no CLS. The `--ttod-banda-arriba` box-shadow trick becomes unnecessary and is removed |
| Left | Brand `道 TTOD` = home link. **Drop the "Inicio/Home" item** from the bar (keep it in the mobile panel and the footer) |
| Primary | 4 text links: Sabiduría · Grafo · Oráculo · Docs. Sentence case (not tracked uppercase), `--ttod-font-ui`, ~15–16 px. Current page = 2 px seal underline + `aria-current="page"` with **prefix match** (F38/A26) |
| Utility (right) | `Biblioteca` only when signed in. Signed out: **`Entrar`** text link (`?next=` = current path, never login itself, F9). Signed in: **`Cuenta`** link showing `display_name` if set (F55). Language: quiet text link **`EN` / `ES`** with `hreflang` + `lang`, visually below the nav, never an ink pill |
| ≥ 64rem | Everything inline |
| 40–64rem | Primary stays visible; utility compresses (language as code, account as short label). **No hamburger on tablets** |
| < 40rem | Brand + `Menú` button. **Disclosure navigation** (WAI-ARIA APG pattern, `aria-expanded`/`aria-controls`) opens a full-width panel *below the bar* that pushes content, with 48 px rows: primary, then utility, then language. Non-modal, so **no focus trap**. Escape and outside-tap close and return focus to the button (keep the current handlers). If AA3 prefers an overlay sheet instead, it must be a modal `<dialog>` (native trap), not a hand-rolled trap |
| Hide-on-scroll | Optional and only < 40rem. Must keep the shipped rules: reveal on Tab or focus-within, `visibility: hidden` when away, none under reduced motion |
| Anchors (F58) | `html { scroll-padding-top: calc(var(--ttod-header-height) + 1rem) }` once. Remove the local patches in `oracle.astro` and `CodigoGrafo` |
| Keep | 44 px targets, the `<noscript>` no-CLS lesson, the network status live region, skip link → `<main id="ttod-main">` (F11) |

Proof: screenshot strip at 390 / 768 / 1440 px × en/es × signed-out/signed-in, plus Lighthouse a11y
and CLS before/after on `/es/`, `/es/wisdom/`, `/es/graph/` (a dark view, to confirm the band hack is gone).

## Library layout (F53)

Wrap in the shell measure. Each saved quote renders as the wisdom `Estela` card (or a shared
quote-card component extracted from it, if AA3 prefers), with a localized section label
(`rotuloSeccion`), saved date, `FavoriteButton` styled with the existing button tokens, and
`id={quote.id}` (anchor per [LOCATORS](../LOCATORS.md)). The empty and failed states reuse `EmptyState`
(the 503 stays). Both `/en/library/` and `/es/library/`.

## User section (F55, UI half)

`/account` gains three blocks with anchors `#profile`, `#password`, `#sessions`:

- **Perfil / Profile:** username (`display_name`, editable when A34 ships `PATCH /auth/profile`;
  read-only "—" until then), email read-only, roles.
- **Contraseña / Password:** current + new + confirm (client and server reject mismatch, same rule as
  A24), `autocomplete="current-password"`/`"new-password"`, visible-password toggle, server error
  messages localized, a success flash after a PRG redirect. Posts to the BFF, which calls A34's
  `POST /api/v1/auth/password`.
- **Sesiones / Sessions:** "Cerrar las demás sesiones" (on by default when changing password),
  plus the existing log out.

Depends on **A34** (AA2) for the endpoints. The UI may land first behind "coming soon" copy only
if the AA0 report allows it; otherwise it waits.

## Deliverables

- Header per spec (A31) including the session-aware account entry (A6), footer `next` (A8) and library gate cue (A9).
- Library layout (A33); account User section (A35); account/reviewer/quote shell polish (A21).
- `aria-current` prefix (A26); skip link on `<main>` (A10); reduced motion (A11).
- GraphIsland localized (A20). If AA0 adopts the AA3b graph IA, it now renders at `/graph/plano/`.
- Empty-state not 500 (A22); localized Forbidden (A23); register confirm (A24); logout attrs (A25).
- Live HTML inventory (en + es), signed-in and signed-out; keyboard smoke note; screenshot strip; cold review.

## Scope

**In:** `services/frontend` shell (`Page.astro` owner), `Footer.astro`, account/library/quote/reviewer
pages, GraphIsland copy, auth pages.  
**Out:** URL policy, ids, search, graph routing (AA3b); SEO/PWA files (AA4); cookie Secure /
allowedDomains / password endpoint (AA2); brand, fonts or palette changes.

## Prompt (Implementation Agent)

```text
Implement PHASE-AA3 per
docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING/PHASES/AA3-nav-a11y-and-url-hygiene.md.

## Deliver
1. Header per "Header spec (F56)": full-width sticky bar, 4 primary links, utility cluster
   (Library when signed in, Entrar/Cuenta, quiet EN/ES), disclosure menu < 40rem,
   --ttod-header-height token + global scroll-padding-top; remove band hack and local patches.
2. Footer next + library gate; aria-current prefix; skip-link on <main>; reduced-motion.
3. /library layout with shared quote card, localized labels, ids, EmptyState.
4. /account User section (#profile #password #sessions) on top of A34 endpoints.
5. Localize GraphIsland; shell polish account/reviewer/quote; empty-state not 500;
   localized Forbidden; register confirm; logout cookie attrs.
6. Screenshot strip 390/768/1440 × en/es × in/out; Lighthouse a11y+CLS before/after;
   cold review. Do not self-certify DONE.

## Constraints
- Reuse tokens/fonts/icons: restyle a component, do not re-brand. Bilingual.
- Do not commit unless asked.
```

## Carried from AA1 (amended 2026-11-10)

- **CSP (AA1, live in report-only):** add no new inline `<script>`; when you touch a layout or page script, prefer moving it to a module. Every inline script is one more hash to manage at enforcement (PHASE-AA1-REPORT §4). Re-run `baselines/aa1-2026-11-10/browser-smoke.mjs`: the CSP report count must not grow.

## Acceptance

- [ ] Header is full-width, not a pill; language switch is not the dominant element; no hamburger at 768 px.
- [ ] Signed-out header shows Entrar (never `next=/…/login`); signed-in shows Cuenta (+ Biblioteca), en and es.
- [ ] `#id` jumps land below the header on every view (spot-check `/es/oracle`, `/es/docs/…#heading`).
- [ ] No UX regression on `/es/` and `/es/wisdom/` at 390 px under the [AA0 regression rule](../PHASE-AA0-REPORT.md#5-ux-baseline-the-no-regression-reference) (re-run `baseline.sh` into this phase's own folder).
- [ ] `/en/library/` and `/es/library/` render as styled cards with localized section names.
- [ ] Changing password from `/account#password` works end-to-end, rejects a wrong current password, and signs out another browser.
- [ ] Graph UI bilingual; skip link → main landmark; reduced-motion verified.
- [ ] Cold review green or amended.

## Risks

- **Cookie SSR mismatch:** test logged-in and logged-out HTML (the header now branches on session).
- **The landing hero was tuned against a 61 px header in flow.** Re-check the hero's pinned scene
  and the measurements quoted in `Page.astro` comments after the height change.
- **Losing the shipped mobile-header lessons** (CLS 0.19 from client-side collapse). Keep the server-side `data-collapsible`.

## References

- GOV.UK Design System, *Service navigation* component (full-width bar, text links, current-page indicator).
- WAI-ARIA Authoring Practices, *Disclosure Navigation Menu* example (button + `aria-expanded`, no focus trap).
- Nielsen Norman Group, *Hamburger Menus and Hidden Navigation Hurt UX Metrics* (keep primary links visible when they fit).
- WCAG 2.2: SC 2.4.11 *Focus Not Obscured (Minimum)*; SC 2.5.8 *Target Size (Minimum)*.
