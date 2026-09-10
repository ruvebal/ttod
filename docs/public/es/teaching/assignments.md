---
title: Tareas y backlog
eyebrow: Qué construyes, para quién y por qué
description: Personas, recorridos de usuario, el backlog de tareas por área y el compromiso de accesibilidad detrás de las seis áreas docentes de TTOD.
permalink: /es/teaching/assignments/
lang: es
---

# Qué construyes, para quién y por qué

La página de [modelo docente]({{ '/es/teaching/' | relative_url }}) explica cómo se mapean las
seis áreas a las unidades del curso. Esta página explica por qué importa cada una y cómo se ve
"terminado" — un backlog en términos de producto, no solo una lista de tareas de ingeniería.

## A quién sirve TTOD

| Persona | Qué quiere |
| --- | --- |
| Visitante | Encontrar un fragmento de sabiduría relevante para un momento, sin fricción y sin registro |
| Lector registrado | Mantener una biblioteca personal de citas a las que merece la pena volver |
| Colaborador | Añadir una cita que cree que pertenece al corpus |
| Revisor | Juzgar propuestas con las mismas herramientas ya usadas para revisar código |
| Desarrollador externo | Construir algo sobre los datos de TTOD sin hacer scraping del HTML |

No existe una "persona de accesibilidad" separada. Cada tarea de abajo hereda el mismo compromiso
de accesibilidad sin importar a qué persona sirva — ver más abajo, "Por qué la accesibilidad es un
compromiso, no una lista de verificación".

## Cuatro verbos

Cada tarea de este backlog es uno de cuatro verbos, hecho para una persona concreta: **encontrar**,
**guardar**, **preguntar**, **contribuir**. Si una funcionalidad no sirve a uno de esos cuatro
verbos para una persona nombrada, no pertenece al backlog.

## Recorridos de usuario

**Un visitante encuentra una cita que encaja con su momento.** Llega a la página de inicio →
navega por sección, etiqueta o nivel → abre el grafo de conocimiento y sigue una conexión → hace
una pregunta real al Oráculo → lee una respuesta fundamentada en una cita → repara en la
invitación a iniciar sesión y guardarla.

**Un lector registrado construye una biblioteca personal.** Inicia sesión → vuelve a una página de
cita → la guarda → regresa más tarde, abre su biblioteca → elimina una que ya no encaja.

**Un colaborador propone una cita nueva.** Inicia sesión → abre el formulario de propuesta →
envía una cita con su fuente → el sistema abre una solicitud de revisión → una persona revisora la
lee y puede pedir cambios → el colaborador revisa → la cita se publica, acreditada a su nombre. La
espera por la revisión es deliberada, no una fricción que eliminar — solo una persona nombrada
acepta jamás una cita en la colección gobernada.

**Una persona revisora procesa una propuesta.** Ve la solicitud en la cola normal de revisión →
lee la cita propuesta y su fuente → comenta, pide cambios o aprueba → la aprobación calcula el
cambio exacto sobre la colección gobernada → una segunda mirada a ese cambio concreto es lo que
realmente lo publica. Dos puntos de control, no uno — aprobar la idea y aprobar el diff exacto se
mantienen deliberadamente separados.

**Un desarrollador externo integra la API pública.** Lee la documentación de la API → crea una
cuenta, inicia sesión → solicita un token de acceso → llama a la API con él → recibe una cita.

## El backlog, por área

Cada tarea de abajo lleva la misma Definición de Terminado: operable por teclado, con un nombre o
etiqueta accesible, sin que el significado dependa solo del color, respetando las preferencias de
movimiento reducido. No se repite en cada punto — no es opcional para ninguno de ellos.

**Explorar y descubrir** — un visitante puede explorar por sección, etiqueta o nivel en su idioma;
cada página de cita muestra su fuente y contexto; las migas de pan llevan de vuelta a donde
empezaste.

