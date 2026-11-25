---
title: "ATELIER-IA"
subtitle: "Memoria técnica · Convocatoria competitiva de proyectos internos de innovación educativa UDIT 2026-2027"
lang: es
---

<!-- BORRADOR 2026-11-24 · redactado con asistencia de IA (Claude, Anthropic) y pendiente de revisión
íntegra del IP. Marcadores [PENDIENTE: …] = datos que solo el IP puede confirmar. Límite: 15 páginas
sin portada ni referencias. -->

# Portada

**Título (ES).** ATELIER-IA: cohortes de desarrollo sobre productos reales con IA agéntica. Un kit
transferible para aprender haciendo en ingeniería *front-end*.

**Title (EN).** ATELIER-IA: Real-product development cohorts with agentic AI. A transferable kit for
learning by doing in front-end engineering.

**Acrónimo.** ATELIER-IA

**Investigador principal.** Rubén Vega Balbás, PhD. Profesor de Desarrollo Web *Front-End* I y II,
UDIT. Funciones: dirección, diseño del kit, docencia del piloto, análisis, difusión.

**Equipo.** [PENDIENTE: miembros adicionales, si los hay]. Funciones previstas sin persona asignada:
custodio independiente de consentimientos (PDI o PTGAS ajeno a la evaluación del grupo); segundo
evaluador de la rúbrica de uso crítico de IA; docente externo al proyecto que revisa el kit
(transferencia).

**Grupo de investigación.** Alineado con el grupo ECSIT, *Innovación y Tecnología desde y para la
Educación, la Cultura y la Sociedad* (IP: Rafael Conde Melguizo, PhD). Departamento: grados
tecnológicos (Desarrollo Full-Stack; Ciencia de Datos e IA).

**Línea temática principal.** 3. Alfabetización visual, digital, mediática y en inteligencia
artificial (uso responsable de la IA generativa).
**Líneas secundarias.** 2. Tecnologías digitales y experiencias emergentes para el aprendizaje ·
8. Cultura académica y visibilización del aprendizaje.

**Tipo de resultado verificable (§3.1).** Modelos transferibles (protocolo, guías, instrumentos de
evaluación, secuencia didáctica) y tecnología educativa (repositorio plantilla y herramientas).
**Evidencia de pilotaje.** *Front-End* I, segundo semestre 2026-27, grupo completo.

**Importe solicitado.** 1.000 € (IVA incluido). **Duración.** 12 meses desde la aceptación.

**Naturaleza.** Propuesta de continuidad (§7): parte de dos casos docentes del curso 2026-27 y
demuestra un avance sustantivo en diseño, evaluación y transferencia.

\newpage

# 1. Diagnóstico y necesidad

**Contexto.** En los grados tecnológicos de UDIT, el alumnado de desarrollo web programa ya con
asistentes de IA generativa a su alcance permanente. El asistente puede producir un componente que
funciona sin que quien lo entrega sepa explicarlo, modificarlo o defenderlo. La literatura de
investigación en educación informática describe esa brecha: el rendimiento con IA no equivale a
aprendizaje, y el alumnado novel puede salir perjudicado si la herramienta sustituye el proceso
(Prather et al. 2024; Liu, Fan y Pan 2026). Liu, Fan y Pan describen además una calibración
metacognitiva atenuada: un desajuste entre la preparación que el estudiante percibe y su capacidad
independiente (2026, 1). En asignaturas avanzadas de desarrollo web, el alumnado usa la IA para
generar código e ideas y declara aprender y producir más, pero teme la sobredependencia y las
soluciones incorrectas (Alpizar-Chacon y Keuning 2025, 1). Aunque la IA mejora la calidad de las
entregas, persisten las entregas sin verificar, y en exámenes sin IA el rendimiento no mejora (Zhu y
Liu 2026, 2). Evaluar solo el producto final convierte el uso indebido de IA en un problema de
medición: si se pierde la visibilidad del proceso, se pierde la evidencia de aprendizaje (Davalos y
Zhang 2026).

**Población.** Alumnado de *Front-End* I (primer curso de las asignaturas de desarrollo web *front-end*),
grupo del curso 2026-27. Durante el primer semestre, el grupo (7 puestos, dos titulaciones) construye
la aplicación pública Neoplastix. En el segundo semestre la asignatura aborda React y su proyecto
integrador. [PENDIENTE: confirmar n matriculado en el segundo semestre.]

**Limitación actual.** La práctica habitual en las asignaturas de desarrollo web tiene tres rasgos:
(a) proyectos individuales de portafolio, cuyo resultado se evalúa sobre todo por el producto;
(b) una política de IA que oscila entre la prohibición difícil de verificar y la permisividad no
documentada; (c) cuando un docente consigue un método mejor, ese método vive en sus materiales
personales y no se transfiere a otras asignaturas ni a otros docentes.

