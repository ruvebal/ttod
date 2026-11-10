// F22 (Phase AA2): whether the session cookie carries `Secure`.
//
// Driven by COOKIE_SECURE at runtime, not by `import.meta.env.PROD`. A production build served over
// plain HTTP on a classroom LAN must still be able to set its cookie, because browsers drop Secure
// cookies on http:// pages.
//   COOKIE_SECURE=true  → always Secure (use behind an external TLS proxy, e.g. Traefik).
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
