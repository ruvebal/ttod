import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    exclude: [
      'node_modules/**',
      'dist/**',
      'src/components/graph/layout.test.mjs'
    ]
  }
});
