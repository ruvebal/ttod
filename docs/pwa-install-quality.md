# PWA Task 5 — install quality

## Status

Repaired on 2026-10-08 on top of Task 4 `a27fb4a`, including teacher main `4b4e774` and merged Task 1 #51. `.aws` is absent. The accepted layout still links one canonical `/site.webmanifest`; Task 5 extends that manifest with the existing 192px/512px PNG exports.

The eight-case PWA guard, six unit/component tests, 33 scoped Task 1–5 Chromium regressions and 236 Python tests pass. Current Chromium reports no manifest or installability errors; a disposable real installation and standalone relaunch also passed as detailed below. The developer reported successful installation in Brave on Omarchy. Final main integration follows #49, last in #46 → #47 → #49 → #50; no dependency PR was merged for this repair.

## Manifest and application identity

`services/frontend/public/site.webmanifest` remains the single manifest linked by
`src/layouts/Page.astro`. The assignment sheet calls it `manifest.webmanifest`, but
this checkout already uses `/site.webmanifest` in its layout and lifecycle
coverage. Retaining that path avoids a second manifest and keeps existing links
consistent.

The manifest retains the existing application name, launch route and colors:

| Field | Value | Design outcome |
| --- | --- | --- |
| `name` | `The Tao of Development` | Full TTOD application name. |
| `short_name` | `TTOD` | Compact launcher label. |
| `id` | `/` | Makes the existing root identity explicit. |
| `start_url` | `/` | Retains the application's current landing route. |
| `scope` | `/` | Includes both locale routes. |
| `display` | `standalone` | Requests an application window for installed launches. |
| `theme_color` | `#fbf8f1` | Matches the layout's existing theme metadata. |
| `background_color` | `#fbf8f1` | Retains TTOD's paper background. |