**Situación de partida y evidencias.** El IP ha ensayado durante el primer semestre de 2026-27 una
alternativa en dos asignaturas (véase §2.3). En *Front-End* II, ocho estudiantes en cinco equipos
desarrollaron como cohorte la plataforma TTOD Oracle: 53 *pull requests* de 7 autores integradas en
el repositorio público, con registro de uso de IA en cada PR y defensa oral el 15 de octubre de 2026.
En *Front-End* I, siete estudiantes construyen la aplicación pública Neoplastix (en línea). Esos dos
casos dejan tres carencias que motivan este proyecto:

1. **El método no está empaquetado.** Vive en los planes del IP (decenas de documentos de fase,
   revisiones y decisiones). Otro docente no podría reproducirlo sin acompañamiento.
2. **No hay línea de base.** Ninguno de los dos casos midió al inicio la capacidad del alumnado para
   explicar y modificar código, de modo que no se puede describir el cambio.
3. **La evidencia de proceso se valoró de forma desigual.** La observación docente del caso 1 indica
   que la excelencia del producto puede convivir con una reflexión débil sobre el uso de IA. Por eso
   conviene puntuar ambos ejes por separado y con más de un evaluador.

# 2. Fundamentación y antecedentes

## 2.1. Marco pedagógico

El proyecto se apoya en tres principios.

**Aprender haciendo en un producto real y en cohorte.** El alumnado participa como equipo de
desarrollo de un producto con usuarios, repositorio público y revisión profesional. El portafolio
auto-codificado ya se ha estudiado como evaluación auténtica en asignaturas de diseño y desarrollo
web (Garcia 2025). Este proyecto da un paso más: un producto común, una cohorte que se revisa entre
sí y unas costuras de trabajo (*seams*) asignadas por equipo.

**La evidencia de proceso como dato principal.** Lo que muestra aprendizaje no es el código final
sino la traza: el plan antes del *prompt*, el registro de qué sugerencia se aceptó, cuál se rechazó y
por qué, qué se verificó personalmente, y la defensa oral de una decisión. La investigación sobre
datos de proceso de programación (Fischer et al. 2024) y sobre autorregulación en la interacción
estudiante-IA (López-Pernas et al. 2025) respalda tratarlos como evidencia, con su propia
arquitectura de consentimiento. Las trazas de revisión permiten interpretar esfuerzo, razonamiento y
posible intervención de la IA más allá del producto entregado (Davalos y Zhang 2026, 8). Además, la
mayoría de los estudios se apoyan en autoinformes o en tareas breves y aisladas, mientras que las
trazas reales de una asignatura de programación web con encargos de complejidad realista muestran
otros patrones de uso (Isa et al. 2026, 1). Planificar antes de pedir ayuda a la IA se asocia a un
mejor rendimiento, aunque sin causalidad establecida (Phung et al. 2025, 9). Ese hallazgo respalda
el eje «Diferir» de la rúbrica (planificar antes del *prompt*).

**Uso crítico de IA como competencia evaluable.** El uso de IA se declara y se convierte en objeto de
evaluación. No se trata como falta automática ni como sustitución silenciosa de la autoría. El marco
*Computer Science Curricula 2023* incorpora la IA generativa, la ética y la responsabilidad
profesional al currículo. El marco de evaluación resistente a la IA de Nikolić y Basta Nikolić
desplaza la evaluación de la calidad del producto al razonamiento, la toma de decisiones y la
apropiación del aprendizaje, y lo hace con cuatro pilares: documentación del proceso, defensa oral,
tareas auténticas y políticas transparentes de uso de IA. Sus autores advierten que el artículo no
aporta resultados empíricos ni datos de validación (2026, 1). En la educación de diseño basada en el
taller, la IA generativa altera la crítica dialógica y difumina la responsabilidad ética, y obliga a
evaluar priorizando la reflexión crítica y la transparencia del proceso (Park 2025, 2, 11). Ese
contexto es especialmente pertinente en una universidad de diseño como UDIT.

## 2.2. Marco metodológico

Se trata de investigación basada en diseño en forma de estudio de caso acotado, de datos ricos y
dominancia cualitativa. No es un experimento controlado: el estudio de caso es observacional y ofrece
menos control que un experimento (Wohlin et al. 2012, 33; Runeson y Höst 2009; Runeson et al. 2012). En investigación en educación informática, una n pequeña es legítima para
obtener comprensión, no confianza estadística (Brown y Guzdial 2024). La transferibilidad, el
consentimiento y los resultados nulos se informan según McGill et al. (2023) y Heckman et al. (2022).
El hueco que se aborda, la IA generativa más allá de los cursos introductorios, es el que señala el
grupo de trabajo de ITiCSE 2026 sobre educación posintroductoria.

## 2.3. Experiencias previas del IP (estado de partida)

| | Caso 1: TTOD Oracle | Caso 2: Neoplastix |
| --- | --- | --- |
| Asignatura | *Front-End* II, 2026-27, 1.er semestre | *Front-End* I, 2026-27, 1.er semestre |
| Producto | Plataforma bilingüe de un corpus pedagógico (Astro, islas Svelte/React, FastAPI, servidor MCP, modelo local Ollama, Redis) | Estudios geométricos medidos de composiciones neoplásticas (Astro, isla Svelte, SVG, analizador Python) |
| Cohorte | 8 estudiantes, 5 equipos | 7 puestos, 2 titulaciones |
| Huella pública | 53 PR integradas de 7 autores; CI con pruebas; defensa oral 15/10/2026 | Sitio en línea; fases M0–M3 cerradas; conjunto de datos de obras medidas (CC BY-NC-SA) |
| Método | Esqueleto andante, costuras por equipo, registro de IA por PR, revisión «en frío», fusión solo humana | El mismo método, con conflictos de git gestionados por el alumnado |

