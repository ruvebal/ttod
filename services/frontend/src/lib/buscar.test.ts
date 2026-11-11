import { describe, expect, it } from 'vitest';

import { corpus } from '../tests/fixtures/locators-corpus';
import { buscar, hayFiltros, LIMITE_Q, leerFiltros, pliega } from './buscar';

const es = corpus.filter((e) => e.lang === 'es');
const ids = (q: string, extra = '') => buscar(es, leerFiltros(new URLSearchParams(`q=${encodeURIComponent(q)}${extra}`))).map((e) => e.id);

describe('wisdom search (F49)', () => {
  it('folds accents and case', () => {
    expect(pliega('DISEÑO Ünico')).toBe('diseno unico');
    expect(ids('diseno')).toEqual(['wis-034']);
    expect(ids('DISEÑO')).toEqual(['wis-034']);
    expect(ids('Diseño')).toEqual(ids('diseno'));
  });
  it('searches text, teaches, tags and id; every word must match', () => {
    expect(ids('koan')).toEqual(['wis-034', 'arch-060']);
    expect(ids('arch-061')).toEqual(['arch-061']);
    expect(ids('teaches arch')).toEqual(['arch-060', 'arch-061']);
    expect(ids('koan debt')).toEqual(['arch-060']);
    expect(ids('nada-de-esto')).toEqual([]);
  });
  it('caps q at 100 characters', () => {
    expect(leerFiltros(new URLSearchParams(`q=${'x'.repeat(300)}`)).q).toHaveLength(LIMITE_Q);
  });
  it('combines section, level and tag with the search', () => {
    expect(ids('', '&section=architecture&level=advanced')).toEqual(['arch-060']);
    expect(ids('koan', '&section=architecture')).toEqual(['arch-060']);
    expect(ids('', '&tag=design')).toEqual(['arch-061']);
  });
  it('treats blank values as no filter', () => {
    expect(hayFiltros(leerFiltros(new URLSearchParams('q=%20%20&section=')))).toBe(false);
    expect(hayFiltros(leerFiltros(new URLSearchParams('level=advanced')))).toBe(true);
    expect(hayFiltros(leerFiltros(new URLSearchParams('q=%CC%81')))).toBe(false);
  });
});
