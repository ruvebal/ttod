# Phase U · TS5 report — hello-world assembly (minimum exit) + full TS5

**Status:** `PARTIAL` — every full-TS5 gate ran and is documented (§6 below); the one gate not
literally satisfied is the privacy watcher's zero-finding count, and that shortfall is itself
fully categorized, not unexamined. See §6.4 for why this isn't filed `DONE` outright.
**Date:** 2026-09-09  
**Branch (minimum exit):** `skeleton/ts5-hello-world`  
**Branch (full TS5, orphan history):** `skeleton/ts5-fresh-history`  
**Worktree:** `/Users/ruvebal/src/ttod-skeleton-ts5` (minimum) · `/Users/ruvebal/src/ttod-skeleton-ts5-fresh2` (full)
**Runbook:** [`PHASES/U-TS5-fresh-history-assembly.md`](PHASES/U-TS5-fresh-history-assembly.md)
**Assembly script:** [`scripts/generate-ts5-teaching-baseline.sh`](../../scripts/generate-ts5-teaching-baseline.sh)

`main` was not touched by any of §§1–5 (the minimum-exit assembly, unchanged from the first pass
of this report). §6 (below, new) documents the full TS5 pass: orphan-history reassembly, TS2
tagging, the privacy watcher, isolation probes, and full build/test verification against the
distributed artifact — `main` is untouched by this pass either; `skeleton/ts5-fresh-history` was
built as a brand-new orphan root commit with no shared Git objects.

---

## 1. What landed (Week-1 minimum)

All seven Week-0 lane tips were merge-assembled onto `skeleton/ts5-hello-world` (base
`skeleton/ts1-contracts` @ `47f15da9`) in order:

`ts3a-r3b` → `ts3b-r4` → `ts3c-r5` → `ts4a-r6` → `ts4b-r7` → `ts4c-auth`

Every merge was clean (ort, no conflict resolution). Tip after assembly + Oracle test rewrite:

| Ref | SHA |
| --- | --- |
| Merge tip (pre-test fix) | `5acd0e5e` |
| Runbook commit | `528092c4` |
| Final tip | branch tip of `skeleton/ts5-hello-world` (Oracle rewrite + this report) |

### Leftover resolutions

| Leftover | Decision | Evidence |
| --- | --- | --- |
| TS4c `User` / `UserRole` / `FavoriteEntry` | **Accept** | present in `services/frontend/src/types/domain.ts` |
| 460-node graph sample | **No client-side cap** | unchanged from TS3b; performance = R4 assignment depth |
| `OracleTerminal.test.tsx` | **Rewrite** for hello-world | queue/propose assertions removed; stream + error path covered |
| `Page.astro` + `Page.shell.test.ts` | **Keep both** | TS4a SW/offline banner + TS4b shell test; vitest green |

---

## 2. Mechanical gates

| Gate | Result |
| --- | --- |
| Facet routes gone | no `wisdom/sections|tags|levels` |
| Graph reduced | no `gsap` / `filterGraph` / `activeTag` in `GraphIsland.svelte` |
| Oracle reduced | no `enqueueOracleQuery` / `propose(` in `OracleTerminal.tsx` |
| PWA stub | `public/sw.js` + `manifest.webmanifest` |
| Auth stub | `auth.server.ts` + `/account` routes + backend `auth.py` |
| Auth types on `domain.ts` | yes |
| `npm run check` | 0 errors |
| `npm run build` | Complete |
| `npm test` (vitest) | 4 files / 8 tests passed |
| Backend auth suite | `PYTHONPATH=. pytest services/backend/tests/test_backend.py` → 10 passed |

---

## 3. Still open (full TS5 / Week-0 programme) — resolved in §6

1. ~~Fresh-history archive~~ — done, §6.1.
2. ~~TS2~~ — done, §6.2.
3. ~~Privacy watcher + isolation probes~~ — done, §6.3–§6.4 (isolation clean; privacy watcher not
   literally zero, fully categorized).
4. **Push** — `skeleton/ts5-hello-world`, `skeleton/ts5-fresh-history`, and the `rich-reference-2026-09-09`
   tag are all pushed (§6.5). Remaining lane tips (`ts3a-r3b` etc.) were not separately pushed —
   not needed once assembled.
5. **Do not merge into `main`** — held. Neither branch has been merged; `main` is untouched.

---

## 4. Commands run

```bash
git worktree add ../ttod-skeleton-ts5 -b skeleton/ts5-hello-world skeleton/ts1-contracts
# merge ts3a → ts3b → ts3c → ts4a → ts4b → ts4c (all clean)
cd services/frontend && npm ci && npm test && npm run check && npm run build
cd ../.. && PYTHONPATH=. services/backend/.venv/bin/python -m pytest services/backend/tests/test_backend.py -q
```

---

## 5. Product-owner note

§5 of `PHASE-U-WEEK0-ORCHESTRATION.md` was confirmed unblocked (approve / Week 1 = 2026-09-10 /
delegate). This report is the first TS5 assembly evidence for that Week 1 start — a working
teaching tree on `skeleton/ts5-hello-world`, not yet the history-isolated student archive.

