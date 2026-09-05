# Phase R closure and cohort-handoff report

**Filed:** 2026-09-05
**Scope:** reconciles Phase R's planning documents with the repository's actual state, formalizes
the R6 deferral, resolves the student-starter boundary, records this pass's R7 evidence, and lists
the TTOD wisdom proposals distilled from this implementation. Read alongside
[`DECISIONS/R6-DEFERRED-STUDENT-OWNED.md`](DECISIONS/R6-DEFERRED-STUDENT-OWNED.md),
[`PHASE-R7-REPORT.md`](PHASE-R7-REPORT.md), and
[`PHASE-R-TTOD-ORACLE-PLATFORM-CASCADE-PROMPT.md`](PHASE-R-TTOD-ORACLE-PLATFORM-CASCADE-PROMPT.md).

## Infrastructure truth, restated once, plainly

**Tanit** is Rubén's own development machine (this machine). **Lilith** is Rubén's private Linux
deployment-validation machine. **Neither is reachable by students, under any circumstance.** Every
student runs the full stack on their own laptop or university lab machine. Scaleway `stg` is the
only potentially externally-reachable environment, and it is gated on a deploy decision that does
not yet exist (§2.5 of the R6 runbook). No document in this tree says otherwise as of this pass —
verified by `grep -rniE "student.*connect.*(lilith|tanit)"` across `docs/`, clean.

## Objective 1 — doc reconciliation

- `PHASE-R-TTOD-ORACLE-PLATFORM-CASCADE-PROMPT.md`'s status line and `docs/DEV_PLAN/INDEX.md`'s
  Phase R row and narrative paragraph were rewritten this pass. The single most load-bearing find:
  `INDEX.md` still carried **"Phase R status remains PROPOSED at the platform level... no container
  has been built"** — flatly false against R0–R5 DONE / R7 PARTIAL. Replaced with an accurate
  account of what shipped and where (reference build on `main` vs. `cohort-starter`).
- `PHASES/R6-pwa-cicd-audit.md` and `PHASES/R7-testing-strategy.md` were re-read in full: both are
  R0-generated **runbooks** (forward-looking agent prompts), not status claims — neither asserts R6
  is done or that students reach Lilith/Tanit. No edit needed.
- No document claims students connect to Lilith or Tanit (see grep result above).

## Objective 2 — R6 deferral, formalized

[`DECISIONS/R6-DEFERRED-STUDENT-OWNED.md`](DECISIONS/R6-DEFERRED-STUDENT-OWNED.md) records: R6
(PWA service worker, CI/CD workflows, Linux CI evidence, Lighthouse, any Scaleway deploy
integration) is **not implemented** and **reserved for student ownership**. It states explicitly
that an open dependency slot (R3b/R4/R5/R7 all DONE-or-PARTIAL, nothing mechanically blocking R6)
is not authorization — only a separate, explicit product-owner instruction reopens it.

## Objective 3 — student-starter boundary

**Decision: a reproducible generation script on a local branch, not a runtime route guard.** A
route guard was considered and explicitly rejected — hiding a route does not remove the completed
source code underneath it, and the whole point of Entrega 1 is that students build R3b onward
themselves. (This exact reasoning is now also preserved as TTOD wisdom — see
`wis-master`-level proposal "The master hid the finished temple behind a closed door..." below.)

Because R1/R2/R3a and R3b/R4/R5/R7 were committed together in one commit (`47b46de5`) for
practical reasons at the time, there is no clean git history point to check out "just the walking
skeleton" from. `scripts/generate-cohort-starter.sh` reconstructs that state by explicit,
documented deletion + trimming rather than pretending a clean commit exists:

**Removed from the starter:** `src/content.config.ts`, `src/content/`,
`src/pages/[locale]/{docs,wisdom,graph.astro,oracle.astro}`, `src/components/{graph,oracle}`,
`src/lib/db.ts`, `src/styles/tokens.css`, `tailwind.config.mjs` (R3b/R4/R5 source);
`PHASE-R{3b,4,5,7}-REPORT.md`, `docs/testing-strategy.md`, `tests/test_r7_platform.py` + its two
fixtures (reference-build-only reports/tests). `astro.config.mjs` is rewritten to drop the `mdx`
integration and Tailwind Vite plugin; `package.json` is trimmed of exactly six dependencies
(`@astrojs/mdx`, `@tailwindcss/typography`, `@tailwindcss/vite`, `tailwindcss`, `framer-motion`,
`gsap`) and `package-lock.json` is regenerated against the trimmed manifest.

