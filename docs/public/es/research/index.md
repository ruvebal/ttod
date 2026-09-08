---
title: Investigación
eyebrow: Evidencia antes de pretensiones de efecto
description: Preguntas de investigación de TTOD, madurez actual, salvaguardas y límites de evidencia.
permalink: /es/research/
lang: es
---

# Un programa de investigación en preparación

TTOD sostiene hoy una indagación de diseño técnico y pedagógico: ¿cómo puede un sistema front-end completo, pero deliberadamente sencillo, hacer más visibles los límites arquitectónicos, la evidencia de proceso y la responsabilidad de diseño del alumnado en un entorno de aprendizaje asistido por IA?

Esto es una propuesta, no un protocolo empírico aprobado. No se afirma que TTOD mejore el aprendizaje, no se autoriza el reclutamiento de participantes y el trabajo estudiantil no se convierte en dato de investigación solo porque se haya producido en un curso.

## Cuatro artefactos que no deben confundirse

1. **Referencia rica del profesorado:** evidencia de viabilidad de que la arquitectura puede ejecutarse de extremo a extremo.
2. **Base docente:** un futuro producto hello world para explicar y recorrer el sistema.
3. **Productos estudiantiles:** trabajo evaluado, ampliado de forma independiente, que demuestra las decisiones del alumnado.
4. **Registros de investigación:** solo el material recogido bajo un protocolo aprobado y comunicado por separado.

## Preguntas candidatas

- ¿Qué trazas ayudan a localizar correctamente el renderizado, el estado, la confianza, los datos y la responsabilidad sobre las pruebas?
- ¿Cuánta implementación de partida sostiene la comprensión del sistema sin colapsar el trabajo auténtico de diseño?
- ¿Qué artefactos de proceso hacen explicables y revisables las contribuciones asistidas por IA?
- ¿Cómo pueden complementarse en la evaluación la explicación oral, la evidencia del repositorio, las comprobaciones de accesibilidad y el comportamiento del producto?

## Lo que la literatura existente puede y no puede hacer

