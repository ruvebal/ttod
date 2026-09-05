# Phase R3a Report — walking skeleton

**Status: DONE**

The Astro/Caddy/Compose walking slice is implemented. Both the four-service host profile and the
five-service container profile are live; the required `llama3.2:1b` model is pulled and verified.
Following the implementation-informed correction to the master/runbook, the reference-runtime
gate is satisfied on macOS Docker. Linux/Podman and Windows/WSL2 remain explicit R6/R7 onboarding
verification targets rather than unverifiable prerequisites on this host. R1, R2, and R3a are
all DONE, so the cohort-start gate is **open**.

## Delivered slice and evidence

- Astro SSR uses the Node adapter plus React and Svelte integrations. Its i18n router prefixes the
  default locale and supports `en` and `es`; `/` redirects to `/en/`.
- `npm run check` reported 0 errors, warnings, or hints, and `npm run build` completed.
- A clean Docker Compose build produced the backend, MCP, and frontend images. In host mode,
  `mcp-server`, `backend`, `frontend`, and `reverse-proxy` all remained running. Host port 8080 was
  already occupied by an unrelated local service, so the ignored test `.env` used 18080/18443;
  the committed defaults remain 8080/8443.
- `GET http://localhost:18080/health` returned
  `{"status":"ok","ttod_version":"3.1.0"}`.
- Both `/en/` ("Welcome to The Tao of Development") and `/es/` ("Bienvenido al Tao del
  Desarrollo") rendered. Both live quote routes caused Astro to request
  `/api/v1/wisdom/sample`; backend logs show HTTP 200, and the rendered page included the real
  entry's `legacy-unknown` origin and `CC-BY-NC-SA-4.0` rights. There is no frontend fixture or
  fallback: a failed/empty backend response throws visibly.
- `docker compose --profile container ps` showed all five services running, including Ollama on
  host port 11435. `docker compose exec ollama ollama list` reported
  `llama3.2:1b` (`baf6a787fdff`, 1.3 GB). After the final rebuild, startup-aware probes returned
  `all R3a route probes OK` for both welcome and both live-quote routes.

Representative compose excerpt:

```text
ttod_oracle-backend-1         Up   8000/tcp
ttod_oracle-frontend-1        Up   4321/tcp
ttod_oracle-mcp-server-1      Up   3001/tcp
ttod_oracle-ollama-1          Up   0.0.0.0:11435->11434/tcp
ttod_oracle-reverse-proxy-1   Up   0.0.0.0:18080->8080/tcp, 0.0.0.0:18443->8443/tcp
```

## Infrastructure choices

Local/Lilith uses standalone plain HTTP on container ports 8080 and 8443 with `auto_https off`.
This is the simplest portable profile and avoids inventing a dependency on the studio mkcert
setup. Scaleway TLS remains R6's concern. Host bindings are configurable, defaulting to the same
ports.

The container light-tier chat model is `llama3.2:1b`: it is small enough for the student-laptop
budget and is the first candidate named by the runbook. The exact pull is
`docker compose exec ollama ollama pull llama3.2:1b`. `nomic-embed-text` remains the independently
configured embedding model.

Compose's truthful topology is four services in host mode (Ollama intentionally omitted), or five
with `--profile container`. `OLLAMA_MODE=container` does not activate a Compose profile by itself;
the onboarding instructions set the URL and explicitly activate it.

## Cross-platform and secrets

Actually tested: macOS with Docker Compose 29.2.1. Podman, Linux, and Windows/WSL 2 were not
available in this session; their instructions are documented but not claimed as executed proof.
The base compose binds none of 80, 443, or 11434; MCP port 3001 remains internal-only.

`.env.example` contains configuration only and is explicitly unignored after cold review exposed
that the pre-existing `.env*` rule also hid the template. A fresh local `.env` needs no credential.
The onboarding document covers shared-machine CLI logout/history risks and keeps Lilith/Scaleway
credentials out of student setup.

## Cold review and lessons for the next phase

A fresh child agent reviewed §5/§8 without editing the implementation. It found and this lane fixed:

- `.env.example` was swallowed by `.env*`; `!.env.example` now makes it committable.
- the frontend lockfile needed to ship and Docker needed reproducible `npm ci`; both are now used.
- the full R1 TypeScript contract and all configurable backend environment variables needed to be
  represented in the shared frontend/environment scaffold; they now are.

Structural findings were escalated to the plan owner: the master/runbook's unconditional
"all 5 containers" language contradicts its intentional four-service host profile, and mode alone
cannot activate a Compose profile. Separately, Compose network wiring is not evidence of working
R1-to-R2 MCP transport; that integration must be proved by R1. These findings must propagate to
the master and remaining runbooks.

## Files touched

- `.gitattributes`, `.gitignore`, `.env.example` (plus ignored local `.env`)
- `docker-compose.yml`, `caddy/Caddyfile`
- `services/frontend/**`
- `docs/DEV_PLAN/PHASES/R3a-ONBOARDING.md`
- `docs/DEV_PLAN/PHASE-R3a-REPORT.md`

## Safe resume point

R3b, R4, R5, and the continuous R7 lane may start. R6/R7 must still run the documented Linux
Compose checks and record real Windows/WSL2 onboarding evidence when that platform becomes
available; neither may claim those platforms from the macOS result.
