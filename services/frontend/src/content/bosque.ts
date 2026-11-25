/**
 * El bosque de estelas: lo que la vista `/wisdom` necesita para presentarse, y
 * nada más. Aquí no se consulta el backend ni se decide qué es el corpus —eso
 * sigue en `content/wisdom.ts`—: esto es la capa de presentación del pasillo.
 *
 * Concepto: en el
 * Beilin de Xi'an los textos no viven en un índice, viven grabados en losas
 * verticales y se leen andando entre ellas. Cada aforismo es una estela; las
 * facetas no son píldoras sueltas, son por qué pasillo entras.
 */
import type { WisdomEntry } from '../types/domain';
import type { Locale } from './wisdom';

/**
 * 20 estelas por pasillo, como el «Showing 1-20 of 48.919» de Poetry
 * Foundation. No es un capricho: las 230 estelas del corpus en una sola página
 * medían 118.362 px de scroll a 390 px (medido el 17 oct sobre la vista
 * anterior), que ni se recorre con el pulgar ni cabe en el presupuesto de
 * velocidad.
 */
export const POR_PASILLO = 20;

/**
 * El dato manda el slug (`images`, `beginner`) porque es la clave de la ruta y
 * del backend; la pantalla manda el rótulo. Una página en español que dice
 * «beginner» está a medio traducir. Lo que no esté en el mapa sale tal cual:
 * las 306 etiquetas son palabras clave del corpus, no vocabulario de interfaz.
 */
const SECCIONES: Record<string, { es: string; en: string }> = {
  images: { es: 'Imágenes', en: 'Images' },
  architecture: { es: 'Arquitectura', en: 'Architecture' },
  'code-craft': { es: 'Oficio del código', en: 'Code craft' },
  'qa-tooling': { es: 'Calidad y herramientas', en: 'QA & tooling' },
  wisdom: { es: 'Sabiduría', en: 'Wisdom' },
  'remote-repo': { es: 'Repositorio remoto', en: 'Remote repo' },
  devops: { es: 'DevOps', en: 'DevOps' },
  debugging: { es: 'Depuración', en: 'Debugging' },
  ux: { es: 'Experiencia de uso', en: 'User experience' },
  operations: { es: 'Operaciones', en: 'Operations' },
  accessibility: { es: 'Accesibilidad', en: 'Accessibility' },
  networking: { es: 'Redes', en: 'Networking' },
  javascript: { es: 'JavaScript', en: 'JavaScript' },
};

const NIVELES: Record<string, { es: string; en: string }> = {
  beginner: { es: 'Principiante', en: 'Beginner' },
  intermediate: { es: 'Intermedio', en: 'Intermediate' },
  advanced: { es: 'Avanzado', en: 'Advanced' },
  master: { es: 'Maestro', en: 'Master' },
};

export const rotuloSeccion = (slug: string, locale: Locale) => SECCIONES[slug]?.[locale] ?? slug;
export const rotuloNivel = (slug: string, locale: Locale) => NIVELES[slug]?.[locale] ?? slug;

/** Orden de lectura de los niveles: de quien empieza a quien enseña, no alfabético. */
const ESCALERA = ['beginner', 'intermediate', 'advanced', 'master'];

export type ClaveOrden = 'corpus' | 'seccion' | 'nivel' | 'enlazadas';

export const ORDENES: ReadonlyArray<{ clave: ClaveOrden; es: string; en: string }> = [
  { clave: 'corpus', es: 'Orden del corpus', en: 'Corpus order' },
  { clave: 'seccion', es: 'Por sección', en: 'By section' },
  { clave: 'nivel', es: 'De principiante a maestro', en: 'Beginner to master' },
  { clave: 'enlazadas', es: 'Más enlazadas primero', en: 'Most linked first' },
];

export const esClaveOrden = (valor: string | null): valor is ClaveOrden =>
  ORDENES.some((o) => o.clave === valor);

export function ordenar(entries: WisdomEntry[], clave: ClaveOrden): WisdomEntry[] {
  const porId = (a: WisdomEntry, b: WisdomEntry) => a.id.localeCompare(b.id);
  const copia = [...entries];
  if (clave === 'seccion') return copia.sort((a, b) => a.section.localeCompare(b.section) || porId(a, b));
  if (clave === 'nivel') return copia.sort((a, b) => ESCALERA.indexOf(a.level) - ESCALERA.indexOf(b.level) || porId(a, b));
  if (clave === 'enlazadas') return copia.sort((a, b) => b.related.length - a.related.length || porId(a, b));
  return copia.sort(porId);
}

/** El pasillo que se pide, siempre dentro de los que existen (y 1 si no se pide nada). */
export function pasilloPedido(bruto: string | null, total: number): number {
  const pasillos = Math.max(1, Math.ceil(total / POR_PASILLO));
  const n = Number.parseInt(bruto ?? '1', 10);
  if (!Number.isFinite(n) || n < 1) return 1;
  return Math.min(n, pasillos);
}

