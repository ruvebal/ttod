/**
 * Server-only session helpers — FE I `session.server.js` ported to Astro frontmatter.
 *
 * Import this file ONLY from page frontmatter (the SSR loader-equivalent).
 * Islands and components must never read the session cookie.
 */
import type { User, UserRole } from '../types/domain';

if (import.meta.env.SSR === false) {
  throw new Error('auth.server.ts is server-only. Call requireUser/requireRole from Astro frontmatter, never from a component.');
}

const backend = import.meta.env.BACKEND_URL ?? 'http://backend:8000';

function cookieHeader(request: Request): string {
  return request.headers.get('cookie') ?? '';
}

function copySetCookies(from: Response, to: Headers): void {
  const cookies =
    typeof from.headers.getSetCookie === 'function' ? from.headers.getSetCookie() : [];
  const fallback = from.headers.get('set-cookie');
  const list = cookies.length > 0 ? cookies : fallback ? [fallback] : [];
  for (const cookie of list) {
    to.append('Set-Cookie', cookie);
  }
}

/** Relative path only — blocks open redirects (`https://…`, `//evil`). */
export function safeNext(value: string | null | undefined, fallback: string): string {
  if (!value || !value.startsWith('/') || value.startsWith('//') || value.startsWith('/\\')) {
    return fallback;
  }
  return value;
}

function redirectResponse(location: string, status = 302, cookies?: Response): Response {
  const headers = new Headers({ Location: location });
  if (cookies) copySetCookies(cookies, headers);
  return new Response(null, { status, headers });
}

export async function getOptionalUser(request: Request): Promise<User | null> {
  const cookie = cookieHeader(request);
  if (!cookie) return null;
  const response = await fetch(`${backend}/api/v1/auth/me`, {
    headers: { accept: 'application/json', cookie },
    cache: 'no-store',
  });
  if (!response.ok) return null;
  const payload: unknown = await response.json();
  if (!payload || typeof payload !== 'object' || !('email' in payload) || !('id' in payload)) {
    return null;
  }
  return payload as User;
}

/**
 * Loader-side guard. React Router throws `redirect()`; Astro pages must
 * `return` the Response (throwing a Response here becomes a 500).
 */
export async function requireUser(
  request: Request,
  { loginPath = '/en/account/login' }: { loginPath?: string } = {},
): Promise<User | Response> {
  const user = await getOptionalUser(request);
  if (!user) {
    const url = new URL(request.url);
    const search = new URLSearchParams({ from: url.pathname });
    return redirectResponse(`${loginPath}?${search.toString()}`);
  }
  return user;
}

export async function requireRole(
  request: Request,
  role: UserRole,
  options: { loginPath?: string } = {},
): Promise<User | Response> {
  const user = await requireUser(request, options);
  if (user instanceof Response) return user;
  if (user.role !== role) {
    return new Response('Forbidden', { status: 403, headers: { 'content-type': 'text/plain; charset=utf-8' } });
  }
  return user;
}

export async function loginWithPassword(
  form: FormData,
  { fallbackNext = '/en/account' }: { fallbackNext?: string } = {},
): Promise<Response> {
  const email = String(form.get('email') ?? '').trim();
  const password = String(form.get('password') ?? '');
  const next = safeNext(String(form.get('next') ?? ''), fallbackNext);
  const response = await fetch(`${backend}/api/v1/auth/login`, {
    method: 'POST',
    headers: { accept: 'application/json', 'content-type': 'application/json' },
    body: JSON.stringify({ email, password }),
    cache: 'no-store',
  });
  if (!response.ok) {
    return new Response(null, { status: 401, headers: { 'x-ttod-auth': 'invalid' } });
  }
  return redirectResponse(next, 303, response);
}

export async function logoutSession(request: Request, loginPath: string): Promise<Response> {
  const response = await fetch(`${backend}/api/v1/auth/logout`, {
    method: 'POST',
    headers: { cookie: cookieHeader(request) },
    cache: 'no-store',
  });
  return redirectResponse(loginPath, 303, response);
}
