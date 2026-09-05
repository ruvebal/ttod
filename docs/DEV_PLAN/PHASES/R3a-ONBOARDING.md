# TTOD Oracle local onboarding

The local stack needs **no real secrets**. Its `.env` contains configuration only.

## Start from a fresh clone

1. Install Git and either Podman Desktop with `podman-compose`, or Docker Desktop with Compose.
   On Windows, run these steps inside WSL 2 and enable the chosen container engine's WSL integration.
2. Clone the repository and enter its directory.
3. Run `cp .env.example .env` (PowerShell: `Copy-Item .env.example .env`).
4. Choose one Ollama mode:
   - Host mode (default): install/start Ollama on the host, then run `podman-compose up --build`
     or `docker compose up --build`.
   - Container mode: change `.env` to `OLLAMA_MODE=container`,
     `OLLAMA_BASE_URL=http://ollama:11434`, and `OLLAMA_MODEL=llama3.2:1b`; run
     `docker compose --profile container up --build`.
     In another terminal, pull the chosen light model with
     `docker compose exec ollama ollama pull llama3.2:1b`, and the embedding model with
     `docker compose exec ollama ollama pull nomic-embed-text`. Podman users may substitute the
     Docker-compatible `podman-compose` commands supported by their installation.
5. Open `http://localhost:8080/en/` and `http://localhost:8080/es/`, then follow the live-quote link.
6. Verify the API: `curl -fsS http://localhost:8080/health`. This is the only health path —
   confirmed via the live Caddyfile, which special-cases bare `/health` alongside `/api/*`; there
   is no `/api/health` alias (that path 404s).

The local/Lilith profile uses plain HTTP on ports 8080 and 8443. It neither requests nor stores a
TLS certificate. Port 8443 is an additional plain-HTTP listener reserved for compatible studio
wiring; use `http://`, not `https://`.

If either default host port is already occupied, change `HTTP_PORT` or `ALT_HTTP_PORT` in `.env`
and use the changed port in the URLs above; container-side routing remains unchanged.

## Shared-machine safety

If anything asks for an API key, password, SSH private key, or other credential, stop and ask an
instructor: this local stack should not need one. A university/shared lab computer can retain
files, shell history, and cached logins for a later user. Log out of any CLI you authenticated
(`gh auth logout` and the equivalent cloud-provider logout), use repository-local `git config`
rather than `--global`, and never pass secrets as bare command-line arguments.

**Corrected 2026-09-06:** you run this entirely on your own machine — there is no shared
LAN environment in this course at all. Lilith and Tanit are private studio infrastructure, not
reachable by students under any circumstance; don't look for a "shared instance" to connect to,
because none exists for you. Scaleway staging credentials are instructor-only and entirely outside
this setup, same as before.
