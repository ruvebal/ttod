# PHASE-AA7: Astro 5 → 7 major upgrade

> **Track:** frontend platform. It closes F19's deferred majors (PHASE-AA5-REPORT, lane B cold review F4).
> **Status:** IN_PROGRESS 2026-11-11 (AA5 DONE). It runs before AA4 and AA6, by owner order ("AA7 -> AA4").
> It must land **before AA6** (the close-out and Phase T handoff): the AA5 guard says "the Astro major upgrade
> comes before any public exposure".
> **Planned:** 2026-11-11, at the owner's request ("get ready for astro upgrade in a dedicated phase").

## Goal

Move `services/frontend` from Astro 5.13 to Astro 7.x with every official integration on its matching major.
No visible change, and no lost guarantee: every earlier AA gate still passes, the production `npm audit` has no
critical or high advisory left, and students meet the same site.

## Why a dedicated phase

Two majors in one jump (v6, then v7) change the compiler (Go → Rust), the bundler (Vite 6 → 8), the Markdown
pipeline (unified → Sätteri), HTML whitespace, and how env variables are inlined. Every AA phase built a guarantee
on the frontend: AA1 headers and CSP, AA2 cookies and Host, AA3b locators, AA3 header and account, AA5 Host guard.
The only honest proof is to re-run all of them, so the gate composes them.

## Where TTOD is affected (mapped 2026-11-11 from the official guides)

| Change | v | TTOD impact | Planned step |
| ------ | - | ----------- | ------------ |
| `import.meta.env` values are always inlined at build time | 6 | `import.meta.env.BACKEND_URL` in ~10 server modules (`lib/*.ts`, `content/wisdom.ts`, pages) becomes a build-time constant | One `lib/backend.ts` reading `process.env.BACKEND_URL` at request time; replace every use; a test that the runtime value wins |
| Zod 4; import `z` from `astro/zod` | 6 | `src/content.config.ts` (`docs` collection schema) | Switch the import; check the `order`/`locale` schema under Zod 4 |
| Container API: `getContainerRenderer` from `@astrojs/<x>/container-renderer` | 7 | 6 test files (React; Svelte if added) | Update the imports; Astro container tests stay in the Node environment (v6: no jsdom for Astro components) |
| `compressHTML` default `'jsx'` (whitespace between inline elements stripped) | 7 | Header utility row, stele foot, breadcrumbs, any `{a} · {b}` text | First pass: pin `compressHTML: true` (old behaviour), then decide per view with screenshots |
| Rust compiler: invalid HTML is a build error; CSS output may change | 7 | Unknown until the first build | Fix what the build reports; compare the CSP inline-script count (AA1) and the screenshots |
| Sätteri renders `.md`/`.mdx`; heading-id rules change (trailing hyphen kept in v6) | 6/7 | `src/content/docs/**` headings and anchors; the AA3 gate's docs anchor check | Diff the docs heading ids before and after; keep `@astrojs/markdown-remark` with `processor: unified()` if they change |
| `Astro.url.pathname` may be partly decoded | 6 | `lib/locators.ts` (open-redirect guard, slash policy) and slug routes | Re-run `middleware.test.ts` and the AA3b and AA5 `//host`, `/\host` and malformed `Host` probes |
| `i18n.routing.redirectToDefaultLocale` defaults to `false` | 6 | Root `/` redirects through `pages/index.astro`; `prefixDefaultLocale: true` | Set both explicitly |
| Official adapters on a new major | 6/7 | `@astrojs/node` 9 → 11, `@astrojs/svelte` 7 → 9, `@astrojs/react`, `@astrojs/mdx` 4 → 8, `@astrojs/check` | `npx @astrojs/upgrade`, then read each CHANGELOG for the standalone Node server, `security.allowedDomains` and the form origin check (AA2 F23) |
| Vite 8 (Rolldown) | 7 | `@tailwindcss/vite`, the Svelte plugin, Vitest (`getViteConfig` needs a matching Vitest) | Upgrade Vitest with it; the PWA guard and its `/_astro/` asset scan |
| Node ≥ 22.12 | 6/7 | `node:22-alpine` images, CI `node-version: "22"` (both resolve to the latest 22.x) | Pin `22.12` or later in `.nvmrc` and CI |

**Not affected** (checked): no `Astro.glob`, `<ViewTransitions />`, `astro:transitions` internals, `@astrojs/db`,
`experimental` flags, remark or rehype plugins, `src/fetch.ts`, `define:vars`, spread props or server islands.

## Deliverables

1. Astro 7.x and matching official integrations; `package-lock.json` regenerated; Node floor pinned.
2. The runtime `BACKEND_URL` reader (`lib/backend.ts`) with a test.
3. Config: `compressHTML` decided and recorded; explicit i18n redirect options; the Markdown pipeline decided by the
   heading-id diff.
4. Container-renderer imports updated; Vitest on the version `getViteConfig` needs.
5. Evidence in `PHASE-AA7-REPORT.md`:
   - `npm audit --omit=dev` before and after (target: 0 critical, 0 high);
   - the docs heading-id diff;
   - the CSP inline-script counts;
   - the AA0 UX rule;
   - a screenshot strip of `/es/`, `/es/wisdom/`, `/es/graph/` and `/es/account/` before and after, at 390 and 1440.
6. Cold review.

## Scope

**In:** `services/frontend/**` (package files, config, the code the migration needs), `.nvmrc`, the CI Node pin.
**Out:**
- any new feature or redesign;
- backend and Compose changes, except a Node pin. *Amended during AA7:* one Caddy guard is in scope (`@rutadoble`,
  404 for `//` and `/\` paths), because Astro 7 hides those paths from the app behind a proxy (report §3b);
- AA4's SEO work. If AA4 lands first, AA7 keeps its output; if not, AA4 rebases onto AA7.

## Exit gate (planner, written with this file)

[`AA7-astro-major-upgrade.exit-gate.sh`](AA7-astro-major-upgrade.exit-gate.sh) checks the versions and the audit,
then re-runs the AA2, AA3b, AA3 and AA5 exit gates unchanged. A guarantee that held on Astro 5 must hold on Astro 7.

## Acceptance

- [ ] `astro` ≥ 7 and every `@astrojs/*` on the major Astro 7 supports; `npm audit --omit=dev` has 0 critical and 0 high.
- [ ] The AA2, AA3b, AA3 and AA5 exit gates each exit 0 on the AA7 branch, unchanged (no gate edits to make them pass).
- [ ] No server module reads `import.meta.env.BACKEND_URL`.
- [ ] The docs heading ids are unchanged, or every change is listed and no registered locator moved.
- [ ] No UX regression under the AA0 rule; CSP inline-script reports at or below AA1.
- [ ] Cold review green or amended.

## Risks

- **Whitespace (`'jsx'`) changes text silently.** That is why `compressHTML: true` is pinned first and screenshots are compared.
- **Rust compiler and CSP:** if Astro inlines or splits scripts differently, the AA1 inline-script count moves. The
  AA3 and AA3b browser checks catch it.
- **The env inlining is the quiet one.** A build-time `BACKEND_URL` works in Compose (same value) but breaks any
  stack that sets it at runtime only. The runtime reader removes the doubt.
- **Lockfile churn hides regressions.** Upgrade in two commits (v6, then v7), each running the frontend suite,
  so a failure points at one major.

## References

- Upgrade to Astro v6: https://docs.astro.build/en/guides/upgrade-to/v6/
- Upgrade to Astro v7: https://docs.astro.build/en/guides/upgrade-to/v7/
- PHASE-AA5-REPORT, lane B, "Cold review amendments" F4: audit numbers and reachability.
