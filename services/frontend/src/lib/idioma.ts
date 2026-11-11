/**
 * Cambiar de idioma sin perderse (AA3b, F57; LOCATORS.md §5).
 *
 * El servidor pinta el enlace sólo con la ruta: el navegador nunca le manda el
 * fragmento. Así que el enlace se completa al pulsarlo con `search + hash`
 * (las claves son las mismas en los dos idiomas, LOCATORS §2).
 *
 * En una cita, la otra lengua no es el mismo id: cada idioma tiene su propia
 * cita, unida a la otra por una arista `translation_of` que en `ttod.yml` está
 * guardada en un solo sentido (`wis-034 → wis-033`). Se busca en los dos.
 */
export interface Arista {
  source: string;
  target: string;
  rel: string;
}

export function mapaGemelas(aristas: Arista[]): Map<string, string> {
  const mapa = new Map<string, string>();
  for (const arista of aristas) {
    if (arista.rel !== 'translation_of') continue;
    if (!mapa.has(arista.source)) mapa.set(arista.source, arista.target);
    if (!mapa.has(arista.target)) mapa.set(arista.target, arista.source);
  }
  return mapa;
}

/**
 * Adónde lleva el cambio de idioma desde una cita. Con gemela, a su ficha; sin
 * ella, al índice del otro idioma con el aviso `?untranslated=`, nunca a una
 * página de «no encontrado». Sin saber (grafo caído), al índice sin aviso.
 */
export function destinoCita(id: string, otro: 'en' | 'es', gemelas: Map<string, string> | null): string {
  if (!gemelas) return `/${otro}/wisdom/`;
  const gemela = gemelas.get(id);
  return gemela ? `/${otro}/wisdom/${gemela}/` : `/${otro}/wisdom/?untranslated=${encodeURIComponent(id)}`;
}

/** El enlace del servidor, completado con lo que el navegador sabe y él no. */
export function conEstado(href: string, actual: { search: string; hash: string; origin: string }): string {
  const destino = new URL(href, actual.origin);
  for (const [clave, valor] of new URLSearchParams(actual.search)) {
    if (!destino.searchParams.has(clave)) destino.searchParams.append(clave, valor);
  }
  if (!destino.hash && actual.hash) destino.hash = actual.hash;
  return destino.pathname + destino.search + destino.hash;
}

/** Mejora en el navegador: los enlaces `[data-cambio-idioma]` se completan al pulsarlos. */
export function enlazarCambioIdioma(raiz: Document = document) {
  raiz.addEventListener('click', (evento) => {
    const enlace = (evento.target as Element | null)?.closest?.('a[data-cambio-idioma]');
    if (!(enlace instanceof HTMLAnchorElement)) return;
    enlace.href = conEstado(enlace.getAttribute('href') ?? enlace.href, location);
  });
}
