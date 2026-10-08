# PWA Task 6 — measured performance budget

## Status

Baseline measured on 2026-10-08 at Task 5 head `a9d6c0b` (branch `pwa-task6-performance`, no application changes). The LCP budget was then set at 2500 ms. The developer enabled response compression for the frontend in `caddy/Caddyfile`; the repeated measurement gives a median LCP of 1806 ms, inside the budget.

## Measurement setup

The same setup must be used for the after-measurement.

| Item | Value |
| --- | --- |
| Build | Production stack from `make up`; served `/sw.js` byte-equal to source |
| URL | `http://localhost:8080/en/oracle`, page load only, no query submitted |
| Tool | Lighthouse 12.8.2 CLI, Performance category only |
| Browser / OS | Headless Chromium 152.0.7977.82 on Omarchy 4.0.4 |
| Emulation | Lighthouse mobile default: 412 × 823 viewport, device scale factor 1.75 |
| Throttling | Simulated: 150 ms RTT, 1638 kbps, 4× CPU slowdown |
| Cache state | Cold: each run starts a new temporary browser profile, so the HTTP cache, Cache Storage and service worker are empty |
| Runs | Five, reported individually and as a median |

Command, run once per sample:

```sh
CHROME_PATH=/usr/bin/chromium npx lighthouse@12 http://localhost:8080/en/oracle \
  --only-categories=performance --output=json --output=html \
  --output-path=run1 --chrome-flags="--headless=new"
```

Lighthouse is run through `npx`; it is not a project dependency.

## Baseline

| Run | FCP (ms) | LCP (ms) | CLS | TBT (ms) | Score |
| --- | --- | --- | --- | --- | --- |
| 1 | 1206 | 3006 | 0.022 | 0 | 94 |
| 2 | 1204 | 3154 | 0.022 | 7.5 | 93 |
| 3 | 1203 | 3154 | 0 | 0 | 93 |
| 4 | 1206 | 3006 | 0.022 | 4 | 94 |
| 5 | 1202 | 3153 | 0 | 0 | 93 |
| **Median** | **1204** | **3153** | **0.022** | **0** | **93** |

LCP ranges from 3006 to 3154 ms across the five runs. A later improvement smaller than that 148 ms spread would not be distinguishable from measurement noise.

## What the baseline reports show

- **LCP element:** the Oracle textarea placeholder, rendered inside the React island. Of the LCP time, 451 ms is time to first byte and about 2700 ms (86%) is render delay.
- **Bytes:** 11 requests, about 371 KiB transferred. The two script bundles, `client.*.js` (187 KB) and `OracleTerminal.*.js` (140 KB), are 88% of that.
- **Compression:** those bundles transfer at their full size. `caddy/Caddyfile` has no `encode` directive, and a request sent with `Accept-Encoding: gzip, br, zstd` returned no `Content-Encoding`.
- **Render-blocking CSS:** `_slug_.*.css` (25.8 KB), `backgrounds.css` and `tokens.css`. Lighthouse estimates 250–550 ms of savings for the three together.
- **`/visual-system/tokens.css`:** about 1.3 KB on the wire. The task sheet names it as the likely bottleneck, describing a starter worker that cached only that file. The current worker and page are different, and the measurements do not support that file as the main cost.

These are observations from the reports. The optimization is chosen after the budget is set.

## Budget

Set on 2026-10-08, after the baseline and before any optimization.

**Median LCP for `/en/oracle` must be at or below 2500 ms** under the setup above (Lighthouse mobile, simulated throttling, cold load, median of five runs).

