/**
 * Los capítulos de la portada como fragmentos (AA3b, F51; LOCATORS §4).
 *
 * La portada tiene dos escenas pegajosas (el hero y el rollo): lo que se ve
 * dentro no depende de dónde esté el elemento en el documento sino de cuánto
 * se ha bajado. Un `#map-architecture` nativo cae en cualquier parte. Aquí:
 *
 * - Al llegar (y en `hashchange`), un capítulo con `data-ancla-progreso` dentro
 *   de una escena viva (`[data-ancla-escena][data-ancla-viva]`) se alcanza con la
 *   misma cuenta que las flechas del rollo: `tope + (alto − pantalla) × fracción`.
 *   Las escenas avisan cuando están medidas (`avisarEscenaLista`) y se vuelve a
 *   colocar hasta que la persona toca el scroll. Con movimiento reducido las
 *   escenas no están vivas y el salto nativo basta.
 * - Al leer, el capítulo actual se escribe en el fragmento con `replaceState`
 *   (nunca `pushState`: Atrás no rebobina el scroll), solo cuando cambia y nunca
 *   dentro de la primera pantalla.
 *
 * Con red lenta (cold review AA3b, F2) las escenas tardan en estar medidas, y
 * mientras tanto todas las paradas del rollo tienen el mismo `top`. Por eso:
 * el capítulo pedido se recuerda al llegar (no se vuelve a leer del fragmento),
 * y el fragmento no se escribe hasta que la persona toca la página: antes de eso
 * no está leyendo, está llegando. Un capítulo de una escena que todavía no está
 * viva no cuenta como leído.
 */
import { idDelFragmento } from './fragmento';

const LISTA = 'ttod:escena-lista';

export const avisarEscenaLista = () => document.dispatchEvent(new Event(LISTA));

const escenaViva = (el: HTMLElement) => el.closest<HTMLElement>('[data-ancla-escena][data-ancla-viva]');

/** La `y` de la página a la que se llega con una fracción del recorrido de una escena viva. */
function enEscena(el: HTMLElement, fraccion: string | undefined): number | null {
  const escena = escenaViva(el);
  const f = Number(fraccion);
  if (!escena || fraccion === undefined || !Number.isFinite(f)) return null;
  const tope = escena.getBoundingClientRect().top + window.scrollY;
  return tope + Math.max(0, escena.offsetHeight - window.innerHeight) * f;
}

const destinoDe = (el: HTMLElement) => enEscena(el, el.dataset.anclaProgreso);

/**
 * Dónde empieza un capítulo, para saber en cuál se está leyendo; `null` si no se
 * sabe todavía (está en una escena que aún no está viva y no es por movimiento
 * reducido, que deja las escenas quietas para siempre y entonces el `top` vale).
 */
function inicioDe(el: HTMLElement, holgura: number, quieto: boolean): number | null {
  const enLaEscena = enEscena(el, el.dataset.anclaDesde);
  if (enLaEscena !== null) return enLaEscena;
  if (el.dataset.anclaDesde !== undefined && !quieto) return null;
  return el.getBoundingClientRect().top + window.scrollY - holgura;
}

export function enlazarCapitulos(raiz: Document = document) {
  const capitulos = [...raiz.querySelectorAll<HTMLElement>('[data-capitulo][id]')];
  if (!capitulos.length) return;
  const ids = new Set(capitulos.map((c) => c.id));
  const quieto = window.matchMedia('(prefers-reduced-motion: reduce)');

  // Lo que pidió el enlace, leído una vez: las escenas avisan varias veces
  // mientras cargan y cada aviso vuelve a este destino, no al fragmento de ese
  // momento.
  let pedido = idDelFragmento(window.location.hash);
  let tocado = false;
  const marcar = () => { tocado = true; };
  for (const ev of ['wheel', 'touchstart', 'keydown', 'pointerdown']) window.addEventListener(ev, marcar, { once: true, passive: true });

  const colocar = (suave: boolean) => {
    const el = pedido ? raiz.getElementById(pedido) : null;
    if (!el) return;
    const y = destinoDe(el);
    if (y === null) return; // fuera de una escena viva el salto nativo ya llegó
    window.scrollTo({ top: y, behavior: suave && !quieto.matches ? 'smooth' : 'auto' });
  };
  raiz.addEventListener(LISTA, () => { if (!tocado) colocar(false); });
  window.addEventListener('load', () => { if (!tocado) requestAnimationFrame(() => colocar(false)); }, { once: true });
  window.addEventListener('hashchange', () => { pedido = idDelFragmento(window.location.hash); colocar(true); });
  colocar(false);

  let pendiente = false;
  const escribir = () => {
    pendiente = false;
    if (!tocado) return; // llegando, no leyendo: el fragmento pedido se respeta
    const y = window.scrollY;
    const actual = idDelFragmento(window.location.hash);
    if (y < window.innerHeight) {
      if (ids.has(actual)) history.replaceState(history.state, '', window.location.pathname + window.location.search);
      return;
    }
    // Lo que tapa la cabecera no cuenta como leído: la misma holgura del salto nativo.
    const holgura = parseFloat(getComputedStyle(raiz.documentElement).scrollPaddingTop) || 0;
    let leyendo = '';
    for (const c of capitulos) {
      const inicio = inicioDe(c, holgura, quieto.matches);
      if (inicio !== null && inicio <= y + 2) leyendo = c.id;
    }
    if (leyendo && leyendo !== actual) history.replaceState(history.state, '', `#${leyendo}`);
  };
  window.addEventListener('scroll', () => {
    if (pendiente) return;
    pendiente = true;
    requestAnimationFrame(escribir);
  }, { passive: true });
}
