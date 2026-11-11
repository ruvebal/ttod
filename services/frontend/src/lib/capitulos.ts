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
 */
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

/** Dónde empieza un capítulo, para saber en cuál se está leyendo. */
function inicioDe(el: HTMLElement, holgura: number): number {
  const enLaEscena = enEscena(el, el.dataset.anclaDesde);
  if (enLaEscena !== null) return enLaEscena;
  return el.getBoundingClientRect().top + window.scrollY - holgura;
}

export function enlazarCapitulos(raiz: Document = document) {
  const capitulos = [...raiz.querySelectorAll<HTMLElement>('[data-capitulo][id]')];
  if (!capitulos.length) return;
  const ids = new Set(capitulos.map((c) => c.id));
  const quieto = window.matchMedia('(prefers-reduced-motion: reduce)');

  let tocado = false;
  const marcar = () => { tocado = true; };
  for (const ev of ['wheel', 'touchstart', 'keydown', 'pointerdown']) window.addEventListener(ev, marcar, { once: true, passive: true });

  const colocar = (suave: boolean) => {
    const id = decodeURIComponent(window.location.hash.slice(1));
    const el = id ? raiz.getElementById(id) : null;
    if (!el) return;
    const y = destinoDe(el);
    if (y === null) return; // fuera de una escena viva el salto nativo ya llegó
    window.scrollTo({ top: y, behavior: suave && !quieto.matches ? 'smooth' : 'auto' });
  };
  raiz.addEventListener(LISTA, () => { if (!tocado) colocar(false); });
  window.addEventListener('load', () => { if (!tocado) requestAnimationFrame(() => colocar(false)); }, { once: true });
  window.addEventListener('hashchange', () => colocar(true));
  colocar(false);

  let pendiente = false;
  const escribir = () => {
    pendiente = false;
    const y = window.scrollY;
    const actual = window.location.hash.slice(1);
    if (y < window.innerHeight) {
      if (ids.has(actual)) history.replaceState(history.state, '', window.location.pathname + window.location.search);
      return;
    }
    // Lo que tapa la cabecera no cuenta como leído: la misma holgura del salto nativo.
    const holgura = parseFloat(getComputedStyle(raiz.documentElement).scrollPaddingTop) || 0;
    let leyendo = '';
    for (const c of capitulos) if (inicioDe(c, holgura) <= y + 2) leyendo = c.id;
    if (leyendo && leyendo !== actual) history.replaceState(history.state, '', `#${leyendo}`);
  };
  window.addEventListener('scroll', () => {
    if (pendiente) return;
    pendiente = true;
    requestAnimationFrame(escribir);
  }, { passive: true });
}
