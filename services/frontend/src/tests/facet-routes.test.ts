import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { JSDOM } from 'jsdom';
import { describe, expect, it, vi } from 'vitest';

import type { WisdomEntry } from '../types/domain';

const { fetchWisdom } = vi.hoisted(() => ({ fetchWisdom: vi.fn() }));

// Only fetchWisdom is faked: frequencies(), labels and isLocale stay real, so these tests exercise
// the reuse the task is actually about instead of a parallel reimplementation.
vi.mock('../content/wisdom', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../content/wisdom')>()),
  fetchWisdom,
}));

import LevelRoute from '../pages/[locale]/wisdom/levels/[level].astro';
import SectionRoute from '../pages/[locale]/wisdom/sections/[section].astro';
import TagRoute from '../pages/[locale]/wisdom/tags/[tag].astro';

const entry = (id: string, section: string, level: WisdomEntry['level'], tags: string[]): WisdomEntry => ({
  id, section, level, tags,
  text: `Aphorism ${id}`,
  teaches: `What ${id} teaches`,
  related: [],
  origin: 'human',
  lang: 'en',
  rights: { license: 'CC-BY-NC-SA-4.0', holder: 'ruvebal@crea-comm.net' },
});

const payload = [
  entry('arch-001', 'architecture', 'advanced', ['boundaries', 'coupling']),
  entry('arch-002', 'architecture', 'beginner', ['boundaries']),
  entry('wis-001', 'wisdom', 'master', ['simplicity']),
];

const render = async (Route: Parameters<AstroContainer['renderToString']>[0], path: string, params: Record<string, string>) => {
  const container = await AstroContainer.create();
  const html = await container.renderToString(Route, {
    params,
    request: new Request(`http://localhost${path}`),
  });
  const main = new JSDOM(html).window.document.querySelector('main');
  if (!main) throw new Error('route rendered no <main>');
  return main;
};

const cardIds = (main: Element) => [...main.querySelectorAll('article.ttod-card')].map((card) => card.querySelector('a')?.textContent?.trim());
const pills = (main: Element) => [...main.querySelectorAll('nav.ttod-clusters a.ttod-pill')].map((pill) => pill.textContent?.replace(/\s+/g, ' ').trim());

describe('wisdom facet routes', () => {
  it('lists only the entries of the requested section', async () => {
    fetchWisdom.mockResolvedValue(payload);
    const main = await render(SectionRoute, '/en/wisdom/sections/architecture/', { locale: 'en', section: 'architecture' });
    expect(cardIds(main)).toEqual(['arch-001', 'arch-002']);
  });

  it('counts sibling facets from the whole payload, not from the filtered slice', async () => {
    fetchWisdom.mockResolvedValue(payload);
    const main = await render(SectionRoute, '/en/wisdom/sections/architecture/', { locale: 'en', section: 'architecture' });
    // 'wisdom (1)' can only appear if frequencies() ran on the unfiltered payload.
    expect(pills(main)).toEqual(['architecture (2)', 'wisdom (1)']);
    expect(main.querySelector('a.ttod-pill[href="/en/wisdom/sections/wisdom/"]')).not.toBeNull();
  });

  it('marks the current facet with aria-current, not with colour alone', async () => {
    fetchWisdom.mockResolvedValue(payload);
    const main = await render(SectionRoute, '/en/wisdom/sections/architecture/', { locale: 'en', section: 'architecture' });
    const current = main.querySelectorAll('a.ttod-pill[aria-current="page"]');
    expect(current).toHaveLength(1);
    expect(current[0].textContent?.replace(/\s+/g, ' ').trim()).toBe('architecture (2)');
  });

  it('filters by tag membership and offers every sibling tag', async () => {
    fetchWisdom.mockResolvedValue(payload);
    const main = await render(TagRoute, '/en/wisdom/tags/boundaries/', { locale: 'en', tag: 'boundaries' });
    expect(cardIds(main)).toEqual(['arch-001', 'arch-002']);
    expect(pills(main)).toEqual(['boundaries (2)', 'coupling (1)', 'simplicity (1)']);
  });

  it('filters by level and offers every sibling level', async () => {
    fetchWisdom.mockResolvedValue(payload);
    const main = await render(LevelRoute, '/en/wisdom/levels/master/', { locale: 'en', level: 'master' });
    expect(cardIds(main)).toEqual(['wis-001']);
    expect(pills(main)).toEqual(['advanced (1)', 'beginner (1)', 'master (1)']);
  });

  it('shows a translated empty state, never a blank page, for a facet with no matches', async () => {
    fetchWisdom.mockResolvedValue(payload);

    const english = await render(SectionRoute, '/en/wisdom/sections/nope/', { locale: 'en', section: 'nope' });
    expect(cardIds(english)).toEqual([]);
    expect(english.querySelector('.ttod-empty')?.textContent).toContain('No English wisdom entry carries this facet yet.');
    expect(english.querySelector('.ttod-empty a')?.getAttribute('href')).toBe('/en/wisdom/');

    const spanish = await render(SectionRoute, '/es/wisdom/sections/nope/', { locale: 'es', section: 'nope' });
    expect(spanish.querySelector('.ttod-empty')?.textContent).toContain('Ninguna entrada de sabiduría en español tiene esta faceta todavía.');
    expect(spanish.querySelector('.ttod-empty a')?.getAttribute('href')).toBe('/es/wisdom/');
  });

  it('keeps the locale prefix on every sibling link', async () => {
    fetchWisdom.mockResolvedValue(payload);
    const main = await render(SectionRoute, '/es/wisdom/sections/architecture/', { locale: 'es', section: 'architecture' });
    const hrefs = [...main.querySelectorAll('nav.ttod-clusters a.ttod-pill')].map((pill) => pill.getAttribute('href'));
    expect(hrefs).toEqual(['/es/wisdom/sections/architecture/', '/es/wisdom/sections/wisdom/']);
  });
});
