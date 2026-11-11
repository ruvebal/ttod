import { defineMiddleware } from 'astro:middleware';
import { redireccionLocator } from './lib/locators';

// Una sola puerta para las direcciones permanentes (LOCATORS.md §3): la regla vive
// en `lib/locators.ts`, donde se prueba sin servidor.
export const onRequest = defineMiddleware((context, next) => {
  // The request's own URL, not `context.url`: since Astro 7 `context.url` arrives normalized, so a raw
  // `//evil.example/x` reads as `/evil.example/x` and the open-redirect guard in lib/locators.ts could
  // not see it (found by re-running the AA3b gate in AA7). `request.url` keeps the path as sent.
  const destino = redireccionLocator(context.request.method, new URL(context.request.url));
  if (destino) return new Response(null, { status: 301, headers: { Location: destino } });
  return next();
});
