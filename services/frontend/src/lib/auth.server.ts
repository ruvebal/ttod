// TODO(Equipo 5): replace this file once their real session gate merges. Tracked upstream:
// PR #54 (shared branch alexx-ivan), #56, #57, #59 — none merged yet, all BEHIND main, zero
// human reviews as of this writing.
//
// Deliberately NOT mirroring lib/auth.ts (the stub their own account.astro/login.astro actually
// import): that file hardcodes a single admin user and sets a cookie named `session`, which does
// not match what their own backend expects. This file instead reimplements the shape of their
// OTHER file, lib/auth.server.ts — unused by any of their pages today, but the one that actually
// matches the real backend contract already shipped in PR #57's `require_session_user`: a
// `ttod_session` cookie or an `Authorization: Bearer` header, carrying either a plain user id or
// JSON claims `{"userId": "..."}`. Picking this shape means that when Equipo 5 fixes their own
// wiring (points account.astro/login.astro at auth.server.ts instead of auth.ts), this file can
// be replaced outright with theirs — same signature, same call sites, nothing else to change.
//
// Never throws, never redirects: T4's own spec asks for an inline "please log in" message, not an
// automatic redirect that could break navigation.
export function requireUser(request: Request): string | null {
  const cookieMatch = request.headers.get('cookie')?.match(/(?:^|;\s*)ttod_session=([^;]+)/);
  const header = request.headers.get('authorization');
  const token = cookieMatch
    ? decodeURIComponent(cookieMatch[1])
    : header?.startsWith('Bearer ')
      ? header.slice('Bearer '.length).trim()
      : null;
  if (!token) return null;

  try {
    const claims = JSON.parse(token) as { userId?: unknown };
    return typeof claims.userId === 'string' && claims.userId.trim() ? claims.userId.trim() : null;
  } catch {
    return token; // same fallback as Equipo 5's own (unused) auth.server.ts
  }
}
