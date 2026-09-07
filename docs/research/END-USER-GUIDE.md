# TTOD Oracle — guía de uso

**Audiencia:** persona que consulta la plataforma.  
**Estado:** describe la referencia completa; la entrega del alumnado puede contener solo el esqueleto inicial.

## Qué es

TTOD Oracle es una interfaz para explorar sabiduría pedagógica de desarrollo: citas, enseñanzas, relaciones entre entradas y documentación. Las respuestas generadas localmente no sustituyen la fuente canónica ni la revisión humana.

## Navegación

- `/en/` y `/es/`: bienvenida localizada.
- `/en/quote` y `/es/quote`: cita real recuperada desde el backend, con texto, sección, nivel, origen y derechos.
- `/en/wisdom` y `/es/wisdom`: exploración por citas, niveles, secciones y etiquetas en la referencia completa.
- `/en/graph` y `/es/graph`: relaciones entre entradas, con filtros coherentes para nodos y enlaces.
- `/en/oracle` y `/es/oracle`: consulta al Oracle local cuando esa isla está incluida.
- `/en/docs` y `/es/docs`: documentación bilingüe.

El selector de idioma cambia la ruta; no presupongas que una cita inglesa tiene traducción española. Si aparece una cita en otro idioma, debe indicarlo mediante su atributo de idioma.

## Cómo leer una cita

Lee conjuntamente el texto, `teaches`, nivel, sección, origen, idioma y licencia. `origin: blackbox` significa propuesta de IA pendiente de revisión humana; no equivale a una verdad aceptada. Una cita no es evidencia académica por sí misma.

## Uso del Oracle

Formula una pregunta concreta y comprueba la respuesta contra la documentación y la cita enlazada. El modelo funciona localmente; no introduzcas datos personales, secretos, credenciales ni material con derechos que no puedas compartir. Una respuesta plausible puede ser incorrecta o incompleta.

## Si algo falla

Recarga y comprueba que el servicio local sigue activo. Informa del comando, ruta, idioma, mensaje de error y sistema operativo; no pegues claves ni archivos `.env`. Si el Oracle no está disponible, continúa con la documentación y las citas canónicas.

## Derechos

El contenido se publica bajo CC BY-NC-SA 4.0 y el código bajo MIT, salvo indicación específica. Conserva la atribución y no presentes una cita TTOD como resultado de una investigación independiente.