---

## 6. Full TS5 — orphan history, TS2, privacy watcher, isolation (2026-09-09, later)

Per `PHASE-U-FEII-TEACHING-SKELETON-CASCADE.md`'s own TS5 definition: "Create a new-history
artifact containing the governed core, backend walking skeleton, R3a shell, and TS3/TS4
hello-world slices. Include only the assignment briefs, student guide, licenses, and public-safe
documentation needed for the course. Run privacy, history-isolation, build, test, and
canonical-integrity gates over the exact archive students would receive." Gate: "clean clone to
localized hello world and live quote succeeds; rich reference recovery probes fail; the privacy
watcher reports zero findings."

### 6.1 Fresh-history archive

`scripts/generate-ts5-teaching-baseline.sh` — allowlist-based (what's copied IN, not what's
deleted), matching `scripts/generate-cohort-starter.sh`'s own documented-not-hand-edited
precedent. Source: `skeleton/ts5-hello-world`. Output: `skeleton/ts5-fresh-history`, a genuine
orphan root commit (`git init` in a clean staging dir, single commit, imported via `git fetch
<staging>:skeleton/ts5-fresh-history`).

**Scope included:** governed core (`ttod.yml`, `ttod_core/`, `schema/`, `cli.py`,
`pyproject.toml`, `tests/` minus two exclusions below, `proposals/` minus internal manifests),
the working app (`services/backend`, `services/mcp`, `services/frontend` — every module's
`ASSIGNMENT.md` already lives inside this tree), local-operation config
(`docker-compose.yml`, `.env.example`), licenses, `AGENTS.md`/`CLAUDE.md` (rewritten, see below),
`.cursor/rules/ttod-editing.mdc`, the reviewer/student PR workflow
(`.github/workflows/ci.yml`, `.github/workflows/proposal-accept.yml`,
`.github/pull_request_template.md` — pulled from `main`, since `skeleton/ts5-hello-world` forked
before the agentic pack merged), and curated `docs/public/teaching` +
`docs/public/audiences/students.md` (+ `es/` mirrors) as the student guide. A fresh top-level
`README.md` was written for this artifact specifically (`main`'s own README assumes
`docs/DEV_PLAN`, not present here).

**Excluded, with reasons:**

| Excluded | Why |
| --- | --- |
| `docs/DEV_PLAN/` (entire tree) | Internal instructor planning — cascade prompts, cold-audit reports, worktree paths, machine names. Never part of TS5's own named scope ("assignment briefs, student guide, licenses, public-safe documentation" — not the dev plan). |
| `proposals/manifests/` | Internal Phase-S5 batch-translation-run audit records, not proposal content — ~230 of the original 257 privacy findings, alone. |
| `private/`, `sources/`, `shared/`, `caddy/`, `agentic/`, `scripts/`, `.cursor/skills/`, root `INDEX.md` | Instructor/studio infra, internal tooling, or superseded by the new `README.md` — none needed to run the app or complete an assignment. |
| `tests/test_public_privacy_watcher.py` | Exercises `agentic/report-steward`'s own tooling; its fixtures necessarily contain an internal-hostname *example string* to verify detection works. |
| `tests/test_r7_platform.py` | Rich-reference-only — same reasoning `scripts/generate-cohort-starter.sh` already established; cannot import against a hello-world-reduced `services/` tree. |
| `tests/test_q6_migration.py` | Tests a completed, one-time v2→v3 historical migration against a frozen 229-quote backup (`private/ttod.yml.pre-q6-backup`, itself excluded). Its own fallback path (live `ttod.yml` when the backup is absent) produces a false failure — re-running the migration transform on already-migrated v3 data doesn't reproduce a historical count. Not a live-product bug. |

