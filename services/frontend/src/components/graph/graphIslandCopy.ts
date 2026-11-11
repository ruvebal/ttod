/**
 * Los textos del plano 2D (GraphIsland) en los dos idiomas (AA3, F32/A20). Antes
 * el plano hablaba solo inglés también en /es/; la constelación 3D y el oráculo ya
 * eran bilingües. Las claves de la URL (`tag`, `node`) no cambian.
 */
import { rotuloSeccion } from '../../content/bosque';
import { sectionLabel } from './layout';

export type Lang = 'en' | 'es';

export const copiaPlano = {
  en: {
    title: 'TTOD knowledge graph',
    counts: (n: number, e: number) => `${n} nodes · ${e} edges`,
    filter: 'Filter by tag', allTags: 'All tags', legend: 'Section legend',
    filtered: (tag: string) => `Filtered to tag: ${tag}`, showingAll: 'Showing all tags',
    loading: 'Loading live graph…', unavailable: 'The live graph is unavailable.',
    noTagNodes: 'No nodes carry this tag.', noNodes: 'No graph nodes are available.',
    graphLabel: (n: number, e: number) => `Knowledge graph with ${n} nodes and ${e} edges`,
    nodeLabel: (id: string, text: string, section: string, origin: string, tags: string[]) =>
      `${id}: ${text}, section: ${section}, origin: ${origin}${tags.length ? `, tags: ${tags.join(', ')}` : ''}`,
    selected: 'Selected node', selectHint: 'Select a node to view its details.',
  },
  es: {
    title: 'Grafo de conocimiento de TTOD',
    counts: (n: number, e: number) => `${n} nodos · ${e} relaciones`,
    filter: 'Filtrar por etiqueta', allTags: 'Todas las etiquetas', legend: 'Leyenda de secciones',
    filtered: (tag: string) => `Filtrado por la etiqueta: ${tag}`, showingAll: 'Se muestran todas las etiquetas',
    loading: 'Cargando el grafo en vivo…', unavailable: 'El grafo en vivo no está disponible.',
    noTagNodes: 'Ningún nodo lleva esta etiqueta.', noNodes: 'No hay nodos en el grafo.',
    graphLabel: (n: number, e: number) => `Grafo de conocimiento con ${n} nodos y ${e} relaciones`,
    nodeLabel: (id: string, text: string, section: string, origin: string, tags: string[]) =>
      `${id}: ${text}, sección: ${section}, origen: ${origin}${tags.length ? `, etiquetas: ${tags.join(', ')}` : ''}`,
    selected: 'Nodo seleccionado', selectHint: 'Elige un nodo para ver sus detalles.',
  },
} as const;

/** El rótulo de una sección: el mismo de Sabiduría en /es/, el del plano en /en/. */
export const rotuloDeSeccion = (section: string, lang: Lang) => (lang === 'es' ? rotuloSeccion(section, 'es') : sectionLabel(section));
