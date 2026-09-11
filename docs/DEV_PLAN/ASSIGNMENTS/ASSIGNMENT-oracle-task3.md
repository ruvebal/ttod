# Assignment — Team 3, Task 3: Grounded vs. creative mode disclosure in the UI

**Seam:** oracle · **Team:** 3 · **Task:** 3 of ~10
**Area(s):** Oracle · **Verb served:** question

## 1. Curriculum map

This task exercises the core principles of **Unit 3 — Semantic HTML and Accessibility** from the web-atelier-udit FE II curriculum. Specifically, it applies the requirement that "no meaning is carried by color alone" and the necessity of providing accessible names and labels for interactive and informational elements.

[Link to Unit 3 — Semantic HTML and Accessibility](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-3-semantic-html-accessibility/)

## 2. Worked example, from the real TTOD app

The existing `OracleTerminal` component in `services/frontend/src/components/oracle/` already renders `OracleResponseChunk` objects. The `types/domain.ts` file defines the `OracleResponseChunk` interface, which includes a `mode` field (either `'grounded'` or `'creative'`) and an optional `citedQuoteIds` array.

Currently, the UI may distinguish these modes visually (e.g., via background color or border style) but lacks explicit textual disclosure. The `citedQuoteIds` are rendered as plain text or simple spans, not as navigable links. This task extends the existing rendering logic to ensure the mode is explicitly labeled and the citations are interactive.

## 3. What "done" looks like

**Visible result:**
The Oracle terminal clearly distinguishes between "grounded" and "creative" responses using both visual cues (color, icon) and explicit text labels (e.g., "Grounded" or "Creative"). The distinction is unmistakable to all users, including those with color vision deficiencies or using screen readers.

**What it includes:**
- A text label indicating the response mode (`grounded` or `creative`) is present in the DOM for every response chunk.
- `citedQuoteIds` on grounded segments are rendered as navigable links (e.g., `<a href="/quotes/<id>">`) rather than plain text.
- The UI passes accessibility audits: no meaning is conveyed by color alone; all interactive elements have accessible names.

**What has to be done:**
1. Audit the current `OracleTerminal` rendering logic to identify where `mode` is applied.
2. Add a visible text label (e.g., `<span className="mode-label">Grounded</span>`) next to or within the response header.
3. Ensure the label is associated with the response container via ARIA attributes (e.g., `aria-label` or `role="status"` with descriptive text).
4. Update the rendering of `citedQuoteIds` to generate `<a>` tags with appropriate `href` and `aria-label` (e.g., "View quote <id>").
5. Verify that the distinction is not color-only: test with a color-blindness simulator and a screen reader (e.g., NVDA, VoiceOver).

## 4. Success criteria (functional)

- A user can distinguish between a grounded and a creative response without relying on color alone.
- `citedQuoteIds` on grounded segments are rendered as navigable links that, when clicked, navigate to the corresponding quote detail page.
- The UI remains accessible: all mode indicators have accessible names, and the distinction is perceivable by screen reader users.

## 5. Quality criteria (the part that's new)

- **Code organization:** The mode label and citation link logic should be encapsulated in a reusable sub-component (e.g., `ResponseHeader` or `CitationLinks`) to keep the main `OracleTerminal` component clean.
- **AI-use/process documentation:** Document in the PR description how the accessibility requirements were verified (e.g., "Tested with NVDA and color-blindness simulator").
- **Test shape:** Per R7's Trophy-not-Pyramid doctrine, write a component test that asserts the presence of the mode label and the `href` of the citation links. Do not test implementation details like class names; test the semantic output.
- **Accessibility:** This task inherits the global Definition of Done: keyboard-operable, one accessible name or label, no meaning carried by color alone, respects reduced-motion preferences. Cite this definition rather than restating it as unique to this task.
- **Oral defense:** Be prepared to explain why color-only distinction is insufficient and how the text label + link structure satisfies both visual and non-visual users. Reference the specific ARIA attributes used and why they were chosen.

**Testing Strategy:**
All testing practices for this task align with [Unit 5 — Testing strategy](https://ruvebal.github.io/web-atelier-udit/lessons/en/feii/unit-5-testing-strategy/), which emphasizes semantic correctness and user-perceivable outcomes over implementation details.

## Closing

> "The visually impaired user cannot see your images, but they can hear them through alt text. Speak clearly. Speak truthfully. Do not say 'image123.jpg'."
> — TTOD `img-057`, *images*

This quote underscores the core principle of this task: accessibility is not an afterthought but a fundamental requirement. Just as alt text must be clear and truthful, the mode disclosure in the Oracle terminal must be explicit and perceivable to all users, regardless of their sensory capabilities.