Without an explicit valid ID, browsers use the start URL as the manifest identity.
Adding `/` therefore retains the existing root identity. See
[MDN's manifest ID reference](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Manifest/Reference/id).
Current installed-app verification confirmed that launching `/` reaches `/en/` and reopening retains standalone mode. This does not establish an offline home-page launch.

## Icon source and generation process

The existing `public/visual-system/favicon.svg` is the source artwork. It retains
TTOD's gold, green and ink mark. PNG exports use the paper-colored `#fbf8f1`
background and are colocated with the SVG under `public/visual-system/`.

| Manifest source, relative to `/site.webmanifest` | Format | Declared size | Locally inspected dimensions |
| --- | --- | --- | --- |
| `visual-system/icon-192.png` | PNG | `192x192` | 192 × 192 pixels |
| `visual-system/icon-512.png` | PNG | `512x512` | 512 × 512 pixels |
| `visual-system/favicon.svg` | SVG | `any` | Scalable source artwork retained. |

The two raster sizes satisfy the assignment's explicit 192px and 512px requirement.
Exporting each directly from the vector avoids enlarging a smaller raster image.
The SVG remains available as a scalable option. Relative icon paths resolve
against the manifest URL; `sizes`, `type` and `purpose` describe each resource. All
three entries use `purpose: any`; no maskable-icon claim is made. See
[MDN's icon reference](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Manifest/Reference/icons).

The documented reproduction commands, run from the repository root, are:

```sh
rsvg-convert --width 192 --height 192 --background-color '#fbf8f1' --output services/frontend/public/visual-system/icon-192.png services/frontend/public/visual-system/favicon.svg
rsvg-convert --width 512 --height 512 --background-color '#fbf8f1' --output services/frontend/public/visual-system/icon-512.png services/frontend/public/visual-system/favicon.svg
```

`rsvg-convert` 2.62.3 was available when documenting the process. Local inspection
with `magick identify` confirmed both PNG formats and target dimensions. That file
inspection does not establish visual quality in the operating system's launcher.
Assistant visual review of both actual exports found the centered TTOD mark,
paper background, clear padding and no clipping. OS launcher and window-chrome appearance remain
unreported.

The existing SVG browser favicon link remains in Page.astro. Installation icons
are defined in the manifest. The Oracle payloads, queue helpers, IndexedDB schema,
worker policies and existing Oracle offline boundary receive no Task 5 feature
changes under this design. The retained `/` start URL does not establish that the
entire home page is available offline.

## Automated coverage and configuration status

Following [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/),
`services/frontend/e2e/pwa-installability.spec.ts` adds two focused browser cases:

1. Inspect the served manifest, one canonical link on both locales’ docs and Oracle shells, theme metadata and expected application identity/presentation fields. Chromium DevTools Protocol also checks the processed manifest URL, absence of critical parse errors and absence of installability errors.
2. Fetch the PNGs, verify their MIME types and PNG signatures, decode them in the
   browser at the declared natural dimensions, and confirm the SVG remains served.

These cases support metadata and asset correctness. They do not perform an actual
browser installation or prove that the installed app launches in standalone mode.
They join the six queue cases in the existing isolated PWA guard,
as described in the [compatibility monitor](pwa-compatibility-monitor.md).

The initial verification failed because the matcher was added to the general
`playwright.config.ts`, including a stray top-level copy outside `defineConfig`.
Both additions have been removed, preserving the full general suite. The isolated
`playwright.pwa.config.ts` now uses this property inside `defineConfig(base, { ... })`:

```ts
testMatch: /pwa-(?:queue-reconnect|installability)\.spec\.ts/,
```

Historical verification after that correction: `npm run pwa:guard` passed locally on 2026-10-07: caller
contract, five checker regression tests, Astro diagnostics with zero errors,
warnings or hints, TypeScript, production build and all eight isolated Chromium
cases (10.9 seconds). These include six queue scenarios and two manifest/icon
cases. The developer's supplied output separately records six passing Vitest
tests, strict repository validation/metadata checks and 236 passing Python tests,
plus a successful Docker rebuild. Those successful commands were not rerun solely
for this configuration correction.

The historical complete Chromium suite then passed all 31 tests in 25.2 seconds against the
developer-rebuilt Docker frontend at `http://localhost:8080`. This includes the new
manifest/icon cases, existing locale/Axe coverage, worker lifecycle/cache policies,
Oracle offline navigation and queue replay/recovery. Automated Axe results support
accessibility regression checks; manual review in the actual installed window is
still required.

## Browser tools and real installation evidence

The assignment refers to Lighthouse's historical PWA installability audit. Chrome
removed that category. Record the browser/tool version and use current Chromium
Application → Manifest diagnostics plus the real install and launch flow; do not
claim a removed audit passed. See
[Chrome's installability update](https://developer.chrome.com/blog/update-install-criteria)
and [DevTools PWA debugging guidance](https://developer.chrome.com/docs/devtools/progressive-web-apps).

Use HTTPS or localhost for the demonstration. Inspect the served manifest and
icons, complete the browser's actual installation dialog, close the app and reopen
it from the launcher. In the installed window, confirm:

```js
window.matchMedia('(display-mode: standalone)').matches
```

Record the actual result without display-mode emulation. See
[MDN's installability guide](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable)
and [display-mode reference](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/display-mode).

### Current repair evidence — 2026-10-08

The assistant checked the rebuilt app against an isolated real corpus backend, with the served worker verified byte-for-byte against source. All 33 scoped Task 1–5 browser cases passed, including current manifest diagnostics and six reconnect cases. This is scoped PWA regression coverage; the unrelated graph selection case was not rerun. The full PWA guard separately passed all eight cases plus contract, checker, Astro, TypeScript and build phases. `npm test` passed six tests; repository `make check` passed validation, metadata checks and 236 Python tests.

A headed system Chromium `152.0.7977.82` on Omarchy `4.0.4` used a disposable profile and temporary XDG data/config directories. It produced the following actual results:

```json
{
  "manifestPath": "/site.webmanifest",
  "manifestErrors": [],
  "installabilityErrors": [],
  "browserGeneratedBeforeInstallPrompt": true,
  "installedLaunchPath": "/en/",
  "standalone": true,
  "reopenedStandalone": true,
  "themeColor": "#fbf8f1",
  "axeViolations": [],
  "keyboardOpenClose": "passed",
  "uninstalledAfterCheck": true
}
```

Installation and relaunch used the real [Chrome DevTools Protocol PWA commands](https://chromedevtools.github.io/devtools-protocol/tot/PWA/). DevTools installs default to browser display mode; the check selected the installed app's actual standalone preference using `PWA.changeAppUserSettings` before launch. It did not emulate display mode or fabricate an install event. The root start URL redirected to `/en/`; closing and relaunching the app again yielded standalone mode. This verifies installed browser behavior, not a human click on a native install dialog or an OS launcher.

The installed Oracle window passed Axe and keyboard activation of open/close controls with `prefers-reduced-motion: reduce` enabled. App viewport screenshots were captured and inspected locally. Full manual focus/navigation/motion review and OS launcher icon/window-chrome appearance remain human checks. The test app was uninstalled and both temporary servers stopped afterward; the developer's existing Brave profile was not used.

| Verification item | Status | Evidence or remaining work |
| --- | --- | --- |
| One manifest and expected metadata | Passed | Both locales’ docs/Oracle shells link `/site.webmanifest` once; installed home also has one link. |
| PNG formats, dimensions and decoding | Passed | Actual PNGs are 192x192 and 512x512; served MIME/signature/browser decoding checks pass. |
| Icon source and visual inspection | Recorded / passed | Existing SVG exports; `rsvg-convert` 2.62.3 documented; both current PNGs inspected without clipping. |
| Current browser manifest/installability diagnostics | Passed | Chromium returned empty manifest and installability error lists. |
| Browser-generated install eligibility event | Observed | Actual `beforeinstallprompt` event in the fresh headed profile. |
| Developer installation | Passed, developer-reported | Successful installation reported on 2026-10-07; user identified Brave on Omarchy on 2026-10-08. Exact Brave version and flow were not supplied. |
| Installed launch/relaunch and display | Passed, automated | Real CDP installation, installed standalone preference, `/` → `/en/`, standalone true on launch and relaunch. |
| Installed Oracle keyboard/Axe with reduced motion | Passed, automated | Open/close controls activate with Enter; Axe violations empty with reduced motion enabled. |
| Full manual accessibility and OS launcher appearance | Unreported | Native dialog, launcher name/icon/chrome appearance and complete focus/motion review still need human evidence. |
| Hosted CI for repaired Task 5 | Pending publication | Check both jobs at the new head; final-main re-review follows #49. |

The removed Lighthouse PWA category is not reported as a passing audit. Current diagnostics and actual install/relaunch results supply the installability evidence; human observations are kept separate.

## AI-use and review record

AI assistance inspected the existing PWA files, prepared the implementation guide,
proposed manifest/icon coverage and checked those proposed snippets in a disposable
frontend copy. The developer applied the local manifest/icon/spec changes and
created the Task 5 branch. AI assistance then prepared this shared documentation,
updated the monitor note, inspected the actual PNG dimensions/appearance, corrected
the misplaced matcher and missing final newlines, and ran the full guard and complete
Chromium regression suite. During the 2026-10-08 repair, AI assistance rebased the task, strengthened canonical-manifest/Chromium diagnostics coverage, ran the current checks and verified a real disposable CDP installation and standalone relaunch. The developer separately reported successful Brave installation on Omarchy. Automated installed-window checks do not establish complete human accessibility or OS launcher review; remaining evidence is recorded above.
