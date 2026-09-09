---
title: Run the reference locally
eyebrow: Local evaluation guide
description: A public-safe path from repository clone to a verified local TTOD experience.
permalink: /guides/local-setup/
---

# From clone to a visible hello world

The application is designed to run locally through Docker Compose. This guide covers only the operations needed for front-end teaching and evaluation.

## Prerequisites

- Git
- Docker Desktop or a compatible Docker Engine with Compose
- `make` (optional but recommended — see the Windows note below if you're not sure you have it)
- Enough free disk space for container images and the local language model
- A browser

## Start

From the repository root, the simple path:

```bash
make up
make ollama-pull
```

`make up` copies `.env.example` to a local, untracked `.env` automatically if one doesn't exist yet
(no values need editing — this stack needs no credentials), builds and starts every service
including the app's own Ollama container, and prints the URL to open. `make ollama-pull` downloads
the small local model the Oracle needs — do this once, right after `make up`; it can take a few
minutes on a fresh volume and only needs repeating if you later remove that volume.

**Without `make`**, the same four steps by hand:

```bash
cp .env.example .env
docker compose up --build -d
docker compose ps
docker compose exec ollama ollama pull llama3.2:1b
```

**Is `make` available on your machine?** macOS and Linux ship with it. Windows does not — but
Docker Desktop on Windows requires the WSL2 backend anyway, and a WSL2 terminal (not PowerShell or
cmd.exe) already has `make`, or gets it via `sudo apt install make`. If you're on a shared/school
Windows PC and unsure whether WSL2 is configured, use the no-`make` block above from PowerShell —
`docker compose` behaves the same either way; only the four-command convenience wrapper differs.

Use the port mapping reported by `docker compose ps` (default `http://localhost:8080`) to open the
web service. Never commit `.env`, credentials, or machine-specific coordinates.

## Verify the journey

1. Open the localized welcome page.
2. Visit a quote and confirm text, language, origin, and rights are visible.
3. Open documentation and a graph relationship.
4. If the local Oracle model is ready, submit a small question and inspect its grounding or creative-mode disclosure.
5. Confirm keyboard focus and readable status or error feedback on interactive controls.

The content and graph remain useful when the optional Oracle model is unavailable. A plausible generated response is not the canonical source and may be incomplete or wrong.

## Inspect and stop

```bash
docker compose logs --tail=100
docker compose down
```

Stopping containers should not remove named data volumes. Delete volumes only when you explicitly intend to discard local model or application data and understand the recovery cost.

## Common blockers

- **Port already in use:** choose a documented alternate mapping; do not stop unrelated containers blindly.
- **Oracle hangs or errors on a fresh setup:** the model likely hasn't been pulled yet — run
  `make ollama-pull` (or the `docker compose exec ollama ollama pull …` equivalent) once; it isn't
  automatic on `make up` since it's a one-time, several-minutes download.
- **Model still downloading:** use the non-generative content areas while it completes.
- **Oracle unavailable:** verify service health and model readiness separately.
- **A route renders but data is empty:** inspect the browser network response and service logs without pasting secrets into an issue.

For support, report the command, route, operating system, and exact error. Replace personal paths, usernames, hostnames, addresses, tokens, and environment values with safe placeholders.
