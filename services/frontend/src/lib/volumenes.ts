/**
 * Los volúmenes del armario como sitios a los que se puede enlazar (AA3b, F50;
 * LOCATORS §4). `#volume-{sección}` abre ese `<details>` y lo trae a la vista; un
 * `#wis-034` que cae dentro de un volumen cerrado lo abre también. Abrir o cerrar
 * un volumen reescribe el fragmento con `replaceState`: el botón Atrás no
 * recorre los libros que se han ido hojeando.
 */
export function enlazarVolumenes(raiz: Document = document) {
  const traerDelFragmento = () => {
    const id = decodeURIComponent(location.hash.slice(1));
    if (!id) return;
    const destino = raiz.getElementById(id);
    if (!destino) return;
    const volumen = destino instanceof HTMLDetailsElement ? destino : destino.closest('details');
    if (!volumen) return;
    if (!volumen.open) volumen.open = true;
    requestAnimationFrame(() => destino.scrollIntoView({ block: 'start', inline: 'nearest' }));
  };
  raiz.querySelectorAll<HTMLDetailsElement>('details[id^="volume-"]').forEach((volumen) => {
    volumen.addEventListener('toggle', () => {
      const fragmento = `#${volumen.id}`;
      if (volumen.open && location.hash !== fragmento) history.replaceState(history.state, '', fragmento);
      else if (!volumen.open && location.hash === fragmento) history.replaceState(history.state, '', location.pathname + location.search);
    });
  });
  traerDelFragmento();
  window.addEventListener('hashchange', traerDelFragmento);
}
