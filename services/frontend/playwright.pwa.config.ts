import { defineConfig } from '@playwright/test';
import base from './playwright.config';

// Isolated built frontend: Oracle/docs SSR does not require inference. Controlled
// SSE responses exercise queue behavior without Docker, models, or credentials.
const origin = 'http://127.0.0.1:4327';
export default defineConfig(base, {
  testMatch: /pwa-queue-reconnect\.spec\.ts/,
  fullyParallel: false,
  workers: 1,
  retries: 0,
  outputDir: 'test-results/pwa-browser',
  reporter: [['list'], ['json', { outputFile: 'test-results/pwa-guard/browser-results.json' }]],
  use: { ...base.use, baseURL: origin },
  webServer: {
    command: 'node ./dist/server/entry.mjs',
    env: { HOST: '127.0.0.1', PORT: '4327', NODE_ENV: 'production', ASTRO_TELEMETRY_DISABLED: '1' },
    url: `${origin}/en/docs/`,
    reuseExistingServer: false,
    timeout: 30000,
  },
});
