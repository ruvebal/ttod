import type { AuthLoginResponse, AuthUser, SessionRole } from '../types/domain';

export const SESSION_COOKIE_NAME = 'ttod_session';

const BACKEND_URL = import.meta.env.BACKEND_URL ?? 'http://backend:8000';
const SESSION_ROLES: readonly SessionRole[] = ['student', 'reviewer', 'instructor'];

export type LoginResult =
  | { ok: true; sessionToken: string; expiresIn: number }
  | { ok: false; reason: 'credentials' | 'service' | 'throttled' };

export type RegisterResult =
  | { ok: true; sessionToken: string; expiresIn: number }
  | { ok: false; reason: 'taken' | 'invalid' | 'service' | 'throttled' };

function isAuthUser(value: unknown): value is AuthUser {
  if (typeof value !== 'object' || value === null) return false;
  const candidate = value as Partial<AuthUser>;
  return (
    typeof candidate.id === 'string' &&
    typeof candidate.email === 'string' &&
    Array.isArray(candidate.roles) &&
    candidate.roles.every((role) => SESSION_ROLES.includes(role)) &&
    (candidate.display_name === undefined || typeof candidate.display_name === 'string')
  );
}

function readSessionToken(request: Request): string | null {
  const cookieHeader = request.headers.get('cookie');
  if (!cookieHeader) return null;
  for (const pair of cookieHeader.split(';')) {
    const separator = pair.indexOf('=');
    if (separator === -1) continue;
    if (pair.slice(0, separator).trim() === SESSION_COOKIE_NAME) {
      return pair.slice(separator + 1).trim() || null;
    }
  }
  return null;
}

function readIssuedSession(value: unknown): { sessionToken: string; expiresIn: number } | null {
  const login = value as Partial<AuthLoginResponse>;
  if (
    typeof login.session_token !== 'string' || login.session_token.length === 0 ||
    login.token_type !== 'Session' ||
    typeof login.expires_in !== 'number' || login.expires_in <= 0 ||
    !isAuthUser(login.user)
  ) return null;
  return { sessionToken: login.session_token, expiresIn: login.expires_in };
}

function localeOf(request: Request): 'en' | 'es' {
  return new URL(request.url).pathname.split('/')[1] === 'es' ? 'es' : 'en';
}

// F3 (Phase AA2): login and register reach the backend from this server, so without help every
// attempt would look like it came from the frontend container. Forward the address Caddy saw
// (left-most X-Forwarded-For hop), falling back to the socket address.
export function clientAddressOf(request: Request, socketAddress?: string): string | undefined {
  const forwarded = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim();
  return forwarded || socketAddress || undefined;
}

function backendHeaders(clientAddress?: string): Record<string, string> {
  const headers: Record<string, string> = { accept: 'application/json', 'content-type': 'application/json' };
  if (clientAddress) headers['x-forwarded-for'] = clientAddress;
  return headers;
}

export async function loginWithBackend(email: string, password: string, clientAddress?: string): Promise<LoginResult> {
  if (email.trim() === '' || password === '') return { ok: false, reason: 'credentials' };

  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: backendHeaders(clientAddress),
      body: JSON.stringify({ email, password })
    });
    if (response.status === 401 || response.status === 422) return { ok: false, reason: 'credentials' };
    if (response.status === 429) return { ok: false, reason: 'throttled' };
    if (!response.ok) return { ok: false, reason: 'service' };

    const session = readIssuedSession(await response.json());
    return session ? { ok: true, ...session } : { ok: false, reason: 'service' };
  } catch (error) {
    console.error('The authentication service could not complete the login request.', error);
    return { ok: false, reason: 'service' };
  }
}

