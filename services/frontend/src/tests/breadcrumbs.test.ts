import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { JSDOM } from 'jsdom';
import { describe, expect, it } from 'vitest';

import Breadcrumbs from '../components/Breadcrumbs.astro';

const render = async (items: { label: string; href?: string }[], locale: 'en' | 'es' = 'en') => {
  const container = await AstroContainer.create();
  const html = await container.renderToString(Breadcrumbs, { props: { locale, items } });
  return new JSDOM(html).window.document;
};

describe('Breadcrumbs', () => {
  it('renders a <nav aria-label> with an <ol> of <li>', async () => {
    const doc = await render([{ label: 'Wisdom', href: '/en/wisdom/' }, { label: 'architecture' }]);
    const nav = doc.querySelector('nav');
    expect(nav).not.toBeNull();
    expect(nav?.getAttribute('aria-label')).toBe('Breadcrumb');
    expect(nav?.querySelector('ol')).not.toBeNull();
    expect(nav?.querySelectorAll('li')).toHaveLength(2);
  });

  it('links every item except the last, which carries aria-current and no link', async () => {
    const doc = await render([{ label: 'Wisdom', href: '/en/wisdom/' }, { label: 'architecture', href: '/en/wisdom/sections/architecture/' }, { label: 'arch-001' }]);
    const items = [...doc.querySelectorAll('li')];
    expect(items).toHaveLength(3);
    expect(items[0].querySelector('a')?.getAttribute('href')).toBe('/en/wisdom/');
    expect(items[1].querySelector('a')?.getAttribute('href')).toBe('/en/wisdom/sections/architecture/');
    expect(items[2].querySelector('a')).toBeNull();
    expect(items[2].getAttribute('aria-current')).toBe('page');
    expect(items[2].textContent?.trim()).toBe('arch-001');
  });

  it('keeps the locale prefix on every linked crumb and translates the nav label in es', async () => {
    const doc = await render([{ label: 'Sabiduría', href: '/es/wisdom/' }, { label: 'arquitectura' }], 'es');
    expect(doc.querySelector('nav')?.getAttribute('aria-label')).toBe('Ruta de navegación');
    expect(doc.querySelector('li a')?.getAttribute('href')).toBe('/es/wisdom/');
  });

  it('renders a single current crumb with no link when there is only one item', async () => {
    const doc = await render([{ label: 'Wisdom' }]);
    const items = [...doc.querySelectorAll('li')];
    expect(items).toHaveLength(1);
    expect(items[0].querySelector('a')).toBeNull();
    expect(items[0].getAttribute('aria-current')).toBe('page');
  });
});