**Posición del Comité de Ética de Investigación (22/10/2026).** Sobre la línea de investigación de
TTOD, el Comité indicó que no necesita emitir dictamen y que la investigación puede seguir,
manteniéndolo informado, bajo cuatro condiciones: aceptación de la práctica como actividad docente
por el departamento; aceptación del alumnado; anonimización en la investigación; y presencia del
alumnado como coautor. Este proyecto cumple esas condiciones y, al añadir instrumentos nuevos
(cuestionarios), solicita de nuevo la evaluación del Comité antes de reclutar (§6.4).

**Lecciones previas (observación docente, no resultados de investigación).** Los datos de los casos
1 y 2 no se analizan aquí como datos de investigación. Su análisis exige el cierre de actas y la
custodia de los consentimientos.

- El registro de IA funcionó cuando el equipo lo trató como superficie de decisión, no como trámite.
- Declarar con honestidad lo que verificó el asistente («lo ejecutó la IA; no lo reclamo como mío»)
  es una señal de control positiva.
- Un producto excelente no garantiza reflexión metacognitiva, así que los dos ejes se puntúan por
  separado.
- La higiene de git la absorbió el docente; el caso 2 ya devuelve los conflictos al alumnado.

# 3. Innovación y valor añadido

**Cambio propuesto.** El proyecto pasa de «un docente con un método» a «un kit que cualquier docente
puede aplicar y evaluar». En el segundo semestre de *Front-End* I, el proyecto integrador de React deja
de ser individual y se desarrolla como producto real de cohorte, con el kit ATELIER-IA y con
evaluación pre/post.

| | Práctica actual | Casos 1–2 (2026-27, 1.er sem.) | ATELIER-IA |
| --- | --- | --- | --- |
| Unidad de trabajo | Proyecto individual | Producto de cohorte | Producto de cohorte |
| IA | Prohibida o no documentada | Declarada y registrada por PR | Declarada, registrada y evaluada con rúbrica de dos evaluadores |
| Evidencia | Producto final | Producto + proceso + defensa | Producto + proceso + defensa + **línea de base pre/post** |
| Transferencia | Ninguna | Depende del IP | **Kit abierto**, revisado por un docente externo |
| Visibilidad | Entrega privada | Repositorio y sitio públicos | Productos desplegados, demostración, coautoría opt-in |

**Novedad contextual.** Cada pieza tiene precedentes: proyectos reales, revisión entre pares,
declaración de IA. Lo nuevo en UDIT es combinarlas en un protocolo con trazabilidad completa, que
ya ha funcionado en dos asignaturas y dos niveles. También es nuevo empaquetarlo como recurso
transferible y medir el cambio con línea de base en una tercera asignatura. ATELIER-IA operacionaliza
los cuatro pilares de Nikolić y Basta Nikolić (proceso, defensa oral, tarea auténtica y política de IA
transparente) con plantillas, una rúbrica y un protocolo de defensa, y los pilota con datos. Sus
autores lo proponen sin validación empírica (2026, 1).

**Por qué no es una actuación ordinaria.** No se digitalizan materiales, no se compra equipo y no se
mantiene una plataforma existente (§3 de las bases). Se diseña, pilota y evalúa una intervención con
hipótesis de diseño, público definido, instrumentos y criterios de éxito.

**Ventaja de equidad.** El kit funciona con un modelo de IA local y gratuito, ejecutado en el equipo
del alumnado. Nadie necesita una suscripción de pago para participar en igualdad de condiciones.

# 4. Objetivos e indicadores

**Objetivo general.** Diseñar, pilotar y evaluar un kit transferible que convierta el desarrollo en
cohorte de un producto real con IA agéntica en una actividad de aprendizaje con evidencias de proceso
verificables.

**Objetivos específicos.**

- **OE1.** Empaquetar el método de los casos 1–2 en un kit abierto (versión 1).
- **OE2.** Pilotar el kit con el grupo completo de *Front-End* I en el segundo semestre de 2026-27.
- **OE3.** Describir pre/post la capacidad del alumnado para explicar y modificar su propio código y
  su uso crítico de la IA.
- **OE4.** Comprobar la transferibilidad mediante la revisión del kit por un docente ajeno al
  proyecto.
- **OE5.** Hacer visible el aprendizaje: productos desplegados, kit publicado, demostración en la
  Semana de Investigación y comunicación a congreso.

