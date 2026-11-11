import { afterEach, describe, expect, it, vi } from 'vitest';

import { backendUrl } from './backend';

afterEach(() => vi.unstubAllEnvs());

describe('backendUrl (AA7: read at request time, not inlined at build)', () => {
  it('follows the running process environment, read on every call', () => {
    vi.stubEnv('BACKEND_URL', 'http://one:8000');
    expect(backendUrl()).toBe('http://one:8000');
    vi.stubEnv('BACKEND_URL', 'http://two:9000/');
    expect(backendUrl()).toBe('http://two:9000');
  });
  it('falls back to the Compose service when unset or blank', () => {
    vi.stubEnv('BACKEND_URL', '  ');
    expect(backendUrl()).toBe('http://backend:8000');
  });
});
