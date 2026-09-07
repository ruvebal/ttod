---
title: Ejecutar la referencia en local
eyebrow: Guía de evaluación local
description: Un camino público y seguro desde el clon del repositorio hasta una experiencia TTOD local verificada.
permalink: /es/guides/local-setup/
lang: es
---

# Del clon a un hello world visible

La aplicación está pensada para ejecutarse en local mediante Docker Compose. Esta guía explica el camino operativo solo lo bastante para sostener la docencia y la evaluación de front-end.

## Requisitos previos

- Git
- Docker Desktop o un motor Docker compatible con Compose
- Espacio libre suficiente para las imágenes de contenedor y el modelo de lenguaje local opcional
- Un navegador

## Arranque

Desde la raíz del repositorio:

```bash
docker compose up --build -d
docker compose ps
```

Usa el mapeo de puertos que informe `docker compose ps` para abrir el servicio web. Si el repositorio ofrece un ejemplo de entorno, cópialo a un archivo de entorno local no versionado y cambia solo los valores documentados. Nunca confirmes credenciales ni coordenadas propias de una máquina.

## Verificar el recorrido

1. Abre la página de bienvenida localizada.
2. Visita una cita y confirma que se ven el texto, el idioma, el origen y los derechos.
3. Abre la documentación y una relación del grafo.
4. Si el modelo local del Oracle está listo, envía una pregunta pequeña e inspecciona su fundamentación o la revelación del modo creativo.
5. Confirma el foco de teclado y la retroalimentación de estado o de error en los controles interactivos.

El contenido y el grafo siguen siendo útiles cuando el modelo opcional del Oracle no está disponible. Una respuesta generada plausible no es la fuente canónica y puede ser incompleta o errónea.

## Inspeccionar y detener

```bash
docker compose logs --tail=100
docker compose down
```

Detener contenedores no debería eliminar volúmenes de datos con nombre. Borra volúmenes solo cuando pretendas de propósito descartar datos locales del modelo o de la aplicación y comprendas el coste de recuperación.

## Bloqueos habituales

- **Puerto ya en uso:** elige un mapeo alternativo documentado; no detengas a ciegas contenedores ajenos.
- **El modelo sigue descargándose:** usa las áreas de contenido no generativo mientras termina.
- **Oracle no disponible:** verifica por separado la salud del servicio y la preparación del modelo.
- **Una ruta se renderiza pero los datos están vacíos:** inspecciona la respuesta de red del navegador y los registros del servicio sin pegar secretos en una incidencia.

Para pedir apoyo, informa el comando, la ruta, el sistema operativo y el error exacto. Sustituye rutas personales, nombres de usuario, nombres de máquina, direcciones, tokens y valores de entorno por marcadores seguros.
