// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest';

import source from './Page.astro?raw';

const labels = {
  en: { online: 'Online', offline: 'Offline' },
  es: { online: 'En línea', offline: 'Sin conexión' },
} as const;

// ponytail: reads the banner and its script out of Page.astro's source instead of rendering the
// layout. Only the `{lang === 'es' ? 'a' : 'b'}` expressions are resolved; render through Astro's
// container API if the banner ever needs more than that.
const bannerSource = source.match(/<p\s+id="ttod-network-boundary"[\s\S]*?<\/p>/)![0];
const scriptSource = source.match(/<script>([\s\S]*?)<\/script>/)![1];

function mountBanner(lang: 'en' | 'es') {
  const online = vi.spyOn(navigator, 'onLine', 'get').mockReturnValue(true);
  document.body.innerHTML = bannerSource.replace(
    /\{lang === 'es' \? '([^']*)' : '([^']*)'\}/g,
    (_, es: string, en: string) => `"${lang === 'es' ? es : en}"`,
  );
  // jsdom has no navigator.serviceWorker, so the script's worker registration is skipped.
  new Function(scriptSource)();

  const setOnline = (value: boolean) => {
    online.mockReturnValue(value);
    window.dispatchEvent(new Event(value ? 'online' : 'offline'));
  };

  return { banner: document.getElementById('ttod-network-boundary')!, setOnline };
}

afterEach(() => vi.restoreAllMocks());

describe.each(['en', 'es'] as const)('network boundary banner (%s)', (lang) => {
  it('follows simulated offline and online events', () => {
    const { banner, setOnline } = mountBanner(lang);
    expect(banner.dataset.state).toBe('online');

    setOnline(false);
    expect(banner.dataset.state).toBe('offline');

    setOnline(true);
    expect(banner.dataset.state).toBe('online');
  });

  it('announces each state as text in a polite status region', () => {
    const { banner, setOnline } = mountBanner(lang);

    for (const state of ['offline', 'online'] as const) {
      setOnline(state === 'online');
      // The state is readable text, not colour alone, and the live region is unchanged.
      expect(banner.textContent).toBe(labels[lang][state]);
      expect(banner.getAttribute('role')).toBe('status');
      expect(banner.getAttribute('aria-live')).toBe('polite');
    }
  });
});