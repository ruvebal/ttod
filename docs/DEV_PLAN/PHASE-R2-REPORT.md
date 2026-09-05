# Phase R2 Report — FastMCP RAG server

**Status: DONE**

All three R2 runtime tools are implemented and gate-clean. R3a's concurrently assembled shared
stack now contains the required `.env.example` default and internal-only compose wiring. The
requested cold-review-equivalent self-audit ran, its two findings were fixed, and all checks pass.

## Shipped tools

- `semantic_retrieval(query, top_k=5, contextTag=None, section=None)` returns
  `{results, indexDigest, indexedQuotes}`. Every result contains `id`, `text`, `section`, `tags`,
  unmodified `origin`, and cosine `score`; R1 retains the grounded/creative policy decision.
- `graph_neighborhood(quoteId=None, tag=None, section=None)` uses `Exporter`'s graph projection
  helpers and returns the one-hop eligible neighborhood as `{nodes, edges, seedIds}`.
- `index_status()` refreshes the SHA-256 source-digest-keyed in-process index and reports its
  digest, eligible record count, and build time.

## Gate evidence

| Gate | Evidence |
| --- | --- |
| Write isolation | Production code only calls `Path.read_bytes`, `yaml.safe_load`, `Exporter` projection helpers, and Ollama's embed endpoint. It imports no repository/proposal mutation path. |
| Provenance | `origin` is copied directly from the canonical quote; `test_search_filters_rights_and_lifecycle_and_preserves_origin_and_scores` passes. |
| Rights filter | Index admission positively requires active lifecycle plus public access, license, and holder, then applies `check_rights_public_export`. Empty, absent, restricted, and deprecated cases are excluded in tests. Graph nodes and both edge endpoints use the same eligible corpus. |
| Local AI | The only inference request is `OLLAMA_BASE_URL/api/embed`; model selection requires `OLLAMA_EMBED_MODEL`. There are no cloud SDKs or API keys. |
| Determinism | Ranking sorts by descending cosine score and canonical ID as a stable tie-breaker. The unchanged-digest cache/ranking test passes. |
| Secrets discipline | No secret is required or present; shared `.env.example` declares `OLLAMA_EMBED_MODEL=nomic-embed-text`. |
| Port isolation | Dockerfile exposes container port 3001 and the server binds 3001. R3a's compose service has no host `ports` binding. |

## Live benchmark and verification

`ollama list` confirmed `nomic-embed-text:latest` (`0a109f422b47`, 274 MB). With
`OLLAMA_EMBED_MODEL=nomic-embed-text`, the live source digest
`b663860b0b6ab4ca7e88c90661848993ae12401be69c74b801c46aa7cf957e97` indexed 229 eligible
records in **2.7192109579918906 seconds**.

Representative real outputs:

```text
$ OLLAMA_EMBED_MODEL=nomic-embed-text .venv/bin/python -m unittest discover -s services/mcp/tests -p 'test_*.py' -v
Ran 5 tests in 0.015s
OK

$ .venv/bin/python cli.py validate --strict --json
{"is_valid": true, "errors": [], "warnings": []}

$ .venv/bin/python cli.py stats --check
Recomputed total_quotes: 229
OK — stored meta matches recomputed snapshot.

$ .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
Ran 204 tests in 2.307s
OK
```

A disposable clean environment installed `services/mcp/requirements.txt`; importing and creating
the application returned `FastMCP`, confirming the declared FastMCP 2.x API is valid.

## Cold-review-equivalent self-audit

Concurrency was fully occupied by the three requested implementation lanes, so this lane performed
the mandated cold-review-equivalent audit rather than claiming a memory-independent reviewer. The
audit traced every §5 gate from inputs to returned fields and found two rights-boundary defects:

1. The shared rights sensor considers an empty rights mapping acceptable in isolation. R2 now
   additionally requires explicit public access, license, and holder before index admission.
2. An eligible graph source could formerly retain an edge to an ineligible target. R2 now requires
   both endpoints to exist in the eligible node set.

Both were fixed and regression-tested. No structural false assertion in the master plan was found.
This fulfills the parent task's explicit cold-review-equivalent self-audit requirement; a separate
memory-independent reviewer would still strengthen the next cascade-wide review.

## Files touched

- `services/mcp/server.py`
- `services/mcp/requirements.txt`
- `services/mcp/Dockerfile`
- `services/mcp/tests/test_server.py`
- `docs/DEV_PLAN/PHASE-R2-REPORT.md`

## Lessons for the next phase

R1 should consume scores, not infer confidence from result presence. Its stable integration call is
`semantic_retrieval`; `contextTag` deliberately matches the frontend spelling. Fail closed if the
MCP service or Ollama is unavailable. R3a has added `OLLAMA_EMBED_MODEL=nomic-embed-text` to the
placeholder-only `.env.example` and wired `mcp-server:3001` only on the internal compose network,
without a host `ports` binding. The safe resume point is R1 integration against the tool contract.
