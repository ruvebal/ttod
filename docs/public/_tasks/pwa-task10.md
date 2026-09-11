---
title: "Document one real design decision for the oral defense"
seam: offline
team_number: 4
team_name: "offline"
task_number: 10
area: "PWA & Local Operations"
verb: question
layout: default
lang: en
alt_lang_missing: true
---

# Assignment — Team 4, Task 10: Document one real design decision for the oral defense

**Seam:** offline · **Team:** 4 · **Task:** 10 of ~10
**Area(s):** PWA & Local Operations · **Verb served:** question

For Team 4, this task requires selecting one concrete architectural choice made during the implementation of the PWA & Local Operations stack—such as the specific caching strategy chosen for the `/wisdom` route versus the `/graph` route, or the decision to prioritize manifest-based installability over a custom install prompt UX. You must be prepared to articulate the specific trade-off involved (e.g., why `stale-while-revalidate` was chosen over `network-first` for a specific asset type) and identify a viable alternative that was considered and rejected, providing the technical rationale for that rejection.

See the shared explanation: docs/public/teaching/tasks.md#the-three-recurring-tasks

> "The cloud model answers in milliseconds. The local model answers in seconds. But the cloud model's answer belongs to someone else. Speed without sovereignty is a leash worn willingly."
> — TTOD `arch-029`, *DevIAC Tao (§40): The Cost of Convenience*

This quote grounds the defense of local-first caching decisions: choosing a slower, local response mechanism is not a failure of performance, but a deliberate assertion of control over the user's data and experience, which must be defended as a feature, not a bug.