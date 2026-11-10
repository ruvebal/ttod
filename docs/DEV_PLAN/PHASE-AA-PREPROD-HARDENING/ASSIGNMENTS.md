<!--
Student assignment cut of FINDINGS-2026-11-10 (amended after backend+frontend deep audits).
Instructor freezes ownership in AA0. Do not treat this as authorization to merge.
-->

# Assignments — pre-production hardening (Phase AA)

**Status:** FROZEN 2026-11-10 by [AA0](PHASE-AA0-REPORT.md). The cut below is affirmed as drafted: students A1–A40, instructor I1–I16, no reassignments. Changes after this date go through an AA0 amendment in the report.  
**Audience:** FE II / TTOD cohort teams.  
**Source of truth for defects:** [FINDINGS-2026-11-10.md](FINDINGS-2026-11-10.md).  
**Rationale:** [RATIONALE.md](RATIONALE.md).  
**Cascade:** [PHASE-AA-PREPROD-HARDENING-CASCADE.md](PHASE-AA-PREPROD-HARDENING-CASCADE.md).

Each row is one PR-sized job. **Done** = code + one test/live probe that would have failed before + PR cites finding ID. Never hand-edit `ttod.yml`. Reuse Phase Z Redis shore — no second database.

---

## How to pick work

1. Read the finding in FINDINGS (severity + evidence).
2. Confirm Equipo ownership.
3. Branch from current `main`; one finding (or tight pair) per PR.
4. PR body: `Closes Fn` + the proving command.

Instructor-only rows stay out of student PRs unless AA0 reassigns them.

---

## Assignment board

