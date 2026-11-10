import { describe, expect, it } from 'vitest';

import { cookieSecure, cookieSecureMode } from './cookie-security';

const http = (headers: Record<string, string> = {}) => new Request('http://tanit.lan:18080/es/login/', { headers });

describe('cookie Secure (F22)', () => {
  it('auto: plain HTTP on a LAN host is not Secure, so the browser keeps the cookie', () => {
    expect(cookieSecure(http(), 'auto')).toBe(false);
    expect(cookieSecure(http({ 'x-forwarded-proto': 'http' }), 'auto')).toBe(false);
  });

  it('auto: Secure when the edge says the request arrived over https', () => {
    expect(cookieSecure(http({ 'x-forwarded-proto': 'https' }), 'auto')).toBe(true);
    expect(cookieSecure(new Request('https://ttod.example/es/login/'), 'auto')).toBe(true);
  });

  it('true/false override the request', () => {
    expect(cookieSecure(http(), 'true')).toBe(true);
    expect(cookieSecure(http({ 'x-forwarded-proto': 'https' }), 'false')).toBe(false);
  });

  it('reads COOKIE_SECURE leniently and defaults to auto', () => {
    expect(cookieSecureMode('TRUE')).toBe('true');
    expect(cookieSecureMode('0')).toBe('false');
    expect(cookieSecureMode(undefined)).toBe('auto');
    expect(cookieSecureMode('nonsense')).toBe('auto');
  });
});
