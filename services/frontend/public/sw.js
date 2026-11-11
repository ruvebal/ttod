const CACHE_PREFIX = 'ttod-pwa-stub-';
/* v6: cacheFirst sobre /visual-system/ conserva un fichero viejo bajo el mismo
   nombre; subir la versión purga las pinturas de la portada anterior.
   v7 (AA3b): las páginas acaban en barra; la forma sin barra es un 301, y una
   respuesta redirigida guardada en caché no sirve para una navegación.
   v8 (AA3, cold review F1): la cabecera cambia con la sesión, así que estas páginas
   se guardan sin cookies y se sirven de la red primero. Subir la versión purga las
   copias que guardó la v7, que podían llevar el nombre de quien estaba dentro. */
const CACHE_NAME = `${CACHE_PREFIX}v8`;
const PROOF_ASSET = '/visual-system/tokens.css';

const OFFLINE_PAGES = ['/en/oracle/', '/es/oracle/'];
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

  // Find this app's quoted HTML asset URLs and JS module references. Only values that
  // look like a path or URL: minified libraries (GSAP) carry quoted code fragments
  // that end in ".svg" too, and fetching those made the whole precache fail.
  for (const match of text.matchAll(/["']((?:\/|\.\.?\/|https?:)[^"'<>\s(){},;]+\.(?:css|js|svg)(?:\?[^"'<>\s]*)?)["']/g)) {
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

    // Sin cookies: lo que se guarda es la página de un visitante anónimo, nunca la de
    // quien tenga la sesión abierta en ese momento (su nombre, su biblioteca).
    const response = await fetch(url, { cache: 'no-store', credentials: 'omit' });
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

async function storeResponse(cache, request, response) {
  // Store successful, complete responses.
  if (!response.ok || response.status === 206) return;

  try {
    await cache.put(request, response.clone());
  } catch (error) {
    console.warn('PWA cache write failed:', error);
  }
}

async function cacheFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);

  if (cached) return cached;

  const response = await fetch(request);
  await storeResponse(cache, request, response);
  return response;
}

/**
 * Las páginas sin conexión (el oráculo): de la red primero, con la sesión de verdad;
 * la copia anónima guardada solo si no hay red. La respuesta con cookies no se guarda
 * nunca: en un navegador compartido de clase, el siguiente vería al anterior.
 */
async function paginaSinConexion(request) {
  try {
    return await fetch(request, { cache: 'no-store' });
  } catch (error) {
    const cache = await caches.open(CACHE_NAME);
    const cached = await cache.match(new URL(request.url).pathname);
    if (cached) return cached;
    throw error;
  }
}

async function networkFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  let response;

  try {
    // Attempt a fresh request instead of using the browser HTTP cache.
    response = await fetch(request, { cache: 'no-store' });
  } catch (error) {
    const cached = await cache.match(request);

    if (cached) return cached;
    throw error;
  }

  // Return HTTP errors normally; fallback is for network failures.
  await storeResponse(cache, request, response);
  return response;
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);

  if (
    request.method !== 'GET' ||
    url.origin !== self.location.origin
  ) {
    return;
  }

  // API data should be fresh whenever the network is available.
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request));
    return;
  }

  const selectedPage = OFFLINE_PAGES.includes(url.pathname);

  const staticAsset =
    url.pathname.startsWith('/_astro/') ||
    url.pathname.startsWith('/visual-system/') ||
    url.pathname.startsWith('/assets/');

  // Task 2's offline pages: network first, anonymous copy offline (AA3). Static assets: cache first.
  if (selectedPage) {
    event.respondWith(paginaSinConexion(request));
  } else if (staticAsset) {
    event.respondWith(cacheFirst(request));
  }
});
