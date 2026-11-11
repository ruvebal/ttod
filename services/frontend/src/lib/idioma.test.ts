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
});