/** Las etiquetas son 306: en la puerta caben las más grabadas, y se dice cuántas son. */
export const TAGS_EN_LA_PUERTA = 30;

export const copia = {
  es: {
    titulo: 'El bosque de estelas',
    tituloFaceta: (rotulo: string) => `Pasillo: ${rotulo}`,
    introFaceta: (rotulo: string, total: number) =>
      `Este pasillo recorre solo las estelas de ${rotulo}. El bosque entero guarda ${total} aforismos grabados.`,
    entrada:
      'En el bosque de estelas los textos no están en un índice: están grabados en losas de piedra y se leen andando entre ellas. Una estela por aforismo.',
    recuento: (mostradas: string, total: number, secciones: number) =>
      `Mostrando ${mostradas} de ${total} aforismos, grabados en ${secciones} secciones.`,
    recuentoFaceta: (mostradas: string, total: number, bosque: number) =>
      `Mostrando ${mostradas} de ${total} aforismos de este pasillo, de los ${bosque} del bosque.`,
    pasilloDe: (n: number, de: number) => `Pasillo ${n} de ${de}`,
    filtrar: 'Filtrar',
    filtrarAyuda: 'Las tres puertas del bosque: por sección, por nivel y por etiqueta.',
    ordenar: 'Ordenar',
    aplicar: 'Aplicar',
    secciones: 'Secciones',
    seccionesAyuda: (n: number) => `${n} pasillos`,
    niveles: 'Niveles',
    nivelesAyuda: (n: number) => `${n} escalones, de quien empieza a quien enseña`,
    etiquetas: 'Etiquetas',
    etiquetasAyuda: (cuantas: number, total: number) => `Las ${cuantas} más grabadas, de ${total}`,
    todas: 'Todo el bosque',
    siguiente: 'Siguiente pasillo',
    anterior: 'Pasillo anterior',
    finPasillo: (hasta: number, total: number) => `Llevas ${hasta} estelas de ${total}.`,
    finBosque: 'Has llegado al final del bosque.',
    estela: 'Estela',
    leer: 'Leer esta estela',
    quitarFiltro: 'Quitar el filtro',
    facetasDe: (id: string) => `Facetas de ${id}`,
    copiarEnlace: 'Copiar el enlace a esta estela',
    enEstaSeccion: (n: number) => `${n} estelas en esta sección`,
    enEsteNivel: (n: number) => `${n} estelas en este nivel`,
    conEstaEtiqueta: (n: number) => `${n} estelas con esta etiqueta`,
  },
  en: {
    titulo: 'The forest of steles',
    tituloFaceta: (rotulo: string) => `Corridor: ${rotulo}`,
    introFaceta: (rotulo: string, total: number) =>
      `This corridor walks only the steles of ${rotulo}. The whole forest holds ${total} carved aphorisms.`,
    entrada:
      'In a forest of steles the texts are not in an index: they are carved into standing stones and read by walking among them. One stele per aphorism.',
    recuento: (mostradas: string, total: number, secciones: number) =>
      `Showing ${mostradas} of ${total} aphorisms, carved across ${secciones} sections.`,
    recuentoFaceta: (mostradas: string, total: number, bosque: number) =>
      `Showing ${mostradas} of ${total} aphorisms in this corridor, of the ${bosque} in the forest.`,
    pasilloDe: (n: number, de: number) => `Corridor ${n} of ${de}`,
    filtrar: 'Filter',
    filtrarAyuda: 'The three gates into the forest: by section, by level and by tag.',
    ordenar: 'Sort by',
    aplicar: 'Apply',
    secciones: 'Sections',
    seccionesAyuda: (n: number) => `${n} corridors`,
    niveles: 'Levels',
    nivelesAyuda: (n: number) => `${n} steps, from beginner to teacher`,
    etiquetas: 'Tags',
    etiquetasAyuda: (cuantas: number, total: number) => `The ${cuantas} most carved, of ${total}`,
    todas: 'The whole forest',
    siguiente: 'Next corridor',
    anterior: 'Previous corridor',
    finPasillo: (hasta: number, total: number) => `${hasta} steles of ${total} walked.`,
    finBosque: 'You have reached the end of the forest.',
    estela: 'Stele',
    leer: 'Read this stele',
    quitarFiltro: 'Clear the filter',
    facetasDe: (id: string) => `Facets of ${id}`,
    copiarEnlace: 'Copy the link to this stele',
    enEstaSeccion: (n: number) => `${n} steles in this section`,
    enEsteNivel: (n: number) => `${n} steles at this level`,
    conEstaEtiqueta: (n: number) => `${n} steles with this tag`,
  },
} as const;
