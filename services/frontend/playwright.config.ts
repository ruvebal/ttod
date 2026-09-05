import { defineConfig, devices } from '@playwright/test';

// Chromium only, per docs/DEV_PLAN/PHASES/R7-testing-strategy.md §2.2 — Firefox/WebKit are not
// required unless a cross-browser bug is filed. Runs against an already-running local stack
// (frontend + backend + mcp, Ollama bare-metal) — this suite does not start those services
// itself, since the full stack (see docker-compose.yml / R3a onboarding) is a precondition, not
// something a browser-automation config should own.
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: 'list',
  use: {
    baseURL: process.env.E2E_BASE_URL ?? 'http://localhost:4321',
    trace: 'retain-on-failure'
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    }
  ]
});
