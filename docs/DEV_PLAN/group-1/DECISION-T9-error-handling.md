# Tarea 9 — Decisión de diseño: captura centralizada de errores de red en `loadWisdom()`

> Ficha: `docs/public/teaching/tasks/content-task9/` · módulo Content, i18n & Proposals UI (Equipo 1)
> Candidato elegido de los dos "naturales" que cita `PLAN-EQUIPO1.md`: política de fallback (T3/T4).

## Contexto

Antes de la Tarea 3, las cinco rutas de contenido (`index`, `[slug]`, y las tres rutas de faceta)
llamaban a `fetchWisdom(locale)` directamente, sin ningún `try/catch`. `fetchWisdom()` lanza una
excepción cuando el backend no responde con éxito o devuelve algo que no es un array
(`services/frontend/src/content/wisdom.ts:10-12`, rama `content-task3-empty-error-states`). Sin
nada que la capturara, un fallo real del backend (red caída, 5xx, JSON malformado) llegaba sin
filtrar hasta el visitante como un stack trace de servidor — exactamente lo que la Tarea 3 pedía
que dejara de pasar, en los cinco sitios y en los dos idiomas.

La decisión no es solo "poner un `try/catch`": es **dónde** vive ese `try/catch`.

## Opciones consideradas

1. **`try/catch` en cada ruta por separado.** Cada uno de los cinco archivos `.astro` envuelve su
   propia llamada a `fetchWisdom()` y decide localmente qué hacer si falla.
2. **La página de error global de Astro** (`500.astro`/manejo de errores de la plataforma). Dejar
   que la excepción se propague sin capturar y que Astro la convierta en una página de error de
   todo el sitio.
3. **Un único punto de captura**, `loadWisdom()`, que envuelve `fetchWisdom()` y devuelve siempre
   un resultado estructurado `{ entries, failed }` — nunca una excepción. Cada ruta solo consulta
   esa bandera.

## Decisión

