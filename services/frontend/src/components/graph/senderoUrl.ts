/**
 * La constelación como dirección (AA3b, F52; LOCATORS §4): `?from=&to=` es el
 * sendero entre dos citas y `?node=` la cita abierta. Se leen al llegar el grafo
 * y se reescriben con `replaceState` al cambiar, así que un sendero sobrevive a
 * recargar y a copiar y pegar la dirección. Las demás claves se respetan.
 */
export interface EstadoSendero {
  from: string;
  to: string;
  node: string;
}

const CLAVES = ['from', 'to', 'node'] as const;

export function leerSendero(search: string): EstadoSendero {
  const params = new URLSearchParams(search);
  return { from: params.get('from') ?? '', to: params.get('to') ?? '', node: params.get('node') ?? '' };
}

/**
 * Cada id pedido se traduce al id del nodo (`alias`): el nodo lleva el id de la
 * cita con relaciones, que es el mismo en `/en/` y en `/es/`, aunque en `/es/` se
 * enseñe el id de su gemela española. Así la dirección vale en los dos idiomas
 * (las claves y los valores son los mismos, LOCATORS §2) y un id español escrito
 * a mano también llega. Lo que el grafo no tiene se descarta, y un sendero de
 * una cita a sí misma, también.
 */
export function validarSendero(estado: EstadoSendero, alias: Map<string, string>): EstadoSendero {
  const nodo = (id: string) => (id ? alias.get(id) ?? '' : '');
  const from = nodo(estado.from);
  const toNodo = nodo(estado.to);
  const to = toNodo !== from ? toNodo : '';
  return { from, to, node: nodo(estado.node) };
}

/** id del nodo → id del nodo, e id enseñado (la gemela del idioma) → id del nodo. */
export function aliasDeNodos(nodos: Array<{ id: string; idTexto?: string }>): Map<string, string> {
  const alias = new Map<string, string>();
  for (const n of nodos) alias.set(n.id, n.id);
  for (const n of nodos) if (n.idTexto && !alias.has(n.idTexto)) alias.set(n.idTexto, n.id);
  return alias;
}

/** Ruta + consulta + fragmento con las tres claves puestas (o quitadas si están vacías). */
export function escribirSendero(href: string, estado: EstadoSendero): string {
  const url = new URL(href, 'http://localhost');
  for (const clave of CLAVES) {
    if (estado[clave]) url.searchParams.set(clave, estado[clave]);
    else url.searchParams.delete(clave);
  }
  return `${url.pathname}${url.search}${url.hash}`;
}
