import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { loadRenderers } from 'astro:container';
import { getContainerRenderer } from '@astrojs/react';
import { JSDOM } from 'jsdom';
import { afterEach, describe, expect, it, vi } from 'vitest';

import LibraryRoute from '../pages/[locale]/library.astro';
import type { WisdomEntry } from '../types/domain';

// F53 (AA3): the library reads like the wisdom corridor: stele cards with the quote id as anchor and the
// localized section, a saved date, and EmptyState for empty and failed loads.
const quote: WisdomEntry = {
  id: 'arch-060', section: 'architecture', level: 'advanced', tags: ['koan'], text: 'Un límite sin pruebas es un deseo.',
  teaches: 't', related: [], origin: 'human', lang: 'es', rights: { license: 'CC-BY-NC-SA-4.0', holder: 'ruvebal@crea-comm.net' },
};
const student = { id: 'u1', email: 'ana@example.test', roles: ['student'] };
afterEach(() => vi.restoreAllMocks());
const backend = (routes: Record<string, unknown>) => vi.spyOn(global, 'fetch').mockImplementation(async (input) => {
  const url = String(input);
  const hit = Object.entries(routes).find(([path]) => url.includes(path));
  if (!hit) return new Response(null, { status: 404 });
  return hit[1] === 'down' ? new Response(null, { status: 503 }) : Response.json(hit[1]);
});
const render = async (locale: 'en' | 'es') => {
  const container = await AstroContainer.create({ renderers: await loadRenderers([getContainerRenderer()]) });
  const response = await container.renderToResponse(LibraryRoute, {
    params: { locale }, request: new Request(`http://localhost/${locale}/library/`, { headers: { cookie: 'ttod_session=t' } }),
  });
  return { status: response.status, main: new JSDOM(await response.text()).window.document.querySelector('main')! };
};

describe('library layout (F53)', () => {
  it('renders each saved quote as a stele card with its id, localized section and saved date', async () => {
    backend({ '/auth/session': student, '/favorites': [{ userId: 'u1', quoteId: 'arch-060', savedAt: '2026-11-01T09:00:00Z' }], '/wisdom/sample': [quote] });
    const { status, main } = await render('es');
    expect(status).toBe(200);
    expect(main.id).toBe('ttod-main');
    const card = main.querySelector('article.piedra#arch-060')!;
    expect(card).not.toBeNull();
    expect(card.querySelector('.piedra-seccion')?.textContent?.trim()).toBe('Arquitectura');
    expect(main.querySelector('time')?.getAttribute('datetime')).toBe('2026-11-01T09:00:00.000Z');
    expect(main.querySelector('.biblioteca-pie button')?.textContent).toBe('Quitar de favoritos');
  });
  it('an empty library is an EmptyState pointing to the wisdom (en)', async () => {
    backend({ '/auth/session': student, '/favorites': [], '/wisdom/sample': [quote] });
    const { status, main } = await render('en');
    expect(status).toBe(200);
    expect(main.querySelector('.ttod-empty h2')?.textContent).toBe('Your library is empty');
    expect(main.querySelector('.ttod-empty a')?.getAttribute('href')).toBe('/en/wisdom/');
  });
  it('a failed load is a 503 with an alerting EmptyState, not "you saved nothing"', async () => {
    backend({ '/auth/session': student, '/favorites': 'down', '/wisdom/sample': [quote] });
    const { status, main } = await render('es');
    expect(status).toBe(503);
    expect(main.querySelector('.ttod-empty[role="alert"]')).not.toBeNull();
    expect(main.textContent).not.toContain('Todavía no has guardado');
  });
});
