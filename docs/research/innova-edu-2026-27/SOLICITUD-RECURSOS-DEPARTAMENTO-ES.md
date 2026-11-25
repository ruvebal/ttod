<!--
Solicitud de recursos al departamento: despliegue, comunicación y congreso.
BORRADOR 2026-11-24, redactado con asistencia de IA (Claude, Anthropic); revisión del IP pendiente.
Este documento NO es la memoria de la convocatoria Innova EDU: va al departamento y no se imputa a esa ayuda.
-->

**Para:** Sandra Garrido (Coordinación de grados tecnológicos) · Fernando Blázquez Piñeiro (Dirección
Full-Stack / Ciencia de Datos e IA)
**CC:** Rafael Conde Melguizo, PhD (IP del grupo ECSIT) · Departamento de Comunicación [PENDIENTE: persona de contacto]
**De:** Rubén Vega Balbás, PhD · Profesor de Desarrollo Web *Front-End* I y II
**Fecha:** [PENDIENTE] · **Asunto:** Recursos para desplegar TTOD y Neoplastix, darlos a conocer y presentarlos en congreso

# Solicitud de recursos: despliegue, comunicación y congreso

## 1. Qué se solicita, en una frase

Recursos institucionales para **desplegar dos aplicaciones reales construidas por cohortes de
estudiantes** en el primer semestre de 2026-27, para que **Comunicación las dé a conocer** y para
**presentarlas en congreso** como experiencia de docencia con IA agéntica sobre proyectos reales.

## 2. Las dos aplicaciones

| | TTOD Oracle (*Front-End* II) | Neoplastix (*Front-End* I) |
| --- | --- | --- |
| Qué es | Plataforma bilingüe de un corpus de aforismos pedagógicos para desarrolladores, con grafo navegable y un oráculo con modelo de IA local | Estudios geométricos medidos de composiciones neoplásticas: galería, editor SVG, impresión calibrada y modo quiosco |
| Quién la hizo | 8 estudiantes en 5 equipos; 53 *pull requests* integradas de 7 autores | 7 estudiantes de dos titulaciones |
| Estado | Endurecimiento previo a producción en curso: cabeceras de seguridad, límites de peticiones, contenedores sin privilegios y comprobaciones de salud hechos; quedan dos integraciones pendientes de fusionar y la fase de cuotas del oráculo | En línea (sitio estático): `https://neoplastix.crea-comm.net` |
| Licencias | Código MIT · contenidos CC BY-NC-SA 4.0 | Código MIT · contenidos CC BY-NC-SA 4.0 |

## 3. Recursos solicitados

### A. Despliegue de TTOD Oracle

| Recurso | Especificación orientativa |
| --- | --- |
| Máquina virtual (UDIT o proveedor contratado por UDIT) | 4 vCPU, 8 GB de RAM y 40 GB de disco; Docker y Docker Compose; sin GPU (el modelo local es pequeño y funciona en CPU) |
| Nombre de dominio y TLS | Subdominio institucional [PENDIENTE: p. ej., `ttod.udit.es`] con certificado; el proxy Caddy del proyecto ya gestiona las cabeceras |
| Acceso | Administración por el IP; copias de seguridad del volumen Redis (cuentas y favoritos) |
| Duración | Al menos hasta el final del curso 2027-28 |

**Condición previa:** antes de exponerla públicamente, el IP cerrará la fase pendiente de
endurecimiento (cuota del oráculo y comprobación final). Hasta entonces el sitio se publicará con
`noindex`.

### B. Neoplastix en un espacio físico de UDIT

| Recurso | Especificación orientativa |
| --- | --- |
| Pantalla táctil o quiosco en un espacio de paso (Materioteca, hall o laboratorio) | Pantalla táctil con navegador en modo quiosco; el visitante transforma una composición y se lleva la receta por QR o la imprime |
| Subdominio institucional (opcional) | Redirección o alias del dominio actual |

Los visitantes del quiosco no dejan datos: solo se cuentan sesiones iniciadas, rondas completadas y
mediana del giro de color, sin imágenes ni identificadores.

### C. Comunicación

1. Noticia en `udit.es` y en redes: «estudiantes de primer y segundo curso construyen y publican
   aplicaciones reales con IA bajo revisión humana».
2. Pieza breve en vídeo del quiosco Neoplastix y del oráculo TTOD.
3. Presencia en la Semana de Investigación de UDIT y en jornadas de puertas abiertas.

**Salvaguardas:** solo aparece quien lo autorice expresamente (consentimiento de imagen separado y
opcional). Los créditos del alumnado figuran en los README de cada producto. Nada de lo que se
comunique se presenta como resultado de investigación antes del análisis.

### D. Presentación en congreso

Apoyo (inscripción y desplazamiento) para presentar en congreso la experiencia de los dos casos:
JENUI en español y, si se acepta, SIGCSE TS o ITiCSE en inglés. Coautoría opcional del alumnado.
[PENDIENTE: fechas y plazos de envío de 2027; importe estimado.]

## 4. Relación con la convocatoria Innova EDU UDIT 2026-27

El IP presenta a esa convocatoria el proyecto **ATELIER-IA**, que empaqueta el método de estos dos
casos como kit transferible y lo pilota en *Front-End* I en el segundo semestre. Esta solicitud cubre
lo que la convocatoria no financia (equipamiento, despliegue institucional permanente, difusión y
congreso) y **no se imputa a ella**, por lo que no hay doble financiación.

## 5. Calendario propuesto

| Cuándo | Qué |
| --- | --- |
| Diciembre de 2026 | Respuesta del departamento; contacto con Comunicación |
| Enero de 2027 | Máquina virtual y subdominio; TTOD desplegada con `noindex`; quiosco instalado |
| Febrero de 2027 | TTOD abierta al público tras el cierre del endurecimiento; noticia y vídeo |
| Primavera de 2027 | Envío a congreso [PENDIENTE: plazo concreto] |
| Semana de Investigación | Demostración de ambos productos y del kit ATELIER-IA |

Quedo a vuestra disposición para concretar cualquier punto.

Rubén Vega Balbás, PhD