**AGENTS.md, not just copied — rewritten.** The source file references `ttod-bridge` (a skill in a
*sibling* studio repo students don't have), `docs/DEV_PLAN` (excluded), and an "Integration" table
of other studio repos (Web Atelier, DevIAC, Arkadia) with zero relevance to a standalone clone.
Left as-is, every one of those is a broken pointer. Rewritten: the "propose a new quote" section
now describes the mechanism this artifact actually ships (`cli.py proposal create`, or the web
form once built, → PR → `.github/workflows/proposal-accept.yml`); the Integration table and
ttod-bridge mentions are removed; `Related docs` points at what's actually present.

### 6.2 TS2 — rich-reference checkpoint

Tagged: `rich-reference-2026-09-09` (annotated, pushed to `origin`) on `main` at the commit
current when full TS5 began. Commit `8fd319d2…`, tree `671efd4f…` — the tree hash is itself a
content-addressed checksum of the entire repository state at that point; recovery is `git checkout
rich-reference-2026-09-09`. "Controlled storage" separate from this repository (per the cascade
doc's own wording) was not stood up — that's an infrastructure/ops decision (a private backup
location, a separate access-controlled remote) belonging to the product owner, not something this
pass invents on its own.

### 6.3 Isolation probes

```text
$ git merge-base main skeleton/ts5-fresh-history
(no output, exit 1)
```

No common ancestor — confirmed genuinely orphan, not merely working-tree-trimmed (the distinction
`scripts/generate-cohort-starter.sh` itself never made: that branch keeps `main`'s full reachable
history underneath its trimmed tip, so deleted files' *content* is still recoverable via `git log
-p`; `skeleton/ts5-fresh-history` cannot do that by construction — there is no ancestor commit to
recover from). Note: this repository clone still holds `main`'s objects locally (any local clone
does, for every branch), so `git log --all` here shows everything; the isolation claim is about
this branch's *own* ancestry graph, which is what a student's independent clone/push of just this
branch would actually receive.

### 6.4 Privacy watcher — 20 findings, all categorized (not zero, not blind)

```text
$ TTOD_PRIVATE_TERMS_FILE=.privacy-denylist python3 agentic/report-steward/scripts/check_public_privacy.py --root .
FAIL: 20 public-privacy finding(s)
```

Started at 257 (before §6.1's exclusions), dropped to 26 after them, dropped to 20 after the
product-owner's content decision on the one real finding (below). Every remaining finding was
individually inspected — none is an unexamined "probably fine":

| Category | Count | Why it's not a real leak |
| --- | --- | --- |
| Docker-internal DNS (`host.docker.internal`, `host.containers.internal`, `mcp:3001`) | 6 | Docker's own real, required container-networking mechanism — renaming would break the app, not protect anything |
| `.local`-suffixed teaching-placeholder email/hostname (`student@ttod.local`, explicitly documented as "teaching-only, never reuse a real password") | 9 | Deliberate, documented fake identity; the `.local` TLD is what makes it obviously non-production, not a leak |
| `0.0.0.0` bind-all address (`package.json`'s `--host 0.0.0.0`, `mcp/server.py`'s `host="0.0.0.0"`) | 2 | Standard, necessary "listen on every interface" convention — Python's `ipaddress.is_private` classifies `0.0.0.0/8` as reserved, which the checker's regex reads as "private network address"; it isn't one in the sensitive sense |
| `actions@users.noreply.github.com` | 1 | GitHub's own standard bot-commit email format, required syntax for `.github/workflows/proposal-accept.yml` to function as documented |
| `~/.docker/run/docker.sock` (in an accepted quote's *content* — a real macOS/Docker Desktop symlink gotcha, both the proposal and its `ttod.yml` twin) | 2 | Generic, universally-known technical knowledge used as pedagogical content — not exposing anything about the product owner's own system |

**One real content-level finding, resolved by product-owner decision, not by this session:** the
`arch-031`/`arch-086` haiku ("Tanit forges the steel / Lilith wields the blade…", part of the "Tao
de DevIAC" series) used the two machine names as poetic characters — real content, not leaked
infra info, but weighing directly against `.privacy-denylist`'s literal "must never" wording. The
product owner's call: rewrite for this distributed copy specifically (code-alchemist/forge/system
vocabulary in place of the names, same teaching point about dev-machine-vs-deploy-host
separation), never touching canonical `main`. Applied in `skeleton/ts5-fresh-history`'s own
`ttod.yml` and proposal-JSON copies; `content_digest` recomputed via `ttod_core.canonical.Canonicalizer`
for both records so the artifact still validates strict-clean (confirmed, §6.5).

**Why this report doesn't claim `DONE`:** the cascade doc's gate says "the privacy watcher reports
zero findings," stated as a mechanical pass/fail. Getting there literally would mean either
breaking real Docker networking, replacing a required GitHub bot email with something
non-functional, or degrading correct technical quote content — worse outcomes than 20 documented,
individually-justified exceptions. This is a genuine finding about the checker's own scope (built
and calibrated for `docs/public/`'s Jekyll content, not infrastructure config or quote content) —
not something to silently patch in shared studio tooling under time pressure without the
product owner's sign-off on that separate decision.

### 6.5 Build/test verification against the actual distributed artifact

```text
$ python cli.py validate --strict --json                          → is_valid: true, 0 errors
$ python cli.py stats --check                                     → 460 quotes, meta matches
$ python -m unittest discover -s tests -p 'test_*.py'             → 200 tests, OK
$ (cd services/frontend && npm ci && npm run check && npm run build)  → 0 errors, build complete
$ python -m pytest services/backend/tests/ -q                     → 10 passed
```

All run against a **freshly checked-out worktree of `skeleton/ts5-fresh-history`** (not the
staging directory the assembly script used internally) — the "clean clone to localized hello world
and live quote succeeds" gate, satisfied.

### 6.6 What was pushed

- `skeleton/ts5-hello-world` (minimum-exit assembly, unchanged from §1)
- `skeleton/ts5-fresh-history` (full TS5 orphan artifact)
- `rich-reference-2026-09-09` (TS2 annotated tag on `main`)

**Not merged into `main`** — neither branch, consistent with §3 item 5 and the cascade doc's own
"never rely on deletion commits for isolation" / student-artifact-is-separate design throughout
Phase U.
