# Lilith deployment-validation checklist

**Audience:** Rubén / TTOD maintainer  
**Scope:** private instructor-only Linux validation; not student distribution and not Scaleway  
**Current state (2026-09-05):** software-side READY; remote execution BLOCKED because Tanit has no
network route to Lilith.

## Artifact decision

Validate the generated `cohort-starter` artifact when the purpose is to see what students first
receive: R1/R2/R3a, bilingual hello world, and a live governed flagship quote. Do not deploy
`main` for that claim; `main` also contains the R3b/R4/R5 reference implementation.

The existing local `cohort-starter` commit (`39489446`) predates the fixes discovered by the
2026-09-05 Lilith-readiness audit. Regenerate it from the amended `main` before deployment. Do not
push merely to move it between Rubén's own machines; a local archive or private git remote is
sufficient. Pushing the student branch remains a separate distribution decision.

## Required configuration on Lilith

Create `.env` from `.env.example` and set:

```dotenv
COMPOSE_PROJECT_NAME=ttod_oracle
HTTP_PORT=8080
ALT_HTTP_PORT=8443
OLLAMA_MODE=container
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2:1b
OLLAMA_EMBED_MODEL=nomic-embed-text
```

If any host port is occupied, change only its host-side value. Both Caddy listeners are plain HTTP;
`8443` is not TLS.

## Bring-up

```bash
docker compose --profile container config --quiet
docker compose --profile container up --build -d
docker compose exec ollama ollama pull llama3.2:1b
docker compose exec ollama ollama pull nomic-embed-text
docker compose --profile container ps
```

Podman may be substituted only after confirming Lilith's installed Compose-compatible command.

## Acceptance probes

```bash
curl -fsS http://localhost:8080/health
curl -fsSL http://localhost:8080/en/ | grep -F 'img-001'
curl -fsSL http://localhost:8080/es/ | grep -F 'img-001'
curl -fsSL http://localhost:8080/en/quote | grep -F 'img-001'
curl -fsSL http://localhost:8443/en/ | grep -F 'img-001'
docker compose --profile container logs --no-color --tail=100
```

Expected quote: `img-001`, “The wise developer knows: the smallest image carries the heaviest
meaning.” It is selected by immutable ID, fetched through Astro → backend → governed `ttod.yml`,
and displayed on both localized hello-world pages. The Spanish page correctly marks the English
fallback quotation with `lang="en"`; it does not pretend a translation exists.

## Security boundary

- Keep ports firewalled to Rubén's private studio network. This is not approved for public
  exposure.
- `npm audit --omit=dev` currently reports six production advisories, including two high-severity
  transitive/direct Astro-stack findings. Their available automated remedy is a major Astro
  upgrade. Record and test that upgrade separately before any public deployment.
- Caddy and Ollama images still use moving tags. Pinning by tested version/digest is recommended
  before making reproducibility claims.
- The frontend image now excludes `.env*`; Astro receives `http://backend:8000` through an explicit
  Docker build argument. Inspecting the built image must find no `.env` file.

## Close condition

Lilith validation is DONE only after the commands above run on Lilith itself and their outputs are
filed. Tanit container evidence is a release candidate check, not Linux-host proof.

