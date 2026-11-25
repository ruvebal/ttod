# Créditos del sistema visual

Qué imagen y qué letra usa cada vista, de dónde sale y con qué licencia.

## El valle de la portada (`valle/`)

Las capas `valle-{fondo,izquierda,derecha,frente}-{1600,2200,3136,movil}.webp` y las dos bandas
`valle-tesis-*` y `valle-cierre-*` salen de una imagen **generada**, no de una obra de museo: el
valle de karst y río que se eligió entre tres candidatos.

- Imagen base: **Flux Pro 1.1 Ultra** (`fal-ai/flux-pro/v1.1-ultra`), 21:9, 3136×1344, semilla 4103.
- Separación en capas: **Qwen-Image-Layered** (`fal-ai/qwen-image-layered`), 5 capas, semilla 7,
  reconstruidas a 3136 px tomando el contorno del modelo y el color del original.
- El alfa de cada capa se endureció (rampa de ~1 px centrada en 128) para que el recorte tenga borde
  limpio. La bruma **no** es una capa recortada: es un degradado de CSS.
- `valle-*-movil.webp` es un recorte de la capa de 3136 px (franja y huellas en `valle/movil.json`,
  vigilado por `src/components/valleMovil.test.ts`).
- Las bandas `tesis` y `cierre` son trozos de la pintura entera, sin alfa, graduados a su distancia.

## El rollo de la portada (`rollo/`) y la hoja de tinta (`tinta/difusion-tinta.webp`)

**River and Mountains on a Clear Autumn Day** (江山秋霽), Dong Qichang (董其昌, 1555–1636),
China, dinastía Ming, *ca.* 1624–27. Rollo de mano, tinta sobre papel.

- Museo: The Cleveland Museum of Art, nº de inventario **1959.46**
- Ficha y descarga: <https://clevelandart.org/art/1959.46>
- Licencia: **CC0 1.0 (dominio público)**.

`rollo/rollo-{2560,3200,4000,5600}.webp` es el tramo pintado del rollo, recortado una sola vez
(11 340 × 4 885 px nativos). `tinta/difusion-tinta.webp` son 14 estados de una aguada recortada de
la misma obra y apilados en una hoja de 1024 × 3584 px; se usa como **máscara de luminancia** para
que las palabras lleguen como tinta que empapa el papel. No se dibujó nada a mano.

## El fondo de Sabiduría (`sabiduria/`)

Hua Yan (華嵒, 1682–h. 1765), «Un letrado a la mesa y un criado que le prepara la tinta», del
*Álbum de paisajes que ilustran poemas antiguos*, 1745. The Cleveland Museum of Art, **1982.68.10**,
**CC0 1.0**. `estudio-hua-yan-{800,1400,2200,3196}.webp`.

## La piedra de las estelas (`estelas/grano-piedra.webp`)

Trama de grano de 200 px generada con ImageMagick para este proyecto.

## Tipografía (`fonts/` y `tinta/`)

- **Gambetta** (Indian Type Foundry / Fontshare), pesos 300, 400 y 500. **ITF Free Font License**
  (`fonts/LICENCIA-Gambetta-FFL.txt`) — <https://www.fontshare.com/fonts/gambetta>. Títulos, citas
  y texto corrido.
- **Erode** (Indian Type Foundry / Fontshare), peso 300. **ITF Free Font License**
  (`fonts/LICENCIA-Erode-FFL.txt`) — <https://www.fontshare.com/fonts/erode>. Titulares del valle.
- **Switzer** (Indian Type Foundry / Fontshare), archivo variable, pesos 300 a 700. **ITF Free Font
  License** (`fonts/LICENCIA-Switzer-FFL.txt`) — <https://www.fontshare.com/fonts/switzer>. Capa de
  interfaz: índice, folios, cartela y etiquetas.
- **Ma Shan Zheng**, recortada a los glifos que usa el pie. **SIL Open Font License 1.1**
  (`tinta/OFL-MaShanZheng.txt`).

Todas autoalojadas. No se usa Google Fonts en ninguna parte del sitio.

## Lo demás

`favicon.svg`, `river-contours.svg`, `knowledge-constellation.svg`, iconos PWA: del propio repo TTOD
(MIT, código), ajenos a este trabajo.
