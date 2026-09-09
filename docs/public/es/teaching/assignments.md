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

- [Modelo docente]({{ '/es/teaching/' | relative_url }})
- [Para estudiantes]({{ '/es/audiences/students/' | relative_url }})
- [Áreas del producto]({{ '/es/platform/' | relative_url }})
