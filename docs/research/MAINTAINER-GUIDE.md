# TTOD Oracle — guía del mantenedor

**Audiencia:** Rubén y futuros mantenedores autorizados.  
**Estado:** guía operativa para la referencia del estudio; no autoriza publicar el repositorio ni abrir R6.

## Límites

- `ttod.yml` es la fuente canónica. No se edita a mano: las mutaciones pasan por `cli.py`, propuestas y revisión humana según `AGENTS.md`.
- R3b, R4 y R5 son la referencia docente en `main`; R6 sigue diferida y reservada al alumnado; R7 sigue `PARTIAL`.
- Tanit y Lilith son infraestructura privada del estudio. El alumnado ejecuta su copia local.
- El starter no puede publicarse desde el mismo remoto que contiene `main`; antes de distribuirlo hay que producir un export separado y ejecutar la prueba de aislamiento de T4.
- El stack local no necesita credenciales. Una solicitud de API key, contraseña o clave SSH es una señal de parada.

## Stack y arranque

El perfil normal tiene `reverse-proxy`, `frontend`, `backend` y `mcp-server`; el perfil `container` añade `ollama`. Caddy escucha HTTP plano en `8080` y `8443`; `8443` no es TLS. El único health check es `/health`, no `/api/health`.

```bash
cp .env.example .env
docker compose config --quiet
docker compose up --build -d
docker compose ps
curl -fsS http://localhost:8080/health
docker compose down
```

Para Ollama en contenedor:

```bash
docker compose --profile container config --quiet
docker compose --profile container up --build -d
docker compose exec ollama ollama pull llama3.2:1b
docker compose exec ollama ollama pull nomic-embed-text
docker compose --profile container ps
```

Si `8080` o `8443` están ocupados, cambia solo `HTTP_PORT` o `ALT_HTTP_PORT` en `.env`.

## Verificación

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
python cli.py validate --strict --json
python cli.py stats --check
python -m unittest discover -s tests -p 'test_*.py'
python -m unittest discover -s services/backend/tests
python -m unittest discover -s services/mcp/tests
```

```bash
cd services/frontend
npm install
npm run check
npx vitest run
node --test src/components/graph/layout.test.mjs
npm run build
```

El conjunto Playwright/axe requiere un stack real. Registra comando, commit, entorno y salida.

## Diagnóstico y liberación

Comprueba `docker compose ps`, `docker compose logs --no-color --tail=100`, `/health` y después `/api/v1/wisdom/sample`. Comprueba que Ollama contiene el modelo configurado. No cambies `ttod.yml`, el esquema, los puertos internos ni `domain.ts` para resolver un fallo visual.

Antes de distribuir el starter, clónalo en limpio y ejecuta:

```bash
git log --all --oneline
git branch -a
```

El resultado debe demostrar que ningún commit de la referencia R3b/R4/R5/R7 es alcanzable. Un push de `cohort-starter` al mismo `origin` no supera esta prueba.

## Derechos

El contenido mantiene CC BY-NC-SA 4.0 y el código MIT. Las citas de investigación proceden del ledger verificado. Las propuestas de sabiduría pasan por `ttod-bridge` y revisión humana; esta guía nunca acepta una propuesta.
