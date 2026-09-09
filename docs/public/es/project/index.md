---
title: Proyecto
eyebrow: Qué es TTOD
description: Misión, gobernanza, procedencia y licencias de 道 The Tao of Development (TTOD).
permalink: /es/project/
lang: es
---

# Sabiduría con cadena de custodia

TTOD es una base de conocimiento pedagógico: aforismos breves sobre desarrollo, organizados por materia y nivel de aprendizaje, conectados con lo que enseñan y con su procedencia. La colección YAML es canónica; las interfaces y las exportaciones son vistas derivadas.

El proyecto se articula en torno a una distinción que importa en educación: un enunciado memorable puede sostener la docencia sin convertirse en evidencia académica. Las entradas de TTOD se citan por un identificador estable, llevan idioma, origen, derechos y metadatos de relación, y permanecen sujetas a gobernanza humana.

## Principios de gobernanza

- Los registros canónicos cambian mediante transacciones validadas, no mediante ediciones casuales del archivo.
- Los identificadores son estables; el material sustituido se marca como obsoleto en lugar de borrarse.
- Los orígenes humano, de estudio, propuesto por IA y heredado siguen siendo distinguibles.
- El material propuesto por IA requiere validación humana antes de aceptarse.
- Las vistas JSON y de grafo derivadas nunca prevalecen sobre la fuente canónica.
- Los aforismos pedagógicos no sustentan por sí solos pretensiones de investigación.

<figure class="diagram-teaser">
  <a class="diagram-teaser-link" href="{{ '/assets/diagrams/ttod-wisdom-dataflow.html' | relative_url }}">
    <img src="{{ '/assets/diagrams/ttod-wisdom-dataflow.png' | relative_url }}" alt="Diagrama del camino gobernado de escritura: una fuente citable pasa por la destilación de un agente hacia una bandeja pendiente, un paso de aceptación humana, el almacén canónico ttod.yml y una exportación C14N que leen Web Atelier, DevIAC MCP y el ajuste fino." loading="lazy">
  </a>
  <figcaption><a href="{{ '/assets/diagrams/ttod-wisdom-dataflow.html' | relative_url }}">Abrir el diagrama interactivo del flujo de datos ↗</a> — el camino gobernado desde una fuente citable hasta la aceptación canónica, y las exportaciones de solo lectura que comparte cada consumidor. (Interfaz en inglés.)</figcaption>
</figure>

## Lo que añade la plataforma

La aplicación hace observables esas decisiones mediante rutas localizadas, vistas de citas individuales, navegación de contenido relacionado, una isla de grafo, una isla Oracle en flujo, documentación y comprobaciones de calidad representativas. Por ahora, la plataforma es una referencia docente local, no un servicio público en la nube.

## Licencias

El código se licencia bajo MIT. El contenido curado se licencia bajo CC BY-NC-SA 4.0 salvo que un registro indique otra cosa. Cualquier socio de investigación o comercial debe respetar los límites de contenido no comercial y de compartir bajo la misma licencia, sin inferir una reutilización irrestricta.

## Custodia

El proyecto se custodia desde el dominio del estudio de investigación `@crea-comm.net`. Los documentos públicos omiten deliberadamente rutas de estaciones de trabajo, nombres de infraestructura interna, coordenadas de red y herramientas privadas del estudio.

## Dónde encaja TTOD en el estudio

TTOD es un proyecto dentro de un pequeño estudio de desarrollo de IA soberana, construido sobre
una regla innegociable: toda llamada a un modelo se ejecuta en infraestructura alojada localmente,
nunca en un proveedor de IA en la nube. El propio Oráculo de TTOD, y cualquier asistencia para
redactar propuestas, siguen esa regla igual que el resto de proyectos del estudio.

Merece la pena nombrar dos proyectos hermanos para que el límite sea explícito, no solo afirmado:
**Athanor**, la plataforma de conocimiento propia del estudio, puede consumir una instantánea de
solo lectura de la colección gobernada de TTOD y puede hacer llegar citas candidatas a la bandeja
de revisión humana habitual de TTOD — nunca escribe un registro canónico directamente, la misma
regla que gobierna cualquier otro camino hacia los datos de TTOD. **Ahmes**, el motor de
extracción de documentos de propósito general del estudio, no tiene relación con la propia
canalización de TTOD; alimenta a Athanor desde otro material de origen y no tiene conexión directa
con la gobernanza de citas de TTOD. Nombrar a ambos aquí es una cuestión de precisión, no de
afiliación por proximidad: las reglas de gobernanza de TTOD se aplican sin importar qué otra
herramienta del estudio esté preguntando.
