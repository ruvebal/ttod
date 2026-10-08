import { readFile } from 'node:fs/promises';
import { test, expect, type Page, type Route, type APIRequestContext } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import type { OfflineLogEntry, OracleQueryPayload } from '../src/types/domain';

// Real built Oracle + real service worker + real IndexedDB. Only the response
// endpoint is controlled, so queue regressions do not depend on model inference.
// Strategy: https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/
async function records(page: Page): Promise<{ version: number; entries: OfflineLogEntry[] }> {
  return page.evaluate(() => new Promise((resolve, reject) => {
    const open = indexedDB.open('ttod-oracle');
    open.onerror = () => reject(open.error);
    open.onsuccess = () => {
      const db = open.result;
      const tx = db.transaction('offline-log');
      const read = tx.objectStore('offline-log').getAll();
      tx.oncomplete = () => {
        const version = db.version;
        db.close();
        resolve({ version, entries: read.result });
      };
      tx.onabort = () => { db.close(); reject(tx.error); };
    };
  }));
}

async function install(page: Page, request: APIRequestContext, locale = 'en') {
  const served = await request.get('/sw.js');
  expect(served.status()).toBe(200);
  expect(await served.text(), 'Rebuild the frontend: the served worker must match source')
    .toBe(await readFile(new URL('../public/sw.js', import.meta.url), 'utf8'));
  // The docs page renders without the backend and does not open the Oracle DB.
  await page.goto(`/${locale}/docs/`);
  await expect.poll(() => page.evaluate(() => Boolean(navigator.serviceWorker.controller))).toBe(true);
}

async function openOracle(page: Page, locale: 'en' | 'es') {
  await page.goto(`/${locale}/oracle`);
  const close = page.getByRole('button', { name: locale === 'en' ? 'Close oracle' : 'Cerrar oráculo', exact: true });
  await close.click();
  await page.getByRole('button', { name: locale === 'en' ? 'Open oracle' : 'Abrir oráculo', exact: true }).click();
}

async function answer(route: Route, payload: OracleQueryPayload) {
  await route.fulfill({
    status: 200, contentType: 'text/event-stream',
    body: `data: ${JSON.stringify({ mode: 'grounded', text: `Answer to ${payload.query}`, citedQuoteIds: [] })}\n\n`,
  });
}

for (const locale of ['en', 'es'] as const) {
  test(`${locale}: offline UI submissions survive reload, replay sequentially and exclude competing tabs`, async ({ page, context, request }) => {
    await install(page, request, locale);
    await openOracle(page, locale);
    await page.clock.setFixedTime(new Date('2026-10-07T10:00:00.000Z'));
    await context.setOffline(true);
    const questions = ['Question A', 'Question B'];
    for (const query of questions) {
      await page.getByRole('textbox').fill(query);
      await page.getByRole('button', { name: locale === 'en' ? 'Ask' : 'Preguntar', exact: true }).click();
      await expect.poll(async () => (await records(page)).entries.some((entry) =>
        entry.kind === 'oracle-query' && (entry.payload as OracleQueryPayload).query === query && !entry.synced,
      )).toBe(true);
    }
    const queued = (await records(page)).entries.sort((a, b) => a.queueOrder! - b.queueOrder!);
    expect(queued.map((entry) => (entry.payload as OracleQueryPayload).query)).toEqual(questions);
    expect(queued[0].timestamp).toBe(queued[1].timestamp);
    expect(queued[0].queueOrder!).toBeLessThan(queued[1].queueOrder!);
    const reload = await page.reload();
    expect(reload?.status()).toBe(200);
    expect(reload?.fromServiceWorker()).toBe(true);
    await expect(page.locator('#ttod-network-boundary')).toHaveAttribute('data-state', 'offline');
    expect((await records(page)).entries.sort((a, b) => a.queueOrder! - b.queueOrder!)).toEqual(queued);

    const sent: OracleQueryPayload[] = [];
    let release!: () => void;
    const firstResponse = new Promise<void>((resolve) => { release = resolve; });
    await context.route('**/api/v1/oracle/stream', async (route) => {
      const payload = route.request().postDataJSON() as OracleQueryPayload;
      sent.push(payload);
      if (sent.length === 1) await firstResponse;
      await answer(route, payload);
    });
    try {
      await context.setOffline(false);
      await expect.poll(() => sent.length).toBe(1);
      expect(sent[0]).toEqual({ query: questions[0], sessionHistory: [], locale });
      expect((await records(page)).entries.every((entry) => !entry.synced)).toBe(true);
      await page.evaluate(() => {
        window.dispatchEvent(new Event('online'));
        window.dispatchEvent(new Event('online'));
      });
      const secondPage = await context.newPage();
      await openOracle(secondPage, locale);
      await expect(secondPage.getByText(locale === 'en' ? 'Retrying queued queries…' : 'Reintentando consultas guardadas…')).toHaveCount(0);
      expect(sent).toHaveLength(1);
      release();
      await expect.poll(async () => (await records(page)).entries.filter((entry) => entry.synced).length).toBe(2);
      expect(sent).toEqual(questions.map((query) => ({ query, sessionHistory: [], locale })));
      expect((await records(page)).entries.sort((a, b) => a.queueOrder! - b.queueOrder!))
        .toEqual(queued.map((entry) => ({ ...entry, synced: true })));
      await context.setOffline(true);
      await context.setOffline(false);
      // Observe the entire idle window, rather than checking immediately before
      // a duplicate async sender has had a chance to run.
      await page.waitForTimeout(500);
      expect(sent).toHaveLength(2);
      await secondPage.close();
      expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
    } finally { release(); await context.setOffline(false); }
  });
}

