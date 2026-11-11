/**
 * El enlace «Entrar» de la cabecera y del pie (AA3, F7/F9): vuelve a donde
 * estabas, salvo que estés en la propia página de entrar o de crear cuenta.
 * Ahí se conserva el `next` que ya traía la dirección (si es de este sitio) o,
 * si no, no se pide ninguno: entrar desde «entrar» no puede devolverte a «entrar».
 */
import { safeNextPath } from './auth.server';

const PAGINA_DE_ACCESO = /^\/(en|es)\/(login|register)\/?$/;

export function enlaceEntrar(lang: 'en' | 'es', url: URL): string {
  const login = `/${lang}/login/`;
  if (PAGINA_DE_ACCESO.test(url.pathname)) {
    const traido = url.searchParams.get('next');
    const seguro = traido ? safeNextPath(traido, lang) : '';
    return seguro && seguro === traido ? `${login}?next=${encodeURIComponent(seguro)}` : login;
  }
  return `${login}?next=${encodeURIComponent(url.pathname + url.search)}`;
}

/** Un enlace de la barra está «aquí» si la ruta actual empieza por él (F38): `/es/wisdom/tags/x/` es Sabiduría. */
export const esActual = (pathname: string, href: string) => pathname === href || pathname.startsWith(href);
