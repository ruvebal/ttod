import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { JSDOM } from 'jsdom';
import { afterEach, describe, expect, it, vi } from 'vitest';

// AA3 shell hygiene: F34 quote empty state, F35 localized Forbidden, F36 register confirm, F37 logout attrs.
const { pideCorpus } = vi.hoisted(() => ({ pideCorpus: vi.fn() }));
vi.mock('../lib/corpus.server', () => ({ pideCorpus }));

import QuoteRoute from '../pages/[locale]/quote.astro';
import ReviewerRoute from '../pages/[locale]/account/reviewer/index.astro';
import RegisterRoute from '../pages/[locale]/register.astro';
import { requireRole } from '../lib/auth.server';
import { atributosSesion } from '../lib/cookie-security';

afterEach(() => vi.restoreAllMocks());
const student = { id: 'u1', email: 'ana@example.test', roles: ['student'] };
const render = async (Route: Parameters<AstroContainer['renderToResponse']>[0], path: string, locale: 'en' | 'es', init?: RequestInit) => {
  const container = await AstroContainer.create();
  const response = await container.renderToResponse(Route, { params: { locale }, request: new Request(`http://localhost${path}`, init) });
  return { response, doc: new JSDOM(await response.text()).window.document };
};

describe('quote page (F34)', () => {
  it('an empty corpus is a localized EmptyState, not a 500', async () => {
    pideCorpus.mockResolvedValue([]);
    const { response, doc } = await render(QuoteRoute, '/es/quote/', 'es');
    expect(response.status).toBe(200);
    expect(doc.querySelector('main .ttod-empty h2')?.textContent).toBe('Todavía no hay citas');
  });
  it('a corpus that cannot load is a 503 alert', async () => {
    pideCorpus.mockRejectedValue(new Error('down'));
    const { response, doc } = await render(QuoteRoute, '/en/quote/', 'en');
    expect(response.status).toBe(503);
    expect(doc.querySelector('main .ttod-empty[role="alert"]')).not.toBeNull();
  });
});

describe('Forbidden (F35)', () => {
  it('requireRole answers a localized HTML page, not plain "Forbidden"', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(Response.json(student));
    const result = await requireRole(new Request('http://localhost/es/account/reviewer/', { headers: { cookie: 'ttod_session=t' } }), 'reviewer');
    expect(result).toBeInstanceOf(Response);
    const response = result as Response;
    expect(response.status).toBe(403);
    expect(response.headers.get('content-type')).toContain('text/html');
    const body = await response.text();
    expect(body).toContain('lang="es"');
    expect(body).toContain('Sin permiso');
  });
  it('the reviewer queue shows the site shell with the message', async () => {
    vi.spyOn(global, 'fetch').mockResolvedValue(Response.json(student));
    const { response, doc } = await render(ReviewerRoute, '/en/account/reviewer/', 'en', { headers: { cookie: 'ttod_session=t' } });
    expect(response.status).toBe(403);
    expect(doc.getElementById('ttod-site-header')).not.toBeNull();
    expect(doc.querySelector('main h1')?.textContent).toBe('Not allowed');
  });
});

describe('register confirm (F36)', () => {
  it('a mismatch is refused without calling the backend', async () => {
    const spy = vi.spyOn(global, 'fetch').mockResolvedValue(new Response(null, { status: 401 }));
    const body = new URLSearchParams({ email: 'ana@example.test', password: 'una-clave-larga', confirm_password: 'otra-clave-larga' });
    const { response, doc } = await render(RegisterRoute, '/es/register/', 'es', { method: 'POST', body, headers: { 'content-type': 'application/x-www-form-urlencoded' } });
    expect(response.status).toBe(400);
    expect(doc.body.textContent).toContain('Las dos contraseñas no coinciden.');
    expect(spy.mock.calls.some(([u]) => String(u).includes('/auth/register'))).toBe(false);
    expect(doc.querySelector('input[name="confirm_password"]')?.getAttribute('autocomplete')).toBe('new-password');
  });
});

describe('session cookie attributes (F37)', () => {
  // A browser matches a cookie by name + domain + path; `path: '/'` is what makes the delete hit the cookie
  // login set. The other attributes are kept equal so the Set-Cookie that deletes reads like the one that set.
  it('one definition: login sets it, logout deletes it at the same path', () => {
    const attrs = atributosSesion(new Request('http://localhost/es/'));
    expect(attrs).toEqual({ httpOnly: true, sameSite: 'lax', secure: false, path: '/' });
    expect(atributosSesion(new Request('https://ttod.example/es/')).secure).toBe(true);
  });
});
