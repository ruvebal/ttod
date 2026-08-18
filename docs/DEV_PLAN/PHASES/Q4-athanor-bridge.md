<!--
Self-contained runbook. Derived from docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md —
that file is normative; regenerate this one if it changes.
-->

# Phase Q4 — Athanor-mediated two-way bridge

**Mode:** TTOD then Athanor (two sub-lanes, sequenced) · **Estimate:** 1.5–2.5 days
**Entry:** Q3 green, and the Athanor side's own S0-WPL freeze is complete (a precondition owned by
the Athanor repository, not this one — verify it before starting the Athanor sub-lane; do not
assume it)
**Exit:** two-way round trip works, with zero canonical-write capability granted to Athanor

## 0. What this phase actually is — and why it's two sub-lanes, not one

Q4 has a TTOD half and an Athanor half, and they are sequenced, not parallel: **freeze and test
the transport schema first, entirely within this repository, before touching anything in the
Athanor repository.** If you are an agent working this phase and you don't have access to the
Athanor repository/worktree, stop after the TTOD sub-lane (§2) and hand off explicitly — do not
simulate the Athanor adapter's behavior inside this repository as a substitute.

This phase is also the sharpest edge of the whole programme's safety model: Athanor is being
granted read access to TTOD data and a *proposal* channel back in, and it must be structurally
incapable of writing `ttod.yml`. Every design choice here should be checked against "what if the
Athanor side is fully compromised or fully wrong — can it still corrupt canonical TTOD data?" The
answer must always be no.

## 1. Required reading, in order

1. `docs/DEV_PLAN/PHASE-Q3-REPORT.md` — the CLI/transaction surface you're exposing over transport.
2. `docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md` §1 (the Quote out / Proposal in / Human
   promotion bullets — this is the transport contract's spec), §3 (independence protocol — quote-
   out carries `usage_role=pedagogical`; this is not decorative, it's the field that keeps a TTOD
   quote from being usable as WPL/Athanor evidence), and §4A (shared bridge bindings — this phase
   implements bindings from `deviac/docs/DEV_PLAN/TTOD-BRIDGE-INTEROPERABILITY-CONTRACT.md`, it
   does not invent a TTOD-specific protocol).
3. `../../../../deviac/docs/DEV_PLAN/TTOD-BRIDGE-INTEROPERABILITY-CONTRACT.md` (relative to this
   repo) — the actual reusable studio contract for transfer IDs, digests, lineage, rights, review
   state, and idempotency semantics that this phase's REST/transport layer must reuse rather than
   reinvent.
4. `.cursor/rules/ttod-editing.mdc` — the human importer on the Athanor side must read this before
   ever running `accept`.

## 2. TTOD sub-lane — transport schema and adapter-facing surface

1. Freeze and test a TTOD transport schema (JSON, versioned) with two message shapes:
   - **Quote-out response:** canonical quote ID, text, `content_digest`, snapshot digest, `origin`,
     item `rights`, review status, `related`, lifecycle, ancestry, and `usage_role=pedagogical`.
     No transport field may be silently dropped between the canonical record and this response —
     write a test that walks every field in `schema/quote.schema.json` and asserts it has a
     corresponding transport field or an explicit, documented reason for exclusion.
   - **Proposal-in request:** the Q2P proposal shape, without a canonical ID, preserving the WPL
     generation record id/digest and the shared `evidence_snapshot_digest` exactly as received.
2. Add CLI/API transport wiring (e.g. a thin serialization layer over the Q3 `proposal
   create/import` commands) that accepts a proposal-in payload and produces a quote-out payload —
   but grants **no** capability beyond what Q3 already exposes. This phase does not add a new way
   to write `ttod.yml`; it adds a wire format for the existing `propose`/`accept`-gated surface.
3. Confirm — and write a test proving — that nothing reachable from this transport layer can call
   an accept/deprecate/erase capability without going through the Q3 CLI's own human-invoked path.

## 3. Athanor sub-lane — adapter, separate worktree/repo

This work happens in the Athanor repository's own declared domain/application/adapter/tests
budget — **not** inside `/Users/ruvebal/src/ttod`. If those paths overlap active Athanor Phase S
work, queue integration rather than overwrite it; do not force a merge.

