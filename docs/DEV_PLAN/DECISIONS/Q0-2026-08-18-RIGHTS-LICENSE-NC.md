# Q0 decision — repository split-license: code MIT, content CC BY-NC-SA 4.0

**Status:** FROZEN (rights-holder instruction, 2026-08-18)
**Decider:** Rubén Vega Balbás (TTOD rights holder)
**Cascade:** Phase Q0 rights/unresolved policy
**Does not mutate:** `ttod.yml`, `cli.py`, source chapters, exports
**Amended:** 2026-08-18 — added the repository split-license (decision 1 below) and the two
`LICENSE-CODE`/`LICENSE-CONTENT` files at repo root; the original NC-default decision (2) is
unchanged, only reframed as the content half of the split.

## Decision

Two separate decisions, frozen together:

1. **Repository split license**, mirroring the pattern already in production at
   [`web-atelier-udit`](https://github.com/ruvebal/web-atelier-udit) (`LICENSE-CODE` +
   `LICENSE-CONTENT` at repo root):
   - **Code** (`cli.py`, `ttod_core/` once created, `schema/*.json`, `pyproject.toml`, tests,
     tooling) is **MIT**. See [`../../../LICENSE-CODE`](../../../LICENSE-CODE).
   - **Content** (`ttod.yml` quote text, `docs/`, `sources/`) is **CC BY-NC-SA 4.0**. See
     [`../../../LICENSE-CONTENT`](../../../LICENSE-CONTENT).
   - This split exists because code and pedagogical prose have different reuse goals: the CLI
     and schema should be freely embeddable in other tooling; the quotes should not be resold
     or folded into a commercial product without the same share-alike terms.

2. **The default license for the TTOD database and for new canonical quotes** is
   **CC BY-NC-SA 4.0**, not CC BY-NC-SA 4.0. This is the content half of decision 1, stated
   precisely for the schema/CLI implementation.

Item-level `rights.license` still travels with each quote. The default fills only
records whose rights were previously database-inherited or unresolved **and**
whose author is this rights holder.

## Why

1. Web Atelier methodology and `sources/tao-of-ai-development/` are already
   CC BY-NC-SA 4.0. Q0 readiness recorded that NC source **cannot** merge into a
   BY-SA database by silent relicensing.
2. The rights holder asked for NC on TTOD as well. Matching the teaching
   materials removes the merge blocker without converting NC work to SA.
3. Q0 forbids guessing licenses. This is an identified human rights decision,
   not an inferred default.

## What this does not do

- It does **not** rewrite `ttod.yml` header/`AGENTS.md` in this session. Legacy `CLAUDE.md` is now
  a redirect; both currently still
  say `License: CC BY-NC-SA 4.0` — stale relative to both halves of this decision. Those strings
  change in **Q6** (docs/migration) after schemas exist; `LICENSE-CODE`/`LICENSE-CONTENT` are the
  authoritative repository-level statement in the meantime.
- It does **not** claw back copies already distributed under CC BY-NC-SA 4.0.
  Prior BY-SA grants remain valid for those copies. Forward snapshots use NC.
- It does **not** invent licenses for third-party text inside quotes. Those
  stay `unresolved` until a source_ref + permission_basis exists.
- It does **not** accept the nine staged Web Atelier proposals. They stay in
  `~/src/.cursor/skills/ttod-bridge/pending/` until Q3 provides a safe atomic
  accept path.

## Q1/Q5 consequences

| Surface                     | Rule                                                                                   |
| --------------------------- | -------------------------------------------------------------------------------------- |
| Default `rights.license`    | `CC-BY-NC-SA-4.0`                                                                      |
| Default `rights.holder`     | `ruvebal@crea-comm.net` (named identity, not inferred origin)                          |
| Public export               | NC restriction must appear in snapshot manifest; commercial reuse is out of license    |
| NC → SA merge               | still forbidden                                                                        |
| SA → NC (own work, forward) | allowed by this decision; record `permission_basis=rights-holder-relicense-2026-08-18` |
| Unresolved item rights      | still block public export (Q5 sensor)                                                  |

## Pending quotes this unblocks (after Q3)

Nine pruned survivors from Web Atelier `docs/` (see
`~/src/.cursor/skills/ttod-bridge/pending/README.md`): arch-060, arch-061,
arch-062, arch-064, arch-066, cc-039, cc-040, wis-018, wis-019. Each should
carry `rights.license: CC-BY-NC-SA-4.0` on accept.
