/**
 * Where the backend lives, read **at request time** (AA7). From Astro 6 on, `import.meta.env.X` is
 * inlined when the site is built, so a server-only setting such as BACKEND_URL would freeze at build
 * time. Compose happens to build and run with the same value, but a stack that sets it only at runtime
 * would silently talk to the wrong place. `process.env` is the running server's own environment.
 */
const PREDETERMINADO = 'http://backend:8000';

export function backendUrl(): string {
  return (process.env.BACKEND_URL ?? '').trim().replace(/\/+$/, '') || PREDETERMINADO;
}
