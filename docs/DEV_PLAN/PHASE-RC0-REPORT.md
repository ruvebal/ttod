# Phase T / RC0 Report — Release baseline and decision freeze

**State:** VERIFYING

**Execution date:** 2026-09-07

**Implementer:** Codex release-steward session

**Independent verifier:** unassigned; required before `DONE`

**Product-owner promotion:** pending

**Cascade:** [`PHASE-T-PUBLIC-RELEASE-EXCELLENCE-CASCADE.md`](PHASE-T-PUBLIC-RELEASE-EXCELLENCE-CASCADE.md)

## 1. Outcome

RC0's baseline, audience gates, retention intentions, work ownership, and RC3/R6 boundary are now
frozen for independent verification. The implementation baseline is green, but none of the three
release outcomes is authorized:

- `PUBLIC_SOURCE`: not evaluated; RC1–RC3 and RC7 remain required;
- `PARTNER_DEMO`: not evaluated; RC5 and RC7 remain required; and
- `STUDENT_DISTRIBUTION`: blocked by reachable reference history until RC4 and RC6 prove otherwise.

RC0 changed planning documents only. It did not change application code, canonical content,
proposal state, remote visibility, infrastructure, or deployment state.

## 2. Baseline identity

| Fact | Observed value |
| --- | --- |
| Local branch | `main` |
| `HEAD` | `fc5a8a572c21ceecde98cd219b15507379255635` |
| `origin/main` | `fc5a8a572c21ceecde98cd219b15507379255635` |
| GitHub repository | `https://github.com/ruvebal/ttod` |
| GitHub visibility | `PRIVATE` |
| GitHub default branch | `main` |
| GitHub detected license | `Other` (expected signal from the split-license repository) |
| Python | `3.14.7` |
| Node | `v22.22.0` |
| npm | `10.9.4` |
| Docker | `29.2.1` |
| Docker Compose | `v5.1.0` |

The checkout was synchronized with `origin/main` but not clean at RC0 entry: the already-requested
Phase T planning edits to `docs/DEV_PLAN/INDEX.md` and the cascade document were present. RC0
preserved those edits and added this report/status transition. No unrelated user change was found.

## 3. Canonical-data immutability

Before RC0 documentation edits:

```text
SHA-256(ttod.yml) = 530b15286488ad4be0a1db63532a920642f25b073d1e89b3876e9ff5951e6e1b
```

The same digest was rechecked after the report and status edits. `ttod.yml` did not change.

## 4. Repository inventory

The pre-report candidate contained 473 tracked files occupying 2,798,276 working-tree bytes.
Git object statistics reported 1,182 loose objects / 5.89 MiB and a 67.24 MiB pack. Working-tree
bytes and packed-history bytes measure different things and must not be compared as though they
were the same metric.

| Top-level surface | Files | Working-tree bytes | RC0 observation |
| --- | ---: | ---: | --- |
| `docs/` | 73 | 828,117 | largest navigation/governance surface |
| `services/` | 54 | 474,111 | application/reference implementation |
| `ttod.yml` | 1 | 448,118 | canonical content; excluded from Phase T mutation |
| `proposals/` | 242 | 439,929 | 239 proposals plus 3 manifests |
| `tests/` | 61 | 156,157 | governed core and platform tests |
| `private/` | 1 | 141,946 | tracked pre-Q6 backup; public disposition unresolved until RC2 review |
| `ttod_core/` | 16 | 138,563 | governed domain implementation |
| `sources/` | 5 | 80,970 | parked licensed teaching sources |
| Remaining root/schema/tooling surfaces | 20 | 129,465 | CLI, schemas, licenses, configuration, and agent rules |

Proposal-state measurement:

| Proposal material | Count |
| --- | ---: |
| Accepted proposal JSON | 229 |
| Proposed proposal JSON | 10 |
| Manifest JSON | 3 |

The largest reachable blobs were current/historical `ttod.yml` snapshots, frontend lockfiles, the
pre-Q6 backup, and the Phase R cascade. This is an information-architecture concern, not evidence
that JavaScript tree shaking is failing.

Ignored local state included `.env`, virtual environments, Node dependencies, Astro/build output,
test output, caches, bytecode, `.DS_Store`, and the local workspace file. None was found tracked.

## 5. Reference-build reachability

The combined reference implementation is commit:

```text
47b46de5d9d6d8688dd8ff070432092c6653acd2
Phase R reference implementation — R1/R2/R3a (instructor) + R3b/R4/R5/R7 (reference build)
```

The exact check was:

