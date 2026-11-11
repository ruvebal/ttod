import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { loadRenderers } from 'astro:container';
import { getContainerRenderer } from '@astrojs/react/container-renderer';
import { JSDOM } from 'jsdom';
import { describe, expect, it, vi } from 'vitest';

import { mapaGemelas } from '../lib/idioma';
import { corpus, edges } from '../tests/fixtures/locators-corpus';

// AA4 (F15, F41): what the <head> says to a search engine or a share card. The quote route renders
// with the registry test's fixture corpus; `gemelas` is swapped per test to drop a twin.
let gemelas: Map<string, string> | null = mapaGemelas(edges);
vi.mock('../lib/corpus.server', () => ({ pideCorpus: async () => corpus }));
vi.mock('../lib/grafo.server', () => ({ gemelasTraduccion: async () => gemelas, planoInicial: () => null, grafoInicial: () => null }));
// `caido`: the backend is down, so loadWisdom reports `failed` (cold review AA4, F2).
let caido = false;
vi.mock('../content/wisdom', async (importOriginal) => {
  const mod = await importOriginal<typeof import('../content/wisdom')>();
  const entries = (locale: 'en' | 'es') => corpus.filter((e) => e.lang === locale);
  return { ...mod, fetchWisdom: async (l: 'en' | 'es') => entries(l),
    loadWisdom: async (l: 'en' | 'es') => (caido ? { entries: [], failed: true } : { entries: entries(l), failed: false }) };
});

import Page from './Page.astro';
import QuoteRoute from '../pages/[locale]/wisdom/[slug].astro';
import SectionRoute from '../pages/[locale]/wisdom/sections/[section].astro';
import TagRoute from '../pages/[locale]/wisdom/tags/[tag].astro';
import WisdomIndex from '../pages/[locale]/wisdom/index.astro';

const O = 'http://aula.example';
const doc = (html: string) => new JSDOM(html).window.document;
const page = async (path: string, lang: 'en' | 'es', props: Record<string, unknown> = {}) => {
  const container = await AstroContainer.create();
  return doc(await container.renderToString(Page, {
    props: { lang, title: 'Título', usuario: null, ...props },
    request: new Request(O + path),
    slots: { default: '<main id="ttod-main"></main>' },
  }));
};
const route = async (r: Parameters<AstroContainer['renderToResponse']>[0], path: string, params: Record<string, string>) => {
  const container = await AstroContainer.create({ renderers: await loadRenderers([getContainerRenderer()]) });
  const res = await container.renderToResponse(r, { params, request: new Request(O + path) });
  return { status: res.status, d: doc(await res.text()) };
};
const canon = (d: Document) => [...d.querySelectorAll('link[rel="canonical"]')].map((l) => l.getAttribute('href'));
const alts = (d: Document) => Object.fromEntries([...d.querySelectorAll('link[rel="alternate"][hreflang]')].map((l) => [l.getAttribute('hreflang'), l.getAttribute('href')]));
const meta = (d: Document, k: string) => [...d.querySelectorAll(`meta[property="${k}"], meta[name="${k}"]`)].map((m) => m.getAttribute('content'));

describe('indexable page head', () => {
  it('one canonical (query dropped), og:url = canonical, en/es/x-default alternates', async () => {
    const d = await page('/es/wisdom/?q=koan&orden=nivel', 'es');
    expect(canon(d)).toEqual([`${O}/es/wisdom/`]);
    expect(meta(d, 'og:url')).toEqual([`${O}/es/wisdom/`]);
    expect(alts(d)).toEqual({ en: `${O}/en/wisdom/`, es: `${O}/es/wisdom/`, 'x-default': `${O}/en/wisdom/` });
    expect(d.querySelectorAll('link[rel="alternate"][hreflang]')).toHaveLength(3);
    expect(meta(d, 'robots')).toEqual([]);
  });
  it('carries the share card: title, description, locale, site, type, image', async () => {
    const d = await page('/en/', 'en', { title: 'Home', description: 'About TTOD.' });
    expect(meta(d, 'og:title')).toEqual(['Home']);
    expect(meta(d, 'og:description')).toEqual(['About TTOD.']);
    expect(meta(d, 'og:locale')).toEqual(['en_US']);
    expect(meta(d, 'og:locale:alternate')).toEqual(['es_ES']);
    expect(meta(d, 'og:site_name')).toEqual(['TTOD']);
    expect(meta(d, 'og:type')).toEqual(['website']);
    expect(meta(d, 'og:image')).toEqual([`${O}/visual-system/icon-512.png`]);
    expect(meta(d, 'twitter:card')).toEqual(['summary']);
  });
});

describe('a Host Astro does not trust', () => {
  it('root-relative canonical and alternates, no og:url or og:image (never its internal address)', async () => {
    const container = await AstroContainer.create();
    const d = doc(await container.renderToString(Page, {
      props: { lang: 'es', title: 'T', usuario: null },
      request: new Request('http://localhost:4321/es/wisdom/', { headers: { host: 'evil.example', 'x-forwarded-host': 'evil.example' } }),
      slots: { default: '<main id="ttod-main"></main>' },
    }));
    expect(canon(d)).toEqual(['/es/wisdom/']);
    expect(alts(d).en).toBe('/en/wisdom/');
    expect(meta(d, 'og:url')).toEqual([]);
    expect(meta(d, 'og:image')).toEqual([]);
    expect(d.head.innerHTML).not.toContain('localhost:4321');
    expect(d.head.innerHTML).not.toContain('evil.example');
  });
});

