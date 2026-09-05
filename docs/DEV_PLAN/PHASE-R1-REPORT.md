# Phase R1 Report — FastAPI backend bridge

**Status: DONE**

All six R1 routes ship and their backend-local gates pass. The initially missing R1→R2 transport
is now resolved with FastMCP's Streamable HTTP client and verified against the live R2 server.
R3a completed the full shared `domain.ts` contract. The root calibration/governance fixtures remain
R7 deliverables by that lane's runbook; R1 contains the equivalent negative assertion.

## Precondition gate

Re-verified before implementation on 2026-09-05:

```text
.venv/bin/python cli.py validate --strict --json
{"is_valid": true, "errors": [], "warnings": []}

.venv/bin/python cli.py stats
Total quotes: 229
By language (derived from quote lang; never hardcoded):
  en: 229
```

`python cli.py stats --check` subsequently reported `OK — stored meta matches recomputed snapshot.`

## Shipped endpoints

- `GET /health`: constructs and reads through `TTODRepository`; live response was
  `{"status":"ok","ttod_version":"3.1.0"}`.
- `GET /api/v1/schema/definitions`: reads the three real schema JSON files; live `jq` assertion
  `.quote | has("properties")` returned `true`.
- `GET /api/v1/wisdom/sample`: emits the client projection after server-side active/public/resolved
  filtering; live response contained 229 eligible records.
- `GET /api/v1/graph`: calls `Exporter.export_graph()` on the filtered snapshot and caches canonical
  bytes by source mtime plus SHA-256; live response contained 229 active nodes and 435 edges.
- `POST /api/v1/oracle/stream`: implements SSE envelopes, named threshold `0.575`, grounded versus
  creative prompts, no citations in creative mode, lightweight en/es matching, Ollama-only
  generation, and semantic retrieval through R2 at `${MCP_SERVER_URL%/}/mcp`. Production fails
  closed if MCP is unavailable; no local semantic fallback exists.
- `POST /api/v1/oracle/propose`: stages a `blackbox` proposal with explicit `lang`, nearest-neighbor
  section/tags, creative-mode source reference and unresolved rights; it never invokes acceptance or
  canonical mutation APIs.

## Gate evidence

| Gate | Evidence |
| --- | --- |
| Write isolation | Static scan found no subprocess, acceptance, canonical mutation, or canonical file-write call under `services/backend`; handlers only read `TTODRepository` and save via `ProposalStore`. |
| Provenance | `test_oracle_propose_cannot_activate_or_allocate_canonical_id` asserts `origin == blackbox`. |
| Creative disclosure | `test_creative_stream_discloses_mode_without_citations` passed. |
| Oracle-propose governance | Negative test passed: persisted status is `proposed`, not `active`; candidate has no `id`; no `accepted_quote_id` exists. |
| Rights filter | Backend test asserts public wisdom projection and active-only graph; live graph statuses were exactly `["active"]`. |
| Schema fidelity | Real schema-serving endpoint passed. Frontend `domain.ts` cross-check was reserved for the frontend lane, so the cross-lane portion is open. |
| Local AI | No cloud-vendor SDK/reference exists. R1 generation uses Ollama; R2 retrieval requires `OLLAMA_EMBED_MODEL`. `/api/tags` confirmed `qwen3.8:27b` and `nomic-embed-text:latest`. |
| MCP integration | FastMCP 2.14.7 Streamable HTTP call to live R2 returned keys `indexDigest,indexedQuotes,results`, 2 results, 229 indexed quotes, and the exact six result fields. Unavailable-MCP negative test proves fail-closed behavior. |
| Determinism | Two live graph responses compared byte-identical with `cmp`. |
| Secrets discipline | Backend `.env.example` contains configuration only; root `.gitignore` already contains `.env*`. |
| Port isolation | Dockerfile only documents backend port 8000; no 80/443/11434 binding or compose block was added. |

Backend-local suite:

```text
.venv/bin/python -m unittest discover -s services/backend/tests -p 'test_*.py' -v
Ran 6 tests in 0.705s
OK
```

Repository regression suite:

```text
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
Ran 204 tests in 2.355s
OK
```

## Oracle proposal acceptance caveat

This report does **not** claim that draft→review→accept works end to end. The pre-existing Phase S
gap remains: `TTODRepository.accept_proposal()` rejects an unvalidated `origin: blackbox` candidate,
while no current CLI review action writes the required candidate validation block. R1 correctly
stops at an inert proposal and does not work around that governance gate.

## Cold-review-equivalent self-audit

The lane was re-read gate-by-gate after implementation, then exercised through both TestClient and a
real localhost Uvicorn process. Findings:

1. The initial in-process embedding implementation incorrectly reused the generation model. It was
   removed from production R1 when retrieval moved to R2; shared configuration still makes
   `OLLAMA_EMBED_MODEL` explicit, and `nomic-embed-text` was verified locally.
2. The initial retrieval return was an internal tuple list; replaced with FastMCP Streamable HTTP
   and strict normalization of R2's `{results, indexDigest, indexedQuotes}` contract.
3. Structural finding resolved: R1 now connects to `${MCP_SERVER_URL%/}/mcp` using
   `fastmcp.Client`. A real call against R2 on port 3001 returned two normalized results over all
   229 eligible records. A connection to `127.0.0.1:1` raised the expected fail-closed error.
4. No canonical-data, schema, core, frontend, MCP, compose, or Caddy file was edited by this lane.

## Files touched

- `services/backend/.dockerignore`
- `services/backend/.env.example`
- `services/backend/Dockerfile`
- `services/backend/requirements.txt`
- `services/backend/app/{__init__,config,main,models,oracle,storage}.py`
- `services/backend/tests/test_backend.py`
- `docs/DEV_PLAN/PHASE-R1-REPORT.md`

## Safe resume point for R2/R3a

R3a can build `services/backend/Dockerfile` from repository-root context, expose container port
8000 only through Caddy, and set `MCP_SERVER_URL=http://mcp:3001`. R1 appends `/mcp` itself and has
already been exercised against R2's live Streamable HTTP endpoint. The backend reads `OLLAMA_MODE`,
`OLLAMA_MODEL`, `OLLAMA_EMBED_MODEL`, `OLLAMA_BASE_URL`, `MCP_SERVER_URL`,
`ORACLE_RETRIEVAL_THRESHOLD`, and `ORACLE_RETRIEVAL_TOP_K`.
