/**
 * Los campos de contraseña de la entrada, el registro y la cuenta, con un solo
 * comportamiento (AA3; cold review F6/F7). Lo enciende el guion de la cabecera.
 *
 * - `button[data-ver-contrasena="id"]`: muestra u oculta ese campo. Viene `hidden` del
 *   servidor (sin JavaScript no haría nada). Su nombre accesible es fijo y dice qué
 *   campo controla (`aria-label`, p. ej. «Mostrar la contraseña actual»); el estado lo
 *   lleva `aria-pressed`. Cambiar las dos cosas a la vez se leería como «Ocultar,
 *   pulsado»: una doble negación. El texto visible sí alterna (`data-mostrar/-ocultar`).
 * - `input[data-igual-que="id"]`: «repite la contraseña» avisa antes de enviar si no
 *   coincide (`setCustomValidity`, con `data-no-coincide`). El servidor lo comprueba igual.
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
      const texto = ver ? boton.dataset.ocultar : boton.dataset.mostrar;
      if (texto) boton.textContent = texto;
      campo.focus();
    });
  });
}

export function enlazarIgualQue(raiz: Document = document) {
  raiz.querySelectorAll<HTMLInputElement>('input[data-igual-que]').forEach((repetida) => {
    const original = raiz.getElementById(repetida.dataset.igualQue ?? '');
    if (!(original instanceof HTMLInputElement)) return;
    const comprobar = () =>
      repetida.setCustomValidity(repetida.value && repetida.value !== original.value ? repetida.dataset.noCoincide ?? 'Mismatch' : '');
    repetida.addEventListener('input', comprobar);
    original.addEventListener('input', comprobar);
  });
}
