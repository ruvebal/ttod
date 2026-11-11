/**
 * «Copiar enlace» (LOCATORS §7): un `<a href="#id" data-copiar>` de verdad. Sin
 * JavaScript es un ancla que funciona; con él, el clic copia la dirección
 * absoluta (ruta + consulta + fragmento) y lo anuncia en la región educada
 * `#ttod-aviso` de `Page.astro`. Si el portapapeles no deja, el ancla navega.
 */
export function direccionDe(enlace: HTMLAnchorElement, actual: Location = location): string {
  const id = (enlace.getAttribute('href') ?? '').replace(/^#/, '');
  return `${actual.origin}${actual.pathname}${actual.search}#${id}`;
}

export function enlazarCopiarEnlace(raiz: Document = document) {
  raiz.addEventListener('click', (evento) => {
    const enlace = (evento.target as Element | null)?.closest?.('a[data-copiar]');
    if (!(enlace instanceof HTMLAnchorElement) || !navigator.clipboard) return;
    evento.preventDefault();
    const direccion = direccionDe(enlace);
    navigator.clipboard.writeText(direccion).then(
      () => {
        history.replaceState(history.state, '', direccion);
        const aviso = raiz.getElementById('ttod-aviso');
        if (!aviso) return;
        // Vaciar y volver a escribir: el mismo texto dos veces seguidas no se repite en voz alta.
        aviso.textContent = '';
        window.setTimeout(() => { aviso.textContent = aviso.dataset.copiado ?? 'Link copied'; }, 50);
      },
      () => { location.hash = enlace.getAttribute('href') ?? ''; },
    );
  });
}