export async function registerWithBackend(email: string, password: string, clientAddress?: string): Promise<RegisterResult> {
  if (email.trim() === '' || password === '') return { ok: false, reason: 'invalid' };

  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/auth/register`, {
      method: 'POST',
      headers: backendHeaders(clientAddress),
      body: JSON.stringify({ email: email.trim(), password })
    });
    if (response.status === 409) return { ok: false, reason: 'taken' };
    if (response.status === 429) return { ok: false, reason: 'throttled' };
    if (response.status === 422) return { ok: false, reason: 'invalid' };
    if (!response.ok) return { ok: false, reason: 'service' };

    const session = readIssuedSession(await response.json());
    return session ? { ok: true, ...session } : { ok: false, reason: 'service' };
  } catch (error) {
    console.error('The authentication service could not complete the sign-up request.', error);
    return { ok: false, reason: 'service' };
  }
}

export async function getSessionUser(request: Request): Promise<AuthUser | null> {
  const sessionToken = readSessionToken(request);
  if (!sessionToken) return null;
  try {
    // La firma solo la comprueba el backend: Astro reenvía la cookie y no confía en su contenido.
    const response = await fetch(`${BACKEND_URL}/api/v1/auth/session`, {
      headers: { accept: 'application/json', cookie: `${SESSION_COOKIE_NAME}=${sessionToken}` }
    });
    if (!response.ok) return null;
    const user: unknown = await response.json();
    return isAuthUser(user) ? user : null;
  } catch (error) {
    // Si el backend no responde se deniega el acceso en lugar de dejar pasar la petición.
    console.error('Unable to verify the server-side session.', error);
    return null;
  }
}

/**
 * Cierra la sesión en el backend, que es quien la guarda (Redis): borrar solo la
 * cookie dejaría viva una sesión que se podría reutilizar. Devuelve `false` si el
 * backend no la pudo revocar, para que la página lo diga en vez de fingir que sí.
 */
export async function logoutWithBackend(request: Request): Promise<boolean> {
  const sessionToken = readSessionToken(request);
  if (!sessionToken) return true;
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/auth/logout`, {
      method: 'POST',
      headers: { accept: 'application/json', cookie: `${SESSION_COOKIE_NAME}=${sessionToken}` }
    });
    return response.ok;
  } catch (error) {
    console.error('The authentication service could not revoke the session.', error);
    return false;
  }
}

/**
 * La ruta a la que volver tras entrar. Solo rutas de este mismo sitio («/algo»):
 * «//otro.com», «/\\otro.com» o una URL completa serían una redirección abierta.
 */
export function safeNextPath(value: unknown, locale: 'en' | 'es'): string {
  const fallback = `/${locale}/account/`;
  if (typeof value !== 'string' || !value.startsWith('/') || value.startsWith('//')) return fallback;
  if (/[\\\u0000-\u001f]/.test(value)) return fallback;
  if (/^\/(en|es)\/(login|register)\/?(\?|$)/.test(value)) return fallback;
  return value;
}

// Las guardas devuelven el Response en vez de lanzarlo: en Astro 5 un `throw` de un
// Response desde el frontmatter termina en un 500, no en la redirección esperada.
export async function requireUser(request: Request): Promise<AuthUser | Response> {
  const user = await getSessionUser(request);
  if (user) return user;
  const { pathname, search } = new URL(request.url);
  // Tras entrar se vuelve aquí: el login lee `next` y solo acepta rutas de este sitio.
  const next = encodeURIComponent(pathname + search);
  return new Response(null, { status: 302, headers: { location: `/${localeOf(request)}/login/?next=${next}` } });
}

export async function requireRole(
  request: Request,
  allowed: SessionRole | readonly SessionRole[]
): Promise<AuthUser | Response> {
  const user = await requireUser(request);
  if (user instanceof Response) return user;

  const allowedRoles: readonly SessionRole[] = typeof allowed === 'string' ? [allowed] : allowed;
  if (user.roles.some((role) => allowedRoles.includes(role))) return user;
  return paginaProhibida(localeOf(request));
}

/**
 * 403 en el idioma de la ruta (AA3, F35), no un «Forbidden» en texto plano. Las páginas
 * que quieren la cabecera y el pie del sitio lo pintan ellas (la cola de revisión);
 * esto es lo que recibe cualquier otra ruta protegida.
 */
export const PROHIBIDO = {
  es: { title: 'Sin permiso', message: 'Esta página es solo para el equipo de revisión. Tu cuenta no tiene ese rol.', back: 'Volver a mi cuenta' },
  en: { title: 'Not allowed', message: 'This page is for the review team only. Your account does not have that role.', back: 'Back to my account' },
} as const;

