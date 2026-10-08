const CACHE_PREFIX = 'ttod-pwa-stub-';
const CACHE_NAME = `${CACHE_PREFIX}v3`;
const PROOF_ASSET = '/visual-system/tokens.css';

const OFFLINE_PAGES = ['/en/oracle', '/es/oracle'];
const STATIC_ASSETS = [
  PROOF_ASSET,
  '/visual-system/backgrounds.css',
  '/visual-system/favicon.svg',
];

function assetReferences(text, baseUrl) {
  const references = new Set();
  const add = (value) => {
    const url = new URL(value, baseUrl);
    if (
      url.origin === self.location.origin &&
      (url.pathname.startsWith('/_astro/') ||
        url.pathname.startsWith('/visual-system/')) &&
      /\.(css|js|svg)$/.test(url.pathname)
    ) {
      references.add(url.href);
    }
  };

  // Find this app's quoted HTML asset URLs and JS module references.
  for (const match of text.matchAll(/["']([^"'<>\s]+\.(?:css|js|svg)(?:\?[^"'<>\s]*)?)["']/g)) {
    add(match[1]);
  }
  // CSS also permits unquoted url(...) references.
  for (const match of text.matchAll(/url\(\s*["']?([^\s)"']+)["']?\s*\)/g)) {
    add(match[1]);
  }
  return references;
}

async function precacheOracle(cache) {
  const pending = [...OFFLINE_PAGES, ...STATIC_ASSETS]
    .map((path) => new URL(path, self.location.origin).href);
  const visited = new Set();

  while (pending.length > 0) {
    const url = pending.pop();
    if (visited.has(url)) continue;
    visited.add(url);

    const response = await fetch(url, { cache: 'no-store' });
    if (!response.ok) throw new Error(`Precache failed: ${url} (${response.status})`);
    await cache.put(url, response.clone());

    const type = response.headers.get('content-type') ?? '';
    if (/(html|css|javascript)/.test(type)) {
      const text = await response.text();
      pending.push(...assetReferences(text, response.url));
    }
  }
}

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    await precacheOracle(cache);
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    // Retire previous PWA versions, preserving unrelated caches.
    await Promise.all(names
      .filter((name) => name.startsWith(CACHE_PREFIX) && name !== CACHE_NAME)
      .map((name) => caches.delete(name)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.origin !== self.location.origin) return;

  const selectedPage = OFFLINE_PAGES.includes(url.pathname);
  const staticAsset = url.pathname.startsWith('/_astro/') ||
    url.pathname.startsWith('/visual-system/');
  if (!selectedPage && !staticAsset) return;

  event.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME);
    const cached = await cache.match(event.request);
    return cached ?? fetch(event.request);
  })());
});