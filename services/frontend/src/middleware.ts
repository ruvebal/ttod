import { defineMiddleware } from 'astro:middleware';
import { destinoDe } from './lib/locators';

// Una sola puerta para las direcciones permanentes (LOCATORS.md §3): la regla vive
// en `lib/locators.ts`, donde se prueba sin servidor.
export const onRequest = defineMiddleware((context, next) => {
  const destino = destinoDe(context.request);
  if (destino) return new Response(null, { status: 301, headers: { Location: destino } });
  return next();
});
