/**
 * Mostrar u ocultar una contraseña (AA3, F55). Los botones vienen `hidden` del
 * servidor: sin JavaScript no harían nada, así que no se enseñan. Con él, cada
 * `[data-ver-contrasena="id"]` cambia su campo entre `password` y `text`, y lo dice
 * con `aria-pressed` y con su propia etiqueta.
 */
export function enlazarVerContrasena(raiz: Document = document) {
  raiz.querySelectorAll<HTMLButtonElement>('button[data-ver-contrasena]').forEach((boton) => {
    const campo = raiz.getElementById(boton.dataset.verContrasena ?? '');
    if (!(campo instanceof HTMLInputElement)) return;
    boton.hidden = false;
    boton.addEventListener('click', () => {
      const ver = campo.type === 'password';
      campo.type = ver ? 'text' : 'password';
      boton.setAttribute('aria-pressed', String(ver));
      boton.textContent = (ver ? boton.dataset.ocultar : boton.dataset.mostrar) ?? boton.textContent;
    });
  });
}
