# Q0 decision — default TTOD license is CC BY-NC-SA 4.0

**Status:** FROZEN (rights-holder instruction, 2026-08-18)
**Decider:** Rubén Vega Balbás (TTOD rights holder)
**Cascade:** Phase Q0 rights/unresolved policy
**Does not mutate:** `ttod.yml`, `cli.py`, source chapters, exports

## Decision

The **default license for the TTOD database and for new canonical quotes** is
**CC BY-NC-SA 4.0**, not CC BY-SA 4.0.

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

- It does **not** rewrite `ttod.yml` header/`CLAUDE.md` in this session.
  Those strings change in **Q6** (docs/migration) after schemas exist.
- It does **not** claw back copies already distributed under CC BY-SA 4.0.
  Prior BY-SA grants remain valid for those copies. Forward snapshots use NC.
- It does **not** invent licenses for third-party text inside quotes. Those
  stay `unresolved` until a source_ref + permission_basis exists.
- It does **not** accept the nine staged Web Atelier proposals. They stay in
  `~/src/.cursor/skills/ttod-bridge/pending/` until Q3 provides a safe atomic
  accept path.

## Q1/Q5 consequences

| Surface | Rule |
| --- | --- |
| Default `rights.license` | `CC-BY-NC-SA-4.0` |
| Default `rights.holder` | `ruvebal@crea-comm.net` (named identity, not inferred origin) |
| Public export | NC restriction must appear in snapshot manifest; commercial reuse is out of license |
| NC → SA merge | still forbidden |
| SA → NC (own work, forward) | allowed by this decision; record `permission_basis=rights-holder-relicense-2026-08-18` |
| Unresolved item rights | still block public export (Q5 sensor) |

## Pending quotes this unblocks (after Q3)

Nine pruned survivors from Web Atelier `docs/` (see
`~/src/.cursor/skills/ttod-bridge/pending/README.md`): arch-060, arch-061,
arch-062, arch-064, arch-066, cc-039, cc-040, wis-018, wis-019. Each should
carry `rights.license: CC-BY-NC-SA-4.0` on accept.
