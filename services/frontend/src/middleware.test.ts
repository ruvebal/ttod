import { describe, expect, it } from 'vitest';

import registry from './lib/locators.registry.json';
import { redireccionLocator } from './lib/locators';

const at = (path: string, method = 'GET') => redireccionLocator(method, new URL(`http://localhost${path}`));
const fill = (s: string, l: string) =>
  s.replace(/\{([a-z-]+)\}/g, (m, k: string) =>
    (({ l, section: registry.values.section, level: registry.values.level, tag: registry.values.tag, a: 'arch-060', b: 'arch-061' }) as Record<string, string>)[k] ?? m);

describe('slash policy (LOCATORS §3)', () => {
  it('301s a slashless page to its slash form and keeps the query', () => {
    expect(at('/es/oracle')).toBe('/es/oracle/');
    expect(at('/en/wisdom/sections/architecture?p=2&orden=nivel')).toBe('/en/wisdom/sections/architecture/?p=2&orden=nivel');
  });
  it('leaves slash pages, endpoints, assets and the API alone', () => {
    for (const path of ['/es/', '/es/wisdom/', '/es/logout', '/api/v1/graph', '/visual-system/tokens.css', '/sw.js', '/_astro/x.js', '/project-docs/es']) {
      expect(at(path), path).toBeNull();
    }
  });
  it('never redirects a POST or other non-GET (the body would be lost)', () => {
    expect(at('/es/login', 'POST')).toBeNull();
    expect(at('/es/wisdom', 'DELETE')).toBeNull();
    expect(at('/es/wisdom', 'HEAD')).toBe('/es/wisdom/');
  });
});

describe('never an off-site Location (cold review AA3b, F1)', () => {
  // A URL object, not a string: `new URL('http://localhost' + '//evil.com/x')` would read evil.com as
  // the host and hide the attack. Built this way the path really is `//evil.com/x`.
  const raw = (path: string) => {
    const url = new URL('http://localhost/');
    url.pathname = path;
    return redireccionLocator('GET', url);
  };
  it('refuses paths that a browser would read as another host', () => {
    expect(new URL('http://localhost//evil.com/x').pathname).toBe('//evil.com/x');
    expect(redireccionLocator('GET', new URL('http://localhost//evil.com/x'))).toBeNull();
    expect(redireccionLocator('GET', new URL('http://localhost/\\evil.com/x'))).toBeNull();
    expect(redireccionLocator('GET', new URL('http://localhost///evil.com/x?y=1'))).toBeNull();
    expect(raw('//evil.com/graph/path')).toBeNull();
  });
  it('still redirects a doubled slash that stays on this site', () => {
    expect(redireccionLocator('GET', new URL('http://localhost/es//evil.com/x'))).toBe('/es//evil.com/x/');
  });
});

describe('legacy and canonical redirects', () => {
  it('sends /graph/path to /graph/ with the query, or to /graph/code/ for the code graph key', () => {
    expect(at('/es/graph/path')).toBe('/es/graph/');
    expect(at('/es/graph/path?from=a-1&to=b-2')).toBe('/es/graph/?from=a-1&to=b-2');
    expect(at('/en/graph/path/?s=app/main.py')).toBe('/en/graph/code/?s=app/main.py');
    expect(at('/en/graph/path?s=x&from=a-1')).toBe('/en/graph/?s=x&from=a-1');
  });
  it('sends the 2D island key ?tag= to /graph/plano/', () => {
    expect(at('/es/graph/?tag=koan')).toBe('/es/graph/plano/?tag=koan');
    expect(at('/es/graph?tag=koan&node=a-1')).toBe('/es/graph/plano/?tag=koan&node=a-1');
    expect(at('/es/graph/?node=a-1')).toBeNull();
  });
  it('sends a single facet without search to its path form, keeping sort and page', () => {
    expect(at('/es/wisdom/?section=architecture')).toBe('/es/wisdom/sections/architecture/');
    expect(at('/es/wisdom/?level=advanced&orden=nivel&p=2')).toBe('/es/wisdom/levels/advanced/?orden=nivel&p=2');
    expect(at('/es/wisdom/?tag=koan&q=')).toBe('/es/wisdom/tags/koan/');
  });
  it('keeps searches, combinations and odd values on /wisdom/', () => {
    expect(at('/es/wisdom/?q=diseno&section=architecture')).toBeNull();
    expect(at('/es/wisdom/?section=architecture&level=advanced')).toBeNull();
    expect(at('/es/wisdom/?tag=a&tag=b')).toBeNull();
    expect(at('/es/wisdom/?section=..%2Fapi')).toBeNull();
  });
  it('walks every redirect and exemption in the registry, in both locales', () => {
    for (const l of ['en', 'es']) {
      for (const r of registry.redirects) {
        const want = new URL(`http://localhost${fill(r.to, l)}`);
        expect(at(fill(r.from, l)), r.from).toBe(want.pathname + want.search);
      }
      for (const e of registry.exempt) expect(at(fill(e, l)), e).toBeNull();
    }
  });
});
