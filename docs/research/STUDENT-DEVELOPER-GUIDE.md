# TTOD Oracle — guía del estudiante desarrollador

**Audiencia:** alumnado de Front-End II.  
**Estado:** guía preparada para el starter; la distribución queda bloqueada hasta superar la prueba T4 de aislamiento de historial.

## Antes de empezar

Cada estudiante trabaja en su propio equipo o en un ordenador de laboratorio. Tanit y Lilith son máquinas privadas del estudio: no hay una instancia compartida. El stack local no necesita credenciales.

No clones `main` ni un remoto que también exponga la referencia docente. El starter debe proceder de un export independiente. Si aún no se ha entregado ese artefacto, no empieces: la compuerta de distribución sigue abierta.

## Requisitos

- Git.
- Docker Desktop con Compose, o Podman Desktop con `podman-compose`.
- En Windows, WSL2 con integración del motor.
- Ollama local para el modo `host`, o el perfil `container` con suficiente espacio y memoria.

## Primer arranque

Desde el artefacto entregado:

```bash
git clone <URL-DEL-STARTER-AISLADO>
cd <DIRECTORIO-DEL-STARTER>
git log --all --oneline
git branch -a
cp .env.example .env
docker compose config --quiet
docker compose up --build -d
docker compose ps
```

**Qué esperar de `git log --all --oneline` y `git branch -a`:** deben mostrar solo el puñado de
commits del esqueleto inicial (R1/R2/R3a) y ninguna rama además de la tuya propia. Si ves un
mensaje de commit que mencione el grafo, el terminal Oracle, el motor de contenido, `R3b`, `R4`,
`R5` o `R7`, o si aparece cualquier rama distinta de la tuya (por ejemplo `main` u
`origin/main`), **detente y avisa al profesor antes de seguir** — significa que este clon no pasó
la prueba de aislamiento y contiene la referencia docente que se supone debes construir tú mismo.
No sigas explorando ese historial para "ver cómo lo hizo el profesor": eso vacía por completo el
propósito de la entrega.

En PowerShell, usa `Copy-Item .env.example .env`. Abre `http://localhost:8080/en/` y `http://localhost:8080/es/`; comprueba después la cita viva y `curl -fsS http://localhost:8080/health`. El path correcto es `/health`, no `/api/health`.

## Ollama local

El modo `host` usa Ollama instalado en tu equipo y omite el servicio `ollama` de Compose. Ajusta solo `OLLAMA_BASE_URL`, `OLLAMA_MODEL` y `OLLAMA_EMBED_MODEL` a modelos que existan localmente; no añadas una API key. El modo `container` se inicia así:

```bash
docker compose --profile container up --build -d
docker compose exec ollama ollama pull llama3.2:1b
docker compose exec ollama ollama pull nomic-embed-text
```

No mezcles `host` y `container` sin volver a revisar `.env`.

## Primera tarea: entender el esqueleto

Traza el recorrido `/en/quote`: Astro solicita al backend, el backend lee mediante `ttod_core`, y la cita vuelve al navegador con idioma y derechos. Comprueba también `/es/` y describe qué está traducido y qué no. No hardcodes una cita ni un recuento.

## Trabajo por fases

R1, R2 y R3a constituyen la base recibida. R3b, R4, R5, R6 y R7 son trabajo de la cohorte:

- R3b: documentación y motor de contenido Astro bilingüe.
- R4: isla Svelte del grafo y relaciones sin referencias colgantes.
- R5: terminal React, streaming, modo de respuesta y cola offline.
- R6: PWA, CI/CD y auditoría de despliegue; está reservada al alumnado.
- R7: pruebas unitarias, de componentes, contratos, Playwright y accesibilidad.

Lee el runbook de tu fase antes de editar. Respeta `services/frontend/src/types/domain.ts` como contrato compartido y coordina cualquier cambio en archivos comunes.

## Evidencia de proceso y uso de IA

Para cada decisión conserva problema, alternativas, evidencia, cambio y verificación. Declara qué herramienta de IA usaste, en qué contribuyó, qué aceptaste o rechazaste y cómo verificaste el resultado. Una salida generada no es una revisión.

La evaluación debe poder leerse como trabajo técnico: commits comprensibles, pruebas reproducibles, documentación de decisiones y defensa oral. La participación en una eventual investigación es voluntaria y nunca condiciona acceso, nota o evaluación.

## Verificación antes de entregar

```bash
cd services/frontend
npm install
npm run check
npx vitest run
npm run build
```

Si tu fase añade Playwright, ejecútalo contra un stack vivo y conserva la salida. Registra sistema operativo, versión del motor, commit y comandos; no afirmes compatibilidad con otro sistema que no hayas probado.

## Equipo compartido

El stack no requiere secretos, pero un ordenador universitario puede conservar historial, archivos y sesiones autenticadas. No uses `git config --global`, no dejes sesiones de `gh` o de un proveedor cloud, y nunca pongas una contraseña en la línea de comandos.

## Qué no hacer

No despliegues en Lilith, Tanit o Scaleway; no publiques el repositorio; no hagas push al remoto del instructor; no edites `ttod.yml` a mano; no aceptes propuestas de sabiduría; no borres una cita para resolver un fallo; y no copies la implementación de referencia de R3b/R4/R5.
