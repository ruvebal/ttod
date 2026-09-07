# Phase U / TS0 Report — Local end-to-end deployment baseline

**State:** VERIFYING

**Date:** 2026-09-07

**Implementer:** Codex deployment session

**Independent verifier:** pending

**Owner:** `@crea-comm.net`

## Outcome

The current reference application is running locally as an isolated five-service Compose project.
Both localized home routes, the live governed quote, documentation, graph, Oracle page, graph API,
and a grounded streamed Oracle response were observed through the reverse proxy. The reference is
therefore sufficient for TS1 to study after independent TS0 verification; no pedagogical refactor
has begun.

## Scope and non-scope

TS0 built and started existing code, installed the two documented lightweight local models, and
performed HTTP observations. It did not edit application code, canonical data, proposals, course
content, deployment configuration, or any external repository. The stack remains running for the
owner's theoretical walkthrough.

## Deployment identity

| Setting | Value |
| --- | --- |
| Compose project | `ttod_teaching_audit` |
| HTTP teaching URL | `http://localhost:18082/` |
| alternate HTTP binding | `18445` |
| container-model host binding | `11436` |
| generation model | `llama3.2:1b` |
| embedding model | `nomic-embed-text` |
| canonical version observed through health | `3.1.0` |

The project uses alternate host bindings so it does not replace or reconfigure another local
stack. Container-internal ports remain those declared by Compose.

## Evidence

| Observation | Result |
| --- | --- |
| backend container health | healthy |
| frontend, retrieval service, model service, reverse proxy | running |
| `GET /health` | `200`; status `ok`, canonical version `3.1.0` |
| English home | rendered project title and governed flagship ID |
| Spanish home | rendered localized title, flagship ID, and English-original disclosure |
| live quote route | rendered the governed flagship ID |
| documentation route | rendered documentation heading |
| graph route | rendered graph surface |
| Oracle route | rendered prompt surface |
| graph API | 458 nodes and 664 edges in this dated observation |
| Oracle stream | `200 text/event-stream`; grounded mode with five cited quote IDs |
| installed local models | both documented lightweight models present |

Counts in this report are dated evidence, not values to copy into evergreen teaching instructions.

## Failed attempts retained

1. The first Compose call could not access the local container-engine socket from the restricted
   execution environment. It changed no repository file. The authorized retry built the images.
2. The first container-model start found host port `11435` already occupied. Compose had created
   the isolated project, but the model service could not bind. The project was resumed on `11436`;
   all five services then started. This is required input for TS1's collision-safe onboarding.
3. The first Oracle curl ended with a truncated-transfer error. A later cold request returned a
   grounded stream after the embedding model and index were ready. The retry proves the path but
   does not erase the cold-start UX risk.
4. The successful-stream capture attempted to assign to a shell-reserved variable after receiving
   streamed events. This produced a shell error after the HTTP evidence had already been captured;
   it did not affect the service. Future scripts must use a non-reserved result variable.

## Pedagogical findings for TS1

- Local onboarding must detect occupied ports or clearly show how to choose alternates.
- Model downloads are material first-run work, not a footnote; the observed generation download
  took roughly two minutes and the embedding download roughly half a minute on this run.
- The Oracle needs a visible “preparing retrieval index” state or preflight because health can be
  green before the first semantic request is warm.
- Static route health and actual streaming retrieval are separate gates.
- The graph is already far beyond hello-world data scale; TS1 must define the tiny teaching view
  without replacing the real backend contract.
- A runnable end-to-end product can support theory before collaboration, but the existing rich UI
  still contains too much finished assignment depth for direct student distribution.

## Integrity

`ttod.yml` retained SHA-256:

```text
530b15286488ad4be0a1db63532a920642f25b073d1e89b3876e9ff5951e6e1b
```

No canonical mutation command ran.

## Safe continuation

TS0 is `VERIFYING`. An independent session should repeat health, both localized homes, live quote,
graph, and one Oracle stream against the running project; inspect logs for unreported errors; and
recheck the canonical digest. Only the product owner may promote TS0 to `DONE` and unblock TS1.

The stack is intentionally still running. Its current local entry point is
`http://localhost:18082/en/`. Stopping it is an operational choice, not part of this report's
verification claim.