describe('noindex page head', () => {
  for (const [path, lang] of [['/es/library/', 'es'], ['/en/account/', 'en'], ['/es/wisdom/propose/', 'es'], ['/en/quote/', 'en'], ['/en/wisdom/?untranslated=wis-034', 'en']] as const) {
    it(`${path}: robots noindex, no canonical, no alternates, no og:url`, async () => {
      const d = await page(path, lang);
      expect(meta(d, 'robots')).toEqual(['noindex']);
      expect(canon(d)).toEqual([]);
      expect(alts(d)).toEqual({});
      expect(meta(d, 'og:url')).toEqual([]);
      expect(meta(d, 'og:title')).toEqual(['Título']);
    });
  }
  it('indexar={false} forces it on any page', async () => {
    expect(meta(await page('/es/', 'es', { indexar: false }), 'robots')).toEqual(['noindex']);
  });
  it('a page that answers 404 is noindex (the layout reads the response status)', async () => {
    const { status, d } = await route(SectionRoute, '/es/wisdom/sections/zz-none/', { locale: 'es', section: 'zz-none' });
    expect(status).toBe(404);
    expect(meta(d, 'robots')).toEqual(['noindex']);
    expect(canon(d)).toEqual([]);
  });
});

describe('quote page head (F41)', () => {
  it('title and description come from the quote; og:type article; alternates are the twin, both ways', async () => {
    const es = (await route(QuoteRoute, '/es/wisdom/wis-034/', { locale: 'es', slug: 'wis-034' })).d;
    expect(es.title).toBe('El diseño es la deuda que se paga antes. · Sabiduría');
    expect(meta(es, 'description')).toEqual(['Teaches wis-034']);
    expect(meta(es, 'og:type')).toEqual(['article']);
    expect(alts(es)).toEqual({ en: `${O}/en/wisdom/wis-033/`, es: `${O}/es/wisdom/wis-034/`, 'x-default': `${O}/en/wisdom/wis-033/` });
    const en = (await route(QuoteRoute, '/en/wisdom/wis-033/', { locale: 'en', slug: 'wis-033' })).d;
    expect(alts(en).es).toBe(`${O}/es/wisdom/wis-034/`);
    expect(en.title.startsWith('wis-033')).toBe(false);
  });
  it('without a twin (or without the graph): canonical only, no alternates', async () => {
    gemelas = new Map();
    try {
      const d = (await route(QuoteRoute, '/es/wisdom/arch-061/', { locale: 'es', slug: 'arch-061' })).d;
      expect(canon(d)).toEqual([`${O}/es/wisdom/arch-061/`]);
      expect(alts(d)).toEqual({});
      gemelas = null;
      expect(alts((await route(QuoteRoute, '/es/wisdom/arch-061/', { locale: 'es', slug: 'arch-061' })).d)).toEqual({});
    } finally {
      gemelas = mapaGemelas(edges);
    }
  });
  it('an unknown quote is a 404 with noindex', async () => {
    const { status, d } = await route(QuoteRoute, '/es/wisdom/zz-999/', { locale: 'es', slug: 'zz-999' });
    expect(status).toBe(404);
    expect(meta(d, 'robots')).toEqual(['noindex']);
  });
});

describe('list pages and ?p= (cold review AA4, F1)', () => {
  it('the layout writes the page it is given, on canonical and alternates', async () => {
    const d = await page('/es/wisdom/tags/koan/?p=2&orden=nivel', 'es', { pagina: 2 });
    expect(canon(d)).toEqual([`${O}/es/wisdom/tags/koan/?p=2`]);
    expect(alts(d).en).toBe(`${O}/en/wisdom/tags/koan/?p=2`);
  });
  it('a facet clamps ?p= to the pages it has (fixture: one page), so ?p=2, ?p=999, ?p=1e1 point at page 1', async () => {
    for (const p of ['2', '999', '1e1']) {
      const { status, d } = await route(TagRoute, `/es/wisdom/tags/koan/?p=${p}`, { locale: 'es', tag: 'koan' });
      expect(status).toBe(200);
      expect(canon(d), p).toEqual([`${O}/es/wisdom/tags/koan/`]);
    }
  });
  it('search with ?p= still points at /wisdom/', async () => {
    const { d } = await route(WisdomIndex, '/es/wisdom/?q=diseno&p=2', { locale: 'es' });
    expect(canon(d)).toEqual([`${O}/es/wisdom/`]);
  });
});

describe('backend down (cold review AA4, F2)', () => {
  it('quote, facet and wisdom pages that could not load the corpus are noindex, with no canonical', async () => {
    caido = true;
    try {
      for (const [r, path, params] of [
        [QuoteRoute, '/es/wisdom/wis-034/', { locale: 'es', slug: 'wis-034' }],
        [SectionRoute, '/es/wisdom/sections/wisdom/', { locale: 'es', section: 'wisdom' }],
        [TagRoute, '/es/wisdom/tags/koan/', { locale: 'es', tag: 'koan' }],
        [WisdomIndex, '/es/wisdom/', { locale: 'es' }],
      ] as const) {
        const { d } = await route(r, path, params);
        expect(meta(d, 'robots'), path).toEqual(['noindex']);
        expect(canon(d), path).toEqual([]);
      }
    } finally {
      caido = false;
    }
  });
});
