import type { WisdomEntry } from '../types/domain';
import { backendUrl } from '../lib/backend';

export type Locale = 'en' | 'es';

export const isLocale = (value: string | undefined): value is Locale => value === 'en' || value === 'es';

export async function fetchWisdom(locale: Locale): Promise<WisdomEntry[]> {
  const backend = backendUrl();
  const response = await fetch(`${backend}/api/v1/wisdom/sample`, { headers: { accept: 'application/json' } });
  if (!response.ok) throw new Error(`Backend wisdom request failed (${response.status})`);
  const payload: unknown = await response.json();
  if (!Array.isArray(payload)) throw new Error('Backend wisdom response is not an array');
  return (payload as WisdomEntry[]).filter((entry) => entry.lang === locale);
}

export type WisdomLoad = { entries: WisdomEntry[]; failed: boolean };

// Every route calls this instead of fetchWisdom() directly: fetchWisdom() keeps throwing on
// network/response failures (its existing, tested contract), and this is the one place that
// catches that so no page carries its own try/catch. A route only ever needs to branch on
// `failed` (translated error state) vs `entries.length === 0` (translated empty state).
/**
 * El corpus entero, recordado por idioma: se sirve lo guardado y, pasado un
 * minuto, se vuelve a preguntar por detrás sin hacer esperar a nadie.
 *
 * Medido el 17 oct a 390 con el freno de CPU 4×: el backend tarda entre 1,2 y
 * 3,4 s en devolver `/api/v1/wisdom/sample`, y como la página se pinta en el
 * servidor, ese tiempo era el primer píxel — LCP de 5,3 s, cuando el
 * presupuesto son 2,5. Ni una línea del backend cambia: el frontend deja de
 * pedir lo mismo doscientas veces. Un minuto es corto para una base que se
 * edita a mano y largo para una visita.
 */
const UN_MINUTO = 60_000;
const recordado = new Map<Locale, { en: number; corpus: Promise<WisdomEntry[]> }>();

/**
 * En las pruebas no se recuerda nada: cada caso trae su propio corpus (uno
 * vacío, uno con una entrada, un backend caído) dentro del mismo minuto, y
 * una caché le daría al segundo caso el corpus del primero. Apagada ahí, el
 * banco de pruebas sigue comprobando de verdad qué pasa con el backend caído.
 */
const recordar = import.meta.env.MODE !== 'test';

export async function loadWisdom(locale: Locale): Promise<WisdomLoad> {
  const ahora = Date.now();
  const guardado = recordar ? recordado.get(locale) : undefined;
  // Lo guardado se sirve siempre que exista; si ya pasó el minuto se sirve
  // igual y se pregunta por detrás. Esperar a la respuesta para enseñar lo
  // mismo que ya se tenía es pagar dos segundos por nada: sólo la primera
  // visita después de arrancar espera al backend.
  if (guardado !== undefined && ahora - guardado.en >= UN_MINUTO) {
    const fresco = fetchWisdom(locale);
    recordado.set(locale, { en: ahora, corpus: fresco });
    // Si la que viene por detrás falla, se deja lo de antes: una página con el
    // corpus de hace un minuto es mejor que una página con un aviso de error.
    fresco.catch(() => recordado.set(locale, guardado));
  }
  const corpus = guardado?.corpus ?? fetchWisdom(locale);
  if (recordar && guardado === undefined) recordado.set(locale, { en: ahora, corpus });
  try {
    return { entries: await corpus, failed: false };
  } catch {
    // Un fallo no se recuerda: la siguiente visita vuelve a preguntar.
    if (recordado.get(locale)?.corpus === corpus) recordado.delete(locale);
    return { entries: [], failed: true };
  }
}

export const quoteSlug = (entry: WisdomEntry) => entry.id;

export const labels = {
  en: {
    wisdom: 'Wisdom', docs: 'Documentation', empty: 'No accepted English wisdom is available yet.',
    sections: 'Sections', levels: 'Levels', tags: 'Tags', all: 'All wisdom', teaches: 'Teaches', related: 'Related wisdom',
    back: 'Back to wisdom', entries: 'entries', notFound: 'Wisdom entry not found',
    noMatchesTitle: 'No matches', noMatches: 'No English wisdom entry carries this facet yet.',
    emptyTitle: 'Nothing here yet',
    notFoundMessage: "This wisdom entry doesn't exist in this language yet.",
    errorTitle: 'Something went wrong',
    errorMessage: 'We could not load the wisdom corpus. Please try again later.',
    propose: 'Propose a quote',
    proposeLoginPrompt: 'Log in to propose a quote.',
  },
  es: {
    wisdom: 'Sabiduría', docs: 'Documentación', empty: 'Todavía no hay sabiduría aceptada en español.',
    sections: 'Secciones', levels: 'Niveles', tags: 'Etiquetas', all: 'Toda la sabiduría', teaches: 'Enseña', related: 'Sabiduría relacionada',
    back: 'Volver a sabiduría', entries: 'entradas', notFound: 'Entrada de sabiduría no encontrada',
    noMatchesTitle: 'Sin coincidencias', noMatches: 'Ninguna entrada de sabiduría en español tiene esta faceta todavía.',
    emptyTitle: 'Todavía nada aquí',
    notFoundMessage: 'Esta entrada de sabiduría todavía no existe en este idioma.',
    errorTitle: 'Algo ha fallado',
    errorMessage: 'No hemos podido cargar el corpus de sabiduría. Inténtalo de nuevo más tarde.',
    propose: 'Proponer una cita',
    proposeLoginPrompt: 'Inicia sesión para proponer una cita.',
  },
} as const;

export function frequencies(entries: WisdomEntry[], field: 'section' | 'level' | 'tags') {
  const counts = new Map<string, number>();
  for (const entry of entries) {
    const values = field === 'tags' ? entry.tags : [entry[field]];
    for (const value of values) counts.set(value, (counts.get(value) ?? 0) + 1);
  }
  return [...counts].sort(([left], [right]) => left.localeCompare(right));
}