Requirements the Athanor adapter must satisfy (verify, don't just implement and assume):
1. Athanor reads only a versioned TTOD export/snapshot (Q2E's output) — **never** `ttod.yml`
   directly, and never with filesystem/database credentials that could write it.
2. Athanor stores its generated proposal/provenance in its own outbox and returns a portable
   proposal artifact. It has no code path, credential, or API surface that mutates canonical TTOD.
3. A human explicitly imports and accepts the proposal through the TTOD CLI, after having read
   `.cursor/rules/ttod-editing.mdc` — this is a human action outside Athanor's automation, not
   something Athanor triggers.

## 4. Round-trip verification

Run the round trip in both directions on fixtures (not live data) and compare **every** protected
field and digest before and after: quote-out → Athanor reads it → Athanor (or a fixture standing
in for it) produces a proposal-in payload → TTOD imports it → a human-simulated accept (using a
named test-reviewer identity, clearly marked as a test fixture, never a real identity) → compare
the accepted record's fields/digests against what was proposed, and the original quote-out's
fields/digests against what Athanor received. Any field that changed unexpectedly is a bridge bug.

## 5. Touched-path budget

**TTOD side, allowed:** bridge schema (new `schema/transport_*.json` or similar), a new
`ttod_core/bridge.py` or equivalent, its tests, CLI transport wiring in `cli.py` (additive only —
do not change existing Q3 command semantics).

**TTOD side, forbidden:** any change to the accept/deprecate/erase authority model from Q3 — this
phase must not loosen it "to make the bridge simpler." No credential, config, or code path that
lets an external caller skip the human-accept step.

**Athanor side:** out of scope for this file entirely — governed by Athanor's own phase docs.

## 6. Do NOT (failure modes seen on this class of task)

- Do not give the Athanor adapter a database or filesystem credential that can write `ttod.yml`,
  even "for the initial version" or "just for testing." There is no acceptable transitional state
  where this is true.
- Do not let the transport layer add a new way to allocate a canonical ID or bypass Q3's lock/
  re-read/validate sequence. It is a serialization layer over an existing gated surface, not a
  parallel write path.
- Do not drop the `usage_role=pedagogical` field, or any rights/review/lifecycle field, from the
  quote-out payload "to keep the response small." Every protected field must round-trip.
- Do not simulate or fabricate Athanor-side behavior inside this repository as a substitute for
  actually coordinating with the Athanor repository/worktree. If you can't reach it, say so.
- Do not use a real human identity string as the test-reviewer in round-trip fixtures — use an
  obviously-fake, clearly-labeled test identity so audit logs are never ambiguous about which
  acceptances were real.

## 7. Applicable gates

| Gate | Required proof |
| --- | --- |
| Round trip | TTOD-out and proposal-in preserve origin/license/validation/related/deprecation/ancestry and all digests |
| Capability | Athanor credentials cannot write canonical TTOD; model can propose but cannot accept |

## 8. Exact commands

```bash
cd /Users/ruvebal/src/ttod
. .venv/bin/activate
python -m unittest discover -s tests -p 'test_bridge*.py'
python cli.py bridge-self-test --fixture tests/fixtures/q4_roundtrip.json
```

(The `bridge-self-test` command name is an acceptance target from the master contract, not a
claim it exists yet — if Q3 didn't create it, this phase adds it as part of the CLI transport
wiring in §2.)

## 9. Report requirements

File `docs/DEV_PLAN/PHASE-Q4-REPORT.md`: state (may be `PARTIAL` if the Athanor sub-lane couldn't
run in this environment — say so explicitly, do not claim `DONE` for work you didn't verify),
field-by-field round-trip proof, confirmation Athanor has no write credential (cite the actual
adapter code/config, not just an assertion), files/repos touched, safe resume point for Q5.

## 10. Agent prompt — paste this into Cascade/Devin

```text
Act as TTOD bridge engineer for Phase Q4, TTOD sub-lane only, inside /Users/ruvebal/src/ttod. If
you do not have access to a separate Athanor repository/worktree, do the TTOD sub-lane only and
say so explicitly in the report rather than fabricating Athanor-side behavior.

Read docs/DEV_PLAN/PHASE-Q3-REPORT.md, docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md
sections 1, 3, and 4A, and ../../../../deviac/docs/DEV_PLAN/TTOD-BRIDGE-INTEROPERABILITY-CONTRACT.md
(relative to this repo) — reuse its transfer IDs/digest/lineage/rights/review-state/idempotency
semantics; do not invent a TTOD-specific protocol fork.

Freeze and test a versioned TTOD transport schema: a quote-out response carrying canonical quote
ID, text, content_digest, snapshot digest, origin, item rights, review status, related, lifecycle,
ancestry, and usage_role=pedagogical (write a test walking every field in schema/quote.schema.json
and asserting a transport-field mapping or a documented exclusion reason — no silent drops); and a
proposal-in request carrying the Q2P proposal shape without a canonical ID, preserving the WPL
record id/digest and evidence_snapshot_digest exactly.

Add CLI/transport wiring over the existing Q3 propose/accept-gated surface — additive only, no new
way to allocate a canonical ID or bypass the lock/re-read/validate transaction. Do not add any
credential or code path that lets an external caller skip the human-accept step.

Build round-trip fixtures (not live data) and prove every protected field/digest survives a
quote-out then proposal-in cycle, using an obviously-fake, clearly-labeled test-reviewer identity
for any simulated accept step — never a real identity.

File docs/DEV_PLAN/PHASE-Q4-REPORT.md with state (mark PARTIAL and explain if the Athanor sub-lane
was out of reach), the field-by-field round-trip proof, confirmation of what Athanor can and
cannot write (cite actual code), files touched, and the safe resume point for Q5.
```