| Ind. | Indicador | Instrumento | Valor de partida | Meta | OE |
| --- | --- | --- | --- | --- | --- |
| I1 | % de PR integradas con registro de IA completo (plan, decisión aceptar/rechazar, verificación nombrada) | Auditoría de PR con plantilla | Agregado de los casos 1–2, calculado en M1 tras el cierre de actas | ≥ 80 % | OE2 |
| I2 | % de estudiantes con al menos un rechazo de sugerencia de IA defendido | Registro de IA + defensa | Caso 1: rastro de rechazos débil en 2 de 5 equipos (observación docente) | ≥ 80 % | OE2 |
| I3 | Tarea de explicar y modificar código propio (rúbrica 0–4) | Tarea estructurada pre (feb.) y post (jun.) | Pre-test | Mejora descrita en ≥ 70 % de participantes | OE3 |
| I4 | Discrepancias entre defensa y artefacto documentadas | Notas estructuradas de defensa | No registradas de forma sistemática | 100 % de defensas con nota estructurada | OE3 |
| I5 | Fiabilidad entre evaluadores de la rúbrica de uso crítico de IA | Doble puntuación de una muestra | No existe | Acuerdo documentado; discrepancias resueltas por consenso | OE3 |
| I6 | Revisión del kit por docente externo | Protocolo de revisión + entrevista breve | Ninguna | ≥ 1 revisión completa; ≥ 1 intención de adopción en 2027-28 | OE4 |
| I7 | Accesibilidad de productos y kit | Auditoría externa WCAG 2.2 AA + pruebas automáticas | Pruebas automáticas parciales | 0 incidencias bloqueantes al cierre | OE1 |
| I8 | Difusión y apertura | Repositorio del kit con licencia abierta y DOI; envío a congreso; demostración | — | Kit v1 publicado; 1 comunicación enviada; demo realizada | OE5 |

**Criterio de éxito global.** Se alcanzan las metas de I1, I3, I6 e I8, y los resultados nulos o
mixtos se informan como tales.

# 5. Público y entorno de pilotaje

| Elemento | Definición |
| --- | --- |
| Perfil | Estudiantes de *Front-End* I (Desarrollo Full-Stack y Ciencia de Datos e IA), mayores de edad |
| Número previsto | Grupo completo del 2.º semestre, n ≈ 7 [PENDIENTE: confirmar] + 1 docente externo (transferencia) |
| Selección y acceso | Todo el grupo realiza la actividad docente. La participación en la investigación es voluntaria, la gestiona un custodio independiente y no afecta a la calificación |
| Criterios de inclusión en el corpus | Aceptación expresa del uso investigador (consentimiento B) |
| Exclusión | Quien no acepte (su trabajo cuenta como actividad docente y no entra en el corpus) |
| Contexto | Presencial, con repositorio público en GitHub y trabajo en el equipo propio del alumnado |
| Calendario | Febrero–junio de 2027 (2.º semestre); el análisis empieza tras el cierre de actas |
| Colaboración externa | Auditoría de accesibilidad por especialista no vinculado a UDIT (factura) |

El acceso al grupo depende directamente de UDIT (docencia del IP), por lo que no se requiere carta de
compromiso de una entidad externa.

# 6. Diseño de la solución

## 6.1. El kit ATELIER-IA

| Componente | Qué es | De dónde procede |
| --- | --- | --- |
| K1. Repositorio plantilla | Esqueleto andante React que funciona de punta a punta desde el primer día, con CI y pruebas | Caso 1 (esqueleto andante) y caso 2 (monorrepo) |
| K2. Mapa de costuras | Cómo dividir un producto en costuras asignables por equipo sin colisiones | Casos 1–2 |
| K3. Contrato de PR y registro de IA | Plantilla de PR: plan, decisión aceptar/rechazar/verificar, fuente | Casos 1–2 |
| K4. Revisión «en frío» | Protocolo de revisión antes de integrar; un modelo local puede comentar (MUST FIX/NIT), nunca aprobar ni fusionar | Casos 1–2 |
| K5. Defensa oral | Guion de defensa de una decisión o un número; nota estructurada | Casos 1–2 |
| K6. Rúbrica de uso crítico de IA | Cuatro ejes (Diferir, Narrar, Criticar, Verificar), 8 señales de 0 a 2, separada de la rúbrica de producto | Caso 1 |
| K7. Paquete ético | Hoja de información, consentimientos A/B, custodia, guion para el Comité | Caso 1 |
| K8. Herramientas de investigación | Script de seudonimización (git, PR y declaraciones convertidos en P01…Pn), plantilla de libro de códigos | Caso 2 |
| K9. Guía docente | Secuencia didáctica de un semestre y guía de adopción para otro docente | Nuevo |

**Experiencia de usuario (alumnado).** El primer día, cada estudiante ejecuta el producto completo en
su equipo y recibe una costura y una primera tarea pequeña. Cada aportación sigue el mismo ciclo:
plan, PR, registro de IA, revisión, corrección, integración por una persona y defensa.

**Arquitectura.** Repositorio público con rama principal protegida, CI obligatoria, revisión humana
para integrar y un modelo de IA local opcional para comentarios. Los productos de los casos 1–2
sirven como ejemplos de referencia. Su despliegue institucional se solicita aparte al departamento.

## 6.2. Accesibilidad e inclusión

