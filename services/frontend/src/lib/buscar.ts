import type { WisdomEntry } from '../types/domain';

/**
 * Buscar en el corpus sin índice ni librería (AA3b, F49): el servidor ya tiene el
 * corpus del idioma en memoria (`loadWisdom`), así que filtrar 230 citas es un
 * recorrido, no una consulta. Funciona sin JavaScript: es un `GET ?q=`.
 *
 * Plegado: sin tildes ni mayúsculas (NFD y fuera las marcas), para que `diseno`
 * encuentre «diseño» y `DEUDA` encuentre «deuda». Varias palabras se exigen todas.
 */
export const LIMITE_Q = 100;

export const pliega = (texto: string) => texto.normalize('NFD').replace(/\p{Mn}/gu, '').toLowerCase();

export interface Filtros {
  q: string;
  section: string;
  level: string;
  tag: string;
}

export function leerFiltros(params: URLSearchParams): Filtros {
  const valor = (clave: string) => (params.get(clave) ?? '').trim();
  const q = valor('q').slice(0, LIMITE_Q);
  // Una búsqueda que al plegarse se queda en nada (una tilde suelta) no es una
  // búsqueda: si no, devolvería las 230 citas bajo el titular «´».
  return { q: pliega(q).trim() ? q : '', section: valor('section'), level: valor('level'), tag: valor('tag') };
}

export const hayFiltros = (f: Filtros) => Boolean(f.q || f.section || f.level || f.tag);

export function buscar(entries: WisdomEntry[], f: Filtros): WisdomEntry[] {
  const palabras = pliega(f.q).split(/\s+/).filter(Boolean);
  return entries.filter((entry) => {
    if (f.section && entry.section !== f.section) return false;
    if (f.level && entry.level !== f.level) return false;
    if (f.tag && !entry.tags.includes(f.tag)) return false;
    if (!palabras.length) return true;
    const pajar = pliega([entry.text, entry.teaches, entry.tags.join(' '), entry.id].join(' '));
    return palabras.every((palabra) => pajar.includes(palabra));
  });
}
