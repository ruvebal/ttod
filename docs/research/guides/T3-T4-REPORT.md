# T3/T4 — guías operativas y del estudiante

## T3

**Estado: DONE como documentación operativa.** Se entregan [MAINTAINER-GUIDE.md](../MAINTAINER-GUIDE.md) y [END-USER-GUIDE.md](../END-USER-GUIDE.md). Sus comandos se contrastaron con `docker-compose.yml`, `.env.example`, `caddy/Caddyfile`, `services/frontend/package.json`, R3a y el cierre de Phase R.

## T4

**Estado: PARTIAL — guía redactada, distribución bloqueada.** Se entrega [STUDENT-DEVELOPER-GUIDE.md](../STUDENT-DEVELOPER-GUIDE.md), pero no se afirma que el artefacto que recibirá el alumnado esté aislado. La prueba pendiente debe ejecutarse sobre el export real, no sobre la rama local `cohort-starter`:

```bash
git log --all --oneline
git branch -a
```

Debe demostrar que ningún commit de la referencia R3b/R4/R5/R7 es alcanzable. Un push de `cohort-starter` al mismo `origin` falla esta compuerta.

## Hallazgos de documentación

- El stack necesita `/health`; `/api/health` no forma parte del contrato.
- `8443` es HTTP plano en el perfil local, no HTTPS.
- Tanit y Lilith no forman parte del camino del alumnado.
- El starter debe mostrar primero el hello world bilingüe y una cita viva antes de asignar R3b–R7.
- La guía no convierte participación investigadora en requisito académico.

## Próxima acción para cerrar T4

Crear o recibir el artefacto de distribución aislado, clonarlo en un directorio limpio, ejecutar la prueba de historial y archivar su salida junto con la referencia exacta del artefacto. Hasta entonces T7 queda pendiente y no se debe generar una hoja de información de participantes.