La accesibilidad es un requisito de diseño y no una comprobación final. Se exigen navegación por
teclado, foco visible, regiones vivas y textos alternativos calculados; se ejecutan pruebas
automáticas en CI y, al final, una auditoría externa WCAG 2.2 AA (I7). El kit se publica en español
e inglés. La participación diferencial (carga de trabajo, equipos desiguales) se trata como pregunta
de investigación. No se recogen datos de género ni otras categorías: con una n pequeña facilitarían la
reidentificación.

## 6.3. Seguridad y sostenibilidad

Los productos de referencia ya pasaron una fase de endurecimiento previa a producción: cabeceras de
seguridad, límites de peticiones, contenedores sin privilegios y comprobaciones de salud. El modelo
local es pequeño y no requiere GPU ni nube. Neoplastix es un sitio estático. El kit no depende de
licencias de pago.

## 6.4. Ética, protección de datos e inteligencia artificial (§13 de las bases)

**Comité de Ética.** Las cuatro condiciones de la posición del Comité del 22/10/2026 se aplican a
esta cohorte desde cero: la aceptación de otras cohortes no se traslada. Como se añaden cuestionarios
y una tarea pre/post, el protocolo se remite al Comité en enero de 2027, antes de reclutar y de
recoger datos. No se solicita evaluación retrospectiva. Hay un precedente comparable: un estudio de 14
estudiantes en una asignatura avanzada de desarrollo web, con consentimiento firmado para analizar las
tareas relacionadas con la IA y publicar citas anonimizadas, participación voluntaria y derecho de
retirada (Alpizar-Chacon y Keuning 2025, 3). El marco de impactos éticos y sociales de la IA
generativa en la educación informática superior (equidad, integridad académica, sesgo y procedencia
de los datos) orienta la guía ética del kit (Mak et al. 2025, 1).

**Datos.** El corpus de investigación es independiente del repositorio docente. Contiene solo trazas
seudonimizadas (P01…Pn) de quienes aceptan. Las calificaciones y los identificadores quedan fuera;
los consentimientos firmados se custodian fuera del repositorio; el análisis empieza tras el cierre
de actas. No se recogen datos de categorías especiales. El riesgo residual de reidentificación (los
repositorios son públicos) se gestiona con consentimiento específico para citar fragmentos y con
retención confidencial, nunca como «datos abiertos anónimos».

**Sistemas de IA utilizados.**

| Sistema | Finalidad | Intervención humana | Datos tratados |
| --- | --- | --- | --- |
| Asistentes de programación que use el alumnado (herramientas autorizadas por UDIT) | Ayuda al desarrollo, declarada en cada PR | El alumnado acepta, rechaza y verifica; integra siempre una persona | Código del proyecto; nunca datos personales |
| Modelo local (Ollama) como revisor | Comentarios MUST FIX/NIT en PR | Nunca aprueba, puntúa ni fusiona | Diff público del PR |
| Modelo local en el producto (oráculo de TTOD) | Funcionalidad del producto de referencia | Respuestas marcadas como generadas; la fuente canónica la gobiernan personas | Corpus pedagógico público |

**Evaluación indelegable.** La IA no califica, no emite resoluciones y no puntúa la rúbrica. Las dos
rúbricas (producto y uso crítico de IA) las aplica el profesorado, que asume la responsabilidad
plena, de acuerdo con la consideración de alto riesgo del Reglamento (UE) 2024/1689 para la IA en
evaluación educativa. Los riesgos de sesgo, error, dependencia y opacidad se abordan con la
declaración obligatoria, el registro de rechazos, la frontera explícita de verificación («qué
comprobé yo y qué ejecutó el modelo») y la defensa oral. No se introducen datos del alumnado en
herramientas no autorizadas: el corpus seudonimizado se analiza en local.

# 7. Metodología de implementación y evaluación

## 7.1. Fases

| Fase | Meses | Contenido |
| -------------------- | -------- | ------------------------------------------------------------ |
| F0. Preparación | M1 | Remisión al Comité; kit v0 a partir de los casos 1–2; instrumentos pre/post; custodio; producto del semestre [PENDIENTE: producto React concreto] |
| F1. Pre-test | M2 | Información, consentimientos (custodio); tarea de explicar y modificar código; cuestionario |
| F2. Pilotaje | M2–M5 | Sprints por costuras; PR con registro de IA; revisiones en frío; observación con diario del IP |
| F3. Cierre docente | M5–M6 | Defensa oral con notas estructuradas; post-test; calificación (solo humana) |
| F4. Análisis | M7–M9 | Tras el cierre de actas: corpus seudonimizado; auditoría de PR (I1–I2); doble puntuación (I5); análisis temático y trazado de proceso |
| F5. Transferencia | M8–M11 | Kit v1; revisión por docente externo (I6); auditoría de accesibilidad (I7); publicación con DOI |
| F6. Difusión y cierre | M10–M12 | Comunicación a congreso; demostración en la Semana de Investigación; memoria final |

## 7.2. Instrumentos y análisis

- **Trazas de proceso** (commits, PR, registros de IA, revisiones): auditoría con plantilla y trazado
  descriptivo del proceso.
