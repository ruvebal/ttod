# PHASE-AA4: SEO robots, meta, and PWA honesty

> **Track:** discoverability — F14, F15, F41–F44 · A12–A13, A27–A28.  
> **Status:** BLOCKED until AA3 **and AA3b** DONE (canonical/sitemap consume the frozen [LOCATORS](../LOCATORS.md) registry)

## Goal

Noindex on classroom hosts, **decided in AA0 D7 (a)**; `robots.txt` (+ sitemap only if a later owner decision allows indexing); OG/canonical/hreflang; quote title/description from text; document or extend Oracle-only PWA (manifest locale + maskable).

## Deliverables

- `public/robots.txt` (+ sitemap if chosen).
- `Page.astro` meta; wisdom slug title/description.
- Manifest/SW disposition (Oracle-only honesty or offline shell).
- `PHASE-AA4-REPORT.md` + cold review.

## Scope

**In:** frontend public, head shell, SW/manifest.  
**Out:** Marketing redesign; Phase T disclosure.

## Prompt (Implementation Agent)

```text
Implement PHASE-AA4 per
docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING/PHASES/AA4-seo-robots-and-meta.md.

## Deliver
1. robots.txt (+ sitemap only if indexing allowed).
2. og/canonical/hreflang on Page.astro; quote meta from text/teaches.
3. PWA: document Oracle-only offline OR add shell; locale-aware start_url; maskable icons if cheap.
4. Evidence + cold review. Do not self-certify DONE.

## Constraints
- Classroom hosts are noindex (AA0 D7 (a)). Put the noindex in the page (`<meta name="robots">`) or an `X-Robots-Tag` header, and do **not** `Disallow` those pages in `robots.txt`: a crawler that may not fetch a page never reads its noindex. If you use `X-Robots-Tag`, add it to the `(seguridad)` snippet in `caddy/Caddyfile` (AA1), so errors Caddy generates itself carry it too. Live checks run on `scripts/isolated-stack.sh` (AA2). No commit unless asked.
```

## Acceptance

- [ ] `/robots.txt` coherent; no private account URLs in sitemap.
- [ ] Sample pages: canonical + hreflang; quote titles not ID-only.
- [ ] Manifest/SW claims match behavior.
- [ ] Cold review green or amended.

## Risks

- Indexing an open-register classroom host: decided against in AA0 D7 (a); reopening it is an owner decision, not a PR choice.
