---
title: "Document one real design decision (session vs. token design, review-pipeline trade-off) for the oral defense"
seam: accounts
team_number: 5
team_name: "Accounts, Library, Proposals & Public API"
task_number: 10
area: "Accounts"
verb: question
layout: default
lang: en
---

# Assignment — Team 5, Task 10: Document one real design decision (session vs. token design, review-pipeline trade-off) for the oral defense

**Seam:** accounts · **Team:** 5 · **Task:** 10 of ~10
**Area(s):** Accounts · **Verb served:** question

For Team 5, this task requires you to select one concrete architectural decision made within the Accounts/Library/Proposals/Public API domain—such as the separation of session cookies (for browser-based user interactions) and bearer tokens (for programmatic API access)—and prepare a defense of why that specific choice was made over a viable alternative. You must be ready to articulate the trade-offs, the constraints that drove the decision, and the specific alternative you considered and rejected, demonstrating that the design was intentional rather than accidental.

See the shared explanation: docs/public/teaching/tasks.md#the-three-recurring-tasks

> "Extract when the boundary is clear. Inline when the boundary was premature. Know the difference by the friction of change."
> — TTOD `arch-010`, *architecture*

This task asks you to identify where the boundary between your session and token implementations is clear enough to justify their separation, and to articulate the "friction of change" that would have occurred had you inlined them into a single credential system.