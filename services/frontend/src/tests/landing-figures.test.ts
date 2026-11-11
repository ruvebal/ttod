import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { JSDOM } from 'jsdom';
import { describe, expect, it, vi } from 'vitest';

import type { WisdomEntry } from '../types/domain';

// F54: the landing figures are read from the corpus, never typed. A fixture corpus of 3 quotes in
// 2 sections at 1 level must render 3 / 2 / 1 in each locale. The AA3b exit gate types a literal
// count into ValleSigue and into each landing page and expects this file to go red.
const q = (id: string, lang: 'en' | 'es', section: string): WisdomEntry => ({
  id, lang, section, level: 'beginner', tags: ['koan'], text: `Quote ${id}`, teaches: 't', related: [],
  origin: 'human', rights: { license: 'CC-BY-NC-SA-4.0', holder: 'ruvebal@crea-comm.net' },
});
const fixture = [
  q('wis-034', 'es', 'wisdom'), q('arch-060', 'es', 'architecture'), q('arch-061', 'es', 'architecture'),
  q('wis-033', 'en', 'wisdom'), q('arch-008', 'en', 'architecture'), q('arch-052', 'en', 'architecture'),
];
vi.mock('../lib/corpus.server', () => ({ pideCorpus: async () => fixture }));

import EnLanding from '../pages/en/index.astro';
import EsLanding from '../pages/es/index.astro';

const figures = async (Route: Parameters<AstroContainer['renderToString']>[0], path: string) => {
  const container = await AstroContainer.create();
  const doc = new JSDOM(await container.renderToString(Route, { request: new Request(`http://localhost${path}`) })).window.document;
  return [...doc.querySelectorAll('dl.cifras > .cifra')].map((pair) => ({
    label: pair.querySelector('dt')?.textContent?.trim(),
    value: pair.querySelector('dd')?.textContent?.trim(),
  }));
};

describe('landing figures guard (F54)', () => {
  it('es: 3 quotes, 2 sections, 1 level, each <dt> a label and its <dd> the number', async () => {
    expect(await figures(EsLanding, '/es/')).toEqual([
      { label: 'citas en español', value: '3' },
      { label: 'secciones', value: '2' },
      { label: 'niveles de profundidad', value: '1' },
    ]);
  });
  it('en: 3 quotes, 2 sections, 1 level', async () => {
    expect(await figures(EnLanding, '/en/')).toEqual([
      { label: 'quotes in English', value: '3' },
      { label: 'sections', value: '2' },
      { label: 'levels of depth', value: '1' },
    ]);
  });
  it('queries the definition list by its parts', async () => {
    const doc = new JSDOM(await (await AstroContainer.create()).renderToString(EsLanding, { request: new Request('http://localhost/es/') })).window.document;
    const dl = doc.querySelector('dl.cifras')!;
    expect(dl.querySelectorAll('dt')).toHaveLength(3);
    expect([...dl.querySelectorAll('dd')].every((dd) => /^\d+$/.test(dd.textContent!.trim()))).toBe(true);
    expect(doc.querySelectorAll(`[id^="map-"]`)).toHaveLength(2);
  });
});
