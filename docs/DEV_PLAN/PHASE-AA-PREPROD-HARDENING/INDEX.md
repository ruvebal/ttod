<!--
Phase AA — Pre-production hardening + student assignment cascade.
Drafted 2026-11-10 from live audit. Author: Rubén Vega Balbás PhD
-->

# Phase AA — Pre-production hardening

**Status:** AUTHORIZED 2026-11-10 (owner: "the defaults are ok"; D1–D6 recorded as written, D7 (a) noindex confirmed by name ("D7 a"), D7 (b) per the React authentication lesson: short PAT expiry + `jti` denylist) · AA0, AA1, AA2, AA3, AA3b, AA4, AA5, AA7 DONE.  
**Programme letter:** AA (after Z Redis shore).  
**Depends on:** Phase Z complete on `main`; cohort accounts/register landed.  
**Related but separate:** [Phase T public release](../PHASE-T-PUBLIC-RELEASE-EXCELLENCE-CASCADE.md) — do not conflate.

## One-sentence claims

- **Product:** Before a real web server, close the gap between “works in Compose” and “safe enough for a classroom host.”
- **Engineering:** Evidence-backed findings → gated phases → cold review; no self-certified DONE.
- **Pedagogy:** Each fix is a student-sized assignment mapped to a seam, not a maintainer-only dump.

## How to read this pack

| Face | File |
| ---- | ---- |
| Index (this) | entry + live snapshot |
| Why | [RATIONALE.md](RATIONALE.md) |
| Evidence | [FINDINGS-2026-11-10.md](FINDINGS-2026-11-10.md) |
| Student brief | [ASSIGNMENTS.md](ASSIGNMENTS.md) |
| URL / locator contract | [LOCATORS.md](LOCATORS.md) |
| Orchestrator | [PHASE-AA-PREPROD-HARDENING-CASCADE.md](PHASE-AA-PREPROD-HARDENING-CASCADE.md) |
| Phases | [PHASES/](PHASES/) AA0→AA7 (+ AA3b locators; AA7 Astro upgrade runs before AA6) |

## Programme (harness-readable)

`cascade-harness.sh` parses only the first word of the Gate column. The prose lives in the
[cascade](PHASE-AA-PREPROD-HARDENING-CASCADE.md). Each step carries a companion
`PHASES/<file>.exit-gate.sh`. A step whose gate script is still missing cannot be verified.

| Step | File | Deliverable | Gate |
| ---- | ---- | ----------- | ---- |
| 0 | [AA0](PHASES/AA0-assignment-cut-and-freeze.md) | Assignment cut, D1–D7, LOCATORS frozen, live re-probe, UX baseline | DONE — cold review PASS-WITH-AMENDMENTS, amended; owner marked DONE 2026-11-10 ("Mark AA0 as done, AA5 lane A as DONE") |
| 1 | [AA1](PHASES/AA1-caddy-security-headers.md) | Caddy security headers, CSP report-only | DONE — cold review PASS-WITH-AMENDMENTS, amended; owner marked DONE 2026-11-10 ("AA1 done") |
| 2 | [AA2](PHASES/AA2-auth-throttle-and-fallback.md) | Throttles, fallback off, PAT, cookie Secure, allowedDomains, oracle auth, password API | DONE — cold review PASS-WITH-AMENDMENTS, amended; owner marked DONE 2026-11-10 ("AA2 done") |
| 3 | [AA3](PHASES/AA3-nav-a11y-and-url-hygiene.md) | Classic header, a11y, library, User section UI | DONE — cold review PASS-WITH-AMENDMENTS (F1–F10), amended and re-verified; owner marked DONE 2026-11-11 ("AA3 done") |
| 3b | [AA3b](PHASES/AA3b-locators-wisdom-and-graph-ia.md) | Locators: slash, wisdom ids/search, graph IA, language switch | DONE — cold review PASS-WITH-AMENDMENTS (F1–F11), amended and re-verified; owner marked DONE 2026-11-11 ("AA3b done") |
| 4 | [AA4](PHASES/AA4-seo-robots-and-meta.md) | robots/sitemap, canonical/hreflang, PWA honesty | DONE — exit gate first, verify exit 0 (re-runs AA1/AA3b/AA3/AA5 green); owner marked DONE 2026-11-12 ("AA4 DONE") while the cold review was still running; its findings are recorded in PHASE-AA4-COLD-REVIEW.md when it returns |
| 5 | [AA5](PHASES/AA5-container-and-deploy-ops.md) | Lane A: proposal bind, health 503, secrets · lane B: ops | DONE — lane A DONE 2026-11-10; lane B cold review PASS-WITH-AMENDMENTS (F1–F8), amended and re-verified; owner marked DONE 2026-11-11 ("AA5 done") |
| 6 | [AA6](PHASES/AA6-oracle-quota-and-closeout.md) | Oracle quota, rubric, disposition, Phase T handoff | READY — AA4 DONE (2026-11-12); the last phase, closes Phase AA; waits for the owner's go |
| 7 | [AA7](PHASES/AA7-astro-major-upgrade.md) | Astro 5 → 7 major upgrade; re-runs the AA1/AA2/AA3b/AA3/AA5 gates | DONE — cold review PASS-WITH-AMENDMENTS (F1–F10), amended and re-verified; owner marked DONE 2026-11-11 ("AA7 done") |

