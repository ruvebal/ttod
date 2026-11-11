import type { APIRoute } from 'astro';
import { isLocale } from '../../content/wisdom';
import { SESSION_COOKIE_NAME, logoutWithBackend } from '../../lib/auth.server';
import { atributosSesion } from '../../lib/cookie-security';

export const prerender = false;

// Solo POST: un enlace o una imagen de otra web no pueden cerrar la sesión de nadie
// (Astro además comprueba el origen de los formularios).
export const POST: APIRoute = async ({ params, request, cookies, redirect }) => {
  const locale = params.locale;
  if (!isLocale(locale)) return new Response(null, { status: 404 });

  if (!(await logoutWithBackend(request))) {
    // La sesión sigue viva en el backend: se conserva la cookie para poder reintentarlo
    // y la cuenta lo explica, en vez de dar por cerrada una sesión que no lo está.
    return redirect(`/${locale}/account/?logout=failed`, 303);
  }

  // Mismos atributos que al ponerla (F37): sobre todo la misma ruta, que es lo que la identifica.
  cookies.delete(SESSION_COOKIE_NAME, atributosSesion(request));
  return redirect(`/${locale}/`, 303);
};

export const ALL: APIRoute = () =>
  new Response('Method Not Allowed', { status: 405, headers: { allow: 'POST' } });
