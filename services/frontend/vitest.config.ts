/// <reference types="vitest/config" />
import { getViteConfig } from 'astro/config';

// getViteConfig so Page.astro can render through AstroContainer in the hello-world
// component test. layout.test.mjs stays on node:test (existing convention).
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