- **Tarea de explicar y modificar** (pre/post): el estudiante explica un fragmento de su propio código
  y lo modifica ante un cambio de requisito. Rúbrica de 0 a 4, aplicada a ciegas respecto al
  momento (pre/post) por dos evaluadores. Se realiza sin asistente de IA. Así mide la capacidad
  independiente, que es la que aparece desajustada respecto a la percibida (Liu, Fan y Pan 2026, 1)
  y la que no mejora en pruebas sin IA aunque mejoren las entregas (Zhu y Liu 2026, 2).
- **Cuestionario breve** (pre/post) de autoeficacia programando con IA y de uso crítico. La selección
  y adaptación de un instrumento con validez documentada se cierra en F0. [PENDIENTE: búsqueda
  bibliográfica; no se citan escalas sin verificar.]
- **Notas estructuradas de defensa** y diario de campo del IP.
- **Protocolo de revisión del kit** para el docente externo.

**Diseño.** Caso único con comparación pre/post descriptiva y triangulación de producto, registro
escrito y defensa oral: una discrepancia entre ellos es evidencia. La pregunta de investigación, el
libro de códigos y las reglas de inclusión se versionan antes de examinar el corpus. Se conservan los
casos que contradicen las expectativas. No se hacen afirmaciones causales.

## 7.3. Riesgos y mitigación

| Riesgo | Mitigación |
| ------------------------------ | ---------------------------------------------------- |
| La resolución o el Comité se retrasan respecto al inicio del semestre | Kit v0 listo en M1; si el Comité no ha respondido, la actividad docente sigue y la recogida de datos de investigación empieza al recibir su respuesta, sin pre-test retrospectivo |
| n pequeña | Diseño de datos ricos y cualitativo; sin inferencia poblacional; transferibilidad argumentada |
| Conflicto entre el papel de docente y el de investigador | Custodio independiente; IP ciego al estado de consentimiento hasta el cierre de actas; análisis posterior |
| Dependencia de la IA o desigualdad de acceso | Modelo local gratuito; declaración y verificación obligatorias |
| Sobrecarga del alumnado por el protocolo | Plantillas breves; RQ-C3 mide qué partes del kit se perciben como sobrecarga |
| Cambios de las herramientas (versiones mayores) | Versiones fijadas en el kit; actualización planificada con las pruebas previas como puerta |

# 8. Cronograma de trabajo

Inicio estimado: aceptación en enero de 2027 (M1 = enero de 2027; M12 = diciembre de 2027). La
memoria final se entrega en los 30 días siguientes.

| Tarea | Resp. | M1 | M2 | M3 | M4 | M5 | M6 | M7 | M8 | M9 | M10 | M11 | M12 |
| ------------------------------------------ | -------------- | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: |
| F0 Preparación y Comité | IP | X | | | | | | | | | | | |
| F1 Pre-test | IP + custodio | | X | | | | | | | | | | |
| F2 Pilotaje | IP | | X | X | X | X | | | | | | | |
| F3 Defensa y post-test | IP | | | | | X | X | | | | | | |
| Informe intermedio (≤ 10 p.) | IP | | | | | | X | | | | | | |
| F4 Análisis | IP + 2.º evaluador | | | | | | | X | X | X | | | |
| F5 Kit v1, revisión externa, auditoría | IP + externo | | | | | | | | X | X | X | X | |
| F6 Congreso, demo, memoria final | IP | | | | | | | | | | X | X | X |

**Hitos y entregables.** H1 (M1): protocolo remitido al Comité y kit v0. H2 (M2): pre-test cerrado.
H3 (M6): defensas, post-test e informe intermedio. H4 (M9): análisis cerrado. H5 (M11): kit v1
publicado con DOI y auditoría hecha. H6 (M12): comunicación enviada, demostración y memoria final.

# 9. Presupuesto

| Partida (§8.1) | Detalle | Coste est. (IVA incl.) | Tarea / entregable |
| --- | --- | ---: | --- |
| Servicios de nube y alojamiento | Entornos de previsualización para las PR del piloto y espacio de demostración, feb. 2027 – ene. 2028 (≈ 20 €/mes) [PENDIENTE: proveedor] | 240 € | F2, F6 / I1, I8 |
| Evaluación técnica especializada: accesibilidad | Auditoría WCAG 2.2 AA del kit y de los productos de referencia, con prueba con lector de pantalla, por especialista externo con factura | 450 € | F5 / I7 |
| Traducción y adaptación | Revisión lingüística de la versión inglesa del kit (recurso educativo abierto) | 160 € | F5 / I8 |
| Materiales para participantes y demostración | Impresión calibrada, pegatinas con QR y cartelería para la demostración en la Semana de Investigación | 150 € | F6 / I8 |
| **Total solicitado** | | **1.000 €** | |

**Escalado.** Con 800 €: se reduce la auditoría a una revisión experta sin prueba con usuarios
(−200 €). Con 600 €: además, se suprime la revisión lingüística y la versión inglesa la revisa el IP.

