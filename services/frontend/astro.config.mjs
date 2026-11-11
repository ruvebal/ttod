import { defineConfig } from 'astro/config';
import node from '@astrojs/node';
import mdx from '@astrojs/mdx';
import react from '@astrojs/react';
import svelte from '@astrojs/svelte';
import tailwindcss from '@tailwindcss/vite';

// F23 (Phase AA2): the other hostnames a classroom reaches TTOD by (LAN name, public domain).
// Comma-separated, hostnames only, read at BUILD time (the Docker build receives it as a build
// arg): TTOD_ALLOWED_HOSTS=tanit.crea-comm.loc,ttod.example.org. Without an entry, Astro does not
// trust that Host header and refuses form POSTs from it with 403.
const extraHosts = (process.env.TTOD_ALLOWED_HOSTS ?? '')
  .split(',')
  .map((host) => host.trim())
  .filter(Boolean);
for (const host of extraHosts) {
  if (!/^[a-z0-9.-]+$/i.test(host)) {
    throw new Error(`TTOD_ALLOWED_HOSTS entry "${host}" must be a bare hostname (no scheme, port or path)`);
  }
}

export default defineConfig({
  output: 'server',
  // El CSS de cada vista va dentro del HTML en vez de en un <link> que bloquea el
  // pintado. Medido con Lighthouse móvil (mediana de 3, detrás de Caddy): primer
  // pintado /es/docs 1219 -> 1066 ms, /es/login 1385 -> 1069, /es/wisdom 1534 -> 1225,
  // portada 1651 -> 1476. Los bytes de la primera visita son los mismos (8-20 KB gzip
  // de CSS); lo que se pierde es la caché del CSS entre vistas: cada navegación los
  // vuelve a traer dentro del HTML (~20-40 ms a 4 Mb/s). Capturas idénticas (0 %).
  build: { inlineStylesheets: 'always' },
  // AA7: Astro 7 changed the default to 'jsx', which strips whitespace between inline elements
  // ("Biblioteca Ada EN" would run together). Keep the Astro 5/6 behaviour until each view is
  // compared; changing it is a separate, screenshot-checked decision.
  compressHTML: true,
  adapter: node({ mode: 'standalone' }),
  integrations: [mdx(), react(), svelte()],
  i18n: {
    locales: ['en', 'es'],
    defaultLocale: 'en',
    // Explicit since Astro 6 changed the default (AA7). The root `/` is redirected by pages/index.astro.
    routing: { prefixDefaultLocale: true, redirectToDefaultLocale: false }
  },
  server: { host: true, port: 4321 },
  // El formulario de login hace POST: sin esto el build de Node no confía en la cabecera Host,
  // toma el origen como `http://localhost` sin puerto y rechaza con 403 el POST del stack local.
  security: {
    allowedDomains: [{ hostname: 'localhost' }, { hostname: '127.0.0.1' }, ...extraHosts.map((hostname) => ({ hostname }))]
  },
  vite: {
    plugins: [tailwindcss()],
    // Solo en dev: Caddy no existe fuera de Docker, así que el fetch del navegador
    // a /api y /health se reenvía al backend local, igual que hace el Caddyfile.
    server: {
      proxy: {
        '/api': process.env.BACKEND_URL ?? 'http://127.0.0.1:8000',
        '/health': process.env.BACKEND_URL ?? 'http://127.0.0.1:8000'
      }
    }
  }
});
