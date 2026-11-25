# PHASE-AA1: Caddy security headers

> **Track:** edge — response headers (F1). Student assignment **A1**.  
> **Status:** BLOCKED until AA0 DONE

**Exit gate:** [`AA1-caddy-security-headers.exit-gate.sh`](AA1-caddy-security-headers.exit-gate.sh). Read it before you start: it serves your Caddyfile in a throwaway container on the live network and states exactly which headers pass.

## Goal

Ship a falsifiable Caddy `header` block so classroom browsers get frame denial, referrer, and permissions policy. CSP starts report-only unless AA0 authorizes enforce.

## Deliverables

- `caddy/Caddyfile` header directives (documented).
- Probe evidence in `PHASE-AA1-REPORT.md` (`curl -sI` before/after).
- Cold review.

## Scope

**In:** Caddyfile (+ compose rebuild notes if needed).  
**Out:** TLS certificates (F2 → AA5); application CSP meta tags as the only fix.

## Prompt (Implementation Agent)

```text
Implement PHASE-AA1 per
docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING/PHASES/AA1-caddy-security-headers.md.

## Deliver
1. Add Caddy header block: frame-ancestors/'X-Frame-Options', Referrer-Policy,
   Permissions-Policy; CSP-Report-Only first if enforce not authorized.
2. Rebuild/reload Caddy; curl -sI http://localhost:${HTTP_PORT:-18080}/en/
3. Record evidence; cold review. Do not self-certify DONE.

## Constraints
- Do not enable auto_https as a fake “HTTPS done.” Do not commit unless asked.
```

## Acceptance

- [ ] Headers present on HTML responses from the public port.
- [ ] API JSON still usable (no broken CORS invented; same-origin classroom).
- [ ] Cold review: no header that breaks Astro assets/SW without a documented exception.

## Risks

- Over-strict CSP breaks Oracle/graph islands — start report-only.
