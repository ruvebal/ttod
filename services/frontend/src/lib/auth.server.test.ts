import { describe, expect, it } from 'vitest';

import { requireUser } from './auth.server';

const req = (headers: Record<string, string> = {}) => new Request('http://localhost/', { headers });

describe('requireUser (session stub)', () => {
  it('returns null when there is no cookie and no Authorization header', () => {
    expect(requireUser(req())).toBeNull();
  });

  it('reads the userId from a ttod_session cookie carrying JSON claims', () => {
    const cookie = `ttod_session=${encodeURIComponent(JSON.stringify({ userId: 'demo-student' }))}`;
    expect(requireUser(req({ cookie }))).toBe('demo-student');
  });

  it('falls back to the raw cookie value when it is not JSON (same fallback as the real file)', () => {
    expect(requireUser(req({ cookie: 'ttod_session=plain-user-id' }))).toBe('plain-user-id');
  });

  it('reads a Bearer token from the Authorization header when there is no cookie', () => {
    expect(requireUser(req({ authorization: 'Bearer plain-user-id' }))).toBe('plain-user-id');
  });

  it('reads JSON claims from a Bearer token', () => {
    expect(requireUser(req({ authorization: `Bearer ${JSON.stringify({ userId: 'bearer-user' })}` }))).toBe('bearer-user');
  });

  it('never throws on a malformed cookie', () => {
    expect(() => requireUser(req({ cookie: 'ttod_session={not json' }))).not.toThrow();
  });

  it('ignores a userId claim that is not a string', () => {
    const cookie = `ttod_session=${encodeURIComponent(JSON.stringify({ userId: 42 }))}`;
    expect(requireUser(req({ cookie }))).toBeNull();
  });
});
