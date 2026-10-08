import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { JSDOM } from 'jsdom';
import { describe, expect, it, vi } from 'vitest';

import type { WisdomEntry } from '../types/domain';

const { fetchWisdom } = vi.hoisted(() => ({ fetchWisdom: vi.fn() }));

vi.mock('../content/wisdom', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../content/wisdom')>()),
  fetchWisdom,
}));

import IndexRoute from '../pages/[locale]/wisdom/index.astro';
import SlugRoute from '../pages/[locale]/wisdom/[slug].astro';
import SectionRoute from '../pages/[locale]/wisdom/sections/[section].astro';

const entry: WisdomEntry = {
  id: 'arch-001', section: 'architecture', level: 'advanced', tags: ['boundaries'],
  text: 'The module that knows its boundaries serves the whole.',
  teaches: 'Boundaries', related: [], origin: 'human', lang: 'en',
  rights: { license: 'CC-BY-NC-SA-4.0', holder: 'ruvebal@crea-comm.net' },
};

const render = async (Route: Parameters<AstroContainer['renderToString']>[0], path: string, params: Record<string, string>) => {
  const container = await AstroContainer.create();
  const html = await container.renderToString(Route, { params, request: new Request(`http://localhost${path}`) });
  const main = new JSDOM(html).window.document.querySelector('main');
  if (!main) throw new Error('route rendered no <main>');
  return main;
};

const crumbTexts = (main: Element) => [...main.querySelectorAll('.ttod-breadcrumbs li')].map((li) => li.textContent?.trim());
const crumbLinks = (main: Element) => [...main.querySelectorAll('.ttod-breadcrumbs li a')].map((a) => a.getAttribute('href'));

describe('breadcrumb hierarchy across content routes', () => {
  it('index: a single, current "Wisdom" crumb with no link', async () => {
    fetchWisdom.mockResolvedValue([entry]);
    const main = await render(IndexRoute, '/en/wisdom/', { locale: 'en' });
    const crumbs = main.querySelectorAll('.ttod-breadcrumbs li');
    expect(crumbTexts(main)).toEqual(['Wisdom']);
    expect(crumbs[0].getAttribute('aria-current')).toBe('page');
    expect(crumbLinks(main)).toEqual([]);
  });

  it('facet route: Wisdom (linked) › raw facet value (current)', async () => {
    fetchWisdom.mockResolvedValue([entry]);
    const main = await render(SectionRoute, '/en/wisdom/sections/architecture/', { locale: 'en', section: 'architecture' });
    expect(crumbTexts(main)).toEqual(['Wisdom', 'architecture']);
    expect(crumbLinks(main)).toEqual(['/en/wisdom/']);
  });

  it('detail route: Wisdom › section (linked to its facet) › quote id (current)', async () => {
    fetchWisdom.mockResolvedValue([entry]);
    const main = await render(SlugRoute, '/en/wisdom/arch-001/', { locale: 'en', slug: 'arch-001' });
    expect(crumbTexts(main)).toEqual(['Wisdom', 'architecture', 'arch-001']);
    expect(crumbLinks(main)).toEqual(['/en/wisdom/', '/en/wisdom/sections/architecture/']);
  });

  it('detail route, unknown slug: Wisdom › translated "not found", no crash', async () => {
    fetchWisdom.mockResolvedValue([entry]);
    const main = await render(SlugRoute, '/en/wisdom/does-not-exist/', { locale: 'en', slug: 'does-not-exist' });
    expect(crumbTexts(main)).toEqual(['Wisdom', 'Wisdom entry not found']);
  });

  it('keeps the /es/ prefix on every linked crumb', async () => {
    fetchWisdom.mockResolvedValue([entry]);
    const main = await render(SlugRoute, '/es/wisdom/arch-001/', { locale: 'es', slug: 'arch-001' });
    expect(crumbLinks(main)).toEqual(['/es/wisdom/', '/es/wisdom/sections/architecture/']);
  });
});
