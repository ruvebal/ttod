---
title: Product areas
eyebrow: The implemented reference
description: The visible areas and front-end boundaries in the TTOD instructor reference.
permalink: /platform/
---

# One product, several teachable boundaries

The instructor reference is locally runnable end to end. Its areas are not separate demonstrations: they share localization, content contracts, API boundaries, accessible browser states, and the same governed quote source.

| Area | User-visible purpose | Front-end idea made observable |
| --- | --- | --- |
| Welcome | enter in English or Spanish | localized routing and document language |
| Quote | inspect one governed entry | typed data, provenance, rights, and semantic presentation |
| Wisdom | browse the collection | information architecture, filters, and empty states |
| Documentation | learn the system in context | content collections and editorial navigation |
| Graph | explore related entries | a hydrated Svelte island with accessible textual state |
| Oracle | ask and receive a streamed response | a React island, streaming state, grounding, and recovery |
| Local operations | start and observe the stack | the browser/service boundary, not a DevOps syllabus |
| Tests | locate evidence at useful layers | unit, component, contract, route, and accessibility reasoning |

## Architecture at teaching scale

```text
localized route
  → Astro document and content contract
  → bounded Svelte or React island
  → HTTP or streamed request
  → application and retrieval contracts
  → governed quote snapshot
  → accessible browser state
  → test at the cheapest useful layer
```

Astro owns the document and content-oriented routes. Interactive islands are used where local state or streaming warrants them. The backend is explained only far enough to trace the request and trust boundary; the teaching emphasis remains front-end architecture.

## Honest maturity

The rich reference demonstrates localized content, graph exploration, and a streamed Oracle. Browser operations, offline behavior, and the testing surface are not yet a complete student-ready implementation. A future teaching baseline will keep every major area present at hello-world depth; that subtraction refactor is planned, not complete.
