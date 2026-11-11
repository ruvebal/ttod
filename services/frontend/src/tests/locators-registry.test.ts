import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { loadRenderers } from 'astro:container';
import { getContainerRenderer } from '@astrojs/react/container-renderer';
import { JSDOM } from 'jsdom';
import { describe, expect, it, vi } from 'vitest';

import registry from '../lib/locators.registry.json';
import { mapaGemelas } from '../lib/idioma';
import { corpus, edges } from './fixtures/locators-corpus';

// LOCATORS §8: walk the registry. Pages under /{l}/ and /{l}/wisdom/ render here with a fixture
// corpus; graph, oracle and docs pages need their islands or the docs collection, so the AA3b exit
// gate's live probe walks them. A new registry page must be mapped below or named in LIVE_ONLY.
vi.mock('../lib/corpus.server', () => ({ pideCorpus: async () => corpus }));
vi.mock('../lib/grafo.server', () => ({
  gemelasTraduccion: async () => mapaGemelas(edges),
  planoInicial: () => null,
  grafoInicial: () => null,
}));
vi.mock('../content/wisdom', async (importOriginal) => {
  const mod = await importOriginal<typeof import('../content/wisdom')>();
  const entries = (locale: 'en' | 'es') => corpus.filter((e) => e.lang === locale);
  return { ...mod, fetchWisdom: async (locale: 'en' | 'es') => entries(locale), loadWisdom: async (locale: 'en' | 'es') => ({ entries: entries(locale), failed: false }) };
});

import EnLanding from '../pages/en/index.astro';
import EsLanding from '../pages/es/index.astro';
import WisdomIndex from '../pages/[locale]/wisdom/index.astro';
import QuoteRoute from '../pages/[locale]/wisdom/[slug].astro';
import SectionRoute from '../pages/[locale]/wisdom/sections/[section].astro';
import LevelRoute from '../pages/[locale]/wisdom/levels/[level].astro';
import TagRoute from '../pages/[locale]/wisdom/tags/[tag].astro';
import AccountRoute from '../pages/[locale]/account.astro';

type RegistryPage = { path: string; ids: string[]; auth?: boolean; owner?: string; conditional?: string[] };
const pages = registry.pages as RegistryPage[];
const LIVE_ONLY = ['/{l}/graph/', '/{l}/graph/plano/', '/{l}/graph/code/', '/{l}/oracle/', '/{l}/docs/'];
const V = registry.values;
const locales = ['en', 'es'] as const;
const idsOf = (l: string) => new Set(corpus.filter((e) => e.lang === l).map((e) => e.id));
const sectionsOf = (l: string) => [...new Set(corpus.filter((e) => e.lang === l).map((e) => e.section))];
const quoteOf = (l: string) => [...idsOf(l)].sort()[0];
const fill = (s: string, l: 'en' | 'es') =>
  s.replace(/\{([a-z-]+)\}/g, (m, k: string) =>
    (({ l, section: V.section, level: V.level, tag: V.tag, word: V.word[l], quote: quoteOf(l),
      'other-quote': quoteOf(l === 'en' ? 'es' : 'en') }) as Record<string, string>)[k] ?? m);

type Route = Parameters<AstroContainer['renderToResponse']>[0];
function routeFor(template: string, l: 'en' | 'es'): { route: Route; params: Record<string, string> } | null {
  const path = new URL(`http://x${fill(template, l)}`).pathname;
  if (path === `/${l}/`) return { route: l === 'en' ? EnLanding : EsLanding, params: {} };
  if (path === `/${l}/wisdom/`) return { route: WisdomIndex, params: { locale: l } };
  let m = path.match(/^\/(?:en|es)\/wisdom\/(sections|levels|tags)\/([^/]+)\/$/);
  if (m) {
    const [, kind, value] = m;
    const route = kind === 'sections' ? SectionRoute : kind === 'levels' ? LevelRoute : TagRoute;
    return { route, params: { locale: l, [kind === 'sections' ? 'section' : kind === 'levels' ? 'level' : 'tag']: value } };
  }
  if (path === `/${l}/account/`) return { route: AccountRoute, params: { locale: l } };
  m = path.match(/^\/(?:en|es)\/wisdom\/([^/]+)\/$/);
  if (m) return { route: QuoteRoute, params: { locale: l, slug: m[1] } };
  return null;
}

async function render(template: string, l: 'en' | 'es') {
  const target = routeFor(template, l);
  if (!target) throw new Error(`no route mapped for ${template}`);
  const container = await AstroContainer.create({ renderers: await loadRenderers([getContainerRenderer()]) });
  const response = await container.renderToResponse(target.route, {
    params: target.params,
    request: new Request(`http://localhost${fill(template, l)}`),
  });
  const html = await response.text();
  return { status: response.status, doc: new JSDOM(html).window.document };
}

const testable = pages.filter((p) => !p.owner && !p.auth && !LIVE_ONLY.includes(p.path));