for (const failure of ['http-503', 'empty-stream', 'invalid-stream', 'synced-transaction-abort'] as const) {
  test(`version-1 migration preserves entries; ${failure} retains ordered work until a later reconnect`, async ({ page, context, request }) => {
    await install(page, request);
    const seed: OfflineLogEntry[] = [
      { id: 'legacy-z', timestamp: '2026-10-01T00:00:00.000Z', kind: 'oracle-query', payload: { query: 'Legacy B', sessionHistory: [], locale: 'en' }, synced: false },
      { id: 'legacy-a', timestamp: '2026-10-01T00:00:00.000Z', kind: 'oracle-query', payload: { query: 'Legacy A', sessionHistory: [], locale: 'en' }, synced: false },
      { id: 'legacy-synced', timestamp: '2026-09-30T00:00:00.000Z', kind: 'oracle-query', payload: { query: 'Already done', sessionHistory: [], locale: 'en' }, synced: true },
      { id: 'legacy-error', timestamp: '2026-09-29T00:00:00.000Z', kind: 'error-report', payload: { errorLog: 'Retain this report' }, synced: false },
    ];
    await page.evaluate((entries) => new Promise<void>((resolve, reject) => {
      const open = indexedDB.open('ttod-oracle', 1);
      open.onupgradeneeded = () => {
        open.result.createObjectStore('offline-log', { keyPath: 'id' }).createIndex('synced', 'synced', { unique: false });
      };
      open.onerror = () => reject(open.error);
      open.onsuccess = () => {
        const db = open.result;
        const tx = db.transaction('offline-log', 'readwrite');
        for (const entry of entries) tx.objectStore('offline-log').put(entry);
        tx.oncomplete = () => { db.close(); resolve(); };
        tx.onabort = () => { db.close(); reject(tx.error); };
      };
    }), seed);
    if (failure === 'synced-transaction-abort') {
      await page.addInitScript(() => {
        const put = IDBObjectStore.prototype.put;
        let abortOnce = true;
        IDBObjectStore.prototype.put = function (value, key) {
          const result = put.call(this, value, key);
          if (abortOnce && value.id === 'legacy-a' && value.synced === true) {
            abortOnce = false;
            result.addEventListener('success', () => this.transaction.abort(), { once: true });
          }
          return result;
        };
      });
    }
    let fail = true;
    let release!: () => void;
    const inspectMigration = new Promise<void>((resolve) => { release = resolve; });
    const sent: string[] = [];
    await page.route('**/api/v1/oracle/stream', async (route) => {
      const payload = route.request().postDataJSON() as OracleQueryPayload;
      sent.push(payload.query);
      if (sent.length === 1) await inspectMigration;
      if (fail && failure === 'http-503') await route.fulfill({ status: 503, body: 'Temporary failure' });
      else if (fail && failure === 'empty-stream') await route.fulfill({ status: 200, contentType: 'text/event-stream', body: '' });
      else if (fail && failure === 'invalid-stream') await route.fulfill({ status: 200, contentType: 'text/event-stream', body: 'data: {"unexpected":true}\n\n' });
      else await answer(route, payload);
    });
    try {
      await openOracle(page, 'en');
      await expect.poll(() => sent.length).toBe(1);
      const migrated = await records(page);
      expect(migrated.version).toBeGreaterThanOrEqual(2);
      expect(migrated.entries).toHaveLength(seed.length);
      for (const entry of migrated.entries) {
        const { queueOrder, ...original } = entry;
        expect(original).toEqual(seed.find((item) => item.id === entry.id));
        expect(queueOrder).toEqual(expect.any(Number));
      }
      expect([...migrated.entries].sort((a, b) => a.queueOrder! - b.queueOrder!).map((entry) => entry.id))
        .toEqual(['legacy-error', 'legacy-synced', 'legacy-a', 'legacy-z']);
      release();
      // Team 3 #42 uses an unavailable notice for HTTP 5xx; queue integrity is unchanged.
      const failureNotice = failure === 'http-503'
        ? /^(A queued query could not be retried yet\.|The Oracle is currently unavailable\. Please try again\.)$/
        : 'A queued query could not be retried yet.';
      await expect(page.getByText(failureNotice)).toBeVisible();
      await page.waitForTimeout(600);
      expect(sent).toEqual(['Legacy A']);
      expect((await records(page)).entries.filter((entry) => ['legacy-a', 'legacy-z'].includes(entry.id))
        .every((entry) => !entry.synced)).toBe(true);
      fail = false;
      await context.setOffline(true);
      await context.setOffline(false);
      await expect.poll(async () => (await records(page)).entries.filter((entry) =>
        ['legacy-a', 'legacy-z'].includes(entry.id) && entry.synced,
      ).length).toBe(2);
      expect(sent).toEqual(['Legacy A', 'Legacy A', 'Legacy B']);
      const retained = (await records(page)).entries.find((entry) => entry.id === 'legacy-error');
      expect(retained).toMatchObject({ synced: false, payload: { errorLog: 'Retain this report' } });
    } finally { release(); await context.setOffline(false); }
  });
}
