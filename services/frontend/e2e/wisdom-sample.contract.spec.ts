import { expect, test } from '@playwright/test';

// Live R3a contract smoke. Hits GET /api/v1/wisdom/sample and asserts WisdomEntry *shape*
// (domain.ts), never quote values, and never opens repository-root ttod.yml.
// If the stack is down this test skips instead of mocking the corpus.

const LEVELS = new Set(['beginner', 'intermediate', 'advanced', 'master']);
const ORIGINS = new Set(['human', 'studio', 'blackbox', 'mixed', 'legacy-unknown']);

const BACKEND_CANDIDATES = [
  process.env.E2E_BACKEND_URL,
  process.env.E2E_BASE_URL,
  'http://127.0.0.1:18080',
  'http://127.0.0.1:8080',
  'http://127.0.0.1:8000',
].filter((value): value is string => Boolean(value));

async function liveBackendOrigin(): Promise<string | undefined> {
  for (const origin of BACKEND_CANDIDATES) {
    try {
      const response = await fetch(new URL('/health', origin), {
        headers: { accept: 'application/json' },
        signal: AbortSignal.timeout(2500),
      });
      if (response.ok) return origin.replace(/\/$/, '');
    } catch {
      // Try the next published origin. Do not read ttod.yml as a fallback.
    }
  }
  return undefined;
}

function assertWisdomEntryShape(entry: unknown, index: number): void {
  expect(entry, `entry ${index}`).toEqual(expect.any(Object));
  const record = entry as Record<string, unknown>;
  expect(typeof record.id).toBe('string');
  expect(typeof record.section).toBe('string');
  expect(LEVELS.has(record.level as string), `entry ${index} level`).toBe(true);
  expect(typeof record.text).toBe('string');
  expect(typeof record.teaches).toBe('string');
  expect(Array.isArray(record.tags)).toBe(true);
  expect((record.tags as unknown[]).every((tag) => typeof tag === 'string')).toBe(true);
  expect(Array.isArray(record.related)).toBe(true);
  expect((record.related as unknown[]).every((id) => typeof id === 'string')).toBe(true);
  expect(ORIGINS.has(record.origin as string), `entry ${index} origin`).toBe(true);
  expect(typeof record.lang).toBe('string');
  expect(record.rights).toEqual(expect.any(Object));
  const rights = record.rights as Record<string, unknown>;
  expect(typeof rights.license).toBe('string');
  expect(rights.license).not.toBe('');
  if (record.subsection !== undefined) expect(typeof record.subsection).toBe('string');
  if (rights.holder !== undefined) expect(typeof rights.holder).toBe('string');
}

test('GET /api/v1/wisdom/sample matches WisdomEntry shape', async ({ request }) => {
  const origin = await liveBackendOrigin();
  test.skip(
    !origin,
    'R3a backend unreachable — live stack required. Not mocked; ttod.yml is not a test fixture. Treat this layer as PARTIAL until Compose is up.',
  );

  const response = await request.get(`${origin}/api/v1/wisdom/sample`, {
    headers: { accept: 'application/json' },
  });
  expect(response.ok(), `status ${response.status()}`).toBe(true);

  const payload: unknown = await response.json();
  expect(Array.isArray(payload)).toBe(true);
  expect((payload as unknown[]).length).toBeGreaterThan(0);
  for (const [index, entry] of (payload as unknown[]).entries()) {
    assertWisdomEntryShape(entry, index);
  }
});