describe('locator registry (LOCATORS §4, §8)', () => {
  it('maps every registry page to a route here or to the live probe', () => {
    for (const p of pages) {
      if (p.owner || p.auth || LIVE_ONLY.includes(p.path)) continue;
      expect(routeFor(p.path, 'es'), p.path).not.toBeNull();
    }
  });

  for (const page of testable) {
    it(`${page.path}: 200, every registered id exactly once, no duplicate ids, en/es structural ids equal`, async () => {
      const structural: Record<string, string[]> = {};
      for (const l of locales) {
        const { status, doc } = await render(page.path, l);
        expect(status, `${l} ${page.path}`).toBe(200);
        const found = [...doc.querySelectorAll('[id]')].map((el) => el.id);
        const dup = found.filter((id, i) => found.indexOf(id) !== i);
        expect(dup, `${l} ${page.path} duplicate ids`).toEqual([]);
        for (const want of page.ids) {
          if (want === '{quote}') expect(found.some((id) => idsOf(l).has(id)), `${l} ${page.path} quote id`).toBe(true);
          else if (want.includes('{section}')) for (const s of sectionsOf(l)) expect(found, `${l} ${page.path}`).toContain(want.replace('{section}', s));
          else expect(found.filter((id) => id === fill(want, l)), `${l} ${page.path} #${want}`).toHaveLength(1);
        }
        const conditional = new Set((page as { conditional?: string[] }).conditional ?? []);
        structural[l] = found.filter((id) => !idsOf(l).has(id) && !conditional.has(id)).sort();
      }
      expect(structural.en, page.path).toEqual(structural.es);
    });
  }

  for (const template of registry.notFound) {
    it(`${template} answers 404`, async () => {
      for (const l of locales) expect((await render(template, l)).status, `${l} ${template}`).toBe(404);
    });
  }

  // Signed-in pages (`auth: true`): rendered with a session the backend accepts (AA3 took over /account/).
  it('signed-in registry pages carry their ids exactly once, en and es alike', async () => {
    const student = { id: 'usr-1', email: 'ana@example.test', roles: ['student'] };
    const spy = vi.spyOn(global, 'fetch').mockImplementation(async () => Response.json(student));
    try {
      for (const page of pages.filter((p) => p.auth && routeFor(p.path, 'es'))) {
        const ids: Record<string, string[]> = {};
        for (const l of locales) {
          const target = routeFor(page.path, l)!;
          const container = await AstroContainer.create({ renderers: await loadRenderers([getContainerRenderer()]) });
          const response = await container.renderToResponse(target.route, {
            params: target.params, request: new Request(`http://localhost${fill(page.path, l)}`, { headers: { cookie: 'ttod_session=t' } }),
          });
          expect(response.status, `${l} ${page.path}`).toBe(200);
          const found = [...new JSDOM(await response.text()).window.document.querySelectorAll('[id]')].map((el) => el.id);
          for (const want of page.ids) expect(found.filter((id) => id === want), `${l} ${page.path} #${want}`).toHaveLength(1);
          ids[l] = found.sort();
        }
        expect(ids.en, page.path).toEqual(ids.es);
      }
    } finally {
      spy.mockRestore();
    }
  });

  it('quote pages switch language to the translation twin, both directions', async () => {
    const es = (await render('/es/wisdom/wis-034/', 'es')).doc;
    expect(es.querySelector('.ttod-lang-switch')?.getAttribute('href')).toBe('/en/wisdom/wis-033/');
    expect(es.querySelector('.pie-idioma')?.getAttribute('href')).toBe('/en/wisdom/wis-033/');
    const en = (await render('/en/wisdom/wis-033/', 'en')).doc;
    expect(en.querySelector('.ttod-lang-switch')?.getAttribute('href')).toBe('/es/wisdom/wis-034/');
  });

  it('search results replace the shelf, keep the query in the sort form, and say so when empty', async () => {
    const hit = (await render('/es/wisdom/?q=DISE%C3%91O', 'es')).doc;
    expect([...hit.querySelectorAll('article.piedra')].map((a) => a.id)).toEqual(['wis-034']);
    expect(hit.querySelector('details.libro')).toBeNull();
    expect(hit.querySelector('form.orden input[name="q"]')?.getAttribute('value')).toBe('DISEÑO');
    expect((hit.querySelector('#armario-q') as HTMLInputElement).getAttribute('value')).toBe('DISEÑO');
    const none = (await render('/es/wisdom/?q=zzqq', 'es')).doc;
    expect(none.querySelectorAll('article.piedra')).toHaveLength(0);
    expect(none.querySelector('.ttod-empty-state, [class*="empty"]')).not.toBeNull();
    expect(none.querySelector('a[href="/es/wisdom/sections/architecture/"]')).not.toBeNull();
  });

  it('the untranslated notice names only a quote that exists in the other locale', async () => {
    expect((await render('/en/wisdom/?untranslated=wis-034', 'en')).doc.querySelector('.armario-aviso')?.textContent).toContain('wis-034');
    expect((await render('/en/wisdom/?untranslated=you-have-been-hacked', 'en')).doc.querySelector('.armario-aviso')).toBeNull();
    expect((await render('/en/wisdom/?untranslated=wis-033', 'en')).doc.querySelector('.armario-aviso')).toBeNull();
    expect((await render('/en/wisdom/?untranslated=%3Cb%3E', 'en')).doc.querySelector('.armario-aviso')).toBeNull();
  });
});