## Live snapshot (2026-11-10)

| Fact | Value | Where checked |
| ---- | ----- | ------------- |
| Compose stack | Up; backend healthy; `redis: ok` | `docker compose ps`; `/health` |
| Site | `http://localhost:18080/en/` → 200 | curl |
| Security headers | **Absent** (F1) | `curl -sI` |
| TLS at Caddy | **Off** both ports (F2) | `Caddyfile` |
| Cookie Secure vs HTTP | **Mismatch risk** (F22) | FE `PROD` + cleartext Caddy |
| Astro allowedDomains | **localhost only** (F23) | `astro.config.mjs` |
| Proposal disk bind | **Missing** (F25) | compose volumes |
| `/health` if Redis down | Still **200** (F27) | `main.py` |
| Rate limits | **None** (F3/F21/F24) | backend grep |
| `robots.txt` | **Missing** (F14) | `public/` |
| Graph i18n | **EN-only island** (F32) | `GraphIsland.svelte` |
| Backend tests in CI | **Skipped** (F45) | `ci.yml` / Makefile |
| Slash duplicates | **Both forms 200** on every page (F8) | curl |
| Deep links in `/es/wisdom/` | **None** (no quote/volume ids, no `?q=`) (F49/F50) | id inventory |
| Landing chapter ids | **3** for hero + thesis + 13-stop scroll + close (F51) | id inventory |
| 3D graph | At `/graph/path`; header "Grafo" opens the 2D view (F52) | `Page.astro` / curl |
| Lang switch on a quote | **200 "not found"** (`wis-034` → `/en/…/wis-034/`) (F57) | curl |
| `/library` layout | Bare `<main>`, raw slugs (F53) | `library.astro` |
| Change password | **No route**; no per-user session index (F55) | `main.py`, `sessions.py` |
| Landing figures (230/13/4) | **Dynamic** from corpus ✓, but unguarded by tests (F54) | `pages/es/index.astro` |
| Redis permanence | Green (prior day) | COMPLETENESS-2026-11-09 |
| Open register | Live, always `student` | `#92` + smoke |
| FINDINGS count | F1–F62 (deep audits + owner walkthrough + AA3b + AA3) | this pack |

## Decision needed from product owner

Authorize **AA0** to freeze the assignment cut (A1–A40 vs I1–I16) and answer **D1–D7** (slash policy, locator keys, graph IA, header, user-section scope, search, PAT/index), before code phases open. **AA5 lane A** (F25/F27/F28) is now eligible right after AA0. Shore permanence and honest health matter before “deployed” demos.