La investigación sobre programación asistida por IA, evaluación auténtica, documentación de proceso y explicación motiva el diseño. [Liu, Fan y Pan 2026](#ref-liu-fan-pan-2026) describen una tensión entre el dominio del campo y el dominio de la herramienta, y distinguen andamiaje de descarga cognitiva; su estudio de teoría fundamentada no adjudica eficacia ni predice resultados en este curso. [Nikolić y Basta Nikolić 2026](#ref-nikolic-basta-nikolic-2026) proponen documentación de proceso, defensa oral, tareas auténticas y políticas transparentes de uso de IA, y declaran explícitamente no disponer de datos de validación.

Trabajo complementario en STEM y educación de la computación afila el mismo límite sin demostrar un efecto de TTOD. [Shihab et al. 2025](#ref-shihab-et-al-2025) estudian cómo Copilot cambia la eficacia, la eficiencia y el proceso en tareas de programación brownfield — útil para preguntas sobre integrar sugerencias en un código base heredado, no como pretensión de transferencia a este andamiaje. [López-Pernas et al. 2025](#ref-lopez-pernas-et-al-2025) examinan la autorregulación en interacciones estudiante–IA durante la resolución de problemas de programación web, lo que motiva atender la dependencia, la delegación y la regulación en el tiempo. [Garcia 2025](#ref-garcia-2025) informa sobre portfolios digitales auto-codificados como evaluación auténtica basada en proyectos en un curso de diseño y desarrollo web, y sostiene diseños de evaluación producto-más-proceso. [Davalos y Zhang 2026](#ref-davalos-zhang-2026) replantean el «uso indebido de la IA» como un problema de visibilidad del aprendizaje y de medición cuando el profesorado conserva productos pero pierde la visión del proceso — una analogía de por qué TTOD trata las trazas y la defensa oral como requisitos de diseño, no como teatro de detección.

La orientación curricular de [*Computer Science Curricula 2023*](#ref-cs2023) trata la IA generativa, la sociedad, la ética y la responsabilidad profesional como preocupaciones de todo el currículo, no como una lección de herramienta desgajada; es una justificación de alcance frente a estándares, no evidencia de aula.

Estas fuentes justifican preguntas y salvaguardas, no un efecto de TTOD. Hace falta más evidencia longitudinal de aula, y las observaciones locales de implementación son evidencia de ingeniería, no resultados educativos. Los primarios clásicos de diseño instruccional sobre carga cognitiva y aprendizaje cognitivo permanecen en la lista de evidencia pendiente hasta que sus metadatos bibliográficos puedan verificarse para la cita pública.

## Perspectiva crítica

El riesgo central es confundir un producto pulido con aprendizaje. Terminar más deprisa puede convivir con una menor capacidad para explicar, depurar o descomponer un problema de forma independiente. Por eso TTOD trata el código generado como objeto de crítica: el alumnado debe localizar sus supuestos, probarlo, modificarlo y explicar quién responde del resultado. El contraste buscado no es «IA o no IA», sino un apoyo que se retira gradualmente frente a una dependencia que permanece invisible.

Esa lente crítica se aplica también a la propia plataforma. Un corpus gobernado puede seguir cifrando omisiones; un grafo puede hacer que las relaciones editoriales parezcan naturales; un Oracle puede proyectar autoridad; los registros de proceso pueden ensayarse; y una defensa oral puede crear carga de trabajo o costes de equidad. La investigación debe examinar esas preguntas de poder y validez, en lugar de usar la trazabilidad como sinónimo de verdad.

Leer el [método y las salvaguardas]({{ '/es/research/methodology/' | relative_url }}) o el [modelo docente]({{ '/es/teaching/' | relative_url }}).

## Estado actual

| Capa | Estado | Siguiente umbral |
| --- | --- | --- |
| Viabilidad de ingeniería | observada en local; verificación independiente abierta | cerrar el informe de evidencia |
| Esqueleto docente | previsto | congelar los contratos de reducción y de tarea |
| Alineación curricular | programada más adelante | revisión bilingüe de paridad semántica |
| Investigación empírica | pre-protocolo, pre-recogida | ética, datos, consentimiento o revisión de base jurídica |

<figure class="diagram-teaser">
  <a class="diagram-teaser-link" href="{{ '/assets/diagrams/ttod-research-maturity.html' | relative_url }}">
    <img src="{{ '/assets/diagrams/ttod-research-maturity.png' | relative_url }}" alt="Diagrama de ciclo de vida de la ruta de investigación: indagación de diseño, redacción del protocolo y una revisión ética y de datos, con la posición actual detenida antes de ese umbral, hacia una recogida autorizada y un análisis que converge en hallazgos validados o diverge en hallazgos negativos o mixtos igualmente válidos." loading="lazy">
  </a>
  <figcaption><a href="{{ '/assets/diagrams/ttod-research-maturity.html' | relative_url }}">Abrir el diagrama interactivo de madurez ↗</a> — dónde está hoy la investigación empírica, el umbral que debe superar a continuación, y por qué los hallazgos negativos o mixtos cuentan como resultados válidos, no como fracasos. (Interfaz en inglés.)</figcaption>
</figure>

## Referencias

- <a id="ref-cs2023"></a>*Computer Science Curricula 2023*. Association for Computing Machinery, IEEE Computer Society, and AAAI. [https://doi.org/10.1145/3664191](https://doi.org/10.1145/3664191).
- <a id="ref-davalos-zhang-2026"></a>Davalos, Eduardo, and Yike Zhang. 2026. “AI Misuse in Education Is a Measurement Problem: Toward a Learning Visibility Framework.” arXiv. [https://doi.org/10.48550/arxiv.2603.07834](https://doi.org/10.48550/arxiv.2603.07834).
- <a id="ref-garcia-2025"></a>Garcia, Manuel B. 2025. “Self-Coded Digital Portfolios as an Authentic Project-Based Learning Assessment in Computing Education: Evidence from a Web Design and Development Course.” *Education Sciences* 15 (9): 1150. [https://doi.org/10.3390/educsci15091150](https://doi.org/10.3390/educsci15091150).
- <a id="ref-liu-fan-pan-2026"></a>Liu, Dandan, Guangrui Fan, and Lihu Pan. 2026. “Tool, Tutor, or Crutch?: A Grounded Theory of Cognitive Scaffolding and Offloading in AI-Assisted Programming Education.” *International Journal of STEM Education* 13: 10. [https://doi.org/10.1186/s40594-025-00592-w](https://doi.org/10.1186/s40594-025-00592-w).
- <a id="ref-lopez-pernas-et-al-2025"></a>López-Pernas, Sonsoles, Kamila Misiejuk, Eduardo Oliveira, and Mohammed Saqr. 2025. “The Dynamics of the Self-Regulation Process in Student-AI Interactions: The Case of Problem-Solving in Programming Education.” In *Proceedings of the 25th Koli Calling International Conference on Computing Education Research*. [https://doi.org/10.1145/3769994.3770043](https://doi.org/10.1145/3769994.3770043).
- <a id="ref-nikolic-basta-nikolic-2026"></a>Nikolić, Dragan, and Marijana Basta Nikolić. 2026. “Designing AI-Resilient Assessment in Higher Education: A Four-Pillar Conceptual Framework.” *Frontiers in Artificial Intelligence* 9. [https://doi.org/10.3389/frai.2026.1841682](https://doi.org/10.3389/frai.2026.1841682).
- <a id="ref-shihab-et-al-2025"></a>Shihab, Md Istiak Hossain, Christopher Hundhausen, Ahsun Tariq, Summit Haque, Yunhan Qiao, and Brian Wise Mulanda. 2025. “The Effects of GitHub Copilot on Computing Students’ Programming Effectiveness, Efficiency, and Processes in Brownfield Coding Tasks.” In *Proceedings of the 2025 ACM Conference on International Computing Education Research V.1*. [https://doi.org/10.1145/3702652.3744219](https://doi.org/10.1145/3702652.3744219).
