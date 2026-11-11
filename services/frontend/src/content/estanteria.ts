/**
 * El armario del corpus: lo que `/wisdom` necesita para presentarse como una
 * estantería de volúmenes, y nada más. Aquí no se consulta el backend ni se
 * decide qué es el corpus (eso sigue en `content/wisdom.ts`).
 *
 * Concepto: cartas animadas que parecen libros en 3D, que se abren y así
 * recopilan mejor todo. Cada sección del corpus es un
 * volumen cosido: el lomo lleva su título y cuántos aforismos guarda, y el
 * grosor del libro **es** ese número, no un adorno. Un corpus con 73 citas de
 * imágenes y 1 de redes se ve antes de leer una palabra.
 */
import type { WisdomEntry } from '../types/domain';
import type { Locale } from './wisdom';
import { rotuloSeccion } from './bosque';

export interface Volumen {
  /** El slug de la sección: clave del backend y de la ruta `/wisdom/sections/…`. */
  slug: string;
  titulo: string;
  /** La inicial que va en el sello de la guarda. */
  sello: string;
  citas: WisdomEntry[];
  /** Grosor del lomo en píxeles: proporcional a cuántas citas tiene. */
  grosor: number;
  /** Índice del tono de tapa (0–4); lo reparte el orden del armario. */
  tono: number;
}

/**
 * De 14 px (una cita) a 46 px (las 73 de imágenes). Abajo de 14 el lomo no
 * admite ni el número, y arriba de 46 el libro se come el ancho del móvil.
 */
const GROSOR_MIN = 14;
const GROSOR_MAX = 46;
const TONOS = 5;

/**
 * Cuántas citas se cosen dentro de cada volumen. El resto se leen en la ruta
 * de la sección: 230 páginas en el HTML de la portada del armario son 230
 * nodos que nadie abre, y la velocidad es un requisito. Diez hojas
 * costaban un fotograma de 66 ms al abrir (freno de CPU 4x); seis caben en
 * el presupuesto de 50 ms y siguen siendo una lectura, no un aperitivo.
 */
export const PAGINAS_POR_VOLUMEN = 6;

export function volumenes(entries: WisdomEntry[], locale: Locale): Volumen[] {
  const porSeccion = new Map<string, WisdomEntry[]>();
  for (const entry of entries) {
    const lista = porSeccion.get(entry.section);
    if (lista) lista.push(entry);
    else porSeccion.set(entry.section, [entry]);
  }
  const lomos = [...porSeccion.entries()].sort(
    ([slugA, a], [slugB, b]) => b.length - a.length || slugA.localeCompare(slugB),
  );
  const mayor = lomos[0]?.[1].length ?? 1;
  return lomos.map(([slug, citas], i) => {
    const titulo = rotuloSeccion(slug, locale);
    // Raíz cuadrada y no proporción directa: con 73 contra 1, la escala lineal
    // deja doce lomos pegados al mínimo y uno enorme. Así los tres gruesos se
    // distinguen entre sí y los finos siguen siendo finos.
    const peso = Math.sqrt(citas.length / mayor);
    return {
      slug,
      titulo,
      sello: titulo.slice(0, 1).toLocaleUpperCase(locale),
      citas,
      grosor: Math.round(GROSOR_MIN + (GROSOR_MAX - GROSOR_MIN) * peso),
      tono: i % TONOS,
    };
  });
}

