import type { WisdomEntry } from '../types/domain';
import { backendUrl } from './backend';

/**
 * El corpus que sirve el backend real, pedido una vez por minuto en vez de en
 * cada visita.
 *
 * Medido el 17 oct con el build de producción: `GET /api/v1/wisdom/sample`
 * devuelve 230 KB —el corpus entero— y el backend tarda **1,07–1,20 s** en
 * contestarlo. La portada lo espera antes de escribir una sola etiqueta, así que
 * ese segundo era el TTFB de la página y, con él, casi todo el LCP: medido a 390
 * con 4G lento, TTFB 1238–1304 ms → LCP 1860–2016 ms, y en las pasadas en que la
 * máquina iba cargada TTFB 1853–2383 ms → LCP 2680–3048 ms, por encima del
 * presupuesto de 2,5 s. El LCP iba siempre ~700 ms por detrás del TTFB: la
 * página no es lenta, la espera lo es.
 *
 * Aquí no se toca el backend ni la forma del dato: es la misma petición al mismo
 * endpoint real, guardada en memoria del servidor del front durante un minuto.
 * La primera visita la paga; las siguientes reciben el HTML en milisegundos. Un
 * minuto es corto a propósito: si el profesor acepta una cita nueva, aparece en
 * la siguiente página que alguien abra pasado ese minuto.
 *
 * Vive aparte de `content/wisdom.ts` a posta: ese módulo tiene su contrato
 * probado (`src/tests/load-wisdom.test.ts` llama tres veces seguidas con `fetch`
 * simulado y espera tres respuestas distintas), y una caché ahí lo rompería.
 */
const VIDA_MS = 60_000;

let guardado: { t: number; entradas: WisdomEntry[] } | undefined;
let enVuelo: Promise<WisdomEntry[]> | undefined;

/** Pide el corpus al backend real. Falla igual que antes: si no hay dato, lanza. */
export function pideCorpus(): Promise<WisdomEntry[]> {
  const viejo = guardado && Date.now() - guardado.t >= VIDA_MS;
  // Nadie espera por una actualización. Con la copia en mano se contesta ya y el
  // minuto siguiente se refresca por detrás: si se esperase, una visita de cada
  // sesenta segundos volvería a pagar el segundo del backend, y justo esa es la
  // que mide el presupuesto (medido: LCP 4244 ms con la copia caducada contra
  // 920 ms con la copia en mano).
  if (guardado) {
    // Si el refresco de fondo falla, se sigue enseñando la copia que hay: para
    // quien está leyendo, una cita de hace un minuto es mejor que un error.
    if (viejo) refresca().catch(() => {});
    return Promise.resolve(guardado.entradas);
  }
  return refresca();
}

// Se pide en cuanto se carga este módulo. Ojo: Astro carga las páginas con su
// primera visita, así que esa primera visita sí espera al backend (en frío, lo
// que tarde en leer `ttod.yml`). Si el backend no está, la siguiente visita lo
// vuelve a intentar y, si tampoco está, falla como fallaba antes.
refresca().catch(() => {});

function refresca(): Promise<WisdomEntry[]> {
  // Dos visitas a la vez comparten la misma petición: sin esto, un pico de
  // tráfico multiplica el segundo de espera por cada visitante.
  if (!enVuelo) {
    const backend = backendUrl();
    enVuelo = (async () => {
      try {
        const respuesta = await fetch(`${backend}/api/v1/wisdom/sample`, { headers: { accept: 'application/json' } });
        if (!respuesta.ok) throw new Error(`Backend flagship quote request failed (${respuesta.status})`);
        const cuerpo: unknown = await respuesta.json();
        if (!Array.isArray(cuerpo)) throw new Error('Backend wisdom response is not an array');
        guardado = { t: Date.now(), entradas: cuerpo as WisdomEntry[] };
        return guardado.entradas;
      } finally {
        enVuelo = undefined;
      }
    })();
  }
  return enVuelo;
}
