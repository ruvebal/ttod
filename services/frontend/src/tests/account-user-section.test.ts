import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { JSDOM } from 'jsdom';
import { afterEach, describe, expect, it, vi } from 'vitest';

import AccountRoute from '../pages/[locale]/account.astro';

// F55 UI (AA3, A35): the User section posts to the account page itself; the page calls AA2's endpoints.
const student = { id: 'u1', email: 'ana@example.test', roles: ['student'] };
afterEach(() => vi.restoreAllMocks());
type Route = { status?: number; body?: unknown };
const backend = (routes: Record<string, Route>) => vi.spyOn(global, 'fetch').mockImplementation(async (input) => {
  const url = String(input);
  if (url.includes('/auth/session')) return Response.json(student);
  const hit = Object.entries(routes).find(([path]) => url.includes(path));
  if (!hit) return new Response(null, { status: 404 });
  const { status = 200, body } = hit[1];
  return body === undefined ? new Response(null, { status }) : Response.json(body, { status });
});
const send = async (locale: 'en' | 'es', fields?: Record<string, string>) => {
  const container = await AstroContainer.create();
  const request = new Request(`http://localhost/${locale}/account/`, fields
    ? { method: 'POST', body: new URLSearchParams(fields), headers: { cookie: 'ttod_session=old', 'content-type': 'application/x-www-form-urlencoded' } }
    : { headers: { cookie: 'ttod_session=old' } });
  const response = await container.renderToResponse(AccountRoute, { params: { locale }, request });
  const html = await response.text();
  return { response, doc: new JSDOM(html).window.document };
};
// The container does not write Astro.cookies into headers; the Node adapter does, from this same jar
// (`Symbol.for('astro.cookies')`, astro/dist/core/cookies/response.js). Read the jar the way it does.
const setCookie = (response: Response) => {
  const jar = Reflect.get(response, Symbol.for('astro.cookies')) as { headers(): Iterable<string> } | undefined;
  return [...(jar?.headers() ?? []), response.headers.get('set-cookie') ?? ''].join('\n');
};
const issued = { session_token: 'new-token', token_type: 'Session', expires_in: 3600, user: student };
const password = (extra: Record<string, string> = {}) => ({ intent: 'password', current_password: 'old-pass-1', new_password: 'new-pass-22', confirm_password: 'new-pass-22', revoke_others: 'on', ...extra });

describe('account User section', () => {
  it('renders #profile #password #sessions with the right autocomplete hints', async () => {
    backend({});
    const { doc } = await send('es');
    for (const id of ['profile', 'password', 'sessions']) expect(doc.getElementById(id)).not.toBeNull();
    expect(doc.querySelector('input[name="current_password"]')?.getAttribute('autocomplete')).toBe('current-password');
    expect(doc.querySelector('input[name="new_password"]')?.getAttribute('autocomplete')).toBe('new-password');
    expect((doc.querySelector('input[name="revoke_others"]') as HTMLInputElement).checked).toBe(true);
    expect(doc.querySelector('button[data-ver-contrasena]')?.hasAttribute('hidden')).toBe(true);
  });
  it('a password change stores the rotated session cookie and redirects with a flash (PRG)', async () => {
    const spy = backend({ '/auth/password': { body: issued } });
    const { response } = await send('es', password());
    expect(response.status).toBe(303);
    expect(response.headers.get('location')).toBe('/es/account/?ok=password#password');
    const cookie = setCookie(response);
    expect(cookie).toContain('ttod_session=new-token');
    expect(cookie).toMatch(/HttpOnly/i);
    expect(cookie).not.toMatch(/Secure/); // plain http://localhost, COOKIE_SECURE=auto (AA2 F22)
    const call = spy.mock.calls.find(([u]) => String(u).includes('/auth/password'))!;
    expect(JSON.parse(String(call[1]?.body))).toEqual({ current_password: 'old-pass-1', new_password: 'new-pass-22', revoke_others: true });
  });
  it('a wrong current password is refused in Spanish, with no new cookie', async () => {
    backend({ '/auth/password': { status: 401 } });
    const { response, doc } = await send('es', password());
    expect(response.status).toBe(401);
    expect(setCookie(response)).not.toContain('ttod_session=');
    expect(doc.querySelector('#password [role="alert"]')?.textContent).toBe('La contraseña actual no es correcta.');
  });
  it('a confirm mismatch never reaches the backend', async () => {
    const spy = backend({ '/auth/password': { body: issued } });
    const { response, doc } = await send('en', password({ confirm_password: 'different-1' }));
    expect(response.status).toBe(400);
    expect(doc.querySelector('#password [role="alert"]')?.textContent).toBe('The two new passwords do not match.');
    expect(spy.mock.calls.some(([u]) => String(u).includes('/auth/password'))).toBe(false);
  });
  it('unchecking the box keeps the other sessions', async () => {
    const spy = backend({ '/auth/password': { body: issued } });
    const fields = password(); delete (fields as Record<string, string>).revoke_others;
    await send('es', fields);
    const call = spy.mock.calls.find(([u]) => String(u).includes('/auth/password'))!;
    expect(JSON.parse(String(call[1]?.body)).revoke_others).toBe(false);
  });
  it('the profile form PATCHes display_name and redirects', async () => {
    const spy = backend({ '/auth/profile': { body: { ...student, display_name: 'Ada' } } });
    const { response } = await send('es', { intent: 'profile', display_name: '  Ada  ' });
    expect(response.status).toBe(303);
    expect(response.headers.get('location')).toBe('/es/account/?ok=profile#profile');
    const call = spy.mock.calls.find(([u]) => String(u).includes('/auth/profile'))!;
    expect(call[1]?.method).toBe('PATCH');
    expect(JSON.parse(String(call[1]?.body))).toEqual({ display_name: 'Ada' });
  });
  it('sign out everywhere calls logout-all, deletes the cookie and goes home', async () => {
    backend({ '/auth/logout-all': { status: 204 } });
    const { response } = await send('en', { intent: 'logout-all' });
    expect(response.status).toBe(303);
    expect(response.headers.get('location')).toBe('/en/');
    expect(setCookie(response)).toMatch(/ttod_session=[^;]*;.*(Max-Age=0|Expires=Thu, 01 Jan 1970)/i);
    expect(setCookie(response)).toMatch(/HttpOnly/i);
  });
});
