import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

// Route/i18n integration coverage for the reference build (R1/R2/R3a + R3b/R4/R5), folding
// @axe-core/playwright assertions into the normal suite per
// docs/DEV_PLAN/PHASES/R7-testing-strategy.md §2.2 — accessibility is not a separate audit.
//
// Requires the full local stack already running: frontend (this build), backend (:8000), mcp
// (:3001), and bare-metal Ollama (:11434) with qwen3.8:27b + nomic-embed-text pulled. See
// docs/DEV_PLAN/PHASE-R-CLOSURE-AND-COHORT-HANDOFF-REPORT.md for the exact commands used to bring
// this stack up locally for this test run.

test.describe('default-locale fallback', () => {
	test('/ redirects to the default locale', async ({ page }) => {
		const response = await page.goto('/');
		expect(response?.status()).toBeLessThan(400);
		await expect(page).toHaveURL(/\/en\/?$/);
		await expect(page.locator('html')).toHaveAttribute('lang', 'en');
	});
});

for (const locale of ['en', 'es'] as const) {
	test.describe(`locale: ${locale}`, () => {
		test(`/${locale}/ resolves and declares its own lang`, async ({ page }) => {
			const response = await page.goto(`/${locale}/`);
			expect(response?.status()).toBe(200);
			await expect(page.locator('html')).toHaveAttribute('lang', locale);
		});

		test(`/${locale}/ has no detectable axe violations`, async ({ page }) => {
			await page.goto(`/${locale}/`);
			const results = await new AxeBuilder({ page }).analyze();
			expect(results.violations, JSON.stringify(results.violations, null, 2)).toEqual([]);
		});

		test(`/${locale}/quote renders a live quote through the full pipeline`, async ({ page }) => {
			const response = await page.goto(`/${locale}/quote`);
			expect(response?.status()).toBe(200);
			const results = await new AxeBuilder({ page }).analyze();
			expect(results.violations, JSON.stringify(results.violations, null, 2)).toEqual([]);
		});

		test(`/${locale}/wisdom index renders and passes axe`, async ({ page }) => {
			const response = await page.goto(`/${locale}/wisdom`);
			expect(response?.status()).toBe(200);
			const results = await new AxeBuilder({ page }).analyze();
			expect(results.violations, JSON.stringify(results.violations, null, 2)).toEqual([]);
		});

		test(`/${locale}/docs index renders and passes axe`, async ({ page }) => {
			const response = await page.goto(`/${locale}/docs`);
			expect(response?.status()).toBe(200);
			const results = await new AxeBuilder({ page }).analyze();
			expect(results.violations, JSON.stringify(results.violations, null, 2)).toEqual([]);
		});

		test(`/${locale}/graph shell renders and passes axe on initial load`, async ({ page }) => {
			const response = await page.goto(`/${locale}/graph`);
			expect(response?.status()).toBe(200);
			const results = await new AxeBuilder({ page }).analyze();
			expect(results.violations, JSON.stringify(results.violations, null, 2)).toEqual([]);
		});

		test(`/${locale}/oracle terminal shell renders and passes axe before any query`, async ({ page }) => {
			const response = await page.goto(`/${locale}/oracle`);
			expect(response?.status()).toBe(200);
			const results = await new AxeBuilder({ page }).analyze();
			expect(results.violations, JSON.stringify(results.violations, null, 2)).toEqual([]);
		});
	});
}
