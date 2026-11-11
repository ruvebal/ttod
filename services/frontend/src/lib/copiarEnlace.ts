/**
 * «Copiar enlace» (LOCATORS §7): un `<a href data-copiar>` de verdad. Sin
 * JavaScript es un enlace que funciona; con él, el clic copia la dirección
 * absoluta y lo anuncia en una región educada: la más cercana marcada
 * `[data-aviso-local]` (el diálogo de la cita al azar tiene la suya, porque un
 * diálogo modal deja fuera lo de detrás) o `#ttod-aviso` de `Page.astro`.
 *
 * El `href` puede ser un fragmento de esta página (`#wis-034`, y entonces la
 * dirección también se escribe en la barra) o la ruta de otra (`/es/wisdom/wis-034/`).
 *
 * Sin portapapeles (un sitio servido por HTTP con un nombre de la red de clase no
 * es «contexto seguro» y el navegador no lo da): el fragmento se escribe en la
 * barra y se anuncia que se copie de ahí, en vez de no hacer nada en silencio.
 */
export function direccionDe(enlace: HTMLAnchorElement, actual: Pick<Location, 'href'> = location): string {
  return new URL(enlace.getAttribute('href') ?? '', actual.href).href;
}

function anunciar(enlace: Element, raiz: Document, clave: 'copiado' | 'sinPortapapeles') {
  const aviso = enlace.closest('dialog')?.querySelector<HTMLElement>('[data-aviso-local]') ?? raiz.getElementById('ttod-aviso');
  if (!aviso) return;
  const texto = clave === 'copiado' ? aviso.dataset.copiado ?? 'Link copied' : aviso.dataset.sinPortapapeles ?? 'Copy the address from the address bar';
  // Vaciar y volver a escribir: el mismo texto dos veces seguidas no se repite en voz alta.
  aviso.textContent = '';
  window.setTimeout(() => { aviso.textContent = texto; }, 50);
}

export function enlazarCopiarEnlace(raiz: Document = document) {
  raiz.addEventListener('click', (evento) => {
    const enlace = (evento.target as Element | null)?.closest?.('a[data-copiar]');
    if (!(enlace instanceof HTMLAnchorElement)) return;
    evento.preventDefault();
    const direccion = direccionDe(enlace);
    const mismaPagina = (enlace.getAttribute('href') ?? '').startsWith('#');
    const escribirEnLaBarra = () => { if (mismaPagina) history.replaceState(history.state, '', direccion); };
    if (!navigator.clipboard) {
      escribirEnLaBarra();
      if (!mismaPagina) window.location.href = direccion;
      else anunciar(enlace, raiz, 'sinPortapapeles');
      return;
    }
    navigator.clipboard.writeText(direccion).then(
      () => { escribirEnLaBarra(); anunciar(enlace, raiz, 'copiado'); },
      () => { escribirEnLaBarra(); anunciar(enlace, raiz, 'sinPortapapeles'); },
    );
  });
}