export function paginaProhibida(locale: 'en' | 'es'): Response {
  const t = PROHIBIDO[locale];
  const html = `<!doctype html><html lang="${locale}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">` +
    `<title>${t.title} · TTOD</title><link rel="stylesheet" href="/visual-system/tokens.css"></head>` +
    `<body><main id="ttod-main"><h1>${t.title}</h1><p>${t.message}</p><p><a href="/${locale}/account/">${t.back}</a></p></main></body></html>`;
  return new Response(html, { status: 403, headers: { 'content-type': 'text/html; charset=utf-8' } });
}

// --- La sección «Usuario» de la cuenta (AA3, F55): la BFF de los endpoints de AA2. ---
// Cada función reenvía solo la cookie de sesión y devuelve un resultado con motivo,
// para que la página diga en su idioma qué ha pasado.

export type PasswordChangeResult =
  | { ok: true; sessionToken: string; expiresIn: number }
  | { ok: false; reason: 'wrong-current' | 'invalid' | 'throttled' | 'signed-out' | 'service' };

/** POST /api/v1/auth/password: el backend rota la sesión de quien llama y devuelve la cookie nueva. */
export async function changePasswordWithBackend(
  request: Request, currentPassword: string, newPassword: string, revokeOthers: boolean,
): Promise<PasswordChangeResult> {
  const sessionToken = readSessionToken(request);
  if (!sessionToken) return { ok: false, reason: 'signed-out' };
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/auth/password`, {
      method: 'POST',
      headers: { ...backendHeaders(clientAddressOf(request)), 'content-type': 'application/json', cookie: `${SESSION_COOKIE_NAME}=${sessionToken}` },
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword, revoke_others: revokeOthers }),
    });
    // 401 con sesión válida es la contraseña actual: la sesión la comprueba antes `requireUser`.
    if (response.status === 401 || response.status === 403) return { ok: false, reason: 'wrong-current' };
    if (response.status === 422 || response.status === 400) return { ok: false, reason: 'invalid' };
    if (response.status === 429) return { ok: false, reason: 'throttled' };
    if (!response.ok) return { ok: false, reason: 'service' };
    const session = readIssuedSession(await response.json());
    return session ? { ok: true, ...session } : { ok: false, reason: 'service' };
  } catch (error) {
    console.error('The authentication service could not change the password.', error);
    return { ok: false, reason: 'service' };
  }
}

export type ProfileResult = { ok: true } | { ok: false; reason: 'invalid' | 'signed-out' | 'service' };

/** PATCH /api/v1/auth/profile {display_name}. */
export async function updateProfileWithBackend(request: Request, displayName: string): Promise<ProfileResult> {
  const sessionToken = readSessionToken(request);
  if (!sessionToken) return { ok: false, reason: 'signed-out' };
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/auth/profile`, {
      method: 'PATCH',
      headers: { ...backendHeaders(clientAddressOf(request)), 'content-type': 'application/json', cookie: `${SESSION_COOKIE_NAME}=${sessionToken}` },
      body: JSON.stringify({ display_name: displayName }),
    });
    if (response.status === 422 || response.status === 400) return { ok: false, reason: 'invalid' };
    if (response.status === 401) return { ok: false, reason: 'signed-out' };
    return response.ok ? { ok: true } : { ok: false, reason: 'service' };
  } catch (error) {
    console.error('The authentication service could not update the profile.', error);
    return { ok: false, reason: 'service' };
  }
}

/** POST /api/v1/auth/logout-all: cierra todas las sesiones, también la de quien llama. */
export async function logoutEverywhereWithBackend(request: Request): Promise<boolean> {
  const sessionToken = readSessionToken(request);
  if (!sessionToken) return true;
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/auth/logout-all`, {
      method: 'POST',
      headers: { ...backendHeaders(clientAddressOf(request)), accept: 'application/json', cookie: `${SESSION_COOKIE_NAME}=${sessionToken}` },
    });
    return response.ok;
  } catch (error) {
    console.error('The authentication service could not close every session.', error);
    return false;
  }
}
