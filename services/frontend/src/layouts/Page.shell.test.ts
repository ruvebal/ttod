import { createRequire } from 'node:module';

import { getByRole } from '@testing-library/dom';
import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { describe, expect, it } from 'vitest';

const { JSDOM } = createRequire(import.meta.url)('jsdom') as {
  JSDOM: new (html: string) => { window: { document: Document } };
};

import Page from './Page.astro';

describe('Page.astro shell', () => {
  it('renders the English locale document shell with title, lang, and slotted main', async () => {
    const container = await AstroContainer.create();
    const html = await container.renderToString(Page, {
      props: { lang: 'en', title: 'Wisdom' },
      slots: { default: '<main><h1>Wisdom</h1></main>' },
    });

    const { document } = new JSDOM(html).window;
    expect(document.documentElement.getAttribute('lang')).toBe('en');
    expect(document.title).toBe('Wisdom');
    expect(getByRole(document.body, 'heading', { level: 1, name: 'Wisdom' }).textContent).toBe('Wisdom');
    expect(getByRole(document.body, 'main')).toBeTruthy();
  });
});
