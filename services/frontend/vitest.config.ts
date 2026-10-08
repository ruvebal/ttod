/// <reference types="vitest/config" />
import { getViteConfig } from 'astro/config';

// getViteConfig (not a bare defineConfig) so vitest can resolve `.astro` imports: the facet-route
// tests in src/tests/ render real pages through Astro's container API.
export default getViteConfig({
  test: {
    exclude: [
      'node_modules/**',
      'dist/**',
      'e2e/**',
      'src/components/graph/layout.test.mjs'
    ]
  }
});