| ID | Equipo / owner | Title | Acceptance (falsifiable) | Cascade · Finding | Size |
| -- | ------------- | ----- | ------------------------ | ----------------- | ---- |
| **A1** | Platform / Caddy | Security response headers | `curl -sI` shows frame denial / referrer / permissions (± CSP-RO) | AA1 · F1 | M |
| **A2** | Accounts (Eq. 5) | Redis throttle register + login | Rapid POSTs → **429**; unit test with fake counter | AA2 · F3 | L |
| **A3** | Accounts (Eq. 5) | Gate signed-cookie fallback | Compose default: missing Redis sid → unauthenticated | AA2 · F4 | S |
| **A4** | Accounts + instructor | PAT revocation (AA0 D7 (b): React authentication lesson) | PATs keep the short expiry and carry a `jti`; Redis denylist `ttod:pat:deny:{jti}` written on logout-all and password change, checked on every read; a test proves a revoked PAT gets 401 before it expires | AA2 · F5 | M |
| **A5** | Accounts (Eq. 5) | Rate-limit proposal create | Shares throttle with A2; test → 429 | AA2 · F20 | S |
| **A16** | Accounts (Eq. 5) | Cookie `Secure` from real TLS signal | Env `COOKIE_SECURE` / `PUBLIC_HTTPS` (not bare `PROD`); HTTP LAN login works when Secure=false | AA2 · F22 | M |
| **A17** | Accounts / shell | Astro `allowedDomains` from env | A browser on a non-localhost host can POST login/register: the matching **Host + Origin** pair (e.g. both `tanit.crea-comm.loc`) returns non-403 in deploy config. Astro checks the Origin; today that pair gets 403 | AA2 · F23 | S |
| **A18** | Oracle (Eq. 3) | Auth-gate oracle stream + propose | Unauthenticated → 401/403; session path works | AA2 · F24 | M |
| **A19** | Oracle (Eq. 3) | Oracle propose → dual-write store | Draft appears in Redis indexes **and** on bound disk path | AA2 · F26 | M |
| **A6** | Shell (Eq. 1–3) | Header Account / Log in | Session-aware; not footer-only | AA3 · F7 | M |
| **A7** | Shell | Trailing-slash hygiene | Always-slash for pages (AA0 D1); slashless page URL → 301; nav/footer consistent | AA3b · F8 | M |
| **A8** | Shell | Footer login `next` | Never `next=/…/login` on login page | AA3 · F9 | S |
| **A9** | Shell + Accounts | Library gate UX | CTA or “requires account” nav cue | AA3 · F10 | S |
| **A10** | Shell / a11y | Skip-link landmark | `#ttod-main` on `<main>` | AA3 · F11 | S |
| **A11** | Shell / visual | Reduced motion CieloRuyi | No continuous rAF under `prefers-reduced-motion` | AA3 · F12 | S |
| **A20** | Graph (Eq. 4) | Localize GraphIsland | `/en/graph` + `/es/graph` UI/errors bilingual | AA3 · F32 | M |
| **A21** | Shell / visual | Style account + library + quote shells | Share `ttod-shell` / acceso patterns; not bare HTML | AA3 · F33 | M |
| **A22** | Shell | quote empty-state | Empty corpus → localized UI, not 500 | AA3 · F34 | S |
| **A23** | Accounts | Localized Forbidden | Student on reviewer route gets HTML/es·en, not bare text | AA3 · F35 | S |
| **A24** | Accounts | Password confirm on register | Client + server reject mismatch | AA3 · F36 | S |
| **A25** | Accounts | Logout cookie delete attrs | Delete matches set (path/secure/sameSite) | AA3 · F37 | S |
| **A26** | Shell / a11y | `aria-current` prefix match | Nested `/wisdom/…` marks Wisdom current | AA3 · F38 | S |
| **A12** | Content / SEO | robots + sitemap | File exists; noindex as decided in AA0 D7 (a) (not a PR choice); robots.txt does not `Disallow` noindexed pages | AA4 · F14 | M |
| **A13** | Content / SEO | OG + canonical + hreflang | On home + login at minimum | AA4 · F15 | M |
| **A27** | Content / SEO | Quote title/description from text | Not ID-only `<title>` | AA4 · F41 | S |
| **A28** | PWA (Eq. 6) | Oracle-only offline honesty **or** shell | Docs + manifest/SW match reality | AA4 · F42–F44 | M |
| **A14** | Oracle (Eq. 3) | Oracle request budget | Redis counter → 429 after budget | AA6 · F21 | L |
| **A15** | Visual (all) | Design QA rubric | Checklist doc; not a redesign | AA6 · F13 | S |
| **A29** | Visual / graph | Graph colors → tokens | Drop purple/magenta drift vs seal/ink | AA6 · F39 | S |
| **A30** | Shell | Single token source | No dual competing token layers without rationale | AA6 · F40 | M |

### Added 2026-11-10 — usability, IA, permanent locators (owner walkthrough)

Contract for every locator row: [LOCATORS.md](LOCATORS.md). Same rules as above: one finding per PR, prove it failed before.

