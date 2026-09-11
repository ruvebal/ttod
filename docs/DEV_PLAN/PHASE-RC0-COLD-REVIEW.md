# PHASE-RC0 Cold Review

**Reviewer:** Claude Sonnet 5, orchestrating a `cascade-cold-reviewer` pass on local `qwen3.8:27b`
for document-comprehension findings, combined with independently re-run live verification.
**Date:** 2026-09-11
**Subject:** [`PHASE-RC0-REPORT.md`](PHASE-RC0-REPORT.md)
**Method:** two passes, deliberately separated by what each can actually check.
1. **Live re-verification** (this session, direct tool access) — re-ran the exact commands RC0's
   own report cites, against the *current* checkout, not the frozen one.
2. **Document-comprehension review** (`qwen3.8:27b` via local Ollama, `think:false`, plain-text
   delimited output — the same calling convention `PHASE-S4-REPORT.md` established for this model)
   — given the report's full text plus the cascade's §1–2 boundaries, with **no live repository
   access**, explicitly disclaimed by the model itself. Raw output preserved in this session's
   scratchpad if needed for audit.

## Verdict, stated first

**RC0's baseline has drifted too far to promote as-written. This is not an editorial cold review —
it needs a fresh RC0 pass against the current commit.** The live re-verification below (§1) found a
P0 issue the document-comprehension pass could not have found, by its own honest admission ("I do
not have live repository access"). The `qwen3.8:27b` pass (§2) found five real, worth-fixing
document-quality issues, none of which are the blocking problem.

## 1. Live re-verification findings (P0 — blocks promotion)

### F0 — RC0's frozen baseline is stale; canonical data has since changed

**Severity:** P0. **Blocks DONE:** Yes, and blocks even "independently verify as-is" — the
baseline itself needs re-freezing, not just review.

**Evidence, re-run live 2026-09-11:**

```text
RC0 claimed:  SHA-256(ttod.yml) = 530b15286488ad4be0a1db63532a920642f25b073d1e89b3876e9ff5951e6e1b
Actual now:   SHA-256(ttod.yml) = 9503e81d6bcd52c5fbdf52c45200372b2a0ca7fef8892a0a7e913fc46d8f7850

RC0 claimed:  HEAD = fc5a8a572c21ceecde98cd219b15507379255635
Actual now:   HEAD = 8d5cdf39a1c67c570f8ec2eeb6b353aee73668ed
```

`git merge-base --is-ancestor fc5a8a57 HEAD` exits `0` — this is a clean fast-forward, not a
diverged/conflicting history — but **22 commits have landed since RC0's baseline**, including real
canonical-data mutation (`ttod.yml`'s digest genuinely changed — S5's bilingual-corpus promotion,
229 Spanish translations accepted, landed after RC0 was filed) and an entire additional teaching
cascade (`Phase V` / TS5 "orphan-history teaching-baseline assembly," not mentioned anywhere in
RC0's report because it didn't exist yet at RC0's baseline commit).

**Why this specifically blocks promotion, not just "needs a note":** RC0's own §3
("Canonical-data immutability") states as a verified fact that "`ttod.yml` did not change" — true
at the time, now false of the current checkout. §11's own safe-resume instruction ("begin from
commit `fc5a8a57`... confirm the final `ttod.yml` digest") describes verifying a baseline that no
longer represents the repository's current state. An independent verifier following RC0's own
instructions literally would check the wrong commit and the wrong digest.

**Fix recommendation:** Re-run RC0's full verification matrix (§4–§6 of its own report) against
current `HEAD`. Do not attempt to "patch" the existing report's numbers — file a fresh baseline
pass; the drift is large enough (canonical-data change, a whole new sub-cascade landed) that a
diff-and-amend would be harder to trust than a clean re-run.

**Not re-run in this pass, and why:** the full RC0 verification matrix (Python/Node suites, `npm
ci`, `docker compose config`) was not re-executed here — this cold review's job was to check RC0's
*own* claims for staleness and internal consistency, not to perform RC0 itself. Re-running the full
matrix is the fresh RC0 pass's job, not this review's.

## 2. Document-comprehension findings (`qwen3.8:27b`, no live access — editorial/consistency only)

Re-triaged against my own judgment of severity; the model's own F1–F5 numbering is preserved for
traceability to the raw output.

| # | Finding | My severity | Blocks DONE? | Worth fixing? |
| --- | --- | --- | --- | --- |
| F1 | "Baseline is green" (§1) sits next to an unmitigated anonymous-write endpoint (§7) — reads as conflating test-green with release-ready | P2 (downgraded from the model's P1 — the same sentence already says none of the three release outcomes is authorized, so the ambiguity is narrower than claimed) | No | Yes — cheap clarity fix |
| F2 | The baseline is a commit *plus* an uncommitted documentation diff, not one immutable commit | P2 | No | Yes, and it compounds F0 above — a fresh RC0 pass should commit its own report as part of freezing the baseline |
| F3 | "Repository remains private" listed under "Accepted Risks" could be misread as privacy-as-mitigation, even though the same row already says "privacy alone is not a readiness claim" | P2 (downgraded — the disclaimer is already present in the same cell) | No | Yes — the model's suggested rewrite is clearer than the original |
| F4 | §1 says "blocked" for `STUDENT_DISTRIBUTION` rather than the cascade's own `GO`/`NO-GO` vocabulary | P3 | No | Yes, trivial |
| F5 | "Zero warnings" (§6, `cli.py validate`) sits near a separate "non-failing maintenance warnings" note (Python suites) — could be misread as contradictory | P3 | No | Yes, trivial — one clarifying sentence |

None of F1–F5 block promotion on their own merit; all are legitimate, cheap clarity improvements a
fresh RC0 pass should fold in while it's already rewriting the baseline for F0.

## 3. What this review does not cover

- Did not re-run the full RC0 verification matrix (see §1 "Not re-run" note above).
- Did not evaluate RC1–RC4's own readiness — RC0 gates them, not the reverse.
- Did not touch `Phase V`/TS5's own content — noted only because its existence is itself evidence
  of F0 (the baseline predates it).

## 4. Recommendation to the product owner

**Do not promote RC0 to `DONE`.** Do not proceed to RC1–RC4 from the existing report. Re-run RC0
against current `HEAD` (`8d5cdf39` at review time — re-check before use, it will have moved again),
folding in F1–F5's cheap clarity fixes while re-freezing. This is squarely a "amend on surprise"
case, not a "findings triaged, promote anyway" case — cascade-forge's own closing protocol says a
surprise that invalidates a downstream phase's assumptions gets the cascade amended in the same
commit as the report, not quietly absorbed.
