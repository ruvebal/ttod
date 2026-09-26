<!--
Solicitud de fondos — producción / hosting de la app TTOD Oráculo ≥ 24 meses.
Destinatarios: dirección/coordinación de grados, IP ECSIT, oficina de investigación.
Importes = propuestas orientativas a confirmar; no son facturas ni compromisos.
-->

# Solicitud de apoyo presupuestario — producción TTOD Oráculo (≥ 24 meses)

**De:** Rubén Vega Balbás, PhD — `ruben.vega@udit.es`  
**Para (según canal institucional):**

| Destinatario | Motivo |
| ------------ | ------ |
| Sandra Garrido — `sandra.garrido@udit.es` | Coordinación grados tecnológicos / viabilidad docente |
| Fernando Blázquez Piñeiro — `fernando.blazquez@udit.es` | Dirección de grados / prioridad académica |
| Rafael Conde Melguizo, PhD — `rafael.conde@udit.es` | IP ECSIT / alineación con líneas del grupo |
| Oficina de investigación / OTRI / fondo interno `[completar email]` | Canal de fondos competitivos o internos |

**Proyecto:** 道 The Tao of Development (TTOD) — plataforma Oráculo (Cohorte Front-End II +
continuidad pública/docente)  
**Código:** TTOD-FEII-2026-27  
**Fecha:** 26 septiembre 2026  
**Horizonte mínimo solicitado:** **24 meses** de operación en producción (prorrogable)

---

## 1. Objeto

Solicitar **partida o apoyo** para mantener la aplicación TTOD Oráculo **en producción**
durante al menos **dos años**, de modo que:

1. el grupo y grupos siguientes puedan demostrar un producto vivo (no solo local);
2. el estudio de caso pedagógico (tras dictamen CEI) conserve un entorno estable de referencia;
3. ECSIT / UDIT dispongan de un demostrador público alineado con innovación docente y
   tecnología.

Esta solicitud es **independiente** de la remisión al CEI y de la autorización pedagógica
(A1). Puede tramitarse en paralelo.

## 2. Qué se financia (alcance)

| Concepto | Descripción | Estimación orientativa (24 meses) |
| -------- | ----------- | --------------------------------- |
| **H1** Hosting / compute | VPS o equivalente (stack Compose: frontend, backend, MCP, Postgres si aplica; Ollama según política de soberanía) | **[completar €]** · orden de magnitud típico pequeño VPS: ~15–60 €/mes → ~360–1 440 € / 24 meses |
| **H2** Almacenamiento / copias | Backups cifrados, retención acordada | **[completar €]** |
| **H3** Dominio / TLS / DNS | Si se usa subdominio institucional o externo | **[completar €]** o coste absorbido por UDIT |
| **H4** Contingencia (10–15 %) | Incidencias, migraciones menores | **[completar €]** |
| **Total propuesto** | Suma H1–H4 | **[completar €]** |

> Las cifras son **propuestas a validar** con servicios informáticos / investigación.
> Preferencia de soberanía del estudio: infra local/LAN (p. ej. Lilith) cuando sea viable;
> si el coste se internaliza como horas de máquina UDIT, sustituir H1 por **imputación
> interna** y dejar constancia en esta tabla.

## 3. Qué no se pide aquí

- Nómina del PI ni carga docente adicional (salvo que el centro lo proponga).
- Licencias cloud de LLM (el diseño del estudio es Ollama / local-first).
- Open data de repositorios de estudiantes.
- Sustituir el dictamen del CEI.

## 4. Justificación breve

Sin producción estable, la evidencia de *aprender haciendo* en producto real se degrada a
demos locales efímeras. Un horizonte de **≥ 24 meses** cubre al menos un ciclo completo
docente + ventana de análisis/publicación del caso, y deja margen a un segundo grupo.

## 5. Entregables de control (si se concede)

1. Informe anual de disponibilidad / coste real vs presupuesto.
2. Inventario de servicios en producción (sin secretos en git público).
3. Aviso al CEI / DPD si el despliegue cambia el flujo de datos personales (no previsto en
   el diseño mínimo).

## 6. Decisiones solicitadas

| # | Decisión | Sí / No / Condicionado |
| - | -------- | ---------------------- |
| 1 | Apoyar la continuidad en producción ≥ 24 meses | ☐ |
| 2 | Canal de fondos: grado / ECSIT / investigación / mixto | ☐ (especificar) |
| 3 | Validar importes con servicios TI antes de compromiso | ☐ |

## 7. Conformidad / enterado

### Coordinación grados tecnológicos — Sandra Garrido

Firma: ______________________ Fecha: ____ / ____ / ________

### Dirección de grados — Fernando Blázquez Piñeiro

Firma: ______________________ Fecha: ____ / ____ / ________

### IP ECSIT — Rafael Conde Melguizo, PhD

Firma: ______________________ Fecha: ____ / ____ / ________

### Oficina de investigación / OTRI (si aplica)

Nombre: ______________________ Firma: ______________________ Fecha: ____ / ____ / ________

---

**Nota:** los firmados no se suben al repositorio git de TTOD.
