import { experimental_AstroContainer as AstroContainer } from 'astro/container';
import { JSDOM } from 'jsdom';
import { describe, expect, it } from 'vitest';

import ProvenanceBlock from '../components/ProvenanceBlock.astro';

const render = async (props: Record<string, unknown>) => {
  const container = await AstroContainer.create();
  const html = await container.renderToString(ProvenanceBlock, { props });
  return new JSDOM(html).window.document;
};

describe('ProvenanceBlock', () => {
  it('renders holder, license and origin as a <dl> with an accessible name', async () => {
    const doc = await render({
      entry: { rights: { holder: 'ruvebal@crea-comm.net', license: 'CC-BY-NC-SA-4.0' }, origin: 'human' },
      locale: 'en',
    });
    const dl = doc.querySelector('dl');
    expect(dl?.getAttribute('aria-label')).toBe('Provenance');
    expect(doc.body.textContent).toContain('ruvebal@crea-comm.net');
    expect(doc.body.textContent).toContain('CC-BY-NC-SA-4.0');
    expect(doc.body.textContent).toContain('Human');
  });

  it('falls back to the project default holder when it is missing, without breaking the layout', async () => {
    const doc = await render({ entry: { rights: { license: 'CC-BY-NC-SA-4.0' }, origin: 'human' }, locale: 'en' });
    expect(doc.body.textContent).toContain('Rubén Vega Balbás');
  });

  it('omits the license pair entirely when license is missing (defensive, not just blank)', async () => {
    const doc = await render({ entry: { rights: {}, origin: 'human' }, locale: 'en' });
    expect(doc.querySelectorAll('dt').length).toBe(2); // holder + origin only
    expect(doc.body.textContent).not.toContain('License');
  });

  it('translates to es, including the origin value', async () => {
    const doc = await render({ entry: { rights: { holder: 'x', license: 'y' }, origin: 'blackbox' }, locale: 'es' });
    expect(doc.querySelector('dl')?.getAttribute('aria-label')).toBe('Procedencia');
    expect(doc.body.textContent).toContain('Propuesto por IA');
  });

  it('falls back to the raw value for an unrecognized origin, never breaking', async () => {
    const doc = await render({ entry: { rights: { holder: 'x', license: 'y' }, origin: 'something-new' }, locale: 'en' });
    expect(doc.body.textContent).toContain('something-new');
  });

  it('supports a compact variant for cards', async () => {
    const doc = await render({ entry: { rights: { holder: 'x', license: 'y' }, origin: 'human' }, locale: 'en', variant: 'compact' });
    expect(doc.querySelector('dl')?.className).toContain('ttod-provenance-compact');
  });
});