Rationale: 2500 ms is the recognised "good" LCP threshold in the [Web Vitals reference](https://web.dev/articles/vitals). The baseline median is 3153 ms, so the budget needs a cut of about 650 ms (21%), well outside the 148 ms run-to-run spread. The baseline reports suggest that much is available: the text resources total about 373 KB uncompressed, which is roughly 1.8 s of download at the simulated 1638 kbps.

Guard metrics, so an LCP gain cannot hide a regression: CLS at or below 0.1, TBT at or below 200 ms, and FCP no worse than the 1204 ms baseline median plus its spread.

## Optimization

One change, applied by the developer: response compression for everything the frontend serves, in the reverse proxy.

```diff
   handle {
+    encode zstd gzip
     reverse_proxy frontend:4321
   }
```

Why this change: the baseline shows a page that waits on downloads, not on main-thread work (TBT 0 ms), and every text resource was sent at full size. Compression shrinks those transfers without changing any file, so the service worker's cache names and precache list stay as they are.

### Backend and Team 3 boundary

The directive sits only in the frontend `handle` block. The `@api` block (`/api/*` and `/health`, proxied to the backend) is unchanged, so the Oracle answer stream that Team 3's terminal reads is not compressed or buffered by this task. No Oracle component, backend or shared type was edited.

Checked through the proxy after the change:

| Request | Result |
| --- | --- |
| `/en/oracle`, `/_astro/*.js`, `/_astro/*.css`, `/sw.js` with `Accept-Encoding: gzip, br, zstd` | `Content-Encoding: zstd` |
| `/health` with the same header | No `Content-Encoding` |
| `POST /api/v1/oracle/stream` with the same header, one real question | 200, `text/event-stream`, no `Content-Encoding`; 284 non-empty lines arriving between about 38 s and 52 s, so the answer still streams incrementally |
| Served `/sw.js` | Byte-equal to source |

## After-measurement

Same setup, command and machine as the baseline; only the proxy configuration changed (proxy container restarted, frontend image not rebuilt).

| Run | FCP (ms) | LCP (ms) | CLS | TBT (ms) | Score |
| --- | --- | --- | --- | --- | --- |
| 1 | 906 | 1806 | 0.022 | 0 | 100 |
| 2 | 1278 | 1803 | 0 | 0 | 99 |
| 3 | 902 | 1953 | 0.022 | 0 | 99 |
| 4 | 903 | 1804 | 0.022 | 0 | 100 |
| 5 | 903 | 1955 | 0 | 0 | 99 |
| **Median** | **903** | **1806** | **0.022** | **0** | **99** |

| Metric | Baseline median | After median | Difference | Budget | Pass |
| --- | --- | --- | --- | --- | --- |
| LCP (ms) | 3153 | 1806 | −1348 (−43%) | ≤ 2500 | Yes |
| FCP (ms) | 1204 | 903 | −301 (−25%) | no worse than baseline | Yes |
| CLS | 0.022 | 0.022 | 0 | ≤ 0.1 | Yes |
| TBT (ms) | 0 | 0 | 0 | ≤ 200 | Yes |

Every after-run LCP (1803–1955 ms) is below every baseline run (3006–3154 ms), so the difference is far larger than the run-to-run spread. Total transfer for the page fell from about 371 KiB to about 127 KiB over the same 11 requests. One after-run FCP (1278 ms) is above the baseline; the other four are near 903 ms.

## Regression checks

Run on 2026-10-08 with the change in place.

| Check | Result |
| --- | --- |
| `npm test` | 6 passed |
| `npm run pwa:guard` | Passed, including its 8 browser cases |
| 33 scoped PWA Chromium cases against `http://localhost:8080` (through the compressing proxy): lifecycle, Oracle offline, cache policies, queue reconnect, installability, locale routes | 33 passed |
| `make check` | Passed, 236 Python tests |

The scoped cases cover the offline banner, both offline Oracle shells and queue replay. The wider suite, including the graph tests, was not run.

## Limitations

- Lab measurements on one machine with simulated throttling. They support a before/after comparison under this setup; they are not field Core Web Vitals.
- Cold loads only. Repeat visits served by the service worker were not measured.
- The ten raw Lighthouse JSON reports are in [`docs/evidence/pwa-task6/`](evidence/pwa-task6/) (`baseline/` and `after/`, five runs each). Lighthouse's embedded screenshots (`screenshot-thumbnails`, `final-screenshot`, `fullPageScreenshot`) were removed to keep the files small; every metric and audit is unchanged. The HTML renderings of the same runs are not committed.
- Compression is configured in the local Caddy proxy. A deployment that serves the frontend another way needs its own compression setting.
- No manual keyboard or reduced-motion pass was repeated; the change does not touch markup, styles or scripts.

## AI-use and review record

AI assistance (Claude Code) started the stack, ran the five Lighthouse audits, extracted the metrics and observations above from the raw reports, and drafted this note. No application code was changed for the baseline. The developer searched and applied the Caddyfile change by hand after; AI assistance suggested its placement outside the API block, then ran the after-measurement, the proxy and streaming checks and the regression checks recorded above. The developer chose the 2500 ms LCP budget; the written rationale and guard metrics were drafted with AI assistance and accepted by the developer.
