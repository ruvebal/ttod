# Assignment — Team 3, Task 2: Live-region announcement of the streaming answer for screen readers

**Seam:** oracle · **Team:** 3 · **Task:** 2 of ~10
**Area(s):** Oracle · **Verb served:** keep

## 1. Curriculum map

This task exercises the accessibility and state management principles found in **Unit 5 — Testing strategy** (specifically the verification of non-visual user flows) and **Unit 3 — Content and Routing** (ensuring semantic structure supports assistive technology). While the specific unit link for "Live Regions" may not yet be published as a standalone lesson in the web-atelier-udit FE II curriculum, the underlying discipline is covered in the general accessibility requirements of the course.

## 2. Worked example, from the real TTOD app

The existing `OracleTerminal` component in `services/frontend/src/components/oracle/` already implements a busy guard using `aria-busy="true"` and `aria-live="polite"` on a status container. This pattern is currently used to announce that a request is in progress. The task is to extend this exact same discipline to the streaming text container itself, ensuring that as `readOracleStream` yields chunks, the DOM updates are structured such that screen readers announce the incremental text rather than waiting for the stream to close.

## 3. What "done" looks like

**Visible result:** A screen-reader user hears the answer as it streams in, not silence followed by the full text at the end.

**What it includes:** The existing `aria-live`/`aria-busy` pattern already used for the busy guard is extended to the streaming text element. The `aria-live` region is updated with each chunk arrival, and `aria-busy` is toggled appropriately to prevent double-announcement of static content while the stream is active.

**What has to be done:**
1. Identify the DOM node that receives the streamed text segments.
2. Ensure this node has `aria-live="polite"` (or `assertive` if immediate interruption is preferred, though `polite` is standard for streaming) and `aria-atomic="false"` so that each chunk is announced as it arrives.
3. Verify that the `aria-busy` attribute is set to `true` during streaming and `false` upon completion, ensuring the screen reader does not attempt to read the entire accumulated text at the end.
4. **Confirm with a real screen reader** (e.g., NVDA, JAWS, or VoiceOver) that incremental updates are actually announced. Visual inspection of the DOM is insufficient; the auditory output must be verified.

## 4. Success criteria (functional)

- The streaming text container has `aria-live="polite"` and `aria-atomic="false"`.
- `aria-busy` is `true` while the SSE stream is open and `false` when the stream closes.
- A screen reader announces each chunk of text as it arrives, rather than waiting for the full response.
- The existing `readOracleStream` and `parseSseEvent` helpers are used unmodified; no new polling or buffering logic is introduced.

## 5. Quality criteria (the part that's new)

- **Code organization:** The `aria-live` and `aria-busy` attributes are managed via React state or direct DOM manipulation in a way that does not conflict with the existing busy guard logic. The streaming text element is clearly separated from the status indicator element.
- **AI-use/process documentation:** The decision to use `aria-live="polite"` over `assertive` is documented in the commit message or PR description, referencing the need to avoid interrupting other screen reader activities.
- **Test shape:** Per R7's Trophy-not-Pyramid doctrine, the test for this task should be an integration test that simulates a screen reader's behavior by asserting that the `aria-live` region's content changes incrementally as chunks are appended, rather than a unit test that only checks the presence of the attribute.
- **Accessibility:** This task inherits the global Definition of Done: keyboard-operable, one accessible name or label, no meaning carried by color alone, respects reduced-motion preferences. Specifically, the live region must not be visually hidden in a way that breaks the accessibility tree.
- **Oral defense:** A defensible answer explains why `aria-atomic="false"` is critical for streaming (to prevent the screen reader from reading the entire accumulated text at the end) and how the `aria-busy` attribute prevents double-announcement. It also acknowledges the limitation that visual inspection is not a substitute for auditory verification.

## Closing

> "The visually impaired user cannot see your images, but they can hear them through alt text. Speak clearly. Speak truthfully. Do not say 'image123.jpg'."
> — TTOD `img-057`, *images*

This quote, while focused on images, encapsulates the core principle of this task: assistive technology users rely on the semantic and textual content of the DOM to understand the interface. Just as alt text must be clear and truthful, the live region announcements must be clear and truthful, ensuring that the streaming answer is heard as it is intended to be understood.