**Coste razonado total y cobertura.** Además de lo solicitado, el proyecto se apoya en: horas del IP
dentro de su dedicación docente e investigadora; equipos propios del alumnado (sin coste); y la
infraestructura institucional de despliegue y la difusión de los productos de referencia, que se
solicitan al departamento y a Comunicación por separado y no se imputan a esta ayuda (sin doble
financiación). No se solicitan gastos de personal, equipamiento general ni licencias ya cubiertas.
[PENDIENTE: declarar otras ayudas solicitadas o concedidas.]

# 10. Resultados, propiedad y transferencia

**Resultados.** (1) Kit ATELIER-IA v1 (K1–K9). (2) Producto React de cohorte desplegado.
(3) Informe de evaluación con resultados nulos o mixtos si los hay. (4) Comunicación a congreso.
(5) Demostración en la Semana de Investigación de UDIT.

**Licencias.** Código con licencia MIT; contenidos y guías con CC BY-NC-SA 4.0, el reparto que ya usa
el caso 1. Esas licencias son compatibles con la cesión no exclusiva a UDIT prevista en §13.3. La OTC
evaluará la conveniencia de protección antes de cualquier divulgación. El kit se deposita con DOI
(p. ej., Zenodo) y en el repositorio institucional con el código asignado por la OTC.

**Licencias de terceros (§13.3).** Astro, React, Svelte, Vite, FastAPI y Ollama (MIT); Caddy (Apache
2.0); Python (PSF). El modelo local es intercambiable: se usará uno con licencia que no restrinja el
uso, la adaptación ni el despliegue (preferentemente Apache 2.0). Redis 7.4+ se distribuye con
licencias RSALv2/SSPL; para garantizar la continuidad se sustituirá por Valkey (BSD-3), compatible.
[PENDIENTE: confirmar la lista final de dependencias en F0.]

**Escalabilidad y continuidad.** El kit está pensado para otras asignaturas de desarrollo de los
grados tecnológicos y para *Front-End* II 2027-28. El docente externo de I6 es la primera vía de
adopción. Las convocatorias externas candidatas (p. ej., programas de innovación docente o de
transferencia de la Comunidad de Madrid) se identificarán con el informe de evaluación en la mano.

**Difusión.** Envío a congreso de educación en ingeniería informática (JENUI en español; SIGCSE TS o
ITiCSE en inglés), con coautoría opt-in del alumnado y sin vincular nombres a seudónimos. Toda
comunicación incluirá el código de la OTC y el reconocimiento de la financiación de UDIT.

# 11. Alineación estratégica

**Grupo ECSIT.** El proyecto es innovación y tecnología *para* la educación: una práctica docente
nueva, sus instrumentos y su evaluación. Continúa la línea de investigación pedagógica sobre aprender
haciendo con IA agéntica (hebra B), ya informada al Comité de Ética y al IP del grupo.

**Departamento y Vicerrectorado de Ordenación Académica.** Responde a una necesidad compartida por
las asignaturas de programación: evaluar con garantías cuando el alumnado programa con IA. Ofrece un
modelo transferible entre asignaturas y titulaciones (Desarrollo Full-Stack y Ciencia de Datos e IA).

**TFG/TFM.** [PENDIENTE: ningún TFG vinculado por ahora; se ofrecerán líneas de TFG sobre el kit al
alumnado de los casos 1–2.]

**ODS.** ODS 4 (principal): 4.4, competencias digitales para el empleo, incluido el uso responsable
de la IA; 4.5, igualdad de acceso (IA local gratuita, accesibilidad). Secundarios: ODS 9 (innovación
e infraestructura abierta) y ODS 10 (reducción de la brecha económica de acceso a herramientas de IA).

\newpage

# Referencias

Alpizar-Chacon, Isaac, y Hieke Keuning. 2025. «Student's Use of Generative AI as a Support Tool in an
Advanced Web Development Course». En *Proceedings of the 30th ACM Conference on Innovation and
Technology in Computer Science Education V. 1*. https://doi.org/10.1145/3724363.3729106.

Brown, Neil C. C., y Mark Guzdial. 2024. «Confidence vs Insight: Big and Rich Data in Computing
Education Research». En *Proceedings of the 55th ACM Technical Symposium on Computer Science Education
V. 1*, 158–64. https://doi.org/10.1145/3626252.3630813.

*Computer Science Curricula 2023*. ACM, IEEE Computer Society y AAAI. https://doi.org/10.1145/3664191.

Davalos, Eduardo, y Yike Zhang. 2026. «AI Misuse in Education Is a Measurement Problem: Toward a
Learning Visibility Framework». arXiv. https://doi.org/10.48550/arxiv.2603.07834.

Fischer, Björn, Berit Barthelmes, Sven Eric Panitz, Eva-Maria Iwer y Ralf Dörner. 2024. «Seeking
Consent for Programming Process Data Collection with Trustee-Based Encryption». En *Proceedings of the
2024 ACM Conference on International Computing Education Research V.1*, 131–42.
https://doi.org/10.1145/3632620.3671125.

Garcia, Manuel B. 2025. «Self-Coded Digital Portfolios as an Authentic Project-Based Learning
Assessment in Computing Education». *Education Sciences* 15 (9): 1150.
https://doi.org/10.3390/educsci15091150.