```bash
git merge-base --is-ancestor 47b46de5 origin/main
```

It exited `0`. Therefore `origin/main` in the private repository already exposes the complete
R3b/R4/R5/R7 reference history to anyone granted repository access. A descendant
`cohort-starter` branch cannot be considered isolated. Remote privacy is not mitigation for a
student who must receive a clone from that remote.

RC4 must create a fresh-history artifact/repository and pass the full object-graph probe. RC7 must
recheck the exact distributed artifact, not infer isolation from the generator script.

## 6. Verification evidence

All required RC0 matrix commands were run from the live candidate checkout.

| Check | Result |
| --- | --- |
| `python cli.py validate --strict --json` | PASS; valid, zero errors, zero warnings |
| `python cli.py stats --check` | PASS; stored metadata matched recomputation |
| root unittest discovery | PASS; 211 tests |
| backend unittest discovery | PASS; 6 tests |
| MCP unittest discovery | PASS; 5 tests |
| `npm ci` | PASS; 619 packages installed; `tsconfck@3.1.6` emitted an unmaintained-package warning |
| `npm run check` | PASS; 30 files, zero diagnostics |
| `npx vitest run` | PASS; 2 files / 6 tests |
| `npm run build` | PASS; server and client production build completed |
| `docker compose config --quiet` | PASS |
| targeted tracked-tree secret-pattern triage | no matching credential/private-key pattern |

The Python suites emitted non-failing maintenance warnings:

- `datetime.utcnow()` deprecation under Python 3.14;
- Starlette TestClient/httpx compatibility deprecation; and
- Authlib `jose`/httpx deprecations.

These warnings are retained as later maintenance work. The secret-pattern scan is triage, not a
security clearance; RC2 must review current and reachable history manually and with dedicated
tools before a public-source decision.

### Failed measurement retained

The first attempt to aggregate top-level byte counts used an incorrectly escaped nested `awk`
program and produced syntax errors. It changed no files. RC0 replaced it with a deterministic
read-only inventory over `git ls-files`; the corrected measurements appear in §4. This failure is
recorded so the report does not present a selectively clean execution history.

## 7. Audit classification

### Release blockers

| Finding | Affected gate | Owning phase |
| --- | --- | --- |
| no root `README.md`; current entry point is stale | public source, partner, student onboarding | RC1 |
| split-license/community/security contract is not presented conventionally | public source | RC1 |
| tracked `private/` backup has not received a confidentiality/retention decision | public source | RC2 |
| personal paths and private infrastructure occur throughout active/history documentation | public source | RC2, with RC1 fixing active entry points |
| targeted pattern scan is not a full present/history disclosure review | public source | RC2 |
| `/api/v1/oracle/propose` is anonymously writable through Caddy | any non-local live exposure | RC3 |
| reference commit is reachable from `origin/main` | student distribution | RC4 |
| no clean-machine novice trial exists for the exact isolated artifact | student distribution | RC6 |

### Accepted risks at RC0

| Finding | Decision |
| --- | --- |
| GitHub reports license as `Other` | acceptable for a deliberately split MIT/code and CC BY-NC-SA/content repository, provided RC1 explains it clearly |
| repository remains private | correct until RC7 plus human `PUBLIC_SOURCE=GO`; privacy alone is not a readiness claim |
| local-only proposal endpoint is convenient | acceptable only in an explicitly local profile; it cannot remain anonymously writable in a non-local exposure profile |

### Later work, not RC0 blockers

| Finding | Reason |
| --- | --- |
| Python/npm dependency deprecation warnings | builds and tests pass; track for maintenance without weakening RC1–RC7 gates |
| R7 interaction and measured-CI gaps | remain honestly partial and coupled to student-owned R6; they do not authorize Phase T to implement R6 |
| frontend chunk sizes | no present evidence of a bundle blocker; measure in the appropriate student/R6 performance work rather than conflate it with repository treeshaking |

### False-positive interpretations rejected

- “Private GitHub means the student branch is isolated” is false; reference history is reachable.
- “No regex secret hit means the repository is safe to publish” is false; RC2 remains required.
- “All tests pass means the application is safe for Internet exposure” is false; RC3 remains
  required.
- “Treeshake means delete historical evidence” is false; retention and provenance govern it.

## 8. Frozen audience gates

1. **Public source:** source readability, rights, disclosure, contribution/security expectations,
   and public-safe defaults. It does not imply a hosted service.
2. **Partner demonstration:** a rehearsed local/private demonstration with truthful maturity labels
   and failure fallbacks. It may become `GO` while public source or students remain `NO-GO`.
