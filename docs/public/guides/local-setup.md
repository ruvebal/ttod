---
title: Run the reference locally
eyebrow: Local evaluation guide
description: A public-safe path from repository clone to a verified local TTOD experience.
permalink: /guides/local-setup/
---

# From clone to a visible hello world

The application is designed to run locally through Docker Compose. This guide explains the operational path only far enough to support front-end teaching and evaluation.

## Prerequisites

- Git
- Docker Desktop or a compatible Docker Engine with Compose
- Enough free disk space for container images and the optional local language model
- A browser

## Start

From the repository root:

```bash
docker compose up --build -d
docker compose ps
```

Use the port mapping reported by `docker compose ps` to open the web service. If the repository supplies an environment example, copy it to a local untracked environment file and change only documented values. Never commit credentials or machine-specific coordinates.

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
- **Model still downloading:** use the non-generative content areas while it completes.
- **Oracle unavailable:** verify service health and model readiness separately.
- **A route renders but data is empty:** inspect the browser network response and service logs without pasting secrets into an issue.

For support, report the command, route, operating system, and exact error. Replace personal paths, usernames, hostnames, addresses, tokens, and environment values with safe placeholders.

