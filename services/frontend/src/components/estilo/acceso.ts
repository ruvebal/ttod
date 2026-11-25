import { entintar } from './letras';

/** Comportamiento común de las páginas de entrar y de crear cuenta. */
export function prepararAcceso(): void {
  // El título se entinta letra a letra, como en el oráculo (kit de estilo).
  entintar(document.querySelector('.acceso h1'), { retraso: .15 });

  const form = document.querySelector<HTMLFormElement>('.acceso-form');
  const clave = form?.querySelector<HTMLInputElement>('#password');

  // Mostrar u ocultar la contraseña y el «repite la contraseña» los lleva
  // `lib/campos-clave.ts`, desde el guion de la cabecera (uno para todo el sitio).

  form?.addEventListener('submit', (ev) => {
    const boton = form.querySelector<HTMLButtonElement>('.acceso-entrar');
    if (!boton) return;
    // Un segundo toque no manda el formulario dos veces.
    if (boton.getAttribute('aria-disabled') === 'true') { ev.preventDefault(); return; }
    if (clave) clave.type = 'password';
    boton.setAttribute('aria-disabled', 'true');
    boton.textContent = boton.dataset.busy!;
  });
}