**Kept:** the frozen `domain.ts` contract, the Docker/Compose/Caddy scaffold, the bilingual
hello-world routes and the live-quote route, and — deliberately — every `PHASES/R*.md` runbook
(students need R3b onward's own runbooks to build their own version) plus the full
Playwright/axe/Testing-Library toolchain (R7 is a continuous lane from day one, not bolted on
later).

**Execution:** committed to `main` first (`9118bcdb`, since the script itself needed a clean tree
to run against), then run, producing branch `cohort-starter` at commit `39489446` — 36 files
changed, 575 insertions, 6126 deletions. Verified: `npm run check` → 0 errors/warnings/hints (9
files, down from 28), `npm run build` succeeded. Switched back to `main`, confirmed clean, confirmed
the full reference build (13 `.astro` pages) intact.

**This branch has not been pushed anywhere** — it exists only in this local clone.

**Correction (2026-09-05, found during the `docs/research/` audit that followed this report):**
the command originally suggested here — `git push -u origin cohort-starter` — was wrong and has
been removed. `ruvebal/ttod` is a **public** repository (`AGENTS.md` line ~106: `access: public`)
with one shared `origin`. Pushing `cohort-starter` there does not isolate it: any student (or
anyone) with clone/fetch access to that same remote can run `git log --all` or
`git fetch origin main` and read the finished R3b/R4/R5/R7 reference build the cohort is meant to
build independently — the exact failure this whole objective exists to prevent, just moved from
the engineering side (a route guard) to the distribution side (a shared remote). See
`docs/research/GUIDE-FORGE-PLAN.md` §2 and `docs/research/PROMPT-FORGE-TTOD-GUIDES.md`'s
non-negotiable truths for the full finding and the required verification step (a git-history
check against whatever artifact a student would actually clone) before any distribution decision
is acted on.

**What this means for the actual next step:** distributing `cohort-starter` safely requires an
artifact with no history reachable to `main` — e.g. an orphan/squashed export of the
`cohort-starter` tree into a brand-new repository (`git checkout --orphan`, or `git archive` into
a fresh `git init`), not a branch push to this repository's existing `origin`. This report does
not perform that export on its own authority — it requires Rubén's explicit instruction, same as
any push did before this correction.

## Objective 4 — R7, honestly advanced this pass

Full detail in [`PHASE-R7-REPORT.md`](PHASE-R7-REPORT.md)'s new "2026-09-05 closure-audit pass"
section. Summary: R3b/R4/R5 are now all DONE, so the E2E/a11y gate no longer needs to wait — only
the CI-wall-clock gate does (it structurally requires R6's workflow files). Built
`playwright.config.ts` + `e2e/i18n-routes.spec.ts` (chromium only, `@axe-core/playwright` folded
in, not a separate audit) and ran it against a **genuinely live local stack**: MCP + backend
bare-metal on this machine (`qwen3.8:27b` + `nomic-embed-text`, already pulled), frontend built and
served standalone.

**First run found a real bug**, not a mocked one: 8 of 15 tests failed on `landmark-one-main` —
`/en/`, `/es/`, `/quote`, `/graph`, and `/oracle` had no `<main>` landmark (only R3b's own
`wisdom`/`docs` pages had wrapped their content in one). Fixed across five files, rebuilt,
re-ran: **15/15 passed, 3.1s wall-clock.** A second, independent finding surfaced along the way and
is now documented in the R7 report for the cohort's benefit: Astro's `output: 'server'` still
inlines `import.meta.env.BACKEND_URL` at **build** time via Vite, not at server-start — a `.env`
file must exist before `astro build`, not just before running the built server.

**R7 stays PARTIAL** — correctly, not as an oversight. The CI-wall-clock gate cannot be honestly
closed without R6 (deliberately unbuilt), and R4's `?tag=` URL-sync test, R5's SSE-streaming/mode-
disclosure test, and the R1↔R2 live-transport harness remain unwritten. No R6 file was written to
manufacture the appearance of completeness.

## Objective 5 — verification suite, run in full this pass

| Command | Result |
| --- | --- |
| `python cli.py validate --strict --json` | exit 0 — `is_valid: true`, 0 errors, 0 warnings |
| `python cli.py stats --check` | exit 0 — 229 quotes, stored meta matches recomputed snapshot |
| `python -m unittest discover -s tests -p 'test_*.py'` | 208 tests, OK, 3.142s |
| `python -m unittest discover -s services/backend/tests` | 6 tests, OK, 0.746s |
| `python -m unittest discover -s services/mcp/tests` | 5 tests, OK, 0.017s |
| `node --test src/components/graph/layout.test.mjs` | 2 tests, OK, 108.7ms |
| `npx vitest run` | 6 tests (2 files), OK, 932ms — see note below |
| `npm run check` | 28 files — 0 errors, 0 warnings, 0 hints |
| `npm run build` | succeeded, ~2.3s wall |
| `npx playwright test --project=chromium` (+ axe, this pass's new suite) | 15/15 passed, 3.1s wall (after the `<main>`-landmark fix above) |

**Self-inflicted gap found and fixed before the Vitest run above:** `npx vitest run` first failed
with `Failed to resolve import "framer-motion"` — not a code regression. Earlier in this session,
generating the `cohort-starter` branch ran a full `npm install` while checked out on that branch;
since `node_modules/` is untracked and shared across branches in one working tree, that install
pruned `framer-motion`/`gsap`/etc. out of the shared `node_modules` to match the *trimmed*
`package.json`. Switching back to `main` never restored them. Fixed with a plain `npm install` on
`main` (`package.json`/`package-lock.json` unchanged, confirmed via `git status`) — worth knowing
for any future session regenerating the starter branch: **run `npm install` again after switching
back to `main`.**

## Objective 6 — TTOD wisdom distillation

Already staged earlier in this session, verified present and correctly formed this pass — all
`status: pending_human_review`, `origin: blackbox`, no `validated_by`, citing
`source: studio/phase-r-oracle-platform-implementation-and-cold-review-2026-09-05`, none accepted,
`ttod.yml` untouched (confirmed: `git status` shows no change to it). Eight proposals staged under
`/Users/ruvebal/src/.cursor/skills/ttod-bridge/pending/`, dated `2026-09-05T19:24:0{7,8}Z`:

| Section | Text | Lesson |
| --- | --- | --- |
| architecture | "Name the road by where it leads, not by who might someday walk it." | Infra docs must distinguish dev/private-validation/student-local/public deploy |
| architecture | "The edge you filter may still reveal the node you concealed." | Rights filtering must cover relationships, not just primary records |
| architecture | "Two services sharing a network are not yet speaking." | Compose connectivity ≠ a proven application-level integration contract |
| architecture | "The boundary is not apart from the whole; by keeping its nature, it lets the whole endure." | Disciplined interfaces/provenance/rights are coherence, not obstruction |
| devops | "Four vessels at home. The fifth wakes beneath a flag. Names preserve the truth." | Operational topology should describe conditional services honestly |
| qa-tooling | "A missing review is not a passing review; emptiness is not approval." | Unavailable verification must yield PARTIAL, never ceremonial DONE |
| wisdom (advanced) | "A gate that tests what no one can reach guards only an illusion." | Acceptance criteria must be executable in the environment actually available |
| wisdom (master) | "The master hid the finished temple behind a closed door. The student opened the source tree. What had been hidden?" | Feature flags gate runtime exposure, not access to completed source — directly the Objective 3 lesson above |

No proposal was accepted; none will be by this or any automated session — that step is
exclusively a human running `cli.py add` plus hand-adding `validated_by: human`, per each
proposal's own `acceptance.note`.

## Final state table

| Phase | State | Owner | Evidence |
| --- | --- | --- | --- |
| R0 | DONE | instructor (generator pass) | `PHASE-R0-REPORT.md`; produced all `PHASES/R*.md` runbooks |
| R1 | DONE | instructor | `PHASE-R1-REPORT.md`; 6 endpoints, in-process `ttod_core`, fails closed without MCP |
| R2 | DONE | instructor | `PHASE-R2-REPORT.md`; 3 FastMCP tools, 229 records indexed |
| R3a | DONE | instructor | `PHASE-R3a-REPORT.md`, `PHASE-R1-R3A-CASCADE-REVIEW.md`; walking skeleton, cohort-start gate open |
| R3b | DONE (reference build) | reference, not student-starter | `PHASE-R3b-REPORT.md`; content engine, on `main` only |
| R4 | DONE (reference build) | reference, not student-starter | `PHASE-R4-REPORT.md`; Svelte graph island, on `main` only |
| R5 | DONE (reference build) | reference, not student-starter | `PHASE-R5-REPORT.md`; React oracle terminal, on `main` only |
| R6 | **DEFERRED / STUDENT-OWNED** | cohort (not started) | `DECISIONS/R6-DEFERRED-STUDENT-OWNED.md` — not implemented, deliberately |
| R7 | **PARTIAL** | cohort (continuous) | `PHASE-R7-REPORT.md`; 15/15 Chromium+axe E2E pass live; CI-wall-clock gate blocked on R6 |
| cohort-starter | DONE (local branch, unpushed) | instructor | `scripts/generate-cohort-starter.sh`; commit `39489446`, verified build-clean |
| TTOD wisdom proposals | DONE (staged, unaccepted) | instructor-reviewable | 8 proposals under `ttod-bridge/pending/`, table above |

## Hard constraints — confirmed held throughout this pass

- **R6 not implemented.** No `.github/workflows/`, `public/sw.js`, or Lighthouse config was written.
- **No deployment.** All test evidence in this report came from processes running on this machine
  (Tanit) only — MCP/backend bare-metal, frontend built and served standalone, all torn down after
  the test run (`kill` on all three PIDs, confirmed via `ps aux` showing none remaining).
- **`ttod.yml` not mutated.** `git status` confirms no change to it; validation/stats above ran
  against the unmodified live file; the 8 wisdom proposals are draft-only artifacts outside this
  repository, in `ttod-bridge/pending/`, never merged.