export const copia = {
  es: {
    titulo: 'Sabiduría',
    mazoTitulo: 'Saca uno al azar',
    mazoIntro: 'Los volúmenes, apilados. Toca la pila: sale una cita del corpus y el libro de su sección se abre por esa página.',
    mazoBoton: 'Sacar uno al azar',
    mazoBotonCuenta: (n: number) => `, una cita entre ${n}`,
    abrirCita: 'Abrir la cita',
    todoElVolumen: 'Todo el volumen',
    otra: 'Otra al azar',
    deslizaCerrar: 'Desliza hacia abajo para cerrar',
    paginaPlantilla: 'Página {p} de {n}',
    aforismosPlantilla: '{n} aforismos',
    buscarRotulo: 'Buscar una cita',
    buscarBoton: 'Buscar',
    buscarAyuda: 'En el texto, en lo que enseña, en sus etiquetas y en su id. Sin tildes ni mayúsculas: «diseno» encuentra «diseño».',
    indice: 'Las secciones',
    resultados: (n: number, q: string, filtros: string) =>
      [q ? `«${q}»` : '', filtros].filter(Boolean).join(' · ') + `: ${n === 1 ? '1 cita' : `${n} citas`}`,
    sinResultados: 'Ninguna cita coincide. Prueba con otra palabra, o entra por una de las secciones de arriba.',
    sinTraduccion: (id: string) => `La cita ${id} todavía no tiene versión en español. Aquí está el resto del corpus.`,
    copiarVolumen: 'Copiar el enlace a este volumen',
    copiarCita: 'Copiar el enlace a la cita',
    copiado: 'Enlace copiado',
    sinPortapapeles: 'Copia el enlace desde «Abrir la cita»',
    estanteTitulo: 'Todos los volúmenes',
    entrada:
      'El corpus cosido en volúmenes: cada sección es un libro y el grosor de su lomo es cuántos aforismos guarda. Saca uno al azar de la pila, o recórrelos todos en la estantería.',
    recuento: (citas: number, libros: number) =>
      `${citas} aforismos cosidos en ${libros} volúmenes`,
    pista: 'Desliza la estantería',
    abrir: (titulo: string, n: number) => `Abrir ${titulo}, ${n} aforismos`,
    cerrar: 'Cerrar el libro',
    aforismos: (n: number) => (n === 1 ? '1 aforismo' : `${n} aforismos`),
    pagina: (i: number, de: number) => `Página ${i} de ${de}`,
    seguir: (n: number, titulo: string) => `Leer los ${n} de ${titulo}`,
    sinMas: (titulo: string) => `Ver ${titulo} entero`,
    volumen: 'Volumen',
    facetas: 'Otras formas de entrar al corpus',
    porNivel: 'Por nivel',
    porEtiqueta: 'Por etiqueta',
    todas: 'Leer el corpus seguido',
    credito:
      'Fondo: Hua Yan (1682–h. 1765), «Un letrado a la mesa y un criado que le prepara la tinta», del Álbum de paisajes que ilustran poemas antiguos, 1745. Hoja de álbum; tinta y color ligero sobre papel. The Cleveland Museum of Art, 1982.68.10 · CC0.',
  },
  en: {
    titulo: 'Wisdom',
    mazoTitulo: 'Draw one at random',
    mazoIntro: 'The volumes, stacked. Tap the pile: a quote comes out of the corpus and the book of its section opens at that page.',
    mazoBoton: 'Draw one at random',
    mazoBotonCuenta: (n: number) => `, one quote out of ${n}`,
    abrirCita: 'Open the quote',
    todoElVolumen: 'The whole volume',
    otra: 'Another one',
    deslizaCerrar: 'Swipe down to close',
    paginaPlantilla: 'Page {p} of {n}',
    aforismosPlantilla: '{n} aphorisms',
    buscarRotulo: 'Search for a quote',
    buscarBoton: 'Search',
    buscarAyuda: 'In the text, in what it teaches, in its tags and in its id. Accents and case do not matter.',
    indice: 'The sections',
    resultados: (n: number, q: string, filtros: string) =>
      [q ? `“${q}”` : '', filtros].filter(Boolean).join(' · ') + `: ${n === 1 ? '1 quote' : `${n} quotes`}`,
    sinResultados: 'No quote matches. Try another word, or go in through one of the sections above.',
    sinTraduccion: (id: string) => `Quote ${id} has no English version yet. Here is the rest of the corpus.`,
    copiarVolumen: 'Copy the link to this volume',
    copiarCita: 'Copy the link to the quote',
    copiado: 'Link copied',
    sinPortapapeles: 'Copy the link from “Open the quote”',
    estanteTitulo: 'All the volumes',
    entrada:
      'The corpus bound into volumes: each section is a book, and the thickness of its spine is how many aphorisms it holds. Draw one at random from the pile, or walk through all of them on the shelf.',
    recuento: (citas: number, libros: number) =>
      `${citas} aphorisms bound into ${libros} volumes`,
    pista: 'Slide the shelf',
    abrir: (titulo: string, n: number) => `Open ${titulo}, ${n} aphorisms`,
    cerrar: 'Close the book',
    aforismos: (n: number) => (n === 1 ? '1 aphorism' : `${n} aphorisms`),
    pagina: (i: number, de: number) => `Page ${i} of ${de}`,
    seguir: (n: number, titulo: string) => `Read all ${n} in ${titulo}`,
    sinMas: (titulo: string) => `See all of ${titulo}`,
    volumen: 'Volume',
    facetas: 'Other ways into the corpus',
    porNivel: 'By level',
    porEtiqueta: 'By tag',
    todas: 'Read the corpus straight through',
    credito:
      'Background: Hua Yan (1682–c. 1765), “A Scholar at a Table with a Servant aside Preparing the Ink”, from Album of Landscape Paintings Illustrating Old Poems, 1745. Album leaf; ink and light color on paper. The Cleveland Museum of Art, 1982.68.10 · CC0.',
  },
} as const;
