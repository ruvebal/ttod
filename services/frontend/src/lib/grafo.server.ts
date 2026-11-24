import { construirGrafo, planoGuardable, type PlanoGuardado, type RespuestaGrafo } from '../components/graph/sendero';
import { mapaGemelas, type Arista } from './idioma';
import { backendUrl } from './backend';

/**
 * El plano 2D de /graph, calculado en el servidor una vez por grafo y por idioma.
 *
 * En la primera visita el navegador tenía que calcularlo él al llegar los datos:
 * 202 nodos x 220 pasadas, ~220 ms de hilo con la CPU a 1/4 (perfil de /es/graph
 * en un móvil emulado), la tarea más larga entre «llegan los datos» y «se ven estrellas».
 * Aquí se calcula con el mismo código (`sendero.ts`) sobre el mismo endpoint real
 * y se incrusta en la página; el navegador solo comprueba la huella.
 *
 * Nunca hace esperar a la página: si todavía no hay grafo guardado, esa visita
 * sale sin plano incrustado (el navegador lo calcula, como antes) y la petición
 * sigue para las siguientes. Se refresca por detrás cada minuto, igual que el
 * corpus de la portada (`corpus.server.ts`).
 */
const VIDA_MS = 60_000;

// En `globalThis` y no en el módulo: en desarrollo (`astro dev`) Vite puede volver
// a evaluar el módulo y la copia se perdería en cada visita.
const memoria = ((globalThis as any).__ttodGrafo ??= { planos: new Map() }) as {
  guardado?: { t: number; datos: RespuestaGrafo; texto: string };
  enVuelo?: Promise<void>;
  falloEn?: number;
  planos: Map<string, PlanoGuardado>;
};
const { planos } = memoria;

function refresca(): Promise<void> {
  if (!memoria.enVuelo) {
    const backend = backendUrl();
    memoria.enVuelo = (async () => {
      try {
        // Con tope: una cita espera a este grafo para su cambio de idioma, y un
        // backend colgado no puede colgar la página (cold review AA3b, F8).
        const r = await fetch(`${backend}/api/v1/graph`, { headers: { accept: 'application/json' }, signal: AbortSignal.timeout(4000) });
        if (!r.ok) { memoria.falloEn = Date.now(); return; }
        const texto = await r.text();
        const datos = JSON.parse(texto) as RespuestaGrafo;
        if (!Array.isArray(datos?.nodes) || !Array.isArray(datos?.edges)) return;
        memoria.guardado = { t: Date.now(), datos, texto };
        planos.clear();
      } catch {
        // Sin backend no hay plano incrustado; la página sale igual.
        memoria.falloEn = Date.now();
      } finally {
        memoria.enVuelo = undefined;
      }
    })();
  }
  return memoria.enVuelo;
}

refresca();

/** El plano de este idioma si ya hay grafo guardado; si no, `null` sin esperar. */
export function planoInicial(idioma: string): PlanoGuardado | null {
  const guardado = vigente();
  if (!guardado) return null;
  let plano = planos.get(idioma);
  if (!plano) {
    const grafo = construirGrafo(guardado.datos, idioma);
    if (!grafo.nodos.length) return null;
    plano = planoGuardable(grafo.nodos, grafo.aristas);
    planos.set(idioma, plano);
  }
  return plano;
}

/**
 * El propio `/api/v1/graph` tal como lo dio el backend, para incrustarlo en la
 * página: así la constelación no espera a una petición del navegador al backend
 * (en la vista que usa el backend compartido son 1,3-3 s por petición). Mismo
 * cuerpo byte a byte; si no hay copia, `null` y el navegador lo pide como antes.
 */
export function grafoInicial(): string | null {
  return vigente()?.texto ?? null;
}

/**
 * Las gemelas de traducción (`translation_of`, en los dos sentidos) para el
 * cambio de idioma de una cita (AA3b, F57). A diferencia del plano, aquí sí se
 * espera al grafo la primera vez: el enlace tiene que llevar a la cita gemela,
 * no a un índice. Si el backend no da grafo, `null` (el enlace va al índice).
 */
let gemelasDe: { datos: RespuestaGrafo; mapa: Map<string, string> } | undefined;
export async function gemelasTraduccion(): Promise<Map<string, string> | null> {
  // Si acaba de fallar, no se vuelve a esperar en cada visita: medio minuto sin
  // grafo (el enlace va al índice) y se vuelve a intentar por detrás.
  const recienFallo = memoria.falloEn !== undefined && Date.now() - memoria.falloEn < 30_000;
  if (!vigente() && !recienFallo) await refresca();
  const guardado = memoria.guardado;
  if (!guardado) return null;
  if (gemelasDe?.datos !== guardado.datos) {
    gemelasDe = { datos: guardado.datos, mapa: mapaGemelas(guardado.datos.edges as Arista[]) };
  }
  return gemelasDe.mapa;
}

function vigente() {
  const guardado = memoria.guardado;
  if (!guardado || Date.now() - guardado.t >= VIDA_MS) refresca();
  return memoria.guardado ?? null;
}
