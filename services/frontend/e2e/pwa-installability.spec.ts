import { test, expect, type APIRequestContext } from '@playwright/test';

// Metadata/asset checks support, but do not replace, a real browser installation.
// Strategy: https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/
type ManifestIcon = { src: string; sizes: string; type: string; purpose?: string };
type InstallManifest = {
  id: string;
  name: string;
  short_name: string;
  start_url: string;
  scope: string;
  display: string;
  theme_color: string;
  background_color: string;
  icons: ManifestIcon[];
};

async function loadManifest(request: APIRequestContext): Promise<InstallManifest> {
  const response = await request.get('/site.webmanifest');
  expect(response.status()).toBe(200);
  expect(response.headers()['content-type']).toMatch(/application\/(?:manifest\+json|json)/);
  return await response.json() as InstallManifest;
}

test('pages link one manifest with the expected TTOD installation metadata', async ({ page, request, baseURL }) => {
  for (const path of ['/en/docs/', '/es/docs/', '/en/oracle', '/es/oracle']) {
    await page.goto(path);
    const link = page.locator('link[rel="manifest"]');
    await expect(link).toHaveCount(1);
    await expect(link).toHaveAttribute('href', '/site.webmanifest');
  }
  const manifest = await loadManifest(request);
  expect(manifest).toMatchObject({
    id: '/', name: 'The Tao of Development', short_name: 'TTOD',
    start_url: '/', scope: '/', display: 'standalone',
    theme_color: '#fbf8f1', background_color: '#fbf8f1',
  });
  await expect(page.locator('meta[name="theme-color"]')).toHaveAttribute('content', manifest.theme_color);
  const manifestURL = new URL('/site.webmanifest', baseURL!);
  const start = new URL(manifest.start_url, manifestURL);
  const scope = new URL(manifest.scope, manifestURL);
  expect(start.origin).toBe(manifestURL.origin);
  expect(start.pathname.startsWith(scope.pathname)).toBe(true);
  expect(manifest.icons).toEqual(expect.arrayContaining([
    expect.objectContaining({ sizes: '192x192', type: 'image/png' }),
    expect.objectContaining({ sizes: '512x512', type: 'image/png' }),
    expect.objectContaining({ sizes: 'any', type: 'image/svg+xml' }),
  ]));
  const diagnostics = await page.context().newCDPSession(page);
  const browserManifest = await diagnostics.send('Page.getAppManifest');
  expect(browserManifest.url).toBe(manifestURL.href);
  expect(browserManifest.errors.filter((error) => error.critical)).toEqual([]);
  expect((await diagnostics.send('Page.getInstallabilityErrors')).installabilityErrors).toEqual([]);
});

test('declared PNG icons are served as PNG and decode at their actual target sizes', async ({ page, request, baseURL }) => {
  await page.goto('/en/docs/');
  const manifest = await loadManifest(request);
  const manifestURL = new URL('/site.webmanifest', baseURL!);
  for (const size of [192, 512]) {
    const icon = manifest.icons.find((entry) => entry.sizes === `${size}x${size}` && entry.type === 'image/png');
    expect(icon, `Missing ${size}px PNG icon`).toBeTruthy();
    const url = new URL(icon!.src, manifestURL);
    expect(url.origin).toBe(manifestURL.origin);
    expect(icon!.src.startsWith('/')).toBe(false);
    const response = await request.get(url.href);
    expect(response.status()).toBe(200);
    expect(response.headers()['content-type']).toContain('image/png');
    expect((await response.body()).subarray(0, 8)).toEqual(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]));
    const dimensions = await page.evaluate(async (src) => {
      const image = new Image();
      image.src = src;
      await image.decode();
      return { width: image.naturalWidth, height: image.naturalHeight };
    }, url.href);
    expect(dimensions).toEqual({ width: size, height: size });
  }
  const svg = manifest.icons.find((icon) => icon.sizes === 'any' && icon.type === 'image/svg+xml');
  expect(svg, 'Keep the SVG option').toBeTruthy();
  const response = await request.get(new URL(svg!.src, manifestURL).href);
  expect(response.status()).toBe(200);
  expect(response.headers()['content-type']).toContain('image/svg+xml');
  expect(await response.text()).toContain('<svg');
});
