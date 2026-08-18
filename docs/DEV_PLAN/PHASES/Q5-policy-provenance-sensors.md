<!--
Self-contained runbook. Derived from docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md —
that file is normative; regenerate this one if it changes.
-->

# Phase Q5 — policy and provenance sensors

**Mode:** parallel by sensor · **Estimate:** 1–1.5 days
**Entry:** Q3/Q4 contract in place
**Exit:** independence, rights, lifecycle, provenance sensors all green

## 0. What this phase actually is

Q2–Q4 built the mechanisms (validation, canonicalization, proposals, the bridge). Q5 builds the
**adversarial checks** that keep those mechanisms honest over time — deterministic sensors that
fail loudly the moment someone (human or model) tries to route around a boundary. Each sensor is
small, single-purpose, and has both a positive and a negative fixture. `arch-052` is the permanent
adversarial fixture running through several of these — treat it as a named test citizen, not an
edge case to special-case away.

## 1. Required reading, in order

1. `docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md` §3 (independence protocol — the exact
   rejected edges list) and §6 (Independence, Rights, Erasure gate rows).
2. `docs/DEV_PLAN/PHASE-Q0-READINESS-REPORT.md` §3 ("Architecture finding") — this is the
   conceptual model (evidence snapshot / canonical quote snapshot / proposal, kept distinct) that
   every sensor in this phase is mechanically enforcing.
3. The Q2V/Q2E/Q2P/Q3/Q4 reports — sensors here consume their outputs (diagnostic codes, digests,
   transport payloads); they do not reimplement that logic.

## 2. Sensors to build (one deterministic check each, positive + negative fixture)

1. **Sibling-process quotation sensor.** Rejects exactly these edges from contract §3:
   `AthanorDraft -> supports -> WPLClaim`; `WPLDraft -> supports -> AthanorDecision`;
   `TTODQuote(source=AthanorPlan) -> supports -> AthanorDecision`; any `quotation` whose evidence
   pointer resolves only to a sibling output or a TTOD copy.
2. **Evidence admissibility sensor.** Given a claim and its cited evidence pointer, determines
   `evidence_admissible` true/false. **`arch-052` is the permanent adversary here**: its ancestry
   points to an Athanor Phase 2 plan; it may round-trip as a pedagogical quote, but when the
   consuming claim belongs to Athanor/WPL architecture, this sensor must set
   `evidence_admissible=false` and `independence_reason=SELF_DERIVED_NOT_EVIDENCE`. Build the
   fixture with `arch-052`'s actual shape (or an exact stand-in with the same ancestry pattern if
   the live record isn't available at this phase), not a generic placeholder.
3. **Rights/public-export sensor.** Unresolved or restricted item rights block public export,
   full stop — no override, no "resolve later" flag that lets export proceed anyway.
4. **Observed-vs-declared generation sensor.** Compares a proposal's declared generation method
   against any observable evidence and flags mismatches — this exists so "the model says it did X"
   is checkable, not just trusted.
