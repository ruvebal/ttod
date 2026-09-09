import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';

// Hello-world accessibility assertion: one rendered route, chromium only, axe in-suite.
// /en/docs/ is R3a's docs index — it does not fetch the governed corpus, so it can run
// against a frontend-only server when the backend is down. If no frontend is reachable,
// skip honestly rather than pointing axe at a fixture HTML file.

const FRONTEND_CANDIDATES = [
  process.env.E2E_BASE_URL,
  'http://127.0.0.1:18080',
  'http://127.0.0.1:8080',
  'http://127.0.0.1:4321',
].filter((value): value is string => Boolean(value));

async function liveDocsUrl(): Promise<string | undefined> {
  for (const origin of FRONTEND_CANDIDATES) {
    try {
      const docs = new URL('/en/docs/', origin).href;
      const response = await fetch(docs, { signal: AbortSignal.timeout(2500) });
      if (response.ok) return docs;
    } catch {
      // Try the next published origin.
    }
  }
  return undefined;
}

test('/en/docs/ has no detectable axe violations', async ({ page }) => {
  const docsUrl = await liveDocsUrl();
  test.skip(
    !docsUrl,
    'Frontend unreachable — live rendered route required. Treat this a11y layer as PARTIAL until the stack or `npm start` is up.',
  );

  const response = await page.goto(docsUrl as string);
  expect(response?.status()).toBe(200);
  await expect(page.locator('html')).toHaveAttribute('lang', 'en');
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible();

  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations, JSON.stringify(results.violations, null, 2)).toEqual([]);
});
