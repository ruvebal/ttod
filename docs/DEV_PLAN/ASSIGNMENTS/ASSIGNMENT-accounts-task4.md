# Assignment — Team 5, Task 4: The GitHub-native review pipeline: a proposal PR, human approval, computed accept-diff, second approval

**Seam:** accounts · **Team:** 5 · **Task:** 4 of ~10
**Area(s):** Accounts · **Verb served:** contribute

## 1. Curriculum map

This task exercises the FE II unit on **Framework-mode authentication and server-side guards**, specifically the application of `requireRole` to gate privileged actions. While the specific "GitHub-native review pipeline" is a TTOD-specific process, the underlying skill — a loader-timed guard deciding who may even reach a page — is the same **FE I Framework-mode auth lesson** ([HELIOS DECK's architecture](https://ruvebal.github.io/web-atelier-udit/tracks/es/geo-physical-aggregator/arch/), `requireUser(request)` in the loader, before render) that Task 1 builds on. `requireRole` layers role-gating on top of that inherited pattern — FE I's own lesson stops at "logged in or not," not "which role"; that extension is TTOD's.

*Note: A specific web-atelier-udit FE II unit link for "GitHub Review Pipelines" is not yet published — the pipeline itself is TTOD-specific, not curriculum content. The verification discipline for tracing it end to end is covered in [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/).*

## 2. Worked example, from the real TTOD app

The pipeline mechanics are already implemented in the backend CLI. The real mutation path is `cli.py proposal accept --reviewer-id ...` (line 361), which is the **only** command that ever writes to `ttod.yml`.

The frontend gate for this pipeline is the `requireRole` function exported from `services/frontend/src/lib/auth.server.ts`. This function is called in the Astro frontmatter of protected pages (like the reviewer queue, if it existed) to ensure that only users with the `reviewer` or `instructor` role can access the UI that triggers the acceptance flow. The `auth.py` backend module (`services/backend/app/auth.py`) provides the `require_session_user` dependency that validates the session cookie before any API call related to proposals is processed.

## 3. What "done" looks like

**Visible result:** A submitted proposal becomes a real PR; a reviewer's approval computes the exact canonical diff; a second approval on that diff is what actually publishes it.

**What it includes:**
*   The pipeline already exists and is documented on the contributing guide (`docs/public/guides/contributing.md`) with its own diagram.
*   Your task is operating it correctly for real proposals, and explaining the two-touchpoint design in your defense.
*   Tracing one real proposal through the entire pipeline end to end at least once before considering this task done.

**What has to be done:**
1.  **Trace the Flow:** Identify the exact sequence of events from a student submitting a proposal (via the form in `services/frontend/src/pages/[locale]/account/` or similar) to the final write in `ttod.yml`.
2.  **Verify the Gate:** Confirm that `requireRole(request, 'reviewer')` is enforced server-side (in Astro frontmatter) for any UI element that allows triggering the `proposal accept` command. Ensure that a student with the `student` role receives a 403 or redirect, not just a hidden button.
3.  **Execute the Pipeline:** Create a test proposal, submit it as a PR, and perform the two-approval process (human approval of the PR, then the computed accept-diff approval) to see the quote appear in the canonical corpus.
4.  **Document the Defense:** Prepare a clear explanation of why the "two-touchpoint" design (PR approval + diff approval) is used, focusing on the separation between *social consensus* (PR review) and *technical integrity* (diff computation/acceptance).

## 4. Success criteria (functional)

*   **Role-gated reviewer view:** `requireRole(request, 'reviewer')` (or `'instructor'`) wraps the reviewer page. The seeded student role receives 403; a reviewer sees the queue. This check is implemented in Astro frontmatter, not just in JSX/Svelte state.
*   **Canonical mutation path:** The only way a quote is added to `ttod.yml` is via `python cli.py proposal accept --reviewer-id …`. No direct writes to `ttod.yml` are performed by the frontend or any other service.
*   **End-to-end trace:** You have successfully traced one real proposal through the entire pipeline, from submission to publication, and can articulate each step.

## 5. Quality criteria (the part that's new)

*   **Code Organization:** Ensure that the `requireRole` check is isolated in the Astro frontmatter of the relevant page/component. Do not import `auth.server.ts` from a client-side island or React/Svelte component.
*   **AI-Use/Process Documentation:** Document your process of tracing the pipeline. Include screenshots or logs of the PR creation, the diff computation, and the final acceptance. This demonstrates your understanding of the "two-touchpoint" design.
*   **Test Shape:** Per R7's Trophy-not-Pyramid doctrine, ensure that your tests for this task focus on the *integration* of the auth gate and the proposal acceptance flow. A unit test for `requireRole` is necessary but insufficient; an integration test that verifies a student cannot trigger `proposal accept` is critical. Link to [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/) for guidance on structuring these tests.
*   **Accessibility:** The reviewer queue UI must be keyboard-operable, have one accessible name or label, no meaning carried by color alone, and respect reduced-motion preferences. Cite the [Accessibility Definition of Done](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/) (or the relevant FE II accessibility unit) rather than restating these requirements as unique to this task.
*   **Oral Defense:** Be prepared to explain why the "two-touchpoint" design is superior to a single-approval system. Focus on the separation of concerns: PR approval ensures social consensus and code review, while diff approval ensures technical integrity and prevents accidental or malicious modifications to the canonical corpus.

## Closing

> "Verify Before You Fix - Not every symptom is a disease."
> — TTOD `arch-027`, *architecture*

The two-touchpoint design is this quote enforced as process: a PR approval alone is a symptom-level check (does this look right to a human?); the computed accept-diff is the actual verification that the change is what it claims to be. Neither touchpoint alone is enough — publishing on the first is treating a symptom as a cure.