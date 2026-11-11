import { describe, expect, it } from 'vitest';

import { alternas, canonica, descripcionCita, indexable, origenPublico, recorte, tituloCita } from './seo';

const O = 'http://aula.example';
const u = (path: string) => new URL(O + path);

describe('robots per page, from the locator registry (AA4)', () => {
  it('public pages are indexable', () => {
    for (const p of ['/es/', '/en/wisdom/', '/es/wisdom/arch-060/', '/en/wisdom/sections/architecture/', '/es/graph/', '/en/login/', '/es/register/', '/en/docs/'])
      expect(indexable(u(p)), p).toBe(true);
  });
  it('signed-in rows (auth) and rows marked index:false are not', () => {
    for (const p of ['/es/library/', '/en/account/', '/es/account/reviewer/', '/en/wisdom/propose/', '/es/quote/'])
      expect(indexable(u(p)), p).toBe(false);
  });
  it('?untranslated= and any non-200 page are not', () => {
    expect(indexable(u('/en/wisdom/?untranslated=wis-034'))).toBe(false);
    expect(indexable(u('/en/wisdom/zz-999/'), 404)).toBe(false);
    expect(indexable(u('/es/'), 503)).toBe(false);
  });
});

describe('canonical (AA3b carry)', () => {
  it('drops the query: search, combined filters, graph path, sign-in next', () => {
    expect(canonica(u('/es/wisdom/?q=dise%C3%B1o'), O)).toBe(`${O}/es/wisdom/`);
    expect(canonica(u('/en/wisdom/?section=architecture&level=advanced&orden=nivel'), O)).toBe(`${O}/en/wisdom/`);
    expect(canonica(u('/en/graph/?from=arch-008&to=wis-033&node=arch-008'), O)).toBe(`${O}/en/graph/`);
    expect(canonica(u('/es/login/?next=%2Fes%2Fwisdom%2F'), O)).toBe(`${O}/es/login/`);
  });
  it('keeps the list page from 2 up, and nothing else', () => {
    expect(canonica(u('/es/wisdom/tags/koan/?p=2&orden=nivel'), O)).toBe(`${O}/es/wisdom/tags/koan/?p=2`);
    expect(canonica(u('/es/wisdom/tags/koan/?p=1'), O)).toBe(`${O}/es/wisdom/tags/koan/`);
    expect(canonica(u('/es/wisdom/tags/koan/?p=x'), O)).toBe(`${O}/es/wisdom/tags/koan/`);
  });
});

describe('hreflang alternates', () => {
  it('this page, its twin and x-default (English), absolute', () => {
    expect(alternas(u('/es/wisdom/wis-034/'), O, 'es', '/en/wisdom/wis-033/')).toEqual([
      { hreflang: 'en', href: `${O}/en/wisdom/wis-033/` },
      { hreflang: 'es', href: `${O}/es/wisdom/wis-034/` },
      { hreflang: 'x-default', href: `${O}/en/wisdom/wis-033/` },
    ]);
  });
  it('none without a twin', () => {
    expect(alternas(u('/es/wisdom/arch-099/'), O, 'es', null)).toEqual([]);
  });
  it('the list page travels with both alternates', () => {
    expect(alternas(u('/en/wisdom/tags/koan/?p=3'), O, 'en', '/es/wisdom/tags/koan/').map((a) => a.href))
      .toEqual([`${O}/en/wisdom/tags/koan/?p=3`, `${O}/es/wisdom/tags/koan/?p=3`, `${O}/en/wisdom/tags/koan/?p=3`]);
  });
});

describe('quote title and description (F41)', () => {
  const largo = 'Un límite sin pruebas es un deseo, y un deseo sin límite es una promesa que nadie podrá cumplir nunca.';
  it('trims at a word boundary and marks the cut', () => {
    const t = recorte(largo, 60);
    expect(t.length).toBeLessThanOrEqual(60);
    expect(t.endsWith('…')).toBe(true);
    expect(largo.startsWith(t.slice(0, -1))).toBe(true);
    expect(t.slice(0, -1)).not.toMatch(/[\s,]$/);
    expect(recorte('  corto   y  claro ', 60)).toBe('corto y claro');
  });
  it('the title starts with the quote, never the id', () => {
    const t = tituloCita('Simplicity is design paid in advance.', 'Wisdom');
    expect(t).toBe('Simplicity is design paid in advance. · Wisdom');
    expect(tituloCita(largo, 'Sabiduría')).toMatch(/^Un límite sin pruebas .*… · Sabiduría$/);
  });
  it('the description is what it teaches, else the quote', () => {
    expect(descripcionCita('Texto.', 'Enseña algo.')).toBe('Enseña algo.');
    expect(descripcionCita('Texto.', '  ')).toBe('Texto.');
    expect(descripcionCita('x', 'y '.repeat(200)).length).toBeLessThanOrEqual(155);
  });
});

describe('public origin (a Host Astro does not trust)', () => {
  it('is the URL origin when the requested host is the one Astro kept', () => {
    expect(origenPublico(new URL('http://aula.example:8080/es/'), new Headers({ host: 'frontend:4321', 'x-forwarded-host': 'aula.example:8080' }))).toBe('http://aula.example:8080');
    expect(origenPublico(new URL('http://localhost:4321/es/'), new Headers({ host: 'localhost:4321' }))).toBe('http://localhost:4321');
  });
  it('is empty when Astro fell back to its internal address', () => {
    expect(origenPublico(new URL('http://localhost:4321/es/'), new Headers({ host: 'evil.example', 'x-forwarded-host': 'evil.example' }))).toBe('');
    expect(origenPublico(new URL('http://localhost:4321/es/'), new Headers({ host: '192.168.1.20:8080' }))).toBe('');
  });
  it('then canonical and alternates are root-relative', () => {
    expect(canonica(u('/es/wisdom/?q=x'), '')).toBe('/es/wisdom/');
    expect(alternas(u('/es/'), '', 'es', '/en/')[0]).toEqual({ hreflang: 'en', href: '/en/' });
  });
});
