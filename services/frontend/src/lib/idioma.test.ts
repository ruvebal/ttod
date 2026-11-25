import { describe, expect, it } from 'vitest';

import { edges } from '../tests/fixtures/locators-corpus';
import { conEstado, destinoCita, mapaGemelas } from './idioma';

describe('language switch (F57, LOCATORS §5)', () => {
  const gemelas = mapaGemelas(edges);
  it('resolves the translation twin in both directions (edges are stored one way)', () => {
    expect(destinoCita('wis-034', 'en', gemelas)).toBe('/en/wisdom/wis-033/');
    expect(destinoCita('wis-033', 'es', gemelas)).toBe('/es/wisdom/wis-034/');
    expect(gemelas.has('arch-061')).toBe(true);
    expect(gemelas.get('arch-060')).toBe('arch-008');
  });
  it('without a twin goes to the other index with the untranslated notice, never to not-found', () => {
    expect(destinoCita('solo-001', 'en', gemelas)).toBe('/en/wisdom/?untranslated=solo-001');
  });
  it('without the graph goes to the other index, no notice', () => {
    expect(destinoCita('wis-034', 'en', null)).toBe('/en/wisdom/');
  });
  it('ignores non-translation edges', () => {
    expect(mapaGemelas([{ source: 'a', target: 'b', rel: 'related' }]).size).toBe(0);
  });
  it('carries search and hash onto the server-rendered target', () => {
    const at = { origin: 'http://x', search: '?q=diseno&orden=nivel', hash: '#search' };
    expect(conEstado('/en/wisdom/', at)).toBe('/en/wisdom/?q=diseno&orden=nivel#search');
    expect(conEstado('/en/wisdom/?untranslated=a-1', { ...at, hash: '' })).toBe('/en/wisdom/?untranslated=a-1&q=diseno&orden=nivel');
    expect(conEstado('/es/', { origin: 'http://x', search: '', hash: '#map-architecture' })).toBe('/es/#map-architecture');
  });
  it('drops what does not survive the switch: next, untranslated, quote-id fragments', () => {
    expect(conEstado('/en/login/', { origin: 'http://x', search: '?next=%2Fes%2Flibrary%2F', hash: '' })).toBe('/en/login/');
    expect(conEstado('/en/wisdom/', { origin: 'http://x', search: '?untranslated=wis-033&q=a', hash: '' })).toBe('/en/wisdom/?q=a');
    expect(conEstado('/en/wisdom/sections/architecture/', { origin: 'http://x', search: '?p=2', hash: '#arch-060' })).toBe('/en/wisdom/sections/architecture/?p=2');
    expect(conEstado('/en/wisdom/', { origin: 'http://x', search: '', hash: '#volume-architecture' })).toBe('/en/wisdom/#volume-architecture');
  });
});

describe('root locale from Accept-Language (AA4, F43)', () => {
  it('picks the highest q among en and es; regions count; q=0 is no; default en', async () => {
    const { idiomaPreferido } = await import('./idioma');
    expect(idiomaPreferido('es-ES,es;q=0.9,en;q=0.5')).toBe('es');
    expect(idiomaPreferido('en-US,en;q=0.9')).toBe('en');
    expect(idiomaPreferido('es;q=0.1, en;q=0.9')).toBe('en');
    expect(idiomaPreferido('fr, es;q=0.5')).toBe('es');
    expect(idiomaPreferido('fr-FR,fr')).toBe('en');
    expect(idiomaPreferido('es;q=0, en;q=0.2')).toBe('en');
    expect(idiomaPreferido('es, en')).toBe('es');
    expect(idiomaPreferido('')).toBe('en');
    expect(idiomaPreferido(null)).toBe('en');
    expect(idiomaPreferido('*')).toBe('en');
  });
});