Se eligió la **opción 3**. Implementación completa en
`services/frontend/src/content/wisdom.ts:16-27` (rama `content-task3-empty-error-states`, PR
[#63](https://github.com/ruvebal/ttod/pull/63)):

```ts
export type WisdomLoad = { entries: WisdomEntry[]; failed: boolean };

export async function loadWisdom(locale: Locale): Promise<WisdomLoad> {
  try {
    return { entries: await fetchWisdom(locale), failed: false };
  } catch {
    return { entries: [], failed: true };
  }
}
```

Las cinco rutas (`index.astro`, `[slug].astro`, `sections/[section].astro`, `tags/[tag].astro`,
`levels/[level].astro`) llaman a `loadWisdom()`, nunca a `fetchWisdom()` directamente, y deciden su
propia UI con el mismo patrón: `failed` → estado de error; `entries.length === 0` → estado vacío;
si no, datos reales.

## Consecuencias

**Qué se gana:**

- **Cero duplicación.** El único `try/catch` de todo el módulo vive en un sitio; no hay 5 copias
  que puedan desincronizarse con el tiempo.
- **UI uniforme.** Las cinco rutas comparten exactamente el mismo patrón de tres ramas
  (error/vacío/datos), con el mismo componente (`EmptyState`, con `variant="error"` añadiendo
  `role="alert"` solo al caso de fallo real — `services/frontend/src/components/EmptyState.astro`).
- **El contrato de `fetchWisdom()` queda intacto.** Sigue lanzando exactamente igual que antes; no
  hubo que re-testear ni cambiar nada de su comportamiento ya probado, y cualquier otro código que
  la llame directamente (si lo hubiera) sigue viendo el mismo comportamiento de siempre.

**Qué se pierde / riesgo aceptado:**

- **Ninguna observabilidad automática.** Astro nunca ve la excepción real porque se captura antes
  de llegar a su runtime, así que no hay ningún log de servidor del fallo sin trabajo extra. Si se
  quisiera un `Sentry.captureException()` o un log estructurado, habría que añadirlo explícitamente
  dentro del `catch` de `loadWisdom()` — no viene gratis con esta solución.
- **Sin código HTTP de error real.** Frente a la opción 2, la página sigue devolviendo `200 OK` con
  el mensaje de error dentro del HTML, no un `500` real. Decisión consciente: el criterio de
  aceptación de la Tarea 3 era "nunca un stack trace", no un código HTTP concreto, y un `200` con
  un mensaje traducido y accesible (`role="alert"`) es mejor experiencia para el visitante que un
  `500` en blanco del navegador.
- **Sin granularidad por ruta.** Frente a la opción 1, ninguna ruta puede reaccionar de forma
  distinta a un fallo (p. ej., un reintento solo en una de las cinco). No se necesitaba esa
  granularidad aquí; si se necesitara en el futuro, una ruta concreta puede seguir llamando a
  `fetchWisdom()` directamente sin tocar las demás.

## Por qué se descartó la opción más "gratis" de la plataforma (opción 2)

La página de error global de Astro parece la solución más barata — no escribir nada — pero tiene
dos problemas reales para este módulo:

1. **No es locale-aware de forma sencilla.** Cada una de nuestras rutas ya resuelve su propio
   `locale` desde `Astro.params.locale` con `isLocale()`; una página de error genérica de todo el
   sitio no comparte ese mismo mecanismo sin lógica adicional, y corría el riesgo de mostrar el
   mensaje de error en el idioma equivocado.
2. **Rompe la forma de probar el módulo.** Nuestra batería de tests de integración
   (`services/frontend/src/tests/empty-error-states.test.ts`) renderiza cada ruta con la Container
   API de Astro (`experimental_AstroContainer.renderToString`) y comprueba el HTML resultante
   dentro de `<main>`. Esa API no ejecuta el pipeline completo de manejo de errores de Astro — solo
   renderiza el componente dado. Si el error se propagara hasta una página de error separada, no
   habría forma de probarlo con el mismo mecanismo que ya probamos todo lo demás; tendríamos que
   añadir una capa de test distinta (p. ej. Playwright) solo para este caso.

## Evidencia en código (rama `content-task3-empty-error-states`, PR #63)

| Archivo | Qué mostrar |
|---|---|
| `services/frontend/src/content/wisdom.ts:16-27` | Definición de `loadWisdom()` — el único `try/catch` |
| `services/frontend/src/pages/[locale]/wisdom/index.astro` | Consumo de `loadWisdom()`, rama `failed` vs `entries.length === 0` |
| `services/frontend/src/pages/[locale]/wisdom/[slug].astro` | Mismo patrón + distinción `notFound` vs `empty` |
| `services/frontend/src/components/EmptyState.astro` | Prop `variant`, `role="alert"` solo en error |
| `services/frontend/src/tests/empty-error-states.test.ts` | Mock de `global.fetch` fallando; confirma `role="alert"` y ausencia de texto de excepción |

**Verificación fuera de los mocks:** se detuvo el contenedor real del backend (`docker compose stop
backend`) con la pila completa levantada (`make up`) y se confirmó en vivo que `/en/wisdom/` y
`/es/wisdom/` muestran el mensaje de error traducido con `role="alert"`, nunca un stack trace, antes
de reiniciar el contenedor.

## Para la defensa oral

- **Pregunta esperada:** "¿por qué no simplemente un `try/catch` en cada página?" → cero
  duplicación, más fácil de mantener, mismo patrón en los cinco sitios.
- **Pregunta esperada:** "¿por qué no la página de error de Astro, que es gratis?" → no es
  locale-aware sin trabajo extra, y rompe el mecanismo de test que ya usa todo el módulo
  (Container API).
- **Pregunta esperada:** "¿qué código HTTP devuelve esto?" → `200 OK` con el mensaje dentro del
  HTML, no un `500`. Es una decisión consciente, no un descuido: el criterio era "nunca un stack
  trace", no un código concreto.
- **Línea exacta a señalar en vivo:** `services/frontend/src/content/wisdom.ts:22-26`.