**Explorar relaciones** — un visitante puede ver cómo se relacionan las citas entre sí en un
grafo; una persona que usa teclado o lector de pantalla obtiene cada selección del grafo reflejada
como texto accesible, no solo como resaltado visual.

**Preguntar al Oráculo** — un visitante puede hacer una pregunta real y recibir una respuesta
fundamentada en citas, transmitida a medida que se genera; una persona con lector de pantalla
recibe esa respuesta en flujo anunciada mientras llega, no en silencio hasta que termina; un
despliegue recién arrancado muestra un estado de "preparando" en lugar de quedarse colgado en
silencio.

**Llevarlo sin conexión** — el contenido visto previamente sigue funcionando sin conexión; la
aplicación se puede instalar como una nativa.

**Hacerlo tuyo** — un visitante puede crear una cuenta e iniciar sesión; un lector registrado
puede guardar y eliminar citas de una biblioteca personal.

**Contribuir sabiduría** — un lector registrado puede proponer una cita nueva; un colaborador
puede ver el estado de su propuesta; una persona revisora puede revisar propuestas con las mismas
herramientas ya usadas para el código; solo la aprobación de una persona nombrada escribe jamás la
colección gobernada — ninguna automatización, IA incluida, lo hace nunca en silencio.

**Construir sobre TTOD** — un desarrollador externo obtiene una API documentada y autenticada por
token, y un pequeño cliente de ejemplo que funciona, prueba de que la API funciona fuera del
navegador, no solo dentro de la interfaz de esta aplicación.

## Tablero de tareas por equipo

