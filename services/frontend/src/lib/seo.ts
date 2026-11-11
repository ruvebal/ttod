/**
 * Lo que cada página dice de sí misma a un buscador o a quien la comparte (AA4: F14, F15, F41).
 *
 * El aula es `noindex` entero (AA0 D7 (a)): esa cabecera la pone Caddy en toda respuesta. Lo de aquí
 * vale por sí solo, por si un día se abre la indexación: qué página queda fuera siempre, cuál es su
 * dirección canónica y cuál su gemela en la otra lengua. La lista de páginas no se repite: sale del
 * registro de localizadores (LOCATORS §4), que ya es el contrato.
 */
import registro from './locators.registry.json';

export type Idioma = 'en' | 'es';

interface Fila {
  path: string;
  auth?: boolean;
  index?: boolean;
}

// Solo las filas de ruta (las que llevan `?` son variantes de consulta de otra fila).
// `{l}` es la lengua; cualquier otro hueco (`{quote}`, `{section}`…) es un segmento.
const filas = (registro.pages as Fila[])
  .filter((fila) => !fila.path.includes('?'))
  .map((fila) => ({
    fila,
    patron: new RegExp(
      '^' +
        fila.path
          .replace(/[.*+?^$()|[\]\\]/g, '\\$&')
          .replace(/\{l\}/g, '(?:en|es)')
          .replace(/\{[a-z-]+\}/g, '[^/]+') +
        '$',
    ),
  }));

/**
 * ¿Puede indexarse esta página? No, si no es un 200, si lleva el aviso `?untranslated=` (una
 * variante de la portada de sabiduría que no aporta nada), o si su fila del registro la deja fuera
 * (`"index": false`) o pide sesión (`"auth": true`). Basta una fila que coincida: `/wisdom/propose/`
 * también encaja en el patrón de una cita.
 */
export function indexable(url: URL, estado = 200): boolean {
  if (estado !== 200) return false;
  if (url.searchParams.has('untranslated')) return false;
  return !filas.some(({ fila, patron }) => patron.test(url.pathname) && (fila.index === false || fila.auth === true));
}

/**
 * El origen con el que escribir direcciones absolutas, o `''` si no se sabe. Astro solo se fía del
 * host que figura en `security.allowedDomains` (TTOD_ALLOWED_HOSTS, AA2); con otro (una IP del aula
 * que nadie dio de alta, un Host inventado) su `url` cae en su propia dirección interna
 * (`http://localhost:4321`), que ningún navegador alcanza. Si el host que se pidió (el de Caddy,
 * `X-Forwarded-Host`, o el `Host` directo) no es el de `url`, las direcciones van relativas a la raíz
 * y lo que exige absoluta (`og:url`, `og:image`) no se escribe.
 */
export function origenPublico(url: URL, cabeceras: Headers): string {
  const pedido = (cabeceras.get('x-forwarded-host') ?? cabeceras.get('host') ?? '').split(',')[0].trim().toLowerCase();
  // Sin cabecera de host no hay nada que desconfiar: la URL es la de la petición misma.
  return !pedido || pedido === url.host.toLowerCase() ? url.origin : '';
}

/** La página de la lista (`?p=`) solo cuenta desde la 2; la 1 es la ruta sin consulta. */
function pagina(url: URL): string {
  const p = Number(url.searchParams.get('p'));
  return Number.isInteger(p) && p >= 2 ? `?p=${p}` : '';
}

/**
 * Dirección canónica: la ruta sin la consulta. Una búsqueda (`?q=`), los filtros combinados, el
 * camino del grafo (`?from=&to=&node=`) o el `?next=` de la entrada son la misma página.
 */
export function canonica(url: URL, origen: string): string {
  return origen + url.pathname + pagina(url);
}

/**
 * Las alternas `hreflang`: esta página, su gemela y `x-default` (la inglesa). `otra` es la ruta de
 * la gemela; `null` cuando no la hay (una cita sin traducción), y entonces no se anuncia ninguna.
 */
export function alternas(url: URL, origen: string, lang: Idioma, otra: string | null): Array<{ hreflang: string; href: string }> {
  if (!otra) return [];
  const sufijo = pagina(url);
  const rutas: Record<Idioma, string> = lang === 'en' ? { en: url.pathname, es: otra } : { en: otra, es: url.pathname };
  return [
    { hreflang: 'en', href: origen + rutas.en + sufijo },
    { hreflang: 'es', href: origen + rutas.es + sufijo },
    { hreflang: 'x-default', href: origen + rutas.en + sufijo },
  ];
}

/** Recorta en el último espacio antes del límite y marca el corte con «…». */
export function recorte(texto: string, max: number): string {
  const limpio = texto.replace(/\s+/g, ' ').trim();
  if (limpio.length <= max) return limpio;
  const corte = limpio.slice(0, max - 1);
  const espacio = corte.lastIndexOf(' ');
  return (espacio > max / 2 ? corte.slice(0, espacio) : corte).replace(/[\s,;:.—–-]+$/, '') + '…';
}

/** Título de una cita: sus primeras palabras, no su id (F41). */
export function tituloCita(texto: string, seccion: string): string {
  return `${recorte(texto, 60)} · ${seccion}`;
}

/** Descripción de una cita: lo que enseña; si no lo dice, la cita misma. */
export function descripcionCita(texto: string, ensena: string | undefined): string {
  return recorte(ensena && ensena.trim() ? ensena : texto, 155);
}
