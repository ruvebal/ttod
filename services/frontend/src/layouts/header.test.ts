import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { JSDOM } from 'jsdom';
import { describe, expect, it } from 'vitest';

import Page from './Page.astro';
import { enlaceEntrar, esActual } from '../lib/enlaces-cuenta';
import type { AuthUser } from '../types/domain';

// AA3 header contract (F7, F9, F10, F11, F38, F56): rendered from the layout with the session the page
// already knows (`usuario`), so no backend is involved.
const render = async (path: string, lang: 'en' | 'es', usuario: AuthUser | null) => {
  const container = await AstroContainer.create();
  const html = await container.renderToString(Page, {
    props: { lang, title: 't', usuario },
    request: new Request(`http://localhost${path}`),
    slots: { default: '<main id="ttod-main"><p>x</p></main>' },
  });
  return new JSDOM(html).window.document;
};
const ana: AuthUser = { id: 'u1', email: 'ana@example.test', roles: ['student'] };
const primary = (doc: Document) => [...doc.querySelectorAll('#ttod-site-nav a:not(.ttod-solo-panel)')].map((a) => a.getAttribute('href'));
const utility = (doc: Document) => doc.querySelector('#ttod-site-header .ttod-utility')!;

describe('header, signed out', () => {
  it('has four primary links and no Home in the bar (es and en)', async () => {
    expect(primary(await render('/es/', 'es', null))).toEqual(['/es/wisdom/', '/es/graph/', '/es/oracle/', '/es/docs/']);
    expect(primary(await render('/en/', 'en', null))).toEqual(['/en/wisdom/', '/en/graph/', '/en/oracle/', '/en/docs/']);
  });
  it('offers Entrar back to this page, and no Library', async () => {
    const doc = await render('/es/wisdom/tags/koan/?p=2', 'es', null);
    const links = [...utility(doc).querySelectorAll('a')];
    expect(links.find((a) => a.textContent === 'Entrar')?.getAttribute('href')).toBe('/es/login/?next=%2Fes%2Fwisdom%2Ftags%2Fkoan%2F%3Fp%3D2');
    expect(doc.querySelector('#ttod-site-header a[href="/es/library/"]')).toBeNull();
  });
  it('marks the section current by prefix (F38)', async () => {
    const doc = await render('/en/wisdom/sections/architecture/', 'en', null);
    expect(doc.querySelector('#ttod-site-nav a[aria-current="page"]')?.getAttribute('href')).toBe('/en/wisdom/');
  });
  it('the language switch is a quiet code with hreflang and lang', async () => {
    const sw = (await render('/es/wisdom/', 'es', null)).querySelector('.ttod-lang-switch')!;
    expect(sw.textContent).toBe('EN');
    expect(sw.getAttribute('hreflang')).toBe('en');
    expect(sw.getAttribute('lang')).toBe('en');
    expect(sw.getAttribute('aria-label')).toContain('EN');
    expect(sw.hasAttribute('data-cambio-idioma')).toBe(true);
  });
  it('the skip link targets the main landmark (F11)', async () => {
    const doc = await render('/es/', 'es', null);
    expect(doc.querySelector('.ttod-skip-link')?.getAttribute('href')).toBe('#ttod-main');
    expect(doc.querySelector('main#ttod-main')).not.toBeNull();
    expect(doc.getElementById('ttod-aviso')).not.toBeNull();
  });
});

describe('header, signed in', () => {
  it('shows Library and the account, never Entrar', async () => {
    const doc = await render('/es/wisdom/', 'es', ana);
    expect(utility(doc).querySelector('a[href="/es/library/"]')?.textContent).toBe('Biblioteca');
    expect(utility(doc).querySelector('a[href="/es/account/"]')?.textContent).toBe('Cuenta');
    expect(doc.querySelector('#ttod-site-header a[href^="/es/login/"]')).toBeNull();
  });
  it('the account link shows display_name once set (F55)', async () => {
    const doc = await render('/en/account/', 'en', { ...ana, display_name: 'Ada' });
    const cuenta = utility(doc).querySelector('a[href="/en/account/"]');
    expect(cuenta?.textContent).toBe('Ada');
    expect(cuenta?.getAttribute('aria-current')).toBe('page');
  });
});

describe('footer sign-in (F9)', () => {
  it('never sends you back to the login page itself', async () => {
    const onLogin = await render('/es/login/', 'es', null);
    expect(onLogin.querySelector('.pie a[href^="/es/login/"]')?.getAttribute('href')).toBe('/es/login/');
    const withNext = await render('/es/login/?next=%2Fes%2Flibrary%2F', 'es', null);
    expect(withNext.querySelector('.pie a[href^="/es/login/"]')?.getAttribute('href')).toBe('/es/login/?next=%2Fes%2Flibrary%2F');
  });
  it('becomes My account when signed in', async () => {
    const doc = await render('/en/wisdom/', 'en', ana);
    expect(doc.querySelector('.pie a[href="/en/account/"]')?.textContent).toBe('My account');
  });
});

describe('enlaceEntrar / esActual', () => {
  const at = (p: string) => new URL(`http://localhost${p}`);
  it('drops an unsafe or self-referencing next on the access pages', () => {
    expect(enlaceEntrar('es', at('/es/register/?next=%2Fes%2Flogin%2F'))).toBe('/es/login/');
    expect(enlaceEntrar('es', at('/es/login/?next=%2F%2Fevil.example'))).toBe('/es/login/');
    expect(enlaceEntrar('en', at('/en/oracle/'))).toBe('/en/login/?next=%2Fen%2Foracle%2F');
  });
  it('matches by prefix', () => {
    expect(esActual('/es/wisdom/wis-034/', '/es/wisdom/')).toBe(true);
    expect(esActual('/es/graph/plano/', '/es/graph/')).toBe(true);
    expect(esActual('/es/', '/es/wisdom/')).toBe(false);
  });
});