| ID | Equipo / owner | Title | Acceptance (falsifiable) | Cascade · Finding | Size |
| -- | ------------- | ----- | ------------------------ | ----------------- | ---- |
| **A31** | Shell (Eq. 1–3) | Classic full-width header + global anchor offset | Not a pill; 4 primary links + utility cluster; no hamburger at 768 px; `scroll-padding-top` from `--ttod-header-height`; no regression under the AA0 regression rule (PHASE-AA0-REPORT §5); screenshot strip 390/768/1440 × en/es × in/out | AA3 · F56, F58 | M |
| **A32** | Content (Eq. 1) | Guard the landing figures | Fixture test (3/2/1) fails if a literal count is typed; `<dt>` label / `<dd>` number | AA3b · F54 | S |
| **A33** | Shell + Accounts | Fix `/library` layout | Styled cards (shared with wisdom), localized section label, `id` per card, `EmptyState`; en + es | AA3 · F53 | M |
| **A34** | Accounts (Eq. 5) | Change-password + profile API | `POST /auth/password` (verify current, throttled, revokes other sids via `ttod:user:{id}:sessions`); optional `PATCH /auth/profile` `display_name`; pytest for each path | AA2 · F55 | M |
| **A35** | Accounts (Eq. 5) | Account "Usuario" section | `/account#profile #password #sessions`; confirm field; localized errors; PRG success flash; works with A34 | AA3 · F55 | M |
| **A36** | Content (Eq. 1–2) | Wisdom locators | Every rendered quote has `id={entry.id}`; `#volume-{section}` opens its volume; dialog shows permalink + copy-link | AA3b · F50 | M |
| **A37** | Content (Eq. 1–2) | Wisdom search + task-first order | `?q=` SSR search works with JS off, accent-insensitive; combined `?section=&level=&tag=`; search before the pile | AA3b · F49 | L |
| **A38** | Visual / landing | Landing chapter deep links | `/es/#map-css` opened cold lands on that stop; hash follows chapters via `replaceState`; reduced-motion jump | AA3b · F51 | M |
| **A39** | Graph (Eq. 4) | Graph IA: 3D where the header points | Per AA0 D3; `?from=&to=&node=` restorable; `/graph/path` 301 keeps query | AA3b · F52 | M |
| **A40** | Shell | Language switch keeps state; quote twin; real 404 | `/es/wisdom/wis-034/` → `/en/wisdom/wis-033/`; lists keep `?q=`/`#id`; unknown quote id → HTTP 404 | AA3b · F57 | S |

### Instructor-owned (not student-scored unless AA0 reassigns)

| ID | Title | Finding | Notes |
| -- | ----- | ------- | ----- |
| **I1** | TLS termination story | F2 | Proxy docs; rename ALT_HTTP if not HTTPS |
| **I2** | Non-root container USER | F16 | Both Dockerfiles |
| **I3** | Frontend (+ mcp) HEALTHCHECK | F17 | Compose-visible |
| **I4** | Image digest pins | F6 | Start with ollama floating tag |
| **I5** | Lilith checklist rewrite | F18 | Redis shore, env-secrets, protected-mode, ports |
| **I6** | npm audit re-measure | F19 | AA5 report; defer majors intentionally |
| **I7** | Proposal dir bind mount | F25 | `./data/proposals` + gitignore; accept path docs |
| **I8** | `/health` 503 when Redis down | F27 | Or live/ready split; Compose must notice |
| **I9** | `ensure_env_secrets` on rebuild + fail-closed empty secrets | F28 | |
| **I10** | Redis `maxmemory` | F29 | Keep `noeviction` |
| **I11** | Stop publishing Ollama host port by default | F30 | |
| **I12** | CI + `make test` run backend suite | F45 | |
| **I13** | Dual-write orphan cleanup note | F31 | |
| **I14** | Redis pool timeouts | F46 | |
| **I15** | Sanitize health/oracle error bodies | F47 | |
| **I16** | Structured JSON access logs with request id | F48 | Added 2026-11-10: F48 had no owner. AA0 kept it instructor-owned (not deferred) |

---

## Rubric hints

- Cite finding ID + probe that failed before.
- For A16/A17: demonstrate **non-localhost Host** (or document why Secure=false on classroom HTTP).
- For A18/A19: dual-write + auth together close the Oracle propose hole.
- For A31/A33/A37: attach before/after screenshots **and** a number (CLS, Lighthouse a11y, or a test). A screenshot alone is not proof.
- For A36–A40: the PR adds its rows to the LOCATORS registry test; a locator not in the registry is not done.
- A35 depends on A34. A38 and A36 VERIFYING depend on A31 (header height).
- Do not claim cascade DONE from one PR.

## Explicit non-goals for students

- Mutating `ttod.yml` / accepting proposals without reviewer.
- Postgres, cloud Redis, captcha SaaS, cloud LLM.
- Self-serve `admin` registration.
- Rewriting Caddy as nginx “for fun.”
- New fonts, palette or logo while restyling the header (A31 is a component restyle on existing tokens).
- A client-side search library or a new backend search endpoint for A37.
- Password reset by email (no mail transport in Compose) or email change in A34/A35.