Isa, Hajara-Yasmin, Matthew Weston, Muhammad Rizky Wellyanto, Ishita Karna, Jerry O. Talton III y
Ranjitha Kumar. 2026. «From Code Generation to Conceptual Learning: Student Use of LLMs in a Web
Programming Course». En *Proceedings of the 2026 CHI Conference on Human Factors in Computing Systems
(CHI '26)*. https://doi.org/10.1145/3772318.3793207.

Heckman, Sarah, Jeffrey C. Carver, Mark Sherriff y Ahmed Al-Zubidy. 2022. «A Systematic Literature
Review of Empiricism and Norms of Reporting in Computing Education Research Literature». *ACM
Transactions on Computing Education* 22 (1): art. 3. https://doi.org/10.1145/3470652.

ITiCSE Working Group. 2026. Informe sobre IA generativa en educación informática posintroductoria.
https://doi.org/10.1145/3760545.3783970. [PENDIENTE: completar autoría y título desde el DOI.]

Liu, Dandan, Guangrui Fan y Lihu Pan. 2026. «Tool, Tutor, or Crutch?: A Grounded Theory of Cognitive
Scaffolding and Offloading in AI-Assisted Programming Education». *International Journal of STEM
Education* 13: 10. https://doi.org/10.1186/s40594-025-00592-w.

López-Pernas, Sonsoles, Kamila Misiejuk, Eduardo Oliveira y Mohammed Saqr. 2025. «The Dynamics of the
Self-Regulation Process in Student-AI Interactions». En *Proceedings of the 25th Koli Calling
International Conference on Computing Education Research*. https://doi.org/10.1145/3769994.3770043.

Mak, Janice, Joyce Nakatumba-Nabende, Alison Clear, Tony Clear et al. 2025. «Navigating the Ethical and
Societal Impacts of Generative AI in Higher Computing Education». ACM ITiCSE Working Group.
https://doi.org/10.1145/3724389.3731282.

McGill, Monica M., Sarah Heckman, Christos Chytas et al. 2023. «Conducting Sound, Equity-Enabling
Computing Education Research». En *Proceedings of the 2023 Working Group Reports on Innovation and
Technology in Computer Science Education*, 30–56. https://doi.org/10.1145/3623762.3633495.

Nikolić, Dragan, y Marijana Basta Nikolić. 2026. «Designing AI-Resilient Assessment in Higher
Education: A Four-Pillar Conceptual Framework». *Frontiers in Artificial Intelligence* 9.
https://doi.org/10.3389/frai.2026.1841682.

Park, Hyunyim. 2025. «Generative AI in Studio-Based Design Education: Human–AI Relationships,
Collaboration and Assessment». En *IASDR 2025: Design Next*. https://doi.org/10.21606/iasdr.2025.845.

Phung, Tung, et al. 2025. «Plan More, Debug Less: Applying Metacognitive Theory to AI-Assisted
Programming Education». arXiv:2509.03171. [PENDIENTE: autoría completa y actas AIED 2025.]

Prather, James, et al. 2024. «The Widening Gap: The Benefits and Harms of Generative AI for Novice
Programmers». En *Proceedings of the 2024 ACM Conference on International Computing Education Research
V.1*. https://doi.org/10.1145/3632620.3671116.

Reglamento (UE) 2024/1689 del Parlamento Europeo y del Consejo, de 13 de junio de 2024, por el que se
establecen normas armonizadas en materia de inteligencia artificial.

Runeson, Per, y Martin Höst. 2009. «Guidelines for Conducting and Reporting Case Study Research in
Software Engineering». *Empirical Software Engineering* 14 (2): 131–64.
https://doi.org/10.1007/s10664-008-9102-8.

Runeson, Per, Martin Höst, Austen Rainer y Björn Regnell. 2012. *Case Study Research in Software
Engineering: Guidelines and Examples*. Hoboken, NJ: Wiley. https://doi.org/10.1002/9781118181034.

Wohlin, Claes, Per Runeson, Martin Höst, Magnus C. Ohlsson, Björn Regnell y Anders Wesslén. 2012.
*Experimentation in Software Engineering*. Berlín: Springer. https://doi.org/10.1007/978-3-642-29044-2.

Zhu, Suyang, y Zhengtao Liu. 2026. «Generative AI in Programming Education: An Empirical Analysis of
Student Performance and Assessment Challenges in the LLM Era». En *Proceedings of the 2026
International Conference on Big Data and Informatization Education*.
https://doi.org/10.1145/3806980.3806985.

# Declaración de uso de IA generativa en esta memoria (§13.2)

En la redacción de este borrador se ha utilizado Claude (Anthropic) como asistente: estructuración
según el esquema §9.3, redacción inicial y comprobación frente a la rúbrica. Los datos proceden de
los repositorios del IP. Las referencias se descubrieron con la búsqueda vectorial del estudio
y se verificaron contra el texto extraído de cada fuente, con su página. El registro de verificación
es `GROUNDING-LEDGER.md`. El IP revisa, corrige y asume íntegramente el contenido.
