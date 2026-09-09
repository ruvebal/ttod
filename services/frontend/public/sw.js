/**
 * TTOD FE II — PWA hello-world stub.
 *
 * This worker is a seam, not the assignment. It logs the service-worker
 * lifecycle (install / activate / fetch) and Cache-First-caches exactly one
 * static asset so a learner can watch a cache hit in DevTools.
 *
 * STUDENT ASSIGNMENT (not implemented here):
 *   - Cache-First for the full static asset set
 *   - Network-First for `/api/*` (fetch, fall back to cache — never Cache-First
 *     for API responses, even in a stub)
 *
 * Do not replace this file with a framework-generated black-box worker unless
 * that choice is documented explicitly in ASSIGNMENT.md. Do not add a deploy job.
 */

const CACHE_NAME = 'ttod-pwa-stub-v1';
const PROOF_ASSET = '/visual-system/tokens.css';

self.addEventListener('install', (event) => {
  console.info('[ttod-sw] install');
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => cache.add(PROOF_ASSET))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener('activate', (event) => {
  console.info('[ttod-sw] activate');
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((key) => key !== CACHE_NAME)
            .map((key) => caches.delete(key)),
        ),
      )
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  console.info('[ttod-sw] fetch', event.request.method, url.pathname);

  if (event.request.method !== 'GET' || url.origin !== self.location.origin) {
    return;
  }

  // Even a stub must not teach Cache-First for API traffic.
  if (url.pathname.startsWith('/api/')) {
    console.info('[ttod-sw] skip /api/* (assignment: Network-First — not implemented here)');
    return;
  }

  if (url.pathname !== PROOF_ASSET) {
    return;
  }

  event.respondWith(cacheFirst(event.request));
});

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) {
    console.info('[ttod-sw] cache-hit', PROOF_ASSET);
    return cached;
  }
  console.info('[ttod-sw] cache-miss', PROOF_ASSET);
  const response = await fetch(request);
  if (!response.ok) {
    return response;
  }
  const cache = await caches.open(CACHE_NAME);
  await cache.put(request, response.clone());
  return response;
}
