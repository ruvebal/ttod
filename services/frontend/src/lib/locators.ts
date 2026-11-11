/**
 * Dónde vive cada cosa (LOCATORS.md §3 y §4): la única función que decide si una
 * dirección pedida se queda o se manda, con un 301, a su forma permanente.
 *
 * La usa `src/middleware.ts` y la prueba `src/middleware.test.ts`, sin servidor:
 * es una función pura de método + URL a «destino o nada».
 *
 * Reglas, en orden:
 * 1. Solo GET y HEAD. Un POST redirigido pierde el cuerpo (el navegador lo
 *    rehace como GET), así que el formulario de entrar nunca se redirige.
 * 2. Lo que no es una página no se toca: `/api/`, los recursos con extensión,
 *    los ficheros de Astro y los endpoints (`/{l}/logout`).
 * 3. Enlaces viejos que ya están pegados en PRs: `/{l}/graph/path` era la
 *    constelación 3D (hoy `/{l}/graph/`) y, con `?s=`, el grafo del código (hoy
 *    `/{l}/graph/code/`); `/{l}/graph?tag=` era el plano 2D (hoy `/{l}/graph/plano/`).
 * 4. `/{l}/wisdom/` con una sola faceta y sin búsqueda es la lista de esa faceta,
 *    que ya tiene su ruta: una dirección por recurso.
 * 5. Toda página acaba en barra (decisión D1 de AA0). La consulta viaja intacta,
 *    tal cual llegó (sin volver a codificarla), salvo cuando se le quita una clave.
 */
const NO_PAGINA = ['/api/', '/_astro/', '/_image', '/_server-islands/', '/visual-system/', '/project-docs/', '/data/'];
const ENDPOINT = /^\/(?:en|es)\/logout\/?$/;
const SLUG = /^[a-z0-9][a-z0-9-]*$/;
const FACETAS = [
  ['section', 'sections'],
  ['level', 'levels'],
  ['tag', 'tags'],
] as const;

const consulta = (params: URLSearchParams) => {
  const texto = params.toString();
  return texto ? `?${texto}` : '';
};

export function redireccionLocator(method: string, url: URL): string | null {
  if (method !== 'GET' && method !== 'HEAD') return null;
  const ruta = url.pathname;
  if (NO_PAGINA.some((prefijo) => ruta.startsWith(prefijo))) return null;
  if (ruta.slice(ruta.lastIndexOf('/') + 1).includes('.')) return null;
  if (ENDPOINT.test(ruta)) return null;
  const params = new URLSearchParams(url.search);

  const sendero = ruta.match(/^\/(en|es)\/graph\/path\/?$/);
  if (sendero) {
    const soloCodigo = params.has('s') && !params.has('from') && !params.has('to') && !params.has('node');
    return `/${sendero[1]}/graph/${soloCodigo ? 'code/' : ''}${url.search}`;
  }
  const grafo = ruta.match(/^\/(en|es)\/graph\/?$/);
  if (grafo && params.has('tag')) return `/${grafo[1]}/graph/plano/${url.search}`;

  const sabiduria = ruta.match(/^\/(en|es)\/wisdom\/?$/);
  if (sabiduria && !(params.get('q') ?? '').trim()) {
    const puestas = FACETAS.filter(([clave]) => params.getAll(clave).some((valor) => valor.trim()));
    if (puestas.length === 1) {
      const [clave, segmento] = puestas[0];
      const valores = params.getAll(clave);
      if (valores.length === 1 && SLUG.test(valores[0])) {
        const resto = new URLSearchParams(params);
        resto.delete(clave);
        resto.delete('q');
        return `/${sabiduria[1]}/wisdom/${segmento}/${valores[0]}/${consulta(resto)}`;
      }
    }
  }

  if (!ruta.endsWith('/')) return `${ruta}/${url.search}`;
  return null;
}
