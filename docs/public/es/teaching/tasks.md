---
title: Detalle de tareas
eyebrow: Cada tarea asignable, explicada
description: Detalle por tarea del tablero de equipo — qué resultado visible busca cada tarea, qué incluye, y qué hay que hacer, extraído directamente del ASSIGNMENT.md de cada módulo.
permalink: /es/teaching/tasks/
lang: es
---

# Cada tarea, explicada

El [tablero de tareas por equipo]({{ '/es/teaching/assignments/' | relative_url }}) lista ~10
tareas por equipo. Esta página es el detalle detrás de cada una — basado directamente en el
archivo `ASSIGNMENT.md` que viene dentro del propio código del módulo, no una repetición aparte.
Tres tareas se repiten idénticas en la lista de cada equipo (PR entre módulos, revisión entre
módulos, documentación para la defensa) — [explicadas una sola vez, al
final](#las-tres-tareas-recurrentes), enlazadas desde cada sección de equipo en vez de repetirlas
cinco veces.

## Equipo 1 — Contenido, i18n y UI de propuestas

**Punto de partida:** una ruta de índice localizada y una ruta de detalle localizada, ambas ya
obteniendo entradas reales y renderizando `en`/`es`. La exploración por sección, etiqueta y nivel
no existe todavía en esta rama — esa ausencia es deliberada, no un fallo que reportar.

**Tarea 1 — Rutas de exploración por sección, etiqueta y nivel**
- *Resultado visible:* tres rutas funcionando (`/wisdom/sections/<id>/`, `/tags/<id>/`,
  `/levels/<id>/`) que filtran los mismos datos en vivo que ya obtiene la página de índice.
- *Qué incluye:* nuevas rutas de Astro, usando el helper `frequencies()` ya existente (ya
  exportado, todavía sin llamar por nada) para calcular las listas de facetas.
- *Qué hay que hacer:* construir la ruta, la UI de la lista de facetas, y el listado filtrado — la
  capa de datos ya existe, falta la capa de presentación y enrutado.

**Tarea 2 — Navegación de migas de pan**
- *Resultado visible:* cada ruta de contenido muestra un camino claro de vuelta a donde estabas
  (índice → sección → detalle, no solo un "atrás" plano).
- *Qué incluye:* un componente o patrón de migas de pan compartido, reutilizado en índice, facetas
  y detalle.
- *Qué hay que hacer:* diseñar la jerarquía de migas de pan una vez existan las rutas de facetas
  de la tarea 1, y conectarla en el layout de cada ruta.

**Tarea 3 — Gestión de estados vacíos y de error**
- *Resultado visible:* una faceta sin resultados muestra un estado vacío claro y con estilo —
  nunca una página en blanco ni un error sin gestionar.
- *Qué incluye:* todas las rutas de contenido, incluidas las que construyes en la tarea 1.
- *Qué hay que hacer:* diseñar un patrón de estado vacío, aplicarlo de forma consistente, y
  confirmar que el caso de backend inalcanzable degrada a un mensaje de error real, no a una
  traza de pila.

**Tarea 4 — Mostrar fuente, derechos y procedencia**
- *Resultado visible:* cada página de cita muestra visiblemente su titular, licencia y origen —
  no solo el texto.
- *Qué incluye:* la ruta de detalle ya tiene estos datos (`WisdomEntry.rights`, `.origin`) — la
  tarea es mostrarlos con claridad, no obtener nada nuevo.
- *Qué hay que hacer:* diseñar un bloque de procedencia compacto y accesible, y aplicarlo en
  cada vista de cita (tarjetas de índice, listados de facetas, página de detalle).

**Tarea 5 — La UI del formulario "proponer una cita"**
- *Resultado visible:* una persona con sesión iniciada puede rellenar una cita, su sección y su
  fuente, y enviarla — la solicitud llega al endpoint que posee el Equipo 5.
- *Qué incluye:* el formulario en sí, validación en cliente, y un estado claro de
  éxito/pendiente tras el envío. **No** incluye el pipeline de revisión en sí (eso es la tarea 4
  del Equipo 5).
- *Qué hay que hacer:* coordinar la forma de la solicitud con el Equipo 5 antes de construir
  contra ella; construir el formulario detrás de acceso protegido por `requireUser()`; gestionar
  con elegancia el caso de "no ha iniciado sesión".

**Tarea 6 — Pruebas unitarias y de componente**
- *Resultado visible:* las rutas de contenido y el formulario de propuesta tienen al menos una
  prueba real, conectada al mismo trabajo de CI que corren las pruebas de todos los demás módulos.
- *Qué incluye:* una prueba unitaria (p. ej., una función pura de filtrado de contenido) y una
  prueba de componente (una ruta renderizada o el formulario), siguiendo la misma capa de Testing
  Trophy que usa todo el proyecto — ver la [tarea de pruebas del Equipo 2](#equipo-2--grafo-de-conocimiento)
  para la filosofía compartida.
- *Qué hay que hacer:* elegir la capa más barata que dé confianza real — no escribas una prueba
  E2E pesada para algo que ya prueba una unitaria.

## Equipo 2 — Grafo de conocimiento

**Punto de partida:** una isla Svelte hidratada que obtiene el grafo en vivo, dispone todos los
nodos, y refleja una selección por clic/teclado en un panel accesible. El filtro por etiqueta, el
estado de URL y el movimiento están deliberadamente ausentes.

**Tarea 1 — Interacción de filtro por etiqueta**
- *Resultado visible:* un desplegable (u opción equivalente) que acota el grafo visible al
  vecindario de una etiqueta.
- *Qué incluye:* `layout.ts` ya exporta `filterGraph` y `selectedTag` — el hello-world nunca los
  llama. Esta tarea es conectar lógica existente y probada a un control de UI.
- *Qué hay que hacer:* construir el control, llamar a `filterGraph`, y confirmar que el grafo se
  vuelve a renderizar correctamente cuando el filtro cambia o se limpia.

**Tarea 2 — Estado de URL para la selección/filtro actual**
- *Resultado visible:* el filtro de etiqueta y la selección de nodo actuales se reflejan en la
  barra de direcciones, y recargar o pulsar atrás los restaura.
- *Qué incluye:* leer y escribir parámetros de consulta, y gestionar el evento `popstate` del
  navegador.
- *Qué hay que hacer:* elegir una forma de URL (p. ej., `?tag=architecture&node=arch-031`),
  mantenerla sincronizada con el estado de filtro/selección, y restaurar el estado desde ella al
  cargar.

**Tarea 3 — Disposición y rendimiento a escala real del corpus**
- *Resultado visible:* el grafo se mantiene responsivo y legible con el conjunto de datos
  gobernado completo cargado — no solo una muestra pequeña.
- *Qué incluye:* la función `radialLayout` ya existente; esta tarea es ajustarla, no
  reemplazarla, salvo que puedas justificarlo.
- *Qué hay que hacer:* medir el rendimiento real de renderizado/interacción a escala completa,
  identificar el cuello de botella real (cálculo de disposición frente a cantidad de nodos DOM
  frente a re-renderizados), y arreglar ese cuello de botella concreto.

**Tarea 4 — Una animación de entrada o de selección**
- *Resultado visible:* al menos un momento del grafo (la aparición de nodos, o un cambio de
  selección) tiene una animación deliberada y justificada — no decoración porque sí.
- *Qué incluye:* la leyenda de color de origen ya existe y puede quedarse tal cual, restilizarse,
  o integrarse en tu UI de filtro — no es la costura evaluada aquí.
- *Qué hay que hacer:* elegir un momento de animación, implementarlo, y estar preparado para
  explicar en la defensa por qué ese momento en concreto merece movimiento.

**Tarea 5 — Auditoría de operabilidad por teclado**
- *Resultado visible:* cada elemento interactivo del grafo (nodos, el control de filtro) es
  completamente operable solo con teclado, con foco visible en cada paso.
- *Qué incluye:* la selección hello-world ya tiene `role="button"`, `tabindex` y `onkeydown` — la
  auditoría es confirmar que nada de lo que añadas lo rompe, y extender el mismo patrón a tu
  nuevo control de filtro.
- *Qué hay que hacer:* recorrer toda la experiencia del grafo solo con teclado, arreglando
  cualquier punto donde se pierda el foco o una acción dependa solo del ratón.

**Tarea 6 — Pruebas unitarias y de componente**
- *Resultado visible:* la isla del grafo tiene al menos una prueba unitaria (una función pura
  como `filterGraph` o `radialLayout`) y una prueba de componente (la isla renderizándose y
  respondiendo a una selección).
- *Qué incluye:* este es el enfoque compartido de Testing Trophy que usa todo equipo — ver la
  [filosofía de pruebas del proyecto]({{ '/es/guides/contributing/' | relative_url }}) para lo que
  significa en la práctica "la capa más barata que sirve".
- *Qué hay que hacer:* probar la lógica pura directamente (rápido, sin necesidad de renderizar), y
  probar la isla renderizada solo para lo que una prueba unitaria no puede cubrir (interacción DOM
  real).

## Equipo 3 — Terminal Oracle

**Punto de partida:** una pregunta, una respuesta en flujo, modo fundamentado frente a creativo,
IDs de cita citados, y un guardián de ocupado/doble envío. La cola offline, el historial
multi-turno, y proponer desde una respuesta están deliberadamente ausentes.

**Tarea 1 — Renderizado de respuesta en flujo**
- *Resultado visible:* ya funciona en esta rama — esta tarea es *extenderlo*, no construirlo
  desde cero: historial multi-turno renderizado como más de un intercambio visible.
- *Qué incluye:* los helpers `readOracleStream`/`parseSseEvent` ya existentes, que deben quedar
  exactamente como están — la lección es consumir un flujo correctamente, no escribir un segundo
  analizador.
- *Qué hay que hacer:* construir `sessionHistory` a partir de los intercambios completados y
  enviarlo en las siguientes peticiones; renderizar la conversación creciente, no solo la última
  respuesta.

**Tarea 2 — Anuncio en región viva para lectores de pantalla**
- *Resultado visible:* una persona con lector de pantalla escucha la respuesta mientras fluye, no
  silencio seguido del texto completo al final.
- *Qué incluye:* el patrón `aria-live`/`aria-busy` ya usado para el guardián de ocupado —
  extender la misma disciplina al propio texto en flujo.
- *Qué hay que hacer:* confirmar con un lector de pantalla real (no solo inspección visual) que
  las actualizaciones incrementales realmente se anuncian, no solo que están presentes en el DOM.

**Tarea 3 — Transparencia del modo fundamentado frente al creativo**
- *Resultado visible:* ya funciona parcialmente — la tarea es hacer la distinción inequívoca,
  nunca solo por color (se exige una etiqueta de texto, no es opcional).
- *Qué incluye:* `citedQuoteIds` en los segmentos fundamentados debe renderizarse como enlaces
  navegables, no solo como texto plano.
- *Qué hay que hacer:* auditar cada lugar donde se muestra el modo y confirmar que una persona
  con daltonismo o que usa lector de pantalla recibe la misma información que una persona vidente.

**Tarea 4 — Integración con la cola offline**
- *Resultado visible:* un Oráculo inalcanzable encola la pregunta en el dispositivo; al
  reconectar se vacían las entradas pendientes en orden.
- *Qué incluye:* el mecanismo `OfflineLogEntry` ya existente en `lib/db.ts`
  (`enqueueOracleQuery`, `markEntrySynced`, `enqueueErrorReport`, `listUnsyncedEntries`) —
  propiedad del Equipo 4, **llamado** desde aquí. No construyas una segunda cola.
- *Qué hay que hacer:* coordinar la forma exacta de la llamada con el Equipo 4 antes de
  conectarla; confirmar que el vaciado al reconectar realmente se dispara con un evento `online`
  real, no solo en una prueba simulada.

**Tarea 5 — Estado de recuperación/error**
- *Resultado visible:* cuando el Oráculo está genuinamente no disponible (no solo arrancando en
  frío), la UI lo dice con claridad en vez de colgarse o mostrar un error crudo.
- *Qué incluye:* distinguir "todavía calentando" de "realmente roto" — son estados distintos con
  respuestas de UI distintas y correctas.
- *Qué hay que hacer:* diseñar ambos estados explícitamente y provocar cada uno deliberadamente
  (matar el backend frente a simular un volumen de Ollama en frío) para confirmar que se muestra
  el correcto.

**Tarea 6 — Proponer desde una respuesta**
- *Resultado visible:* una respuesta creativa (no fundamentada) completada puede proponerse para
  revisión humana — pero solo con un clic explícito, nunca como efecto secundario de que el flujo
  termine.
- *Qué incluye:* `POST /api/v1/oracle/propose`, ya un endpoint real.
- *Qué hay que hacer:* añadir la posibilidad en la UI, confirmar que solo aparece en respuestas en
  modo creativo, y confirmar que el clic es el único disparador.

**Tarea 7 — Pruebas unitarias y de componente**
- *Resultado visible:* la terminal y su lógica de streaming tienen al menos una prueba real cada
  una.
- *Qué incluye:* probar la máquina de estados del streaming (una cuestión a nivel unitario) por
  separado del comportamiento de la terminal renderizada (a nivel de componente).
- *Qué hay que hacer:* no hagas polling al endpoint de streaming ni colapses el SSE en una
  respuesta única en búfer solo para facilitar las pruebas — prueba el comportamiento real en
  flujo.

## Equipo 4 — PWA y operación local

**Punto de partida:** un service worker, un manifiesto instalable, y un aviso visible de
online/offline — suficiente para observar un límite local/offline. No es una PWA terminada, un
programa de rendimiento, ni un pipeline de CI/CD.

**Tarea 1 — Política Cache-First frente a Network-First**
- *Resultado visible:* los recursos estáticos cargan al instante desde caché; las respuestas de
  `/api/*` nunca se sirven obsoletas desde caché.
- *Qué incluye:* el `sw.js` del punto de partida ya hace Cache-First de exactamente un archivo
  (`tokens.css`) — la tarea es extender esa política correctamente, recurso a recurso, nunca
  aplicando Cache-First a `/api/*` "solo para el stub".
- *Qué hay que hacer:* leer `public/sw.js` por completo primero — sus propios comentarios nombran
  lo que está deliberadamente sin implementar; extiende desde ahí, no lo reescribas.

**Tarea 2 — Cola offline que se vacía al reconectar**
- *Resultado visible:* las acciones realizadas sin conexión (como una pregunta al Oracle del
  Equipo 3) se encolan y se reproducen cuando vuelve la conexión, en orden.
- *Qué incluye:* la cola ya existente de `src/lib/db.ts`, de la que eres propietario y que llama
  el Equipo 3 — léela y extiéndela, no la reescribas debajo de ellos.
- *Qué hay que hacer:* coordinar la interfaz exacta con el Equipo 3; confirmar que se conserva el
  orden y que los éxitos se marcan como sincronizados, no reintentados en silencio para siempre.

**Tarea 3 — Comprobaciones de calidad de instalación**
- *Resultado visible:* un navegador Chromium trata la aplicación como genuinamente instalable —
  icono, nombre, color de tema y `display: standalone` correctos.
- *Qué incluye:* el manifiesto de partida ya tiene los campos mínimos; esta tarea los verifica y
  completa para un aviso de instalación real, no solo un JSON técnicamente válido.
- *Qué hay que hacer:* disparar de verdad el flujo de instalación en un navegador real y
  confirmar que se ve bien, no solo que el comprobador de manifiesto de DevTools está en
  silencio.

**Tarea 4 — Presupuesto de rendimiento medido**
- *Resultado visible:* una optimización concreta y nombrada con un número medido de antes/después
  (Core Web Vitals o equivalente) — nunca una mejora afirmada sin medición.
- *Qué incluye:* diseñar tu propio presupuesto es explícitamente parte de esta tarea — el punto
  de partida deliberadamente no trae todavía una puerta de Lighthouse CI, para que no heredes los
  números de otra persona.
- *Qué hay que hacer:* medir primero, elegir un cuello de botella real, arreglarlo, medir de
  nuevo, y guardar ambos números para la defensa.

**Tarea 5 — Corrección del ciclo de vida del service worker**
- *Resultado visible:* puedes demostrar que `install`, `activate` y `fetch` se comportan
  correctamente, incluyendo que el worker reclama a los clientes y actualiza el nombre de su
  caché en una nueva versión.
- *Qué incluye:* explicar esto es en sí mismo un resultado de aprendizaje — la defensa pedirá que
  expliques qué pasa cuando cambia el token/la versión de caché.
- *Qué hay que hacer:* provocar deliberadamente una actualización (cambiar el nombre de la
  caché, recargar) y confirmar que las cachés antiguas se limpian, no se acumulan en silencio.

**Tarea 6 — Pruebas unitarias y de componente**
- *Resultado visible:* el límite offline (cola + aviso) tiene al menos una prueba real.
- *Qué incluye:* probar la lógica de orden/vaciado de la cola directamente, por separado del
  estado visual online/offline del aviso.
- *Qué hay que hacer:* simular eventos `online`/`offline` en la prueba en vez de requerir un
  cambio de red real para verificar el comportamiento.

## Equipo 5 — Cuentas, biblioteca, propuestas y API pública

**Punto de partida:** un usuario sembrado, `requireUser()` protegiendo `/account`, una cookie de
sesión firmada httpOnly, y un token de acceso separado desde `POST /api/v1/auth/token`. Este es el
único equipo cuya área no tiene código de referencia existente que reducir — es nuevo, no una
resta.

**Tarea 1 — Inicio de sesión**
- *Resultado visible:* ya funciona en esta rama para la cuenta sembrada — la tarea es extenderlo
  a registro real, no solo ese único usuario de prueba.
- *Qué incluye:* las guardas `requireUser()`/`requireRole()` ya existentes se ejecutan en el
  frontmatter de Astro — antes de enviar cualquier HTML, siguiendo el patrón de autenticación SSR
  de FE I sobre el que está construido directamente.
- *Qué hay que hacer:* nunca proteger una ruta solo en estado de cliente JSX/Svelte — un `curl`
  sin sesión a una URL protegida no debe contener contenido protegido en la respuesta cruda.

**Tarea 2 — Biblioteca personal de favoritos**
- *Resultado visible:* una persona con sesión iniciada puede guardar una cita, ver su lista
  guardada, y eliminar una de ella.
- *Qué incluye:* un almacén de backend nuevo y pequeño para favoritos — deliberadamente **no**
  `ttod.yml`, ya que los favoritos son datos de preferencia por usuario, no datos del corpus
  gobernado.
- *Qué hay que hacer:* diseñar el esquema mínimo de favoritos, los tres endpoints (guardar,
  listar, eliminar), y la página de UI que los usa.

**Tarea 3 — El endpoint de backend de proponer una cita**
- *Resultado visible:* el formulario de propuesta del Equipo 1 crea con éxito un registro de
  propuesta real al enviarse.
- *Qué incluye:* llamar exactamente a la misma primitiva `ttod_core.proposals.create_proposal(...)`
  que ya usa `cli.py proposal create` — esto reutiliza el 100% de la infraestructura de propuestas
  existente, no construye una paralela.
- *Qué hay que hacer:* acordar la forma de la solicitud con el Equipo 1 primero; el único trabajo
  del endpoint es traducir una petición web autenticada en esa primitiva ya existente.

**Tarea 4 — El pipeline de revisión nativo de GitHub**
- *Resultado visible:* una propuesta enviada se convierte en una PR real; la aprobación de una
  persona revisora calcula el diff canónico exacto; una segunda aprobación sobre ese diff es lo
  que realmente lo publica.
- *Qué incluye:* el pipeline ya existe y está documentado en la [guía de
  contribución]({{ '/es/guides/contributing/' | relative_url }}) con su propio diagrama — tu
  tarea es operarlo correctamente para propuestas reales, y explicar el diseño de doble punto de
  control en tu defensa.
- *Qué hay que hacer:* seguir una propuesta real a través de todo el pipeline de principio a fin
  al menos una vez antes de considerar esta tarea terminada.

**Tarea 5 — API pública autenticada por token**
- *Resultado visible:* un cliente externo (no un navegador) puede llamar a
  `GET /api/v1/wisdom/random` con `Authorization: Bearer <token>` y recibir una cita.
- *Qué incluye:* el token viene de `POST /api/v1/auth/token` — una credencial genuinamente
  separada de la cookie de sesión, nunca el mismo JWT reutilizado en ambos sitios.
- *Qué hay que hacer:* verificar que el endpoint rechaza peticiones sin token, con un token
  inválido, y con una cookie de sesión válida presentada como si fuera un token de acceso (no debe
  funcionar).

**Tarea 6 — Documentación de la API y un cliente de ejemplo mínimo**
- *Resultado visible:* una página de documentación que cualquier desarrollador externo podría
  seguir, y un pequeño script (no una segunda aplicación) que prueba que la API funciona fuera de
  un navegador.
- *Qué incluye:* la documentación debería generarse o comprobarse contra las mismas formas de
  `domain.ts` que gobiernan todos los demás módulos — "los tipos son el contrato", aplicado
  también aquí.
- *Qué hay que hacer:* escribir la documentación, y luego ejecutar de verdad el script de
  ejemplo contra tu propia instancia en ejecución antes de dar esto por terminado — un script que
  nunca se ha ejecutado no es prueba de nada.

**Tarea 7 — Pruebas unitarias y de componente**
- *Resultado visible:* la autenticación, la biblioteca y la API tienen al menos una prueba real
  cada una.
- *Qué incluye:* una prueba de que una petición sin sesión a una ruta protegida realmente se
  rechaza — no solo que una con sesión iniciada tiene éxito.
- *Qué hay que hacer:* nunca guardar la sesión en `localStorage`, nunca implementar a mano el
  hash de contraseñas, nunca reutilizar el token de sesión como token de acceso — son atajos
  prohibidos, no preferencias de estilo, y una prueba que solo comprueba el camino feliz no los
  detectará.

## Las tres tareas recurrentes

La lista de cada equipo termina con las mismas tres tareas — explicadas aquí una sola vez, no
cinco veces arriba.

**PR entre módulos.** Abre al menos una PR real hacia un módulo que no es el tuyo — una
corrección o mejora genuina, no un commit de tipo al vuelo. Se evalúa como evidencia de proceso,
no como crédito extra, y es la única tarea que genuinamente no se puede resolver de un solo golpe
con un asistente de codificación con IA: exige leer y modificar código que no escribiste tú.

**Revisión entre módulos.** Revisa formalmente al menos una PR fuera de tu propio módulo, usando
el propio `ASSIGNMENT.md` de ese módulo como lista de comprobación de revisión — el mismo
documento que le dijo a su propio equipo qué significa "terminado" te dice a ti qué comprobar.

**Documentación para la defensa.** Elige una decisión de diseño real que hayas tomado — no una
hipotética — y prepárate para explicarla, junto con una alternativa real que consideraste, en la
defensa oral. "No pensé en alternativas" es una respuesta de defensa más débil que "consideré X,
lo rechacé porque Y".

## Páginas relacionadas

- [Tablero de tareas por equipo]({{ '/es/teaching/assignments/' | relative_url }})
- [Modelo docente — las seis áreas de ampliación]({{ '/es/teaching/' | relative_url }})
- [Contribuir — cómo abrir una PR, cómo funciona la revisión]({{ '/es/guides/contributing/' | relative_url }})
