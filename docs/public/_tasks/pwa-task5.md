---
title: "Install-quality checks (manifest correctness, icons, installability)"
seam: pwa
team_number: 4
team_name: "PWA & Local Operations"
task_number: 5
area: "PWA/Offline"
verb: keep
layout: default
lang: en
---

# Assignment — Team 4, Task 5: Install-quality checks (manifest correctness, icons, installability)

**Seam:** pwa · **Team:** 4 · **Task:** 5 of ~10
**Area(s):** PWA/Offline · **Verb served:** keep

## 1. Curriculum map

This task exercises the **Installability** learning outcome from the PWA module, which aligns with **Unit 3 — PWA fundamentals** in the web-atelier-udit FE II curriculum. The specific focus on manifest correctness and icon sizing corresponds to the "Installability" section of the module's own `ASSIGNMENT.md`, which explicitly requires producing a manifest that a Chromium browser treats as installable, including icon sizes Lighthouse actually checks.

## 2. Worked example, from the real TTOD app

The starter manifest at `services/frontend/public/manifest.webmanifest` already contains the minimum fields required for a technically valid manifest: `name`, `short_name`, `start_url`, `display: standalone`, `theme_color`, and a single icon entry. However, as noted in the module's own `ASSIGNMENT.md` Acceptance Criterion 3, "the stub's single SVG is not enough." The current manifest references one SVG icon, which is insufficient for Lighthouse's installability check, which requires specific raster icon sizes (typically 192x192 and 512x512 PNGs). This task extends the existing manifest by adding the required icon sizes and verifying that the install prompt appears correctly in a real Chromium browser.

## 3. What "done" looks like

**Visible result:** A Chromium browser treats the app as genuinely installable — the "Add to Home Screen" or install prompt appears, and when installed, the app launches in standalone mode with the correct icon, name, and theme color.

**What it includes:** 
- The manifest at `services/frontend/public/manifest.webmanifest` is updated to include the required icon sizes (192x192 and 512x512 PNGs) in addition to the existing SVG.
- The manifest's `name`, `short_name`, `start_url`, `display: standalone`, and `theme_color` fields are verified to be correct and consistent with the app's branding.
- The install flow is triggered in a real Chromium browser, and the installed app is confirmed to launch correctly in standalone mode.

**What has to be done:**
1. Generate or obtain the required raster icon sizes (192x192 and 512x512 PNGs) for the app.
2. Update `services/frontend/public/manifest.webmanifest` to include these new icon entries alongside the existing SVG.
3. Verify that the manifest passes Lighthouse's installability check (name, display `standalone`, theme color, and icon sizes).
4. Trigger the install flow in a real Chromium browser and confirm that the app installs correctly and launches in standalone mode with the correct icon, name, and theme color.
5. Document the icon sizes used and the rationale for choosing them, ensuring that the manifest is not just technically valid but also visually correct when installed.

## 4. Success criteria (functional)

- The web app manifest passes Lighthouse's installability check (name, display `standalone`, theme color, and the icon sizes that check requires — the stub's single SVG is not enough).
- The install prompt appears in a real Chromium browser when the app is loaded.
- The installed app launches in standalone mode with the correct icon, name, and theme color.

## 5. Quality criteria (the part that's new)

**Code organization:** The manifest file (`services/frontend/public/manifest.webmanifest`) is the single source of truth for the app's installability metadata. All icon files are colocated in the `public/` directory, and the manifest references them with relative paths. No other files in the codebase should duplicate or override the manifest's icon definitions.

**AI-use/process documentation discipline:** Document the process of generating or obtaining the required icon sizes, including any tools or scripts used. If an AI tool was used to generate the icons, note this in the process documentation and ensure that the icons are visually consistent with the app's branding.

**Test shape per R7's own Trophy-not-Pyramid doctrine:** The installability check is a functional requirement that can be verified manually in a real browser. However, to ensure that the manifest remains valid over time, consider adding a simple test that validates the manifest's structure (e.g., checking that the required fields are present and that the icon files exist). This test should be lightweight and focused on the manifest's correctness, not on the visual appearance of the icons.

**Accessibility:** This task inherits the global Definition of Done for accessibility: keyboard-operable, one accessible name or label, no meaning carried by color alone, respects reduced-motion preferences. While the manifest itself is not directly interactive, ensure that the app's UI is accessible when launched in standalone mode.

**Defensible oral-defense answer:** "I updated the manifest to include the required icon sizes (192x192 and 512x512 PNGs) and verified that the install prompt appears correctly in a real Chromium browser. I documented the process of generating the icons and ensured that the manifest passes Lighthouse's installability check. The installed app launches in standalone mode with the correct icon, name, and theme color, which I confirmed by testing the install flow manually."

## Closing

> "One source of truth. One place to change. One mind at peace."
> — TTOD `arch-013`, *architecture*

The manifest is exactly this: the single source of truth for the app's installability metadata. Every icon, name, and color a real install prompt shows comes from that one file — get it right there, once, rather than patching install-quality complaints piecemeal across the codebase.