5. **Human-acceptance sensor.** Confirms blackbox/mixed-origin content cannot be `active` without
   an identified human acceptance activity (built on Q2P's append-only review-activities model).
6. **Immutable-ID/deprecation sensor.** Once assigned, a canonical ID never changes and is never
   reused; retirement always goes through `deprecated`, never silent removal.
7. **Higher-law erasure sensor.** The exceptional path: ordinary deletion always fails (assert
   this as a positive requirement, not just "unimplemented"). A higher-law erasure requires an
   identified human authority, a decision reference, an exact scope, and a protected audit record;
   it replaces public content with a tombstone and must **not** retain the erased personal content
   merely to satisfy provenance record-keeping — those two goals conflict here and the sensor must
   enforce that erasure wins for the specific scoped content while the *fact and authority* of the
   erasure remains auditable. The system records the decision and authority; it does not itself
   adjudicate whether the underlying legal claim is valid.
8. **Digest transfer sensor.** Any content/snapshot/WPL/evidence digest that doesn't match its
   claimed source fails — this is largely Q2E's Integrity gate re-asserted at the policy layer
   with adversarial fixtures (deliberately tampered digests), not just the happy-path unit test.
9. **Shared-snapshot equality sensor.** Confirms Athanor and WPL, when they claim to be using "the
   same" evidence snapshot, are actually referencing the identical digest — not two snapshots that
   merely look similar.

## 3. Touched-path budget

**Allowed:** a new policy module (e.g. `ttod_core/policy.py` or `ttod_core/sensors/`), sensor
scripts, focused fixtures/tests under `tests/fixtures/q5_*` and `tests/test_sensors*.py`.

**Forbidden:** any live canonical or corpus mutation. Sensors read/inspect; they do not write
`ttod.yml`, and testing them must not run against the live repository-root file.

## 4. Do NOT (failure modes seen on this class of task)

- Do not special-case `arch-052` out of the evidence-admissibility sensor "since it's just a test
  fixture." It is the adversarial fixture precisely because it's a real, currently-existing record
  with this exact ancestry shape — the sensor must handle it as real data, because it is.
- Do not implement the erasure sensor so that it either (a) never actually removes content
  (defeating the point of erasure) or (b) removes content so thoroughly that the audit record of
  *who authorized what, when, under what scope* is also gone. Both failure directions are wrong;
  re-read §2.7 above before implementing.
- Do not build a "resolve later" escape hatch on the rights/public-export sensor. Unresolved
  blocks export; there is no configuration flag that changes this.
- Do not write a digest-tampering test that only checks the happy path (untampered digest passes).
  The gate requires proving tampering is *caught*, not just that correctness is preserved.
- Do not treat "the two snapshot digests are equal" and "the two snapshots are semantically
  similar" as the same check. The shared-snapshot sensor must compare digests, not fuzzy content.

## 5. Applicable gates

| Gate | Required proof |
| --- | --- |
| Independence | sibling prose and arch-052 cannot satisfy supports_claim; common snapshot remains usable by both processes |
| Rights | item terms survive round trip; unresolved/restricted content cannot enter public export |
| Erasure | normal delete fails; authorized tombstone path removes protected content and keeps minimal lawful audit |

## 6. Exact commands

```bash
cd /Users/ruvebal/src/ttod
. .venv/bin/activate
python -m unittest discover -s tests -p 'test_sensors*.py'
```

## 7. Report requirements

File `docs/DEV_PLAN/PHASE-Q5-REPORT.md`: state, one line per sensor confirming positive+negative
fixtures exist and pass, explicit confirmation of the `arch-052` expected verdict
(`evidence_admissible=false`, `independence_reason=SELF_DERIVED_NOT_EVIDENCE`), confirmation that
ordinary deletion fails and the authorized erasure path is tested against a fixture (not live
data), files touched, safe resume point for Q6.

## 8. Agent prompt — paste this into Cascade/Devin

```text
Act as TTOD policy/sensor engineer for Phase Q5. Work only inside /Users/ruvebal/src/ttod. Read
docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md sections 3 and 6, and docs/DEV_PLAN/
PHASE-Q0-READINESS-REPORT.md section 3.

Build nine deterministic sensors, each with a positive and negative fixture under
tests/fixtures/q5_*: (1) sibling-process quotation — reject AthanorDraft-supports-WPLClaim,
WPLDraft-supports-AthanorDecision, TTODQuote(source=AthanorPlan)-supports-AthanorDecision, and any
quotation whose evidence resolves only to a sibling output or TTOD copy; (2) evidence
admissibility, with arch-052's real ancestry shape (Athanor Phase 2 plan origin) as the permanent
adversary — must yield evidence_admissible=false and independence_reason=SELF_DERIVED_NOT_EVIDENCE
when the consuming claim is Athanor/WPL architecture, with NO special-casing that exempts it; (3)
rights/public-export — unresolved or restricted rights block export with no override flag; (4)
observed-vs-declared generation method mismatch detection; (5) human-acceptance — blackbox/mixed
content cannot be active without an identified human acceptance activity; (6) immutable-ID/
deprecation — no ID reuse or silent removal, retirement only via deprecated; (7) higher-law
erasure — ordinary deletion always fails; authorized erasure requires identified human authority,
decision reference, exact scope, and a protected audit record, replaces content with a tombstone,
but does not retain the erased content merely to satisfy provenance (the erasure itself, and its
authority, stays auditable; the erased content does not); (8) digest transfer — content/snapshot/
WPL/evidence digest tampering is caught (test tampered fixtures, not just clean ones); (9)
shared-snapshot equality — compares actual digests, not fuzzy content similarity.

Do not special-case arch-052 out of sensor 2. Do not build a bypass flag for sensor 3. Do not let
sensor 7 either fail to remove content or destroy the audit trail of who authorized the erasure.
Test everything against fixtures, never the live ttod.yml.

File docs/DEV_PLAN/PHASE-Q5-REPORT.md with per-sensor pass confirmation, explicit arch-052 verdict
confirmation, erasure-vs-deletion proof, files touched, and the safe resume point for Q6.
```