3. **Student distribution:** a clean-history starter, supported-machine onboarding, and
   pedagogical non-disclosure of reference answers. It is independent of repository visibility.

RC7 and the product owner must decide all three separately.

## 9. Frozen decisions

### D-RC0-1 — RC3 may harden application boundaries without implementing R6

RC3 is authorized to change only the FastAPI/backend security boundary, Caddy exposure and
headers, local/demo/public configuration profiles, corresponding `.env.example`/Compose settings,
and security-focused backend tests/documentation. This is prerequisite hardening, not deployment.

RC3 must not add or modify `.github/workflows/`, a PWA/service worker, Lighthouse budgets,
Scaleway provisioning/deployment, CI sharding, or any other deliverable enumerated in the frozen
R6 decision. Discovery of a required overlap blocks RC3 for a product-owner decision.

### D-RC0-2 — Proposal records remain evidence; public navigation changes

All proposal IDs, accepted/proposed states, review activities, and manifests are retained until
RC2 produces and verifies a content-addressed disposition. The intended public shape is:

- active proposal workflow stays operational but is not presented as newcomer content;
- accepted records remain resolvable as governance/provenance evidence through an indexed,
  checksummed archive or release artifact; and
- no record is silently deleted or rewritten for cosmetic cleanup.

RC2 selects the exact storage shape after checking code/tests/links and public-data sensitivity.

### D-RC0-3 — Development reports move behind an archive index

Detailed phase reports remain part of the scholarly engineering record but should not dominate
the public path. RC2 may reorganize them under a link-checked archive/index. RC1 owns the concise
current roadmap and public entry point. Historical claims remain dated rather than rewritten as
current truth.

### D-RC0-4 — Parked sources remain, subject to rights review

`sources/` is intended to remain public because it contains documented, licensed teaching-source
material and provenance context. RC2 must verify authorship, third-party quotation limits,
frontmatter, and license claims. Any unresolved rights item blocks public-source release or is
excluded through a documented, recoverable archive decision.

### D-RC0-5 — The pre-Q6 backup is excluded from the public candidate

`private/ttod.yml.pre-q6-backup` is not part of the intended public working tree. RC2 must first
confirm whether it is confidential, required by tests, or required as a migration/provenance
record, then preserve its digest and place the required copy in an appropriate controlled archive.
If it contains confidential material, deletion commits are insufficient: public source remains
`NO-GO` until an approved history rewrite/remediation has been coordinated. RC0 itself neither
deletes nor rewrites it.

## 10. RC1–RC4 ownership and collision boundary

| Lane | Named owner profile | Exclusive primary files/surfaces | Must not edit |
| --- | --- | --- | --- |
| RC1 | documentation/release owner | root `README.md`, `INDEX.md`, `CONTRIBUTING.md`, `SECURITY.md`, support/community policy, `pyproject.toml` descriptive metadata, active public onboarding except the student guide | archives/proposal records, backend/Caddy code, starter generator/artifact |
| RC2 | repository curator plus security reviewer | retention/disclosure inventory, archive structure, `proposals/`, `private/`, historical reports, `sources/`, link/disclosure reports | root public entry/community files, application security code, starter generator |
| RC3 | application-security owner | `services/backend/`, `caddy/`, security-specific service tests, exposure-profile keys in `.env.example`/Compose, threat-model report | `.github/`, PWA/service worker, cloud deploy, canonical/proposal content, root public narrative |
| RC4 | instructor release engineer | `scripts/generate-cohort-starter.sh` or replacement exporter, allow/deny manifests, checksum/isolation probes, isolated artifact, student-specific guide | reference implementation, canonical data, RC1 public entry point, RC3 security implementation |

If a lane needs an exclusively owned file from another lane, it stops and requests orchestration;
it does not create a competing edit. Parallel execution requires separate worktrees. Reports are
lane-owned and may be added independently.

## 11. State transition and safe resume

RC0 is `VERIFYING`, not `DONE`. RC1–RC4 remain `BLOCKED` until:

1. an independent verifier repeats or samples this baseline, checks the frozen decisions against
   the cascade and R6 decision, and records approval or corrections; and
2. the product owner explicitly promotes RC0 to `DONE`.

The safe next action is independent RC0 verification. It should begin from commit
`fc5a8a572c21ceecde98cd219b15507379255635` plus the uncommitted Phase T/RC0 documentation diff,
confirm the final `ttod.yml` digest, and inspect `git diff --check`. It must not start RC1–RC4 or
change GitHub visibility.
