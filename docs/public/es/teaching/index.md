---
title: Modelo docente
eyebrow: Front-end II · primera mitad del semestre
description: Cómo TTOD se mapea a las Unidades 1–7 de Front-end II en UDIT, a la Entrega 1 y al examen parcial de proceso y comprensión.
permalink: /es/teaching/
lang: es
---

# Columna completa a profundidad hello world

TTOD es el producto docente de la **primera mitad** de [Front-end II](https://ruvebal.github.io/web-atelier-udit/tracks/feii/) en UDIT: arquitectura de producción con Astro, comportamiento del navegador sin conexión, pruebas y revisión asistida por IA, y rendimiento medido. El [índice del track](https://ruvebal.github.io/web-atelier-udit/tracks/feii/) nombra el semestre de doce unidades; TTOD concentra las Unidades 1–7 en un solo artefacto coherente.

La base docente está construida: un recorrido de producto pequeño pero completo, donde cada
costura mayor está presente, pero ninguna se entrega como respuesta acabada de la tarea. Las áreas
avanzadas aparecen como ejemplos hello world operativos. El profesorado puede explicar primero
cómo encaja el sistema; después, el alumnado amplía esas mismas costuras mediante diseño e
implementación evaluados. El ensayo del profesorado sobre este mismo artefacto es la puerta que
queda antes de abrir la colaboración — ver [Para
estudiantes]({{ '/es/audiences/students/' | relative_url }}).

## Conexión con el curso

| Superficie del curso | Papel de TTOD | Peso oficial (indicativo) |
| --- | --- | --- |
| [Entrega 1 — Arquitectura Astro (Unidades 2–6)](https://ruvebal.github.io/web-atelier-udit/tracks/en/feii/how-to-pass-this-track/) | Primer entregable: el producto Astro del alumnado, con colecciones de contenido, rutas obligatorias `es` + `en`, islas, integración de varios frameworks, suite de pruebas y flujo de revisión asistida por IA | 25 % · Semana 7 |
| Examen parcial (Unidades 1–7) | Comprobación escrita y práctica del **uso declarativo del sistema**, de la defensa del proceso y de la comprensión del código — no una demo de caja negra pulida | 15 % · Semana 7 |
| Unidades 1–7 en conjunto | Aproximadamente la mitad del semestre, antes de 3D, IoT y el proyecto final | — |

Las reglas autoritativas de calificación, calendario y recuperación viven en el sitio del curso: [Cómo aprobar Front-end II](https://ruvebal.github.io/web-atelier-udit/tracks/feii/) (guía de aprobación enlazada desde el track) y el [track FE II](https://ruvebal.github.io/web-atelier-udit/tracks/feii/). Este sitio de documentación describe el producto y la pedagogía; no sustituye la guía oficial.

<figure class="diagram-teaser">
  <a class="diagram-teaser-link" href="{{ '/assets/diagrams/ttod-feii-architecture.html' | relative_url }}">
    <img src="{{ '/assets/diagrams/ttod-feii-architecture.png' | relative_url }}" alt="Diagrama de arquitectura front-end en el vocabulario de FE II: del navegador al documento Astro, al shell de página, a una isla Svelte o React, HTTP/SSE hacia la API Oracle y la instantánea gobernada de citas, con la propiedad del documento, la isla y el límite de servicio señalados, más Ollama mostrado como infraestructura propia de la aplicación en su propio contenedor." loading="lazy">
  </a>
  <figcaption><a href="{{ '/assets/diagrams/ttod-feii-architecture.html' | relative_url }}">Abrir el diagrama interactivo de las Unidades 1–7 ↗</a> — el mismo recorrido de petición en vocabulario del curso: propiedad del documento frente a la isla, el diseño offline de la Unidad 4, y las costuras que la Entrega 1 y el parcial piden defender. (Interfaz en inglés.)</figcaption>
</figure>

## Unidades 1–7 en la columna TTOD

| Unidades | Foco del curso | Qué hace observable TTOD |
| --- | --- | --- |
| 1–3 | Arquitectura de producción con Astro (SSR, islas, micro-frontends) | Rutas localizadas, contratos de contenido, responsabilidad sobre el documento Astro, islas Svelte/React acotadas |
| 4 | PWA y capacidades offline | Un límite local/offline observable que el alumnado debe diseñar y defender |
| 5–6 | Estrategia de testing y revisión de código asistida por IA | Aserciones representativas en capas útiles; uso de IA declarado con evidencia humana de aceptar/rechazar/escalar |
| 7 | Ingeniería de rendimiento | Presupuestos medidos y coste de paquete o de ejecución antes de afirmar una optimización |

Las Unidades 8–12 (3D, IoT/Python y defensa del proyecto final) son trabajo posterior del curso. Quedan fuera de esta base docente de TTOD.

## Las seis áreas de ampliación

| Área | Hello world entregado | Profundidad a cargo del alumnado (Entrega 1) |
| --- | --- | --- |
| Contenido Astro | una colección localizada y un recorrido índice/detalle | taxonomía, amplitud editorial, política de respaldo y arquitectura de información |
| Grafo Svelte | un vecindario real pequeño y una selección accesible | exploración, filtros, disposición, estado de URL y rendimiento a escala de corpus |
| Oracle React | una pregunta, un modo de respuesta en flujo y una cita | estado robusto, sesiones, recuperación, transparencia, propuestas sin conexión y diseño de interacción |
| Operación del navegador y comportamiento sin conexión | un límite local/offline observable | caché, instalación, colas, presupuestos y evidencia operativa |
| Cuentas, biblioteca personal y propuestas de la comunidad | inicio de sesión, una ruta protegida y un endpoint autenticado por token | una biblioteca de favoritos, un flujo de "proponer una cita" con sesión iniciada, y el camino revisado que sigue una propuesta hasta la colección gobernada |
| Pruebas | una aserción representativa en cada capa útil | estrategia de riesgo, E2E de interacción, amplitud de contrato, accesibilidad, rendimiento y control de inestabilidad |

La sexta área no tiene ninguna referencia existente que reducir — es genuinamente nueva, construida
sobre los mismos patrones de sesión verificada en servidor y token de acceso ya cubiertos en la
unidad previa de autenticación de Front-end I, de modo que el grupo amplía un patrón que ya conoce
en lugar de aprenderlo desde cero. Ver [tareas y
backlog]({{ '/es/teaching/assignments/' | relative_url }}) para el desglose completo por área,
las personas y los recorridos detrás de las seis.

## Secuencia pedagógica

1. Ejecutar y trazar el recorrido completo de la petición antes de abrir la colaboración.
2. Nombrar dónde viven el renderizado, el estado, la confianza, la gobernanza del contenido y las pruebas.
3. Examinar una implementación mínima en cada frontera de marco.
4. Convertir los comportamientos deliberadamente ausentes en criterios explícitos de la Entrega 1.
5. Exigir que el alumnado explique decisiones de diseño y evidencia — comportamiento del producto, registro de proceso y defensa de la comprensión en el parcial — no que se limite a presentar una interfaz acabada.

Esto es una justificación de diseño, no la afirmación de que TTOD mejore el aprendizaje. La base
está construida y verificada de forma independiente sobre una copia limpia; queda por delante el
ensayo del profesorado sobre ese mismo artefacto y la sincronización final con los materiales
localizados del curso.

## Cómo transcurre una sesión

Cada sesión sigue el mismo ritmo de tres partes, ajustado al tiempo real de esa sesión (una
primera sesión más corta, después un bloque semanal constante): una lección breve extraída
directamente del contenido curricular de esa unidad, un breve punto de control en equipo (qué se
entregó, qué está bloqueado, qué sigue) y el resto como tiempo de laboratorio práctico. La lección
se mantiene breve a propósito — las unidades con framework nuevo merecen un bloque docente real;
una vez que el patrón es familiar, la mayor parte de la sesión es tiempo de laboratorio,
coincidiendo con el reparto oficial de horas entre clase magistral y laboratorio de este track. El
punto de control también es donde un cambio en el contrato compartido de un área (un nombre de
ruta, una forma de datos) se detecta antes de que rompa silenciosamente el trabajo de otra área.

## Por qué el andamiaje debe desvanecerse

El patrón docente se apoya en el aprendizaje cognitivo: primero hacer visible el pensamiento experto mediante modelado y acompañamiento, y después retirar gradualmente el apoyo a medida que el alumnado asume la responsabilidad. Un estudio cualitativo reciente sobre programación asistida por IA agudiza el riesgo: el apoyo funciona como andamiaje cuando el alumnado sigue modificando, probando y explicando los resultados, pero puede convertirse en descarga cognitiva cuando desaparecen esas actividades de comprensión. El estudio propone un modelo de proceso, no un resultado universal de eficacia; por eso TTOD lo trata como una justificación que hay que poner a prueba, no como una prueba de aprendizaje ([Liu, Fan y Pan 2026](#ref-liu-fan-pan-2026)).

La consecuencia práctica es una incompletud deliberada. El alumnado recibe un sistema trazable, pero las decisiones valiosas —arquitectura de información, comportamiento de interacción, accesibilidad, recuperación, rendimiento y estrategia de pruebas— siguen siendo suyas. El uso de IA es visible y discutible; una salida generada nunca sustituye explicar o cambiar el código. Los estudios sobre autorregulación en la interacción estudiante–IA durante la programación web motivan además vigilar la dependencia y la delegación a lo largo del tiempo, no solo los commits finales ([López-Pernas et al. 2025](#ref-lopez-pernas-et-al-2025)).

La evaluación, por tanto, triangula el comportamiento del producto con evidencia de proceso y una defensa breve, oral o escrita, de la comprensión. El marco de cuatro pilares de [Nikolić y Basta Nikolić 2026](#ref-nikolic-basta-nikolic-2026) motiva esta estructura, pero es conceptual y explícitamente no validado; es un recurso de diseño de la evaluación, no evidencia de que este diseño de curso funcione. Mantener el proceso visible responde también a una preocupación de medición: cuando la IA entra en el bucle, el profesorado puede conservar productos y perder cómo se produjo el trabajo ([Davalos y Zhang 2026](#ref-davalos-zhang-2026)). La evaluación auténtica de portfolios en cursos web que exige al alumnado codificar el artefacto sostiene asimismo la responsabilidad compartida entre producto y proceso, sin pretender resultados idénticos aquí ([Garcia 2025](#ref-garcia-2025)).

## Alcance de la teoría

La teoría cubre renderizado, sistemas de contenido, localización, islas, estado, interfaces en flujo, comportamiento del navegador sin conexión, accesibilidad, pruebas y rendimiento medido: la mitad de FE II correspondiente a las Unidades 1–7. Los contenedores son solo un medio para ejecutar el sistema local. Las operaciones en la nube y la administración de servidores quedan fuera de este alcance docente de front-end.

La accesibilidad forma parte de la arquitectura y de la evaluación desde el primer hello world. La base compartida apunta a una estructura semántica, uso por teclado, foco visible, estados legibles y señales que no dependan solo del color, en línea con los criterios comprobables de WCAG 2.2; la conformidad sigue siendo una cuestión de verificación independiente ([W3C 2024](https://www.w3.org/TR/WCAG22/)).

## Páginas relacionadas del curso

- [Track FE II (publicado)](https://ruvebal.github.io/web-atelier-udit/tracks/feii/)
- [Índice del track en inglés](https://ruvebal.github.io/web-atelier-udit/tracks/en/feii/)
- [Cómo aprobar Front-end II](https://ruvebal.github.io/web-atelier-udit/tracks/en/feii/how-to-pass-this-track/)
- [Para estudiantes]({{ '/es/audiences/students/' | relative_url }})

## Referencias

- <span id="ref-davalos-zhang-2026"></span>Davalos, Eduardo, and Yike Zhang. 2026. “AI Misuse in Education Is a Measurement Problem: Toward a Learning Visibility Framework.” arXiv. [https://doi.org/10.48550/arxiv.2603.07834](https://doi.org/10.48550/arxiv.2603.07834).
- <span id="ref-garcia-2025"></span>Garcia, Manuel B. 2025. “Self-Coded Digital Portfolios as an Authentic Project-Based Learning Assessment in Computing Education: Evidence from a Web Design and Development Course.” *Education Sciences* 15 (9): 1150. [https://doi.org/10.3390/educsci15091150](https://doi.org/10.3390/educsci15091150).
- <span id="ref-liu-fan-pan-2026"></span>Liu, Dandan, Guangrui Fan, and Lihu Pan. 2026. “Tool, Tutor, or Crutch?: A Grounded Theory of Cognitive Scaffolding and Offloading in AI-Assisted Programming Education.” *International Journal of STEM Education* 13: 10. [https://doi.org/10.1186/s40594-025-00592-w](https://doi.org/10.1186/s40594-025-00592-w).
- <span id="ref-lopez-pernas-et-al-2025"></span>López-Pernas, Sonsoles, Kamila Misiejuk, Eduardo Oliveira, and Mohammed Saqr. 2025. “The Dynamics of the Self-Regulation Process in Student-AI Interactions: The Case of Problem-Solving in Programming Education.” In *Proceedings of the 25th Koli Calling International Conference on Computing Education Research*. [https://doi.org/10.1145/3769994.3770043](https://doi.org/10.1145/3769994.3770043).
- <span id="ref-nikolic-basta-nikolic-2026"></span>Nikolić, Dragan, and Marijana Basta Nikolić. 2026. “Designing AI-Resilient Assessment in Higher Education: A Four-Pillar Conceptual Framework.” *Frontiers in Artificial Intelligence* 9. [https://doi.org/10.3389/frai.2026.1841682](https://doi.org/10.3389/frai.2026.1841682).
