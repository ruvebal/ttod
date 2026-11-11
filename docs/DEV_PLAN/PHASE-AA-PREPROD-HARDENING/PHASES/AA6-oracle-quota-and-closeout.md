# PHASE-AA6: Oracle quota and cascade closeout

> **Track:** oracle + visual + programme close — F13, F21, F39, F40 · A14–A15, A29–A30.  
> **Status:** BLOCKED until AA2, AA3b and AA5 (both lanes) DONE

## Goal

Classroom Redis budget on Oracle/SSE (auth already AA2); design QA rubric + graph token retune + single token source; close or defer **F1–F58**; hand evidence to Phase T without claiming Phase T DONE.

## Deliverables

- Oracle/SSE quota middleware (Redis); tests.
- Design QA rubric; graph palette vs tokens; token-layer audit.
- `PHASE-AA6-REPORT.md` disposition table for F1–F58.
- Optional dated completeness note.
- **Oracle quota (F21), carried from AA2:** reuse `app/throttle.py` (`Budget`, the `guard` pattern in `main.py`) keyed by the session's user id. The stream already requires a session, and the terminal already shows 429 ("too many requests"). No second rate-limit mechanism.
- **AA2 accepted P2s to dispose:** the revoke-all race (a PAT minted during `logout-all` survives up to its 1 h TTL; fix with a per-user "revoked-before" timestamp + `iat`), and per-account lockout by a third party (10 bad logins lock an account for 5 min; unlock recipe in PHASE-AA2-REPORT §4).
- **Follow-ups carried from AA1** (dispose of each: done, scheduled with an owner, or explicitly deferred):
  - **CSP enforcement.** Give `script-src` one owner (Astro's per-page hashes, or TTOD's 4 inline scripts moved to modules), switch Caddy to `Content-Security-Policy`, browser smoke at 0 violations, and bump the service worker cache so cached pages drop the old policy (PHASE-AA1-REPORT §4).
  - **Duplicate `Cache-Control` on `/sw.js`.** Present before AA1; pick one rule (PHASE-AA1-REPORT §6).
- Whole-cascade cold review.

## Scope

**In:** oracle quota, visual checklist, FINDINGS ledger close.  
**Out:** New models; cloud inference; Phase T RC execution.

## Prompt (Implementation Agent)

```text
Implement PHASE-AA6 per
docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING/PHASES/AA6-oracle-quota-and-closeout.md.

## Deliver
1. Per-user/IP Redis quota on oracle SSE; 429; test (assumes AA2 auth gate).
2. Design QA rubric; retune graph colors; resolve dual token layers.
3. Walk F1–F58: closed with evidence or deferred with named owner.
4. Phase AA ≠ Phase T. Whole-cascade cold review. Do not self-certify DONE.

## Constraints
- Local Ollama only. No ttod.yml. No commit unless asked.
```

## Carried from AA3b (amended 2026-11-11)

- **CSP enforcement:** AA3b added no inline script; `/es/graph/` dropped from 6 to 5 inline-script reports. The
  service worker cache is at `v8` (AA3b went to v7 for slash-form offline pages; AA3 went to v8 for anonymous,
  network-first offline pages), so the CSP rollout bumps to `v9`.
- **Close-out inputs:** F59 (es corpus has no `related` edges), F60 (2D plano CLS 0.47), F61 (harness ignores `3b`)
  need a disposition in the AA6 ledger.

## Carried from AA7 planning (2026-11-11)

- AA6 waits for **AA7** (Astro 5 → 7), not only AA5. The close-out hands Phase T a frontend with no critical or high
  production advisory, so AA6's ledger cites `PHASE-AA7-REPORT.md` for F19.
- **Node floor:** Astro 7.4.11 needs Node **>= 22.23.4** (`.nvmrc`). Student setup guides and the Lilith checklist
  should say so in the close-out.
- The proposal form's browser POST went to `http://backend:8000` until AA7 fixed it (cold review F6). Note it in
  the ledger as a pre-existing defect found late.

## Carried from AA4 (2026-11-12)

AA4 is DONE (owner, 2026-11-12). Its cold review ([PHASE-AA4-COLD-REVIEW.md](../PHASE-AA4-COLD-REVIEW.md))
returned PASS-WITH-AMENDMENTS after the owner's DONE. Items the owner has not assigned to an AA4 follow-up
belong here:

- **F62:** breadcrumb current-item alignment (AA4 did not touch `Breadcrumbs`).
- **`/{l}/quote/` always shows the first quote** (`quote.astro`, cold review AA4 F5). It is noindex either way;
  the bug is that it is not random.
- **Indexing switch:** if an owner opens a host to indexing, removing `X-Robots-Tag` from Caddy's `(seguridad)` is the
  whole switch; the page-level rules in `lib/seo.ts` then apply, and a sitemap is built from
  `locators.registry.json` (indexable rows, corpus values only). Note: a deploy that bypasses Caddy loses the noindex
  (cold review AA4 F6).
- **CSP enforcement** bumps the service worker to v9 in the same change (AA1 R8).
- **The AA4 cold review's P3s** (F4, F6–F10): `docs/pwa-install-quality.md` vs the manifest, Go-level 400s without
  headers, `origenPublico` comment and relative hreflang, `404.astro` locale rule vs `idiomaPreferido`, gate gaps,
  `robots.txt` plan ids and Markdown in quote titles. The owner decides whether each is fixed or recorded as accepted.

## Acceptance

- [ ] Oracle abuse → 429 under synthetic load.
- [ ] Design rubric linked; F39/F40 disposed.
- [ ] F1–F58 disposition complete; no silent won’t-fix.
- [ ] Cold review accepts closeout or lists amends.

## Risks

- Quota too tight for demos — env-tunable defaults.