Ocho estudiantes, cinco equipos — tres parejas en las áreas más ricas y con más contrato; dos
personas en solitario en las dos más acotadas. La lista de cada equipo tiene ~10 tareas, etiquetadas
según cuál de las seis áreas toca realmente cada una: tu propia área es profundidad, las demás son
la amplitud que este curso evalúa explícitamente (ver [Por qué la accesibilidad es un
compromiso](#por-qué-la-accesibilidad-es-un-compromiso-no-una-lista-de-verificación) para saber
por qué la etiqueta de pruebas/accesibilidad se aplica a cada fila, de cada equipo, no solo a uno).

**Esto es el resumen.** Para qué busca el resultado visible de cada tarea, qué incluye, y qué hay
que hacer de verdad — basado en el `ASSIGNMENT.md` real que trae cada módulo, no una repetición
genérica — ver [detalle de tareas]({{ '/es/teaching/tasks/' | relative_url }}).

**Lecciones para estas tareas.** El itinerario de FE II en web-atelier-udit enseña la arquitectura
Astro sobre la que construye cada equipo. Hay tres unidades publicadas por ahora — se enlazarán
más aquí a medida que se publiquen:

- [Unidad 1 — Arranque](https://ruvebal.github.io/web-atelier-udit/lessons/es/feii/unit-1-kickoff/) — orientación para todos los equipos, antes de la tarea 1
- [Unidad 2 — Fundamentos de Astro](https://ruvebal.github.io/web-atelier-udit/lessons/es/feii/unit-2-astro-fundamentals/) — routing, layouts y una primera isla de framework; prerrequisito de la tarea 1 de los Equipos 1, 2 y 3
- [Unidad 3 — Astro avanzado](https://ruvebal.github.io/web-atelier-udit/lessons/es/feii/unit-3-astro-advanced/) — content collections, routing i18n, obtención de datos e islas multi-framework, trabajado enteramente sobre el código fuente real de TTOD; prerrequisito de las tareas 1 y 6 del Equipo 1, y de la tarea 1 de los Equipos 2 y 3

### Equipo 1 — Contenido, i18n y UI de propuestas (pareja)

| # | Tarea | Área(s) |
| - | --- | --- |
| 1 | Construir las rutas localizadas de índice y detalle de sabiduría (`en` + `es`) — ver [Unidad 3: content collections + routing i18n](https://ruvebal.github.io/web-atelier-udit/lessons/es/feii/unit-3-astro-advanced/) | Contenido |
| 2 | Rutas de exploración por sección, etiqueta y nivel | Contenido |
| 3 | Navegación de migas de pan en todas las rutas de contenido | Contenido |
| 4 | Gestión de estados vacíos y de error en las rutas de contenido | Contenido |
| 5 | Construir la UI del formulario "proponer una cita" — envía al endpoint que posee el Equipo 5 | Contenido, Cuentas |
| 6 | Mostrar fuente, derechos y procedencia en cada página de cita — ver [Unidad 3: esquemas de content collection](https://ruvebal.github.io/web-atelier-udit/lessons/es/feii/unit-3-astro-advanced/) | Contenido |
| 7 | Pruebas unitarias y de componente para las rutas de contenido y el formulario de propuesta | Pruebas |
| 8 | Abrir una PR hacia un módulo que no es el tuyo | Entre módulos |
| 9 | Revisar formalmente una PR fuera de tu propio módulo | Entre módulos |
| 10 | Documentar una decisión de diseño real (taxonomía, política de respaldo) para la defensa oral | Proceso |

### Equipo 2 — Grafo de conocimiento (solo)

| # | Tarea | Área(s) |
| - | --- | --- |
| 1 | Obtener y renderizar el grafo desde la API gobernada — ver [Unidad 3: obtención de datos + la isla del grafo](https://ruvebal.github.io/web-atelier-udit/lessons/es/feii/unit-3-astro-advanced/) | Grafo |
| 2 | Una selección de nodo accesible, reflejada como texto y no solo como resalte visual | Grafo |
| 3 | Interacción de filtro por etiqueta | Grafo |
| 4 | Estado de URL para la selección/filtro actual | Grafo |
| 5 | Disposición y rendimiento a escala real del corpus (la muestra no es pequeña) | Grafo |
| 6 | Auditoría de operabilidad por teclado en cada elemento interactivo del grafo | Pruebas |
| 7 | Pruebas unitarias y de componente para la isla del grafo | Pruebas |
| 8 | Abrir una PR hacia un módulo que no es el tuyo | Entre módulos |
| 9 | Revisar formalmente una PR fuera de tu propio módulo | Entre módulos |
| 10 | Documentar una decisión de diseño real (elección de disposición, compromiso de accesibilidad) para la defensa oral | Proceso |

### Equipo 3 — Terminal Oracle (pareja)

| # | Tarea | Área(s) |
| - | --- | --- |
| 1 | Renderizado de respuesta en flujo, de una pregunta a una respuesta citada — ver [Unidad 3: la isla Oracle como ejemplo multi-framework](https://ruvebal.github.io/web-atelier-udit/lessons/es/feii/unit-3-astro-advanced/) | Oracle |
| 2 | Anuncio en región viva de la respuesta en flujo para lectores de pantalla | Oracle |
| 3 | Transparencia del modo fundamentado frente al modo creativo en la UI | Oracle |
| 4 | Gestión del historial de sesión/intercambios | Oracle |
| 5 | Un estado "preparando" en lugar de un cuelgue silencioso en un despliegue recién arrancado | Oracle |
| 6 | Estado de recuperación/error cuando el Oráculo no está disponible | Oracle |
| 7 | Pruebas unitarias y de componente para la terminal Oracle y su lógica de streaming | Pruebas |
| 8 | Abrir una PR hacia un módulo que no es el tuyo | Entre módulos |
| 9 | Revisar formalmente una PR fuera de tu propio módulo | Entre módulos |
| 10 | Documentar una decisión de diseño real (gestión de estado, diseño de la transparencia) para la defensa oral | Proceso |

### Equipo 4 — PWA y operación local (solo)

| # | Tarea | Área(s) |
| - | --- | --- |
| 1 | Registro del service worker y un manifiesto instalable | PWA/Offline |
| 2 | Un límite offline observable — contenido que sigue funcionando sin conexión | PWA/Offline |
| 3 | Política cache-first frente a network-first para las rutas correctas | PWA/Offline |
| 4 | Una cola offline que se vacía al recuperar la conexión | PWA/Offline |
| 5 | Comprobaciones de calidad de instalación (corrección del manifiesto, iconos, instalabilidad) | PWA/Offline |
| 6 | Presupuesto de rendimiento medido antes/después de una optimización (Core Web Vitals) | PWA/Offline |
| 7 | Pruebas unitarias y de componente para el límite offline | Pruebas |
| 8 | Abrir una PR hacia un módulo que no es el tuyo | Entre módulos |
| 9 | Revisar formalmente una PR fuera de tu propio módulo | Entre módulos |
| 10 | Documentar una decisión de diseño real (política de caché, UX de instalación) para la defensa oral | Proceso |

### Equipo 5 — Cuentas, biblioteca, propuestas y API pública (pareja)

| # | Tarea | Área(s) |
| - | --- | --- |
| 1 | Inicio de sesión (verificado en servidor, una ruta protegida) | Cuentas |
| 2 | Biblioteca personal de favoritos — guardar, ver, eliminar | Cuentas |
| 3 | El endpoint de backend de "proponer una cita" al que envía el formulario del Equipo 1 | Cuentas, Contenido |
| 4 | El pipeline de revisión nativo de GitHub: una PR de propuesta, aprobación humana, diff de aceptación calculado, segunda aprobación | Cuentas |
| 5 | Un endpoint de API pública autenticado por token (`GET` de una cita aleatoria) | Cuentas |
| 6 | Página de documentación de la API y un cliente de ejemplo externo mínimo | Cuentas |
| 7 | Pruebas unitarias y de componente para la autenticación, la biblioteca y la API | Pruebas |
| 8 | Abrir una PR hacia un módulo que no es el tuyo | Entre módulos |
| 9 | Revisar formalmente una PR fuera de tu propio módulo | Entre módulos |
| 10 | Documentar una decisión de diseño real (sesión frente a token, compromiso del pipeline de revisión) para la defensa oral | Proceso |

**Sobre el número de estudiantes:** este tablero usa el reparto confirmado de 8 estudiantes en
cinco equipos (2+1+2+1+2 — tres parejas en las áreas más ricas, dos personas solas en las más
acotadas). Si tu grupo real es de siete, mantén fijos los límites de los módulos y reduce una
pareja a un trío en lugar de eliminar un módulo — las seis áreas y la forma de diez tareas por
equipo no necesitan cambiar, solo quién está en qué equipo.

## Por qué la accesibilidad es un compromiso, no una lista de verificación

Un aforismo se ofrece como sabiduría que vale sin importar quién lo lea, cuándo o cómo. Un
producto construido sobre esa afirmación no puede después reducir en silencio quién es capaz de
recibirla según cómo perciba una pantalla — eso no sería solo una carencia de experiencia de
usuario, contradiría la premisa misma del contenido.

Esto se resuelve en tres compromisos que atraviesan cada tarea anterior: **paridad de contenido**
— ningún significado existe en un solo canal, así que una selección del grafo siempre se puede
leer como texto y una respuesta en flujo siempre se anuncia, no solo se renderiza; **proceso, no
una puerta** — las comprobaciones de accesibilidad se ejecutan en cada cambio, no como una carrera
antes de entregar; **una base de todo el producto** — cada tarea hereda la misma Definición de
Terminado, no solo las áreas que se sienten visualmente interactivas.

## Páginas relacionadas

- [Detalle de tareas — cada tarea explicada]({{ '/es/teaching/tasks/' | relative_url }})
- [Modelo docente]({{ '/es/teaching/' | relative_url }})
- [Para estudiantes]({{ '/es/audiences/students/' | relative_url }})
- [Áreas del producto]({{ '/es/platform/' | relative_url }})
- [Contribuir — cómo abrir una PR, cómo funciona la revisión]({{ '/es/guides/contributing/' | relative_url }})
