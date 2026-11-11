// F22 (Phase AA2): whether the session cookie carries `Secure`.
//
// Driven by COOKIE_SECURE at runtime, not by `import.meta.env.PROD`. A production build served over
// plain HTTP on a classroom LAN must still be able to set its cookie, because browsers drop Secure
// cookies on http:// pages.
//   COOKIE_SECURE=true  → always Secure. For a deployment behind an external TLS proxy (Traefik):
//                         that also needs Caddy to trust the proxy (`trusted_proxies`, AA5 lane B /
//                         F2), or Astro sees http:// and refuses the https:// form POST with 403.
//                         Until then TTOD is an HTTP-only classroom stack.
//   COOKIE_SECURE=false → never Secure (local HTTP only).
//   COOKIE_SECURE=auto  → Secure when the request reached the edge over HTTPS (the default). Caddy
//                         overwrites X-Forwarded-Proto from untrusted clients, so a client cannot
//                         spoof it.
export type CookieSecureMode = 'auto' | 'true' | 'false';

export function cookieSecureMode(raw: string | undefined = process.env.COOKIE_SECURE): CookieSecureMode {
  const value = (raw ?? '').trim().toLowerCase();
  if (value === 'true' || value === '1') return 'true';
  if (value === 'false' || value === '0') return 'false';
  return 'auto';
}

export function cookieSecure(request: Request, mode: CookieSecureMode = cookieSecureMode()): boolean {
  if (mode === 'true') return true;
  if (mode === 'false') return false;
  const forwarded = request.headers.get('x-forwarded-proto')?.split(',')[0]?.trim().toLowerCase();
  if (forwarded) return forwarded === 'https';
  return new URL(request.url).protocol === 'https:';
}

/**
 * Los atributos de la cookie de sesión, en un solo sitio (AA3, F37). El navegador
 * reconoce una cookie por nombre + dominio + ruta: es el mismo `path: '/'` lo que hace
 * que el borrado alcance a la que puso la entrada. `HttpOnly`, `SameSite` y `Secure` no
 * cuentan para eso; se repiten para que poner y borrar se lean igual y no diverjan.
 */
export function atributosSesion(request: Request) {
  return { httpOnly: true, sameSite: 'lax' as const, secure: cookieSecure(request), path: '/' };
}
