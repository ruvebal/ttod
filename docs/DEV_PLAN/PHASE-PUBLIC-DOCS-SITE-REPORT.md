# Public documentation site report

**State:** VERIFYING — source and local render are green; remote publication is not configured or claimed

**Execution date:** 2026-09-07

**Implementer:** Codex documentation/release session

**Independent verifier:** unassigned

**Governing decisions:**
[`U1-2026-09-07-PUBLIC-DOCS-PAGES-BOUNDARY.md`](DECISIONS/U1-2026-09-07-PUBLIC-DOCS-PAGES-BOUNDARY.md),
[`PHASE-T-PUBLIC-RELEASE-EXCELLENCE-CASCADE.md`](PHASE-T-PUBLIC-RELEASE-EXCELLENCE-CASCADE.md) RC1

## 1. Outcome

A curated, role-oriented Jekyll publication now exists at `docs/public`. It has a central menu for
the project, product areas, teaching model, research, guides, students, university partners,
research/venture partners, and roadmap. The publication explicitly separates public documentation
from application hosting and from whole-repository visibility.

The source and a local rendered artifact pass privacy, internal-link, responsive-layout, canonical
integrity, and governed repository checks. The evidence supports `VERIFYING`, not `DONE`: the
workflow has not run on GitHub, the required protected secret and Pages source setting have not
been confirmed, no remote artifact has been deployed, and independent editorial review is still
unassigned.

## 2. Scope

Changed in this lane:

- 23 Jekyll source/configuration files under `docs/public`;
- one docs-only Pages workflow;
- one publication-boundary decision;
- the root index's public guide map and stale verification wording;
- the reusable privacy watcher, rule, and skill; and
- Phase U/R6 cross-references establishing that docs hosting is not student-owned app CI/CD.

Explicitly excluded:

- application code and cloud deployment;
- R3b–R7 subtraction/refactor work;
- course-repository synchronization;
- canonical quote mutation;
- repository visibility changes;
- container stop, rename, removal, or regrouping; and
- research recruitment, collection, approval, or effect claims.

Existing research reports were not moved wholesale. Their claims were curated into new public
pages so internal evaluation and execution material cannot enter the Pages build by directory
proximity.

## 3. Baseline and integrity

| Fact | Observed value |
| --- | --- |
| Baseline commit | `fc5a8a572c` |
| Worktree | already contained the requested Phase T/U planning edits; preserved |
| Canonical digest | `530b15286488ad4be0a1db63532a920642f25b073d1e89b3876e9ff5951e6e1b` |
| Canonical diff | none |
| Public source files | 23 |
| Local rendered files | 18 |

The canonical collection, proposals, services, and app configuration were not changed by this
lane.

## 4. Publication architecture

The Pages artifact is built from `docs/public` only. Internal `docs/research` and `docs/DEV_PLAN`
material is outside the Jekyll source. Layouts use `relative_url` so project-site links honor the
configured base path.

The workflow has two distinct behaviors:

1. pull requests build, scan generically, and validate internal links without deployment; and
2. a default-branch push additionally requires a protected private-term secret, scans source and
   output with that denylist, uploads the Pages artifact, and deploys through the protected Pages
   environment.

Build and deployment permissions are separated; only the deployment job receives Pages and
identity-token write access.

## 5. Verification evidence

| Gate | Evidence | Result |
| --- | --- | --- |
| publication privacy | watcher over root index, `docs/public`, workflow, and rendered output with local denylist | PASS, zero findings |
| watcher behavior | positive cases for tilde, mount/temp, internal suffix, private IPv6, and non-studio email; allowed local preview/studio domain negative case | PASS |
| Jekyll build | production build from `docs/public` using locally available Jekyll 3.10 | PASS, 18 rendered files |
| Liquid corruption | build output/source search | PASS, no Liquid warning |
| internal navigation/assets | every rendered relative `href`/`src` resolved inside the project-site artifact | PASS |
| workflow syntax | YAML parse | PASS |
| desktop visual check | full-page render | PASS; navigation, maturity panel, cards, callout, and footer visible |
| mobile visual check | 390×844 viewport | PASS; ten navigation links present, document width equals viewport width |
| interaction check | navigated through the Research menu item and asserted destination heading | PASS |
| skill structure | skill-creator validation for both report-steward skills | PASS |
| canonical validation | strict CLI validation | PASS; zero errors and warnings |
| metadata | stats consistency check | PASS |
| repository tests | unit discovery | PASS; 211 tests |
| bridge contract | external bridge suite | PASS; 8 of 8 |
| diff hygiene | `git diff --check` | PASS |

## 6. Failed or incomplete attempts retained

- The first local web-server start was blocked by the sandbox's socket policy. The same scoped
  local-only server was started after approval; no external service was changed.
- The declared Jekyll 4.3/HTMLProofer bundle is not installed in the workstation's older Ruby
  environment. A Jekyll 3.10 compatibility build succeeded, but exact Ruby 3.2 dependency and
  HTMLProofer execution remain CI evidence, not a local claim.
- The first bridge test attempt could not create its disposable fixture outside the repository.
  The approved rerun passed all eight tests.
- No GitHub Pages setting, secret, environment, commit, push, or deployment was performed.

## 7. Decisions and residual risk

| Risk | Consequence | Owner / gate |
| --- | --- | --- |
| whole-repository files/history remain unsanitized | Pages may be safe while making the repository public is not | RC2 and RC7 |
| private-term secret not confirmed | default-branch documentation deployment fails closed | repository owner |
| exact CI bundle not executed | gem/action compatibility remains unproven | first workflow run |
| independent content review absent | maturity, audience, and localization language remains implementer-reviewed only | documentation reviewer |
| application remains local | public docs must not link to or imply a cloud application | U1 boundary |

The container inventory showed separate project labels for the two TTOD contexts and the studio
context; the standalone container had no Compose project label. That observation justified no
mutation and is intentionally not reproduced with private operational identifiers.

## 8. Safe continuation

Exact next action: assign an independent reviewer to cold-read `docs/public`, inspect the rendered
preview, and review the workflow. If accepted, configure the Pages source and protected
private-term secret, commit through normal review, and observe the first workflow run before
promoting this lane to `DONE`.

Do not combine that action with changing repository visibility, deploying the application,
cleaning containers, or opening student collaboration.

