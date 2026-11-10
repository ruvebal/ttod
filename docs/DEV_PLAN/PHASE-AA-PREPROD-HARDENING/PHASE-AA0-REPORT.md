<!--
AA0 report: assignment cut, owner decisions, locator freeze, live re-probe, UX baseline.
Author: Rubén Vega Balbás PhD (agent-assisted). Status VERIFYING. The agent does not mark DONE.
-->

# PHASE-AA0 report: assignment cut and freeze

**Status:** VERIFYING · cold review **PASS-WITH-AMENDMENTS** ([PHASE-AA0-COLD-REVIEW.md](PHASE-AA0-COLD-REVIEW.md)).
Blocking items F2–F4 are amended in this session. F1: the owner confirmed D7 (a) ("D7 a"); **D7 (b) still needs the owner** (O1). The exit gate is
[`PHASES/AA0-assignment-cut-and-freeze.exit-gate.sh`](PHASES/AA0-assignment-cut-and-freeze.exit-gate.sh),
and the harness verify log will sit next to it. A cold review follows, and only the owner promotes
this phase to DONE.
**Date:** 2026-11-10 · **Host:** Tanit (Compose project `ttod_oracle`, `HTTP_PORT=18080`) ·
**Branch:** `cascade/PHASE-AA-PREPROD-HARDENING-0`.

## 1. Owner decisions D1–D7

**Owner answer (verbatim), 2026-11-10:** "PR Merged. PR #8 was merged too. Quick hotfix to noindex
/assignments/ please! Add the stash and commit all, and push to main, Then lets switch to ttod AAO
(D1-D7) I decide the defaults are ok, go, paralel running?"

**Owner follow-up (verbatim), 2026-11-10, after the cold review:** "D7 a". Recorded as the owner
confirming **D7 (a)** (noindex on classroom hosts) by name, so (a) is no longer an inference. It does
not clearly settle **D7 (b)**: "a" could mean the first token option, but (a) is also the label of
the index part. (b) stays open (O1) until the owner answers it by name.

The first three sentences of the first message are about the Mondrian repository. "AAO" is read as AA0. The question
"paralel running?" is answered in §7 and left to the owner as O2.

Each row below is therefore the **Recommended** column of the AA0 phase file, adopted as written.
The agent added nothing except where a row had no single default. That case is D7 (b), which is
marked open.

| # | Decision | Recorded answer | Source of the default | Unblocks |
| - | -------- | --------------- | --------------------- | -------- |
| D1 | Trailing-slash policy | **Always-slash for pages**, 301 from the slashless form in Astro middleware; non-page endpoints (`/es/logout`, `/api/…`) exempt | AA0 table; [LOCATORS §3](LOCATORS.md#3-trailing-slash) | AA3b, AA4 |
| D2 | Query/fragment keys | **Keys are code, labels are copy.** New keys in English, shipped keys (`orden`, `p`, `s`, `tag`, `node`) frozen as-is | AA0 table; [LOCATORS §2](LOCATORS.md#2-keys-are-code-labels-are-copy) | AA3b |
| D3 | Graph IA (F52) | **3D at `/{l}/graph/`**, 2D at `/{l}/graph/plano/`, code graph at `/{l}/graph/code/`, `/{l}/graph/path` → 301 keeping the query. The "minimal header-link fallback" is **not** chosen | AA0 table (primary option); LOCATORS §4 graph registry | AA3b, A20, A39 |
| D4 | Header (F56) | **Full-width classic bar** per the AA3 header spec, on existing Equipo tokens. Confirmed as a **component restyle, not a brand redesign** (fonts, palette and logo unchanged) | AA0 table | AA3 |
| D5 | User section scope (F55) | Username (`display_name`) + change password + revoke other sessions. **No** email change, **no** reset-by-email | AA0 table | AA2 A34, AA3 A35 |
| D6 | Wisdom search (F49) | **SSR `?q=`** over the locale corpus; no backend search endpoint | AA0 table | AA3b |
| D7 | PAT policy (F5) and index/noindex (F14) | **(a) Index: noindex on classroom hosts**, no sitemap while noindex. Confirmed by the owner by name ("D7 a", 2026-11-10). Mechanism, for AA4: page-level `<meta name="robots">` or `X-Robots-Tag`. `robots.txt` must **not** `Disallow` those pages, because a crawler that may not fetch a page never reads its noindex. **(b) PAT: OPEN, provisional.** TTL-only classroom policy with a docs note (A4's second branch). The other branch, a revocation denylist (`ttod:pat:{jti}`), stays available; the agent does not schedule it. The AA0 table gave no single default for D7 ("already listed in AA2/AA4"), and A4 offers two equal branches, so (b) is the agent's reading, not an owner answer | (a) AA4 phase file: "Classroom default may be noindex", "prefer noindex unless owner says otherwise". (b) A4: "Denylist on logout-all **or** AA0-accepted docs note" | (a) AA4 · (b) AA2 (A4). (b) must be answered before AA2 opens. AA2's status line now says so, since AA2 may otherwise open on AA0 alone |

## 2. Assignment cut (frozen)

[ASSIGNMENTS.md](ASSIGNMENTS.md) is **affirmed as drafted** and marked FROZEN:

- **Students:** A1–A40 (40 rows).
- **Instructor:** I1–I16 (16 rows). I16 (F48, structured access logs) is instructor-owned, as
  drafted, so F48 has an owner.
- **Reassignments:** none. **Deferred:** none at AA0. AA6 dispositions whatever is still open.
- **Coverage:** every finding F1–F58 maps to at least one A or I row. F43 is covered through A28's
  range "F42–F44". The exit gate checks this mechanically, expanding ranges.

## 3. Locator contract (frozen)

[LOCATORS.md](LOCATORS.md) is marked **FROZEN 2026-11-10**, with D1–D3 written into its status line
and §3. No registry row changed, because the registry already encoded the recommended D3 layout.
After this date, any new locator is an amendment recorded in this report.

## 4. Live re-probe (2026-11-10T16:52:09Z; amendment 17:04:27Z)

Command: `baselines/aa0-2026-11-10/probe.sh http://127.0.0.1:18080 --with-redis-down`. The full
output is in [`baselines/aa0-2026-11-10/probe.log`](baselines/aa0-2026-11-10/probe.log). The probe
uses the live stack's Compose file (`-p ttod_oracle`), so it runs correctly from a worktree. F27
stops Redis for about 2 s on the instructor host and waits until `/health` reports `redis: ok`
again.

| Finding | Expected (FINDINGS) | Measured today | Verdict |
| ------- | ------------------- | -------------- | ------- |
| F1 headers | absent | `/es/`: no CSP, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Content-Type-Options` or HSTS; only `Via: 1.1 Caddy` | **confirmed** |
| F2 TLS | alt port not TLS | `https://…:18443` handshake fails (000); `http://…:18443/es/` → 200 | **confirmed** |
| F22 cookie Secure | tied to `PROD` | `login.astro:42`, `register.astro:33` `secure: import.meta.env.PROD` | **confirmed** (code) |
| F23 allowedDomains | localhost only | Astro decides on the **Origin** header. Origin `http://localhost` → 200; Origin `http://tanit.crea-comm.loc` or no Origin → **403**, whatever the Host. A browser on a LAN host always sends its own Origin, so LAN login fails. Full Host × Origin matrix in [`probe-amend.log`](baselines/aa0-2026-11-10/probe-amend.log) | **confirmed live** |
| F25 proposal mount | missing | backend container has **0 mounts**; `TTOD_PROPOSAL_DIR` points inside the image | **confirmed** |
| F27 health | 200 with Redis down | Redis stopped → `/health` **HTTP 200** `{"status":"ok",…,"redis":"down"}`; recovered to `redis: ok` | **confirmed live** |
| F3 open register | open, no limiter | `/es/register/` → 200; no `REGISTRATION_OPEN` or rate limiter in backend code | **confirmed** |
| F14 robots | missing | `/robots.txt`, `/sitemap.xml`, `/sitemap-index.xml` → 404 | **confirmed** |
| F32 graph locale | EN island | `/es/graph/` (the 2D island page) is `lang="es"` but renders all 6 English strings live (`probe-amend.log`); `/es/graph/path/` renders none. Source: `GraphIsland.svelte` hard-codes them ("TTOD knowledge graph", "All tags", "Section legend", "Loading live graph…", "Selected node", "Select a node to view its details.") | **confirmed** |
| F8 slash duplicates | both 200 | 7 of 8 probed pages return 200 for both forms; `/es/library` returns 302 (login redirect) for both | **confirmed** |
| F50/F51 ids | no deep links | `/es/`: 8 ids, 3 of them chapter ids (`flagship-quote-heading`, `sigue-tesis`, `sigue-rollo`); `/es/wisdom/`: 9 ids, none on a volume or quote | **confirmed** |
| F57 language switch | soft "not found" | the switch on `/es/wisdom/wis-034/` links to `/en/wisdom/wis-034/` → **HTTP 200, "Wisdom entry not found"**. An unknown page (`/es/no-such-page/`) does return a real 404 | **confirmed** |
| F56 header | floating pill | at 1440 px the header is a centred rounded pill about 770 px wide (brand, 6 links, ENGLISH), not a full-width bar; at 390 px it shows brand, MENÚ and ENGLISH | **confirmed** (`header-*-{390,768,1440}.png`) |
| F7 account entry | none in header | no account or login link at any of the three widths | **confirmed** |

No finding was refuted, and no new finding surfaced, so FINDINGS needs no amendment.

## 5. UX baseline (the "no regression" reference)

Command: `baselines/aa0-2026-11-10/baseline.sh`. It runs Lighthouse 12.6.0 with the mobile form
factor at 390×844 @2x and simulated throttling, then takes Playwright screenshots in system
Chrome. The numbers are in
[`ux-baseline.json`](baselines/aa0-2026-11-10/ux-baseline.json), and the gzipped raw reports are in
`lighthouse/`.

| View | Lighthouse a11y | Failing a11y audits | Perf | CLS | LCP |
| ---- | --------------- | ------------------- | ---- | --- | --- |
| `/es/` | 100 | 0 | 81 | 0.0130 | 5047 ms |
| `/es/wisdom/` | 100 | 0 | 98 | 0.0000 | 2330 ms |
| `/es/graph/path` | 100 | 0 | 77 | 0.0003 | 4959 ms |

**AA0 regression rule (the single rule; AA3, AA3b, A31 and `baseline.sh` cite this section).**
A later phase re-runs `baseline.sh <base> <its own folder>` **on Tanit**. LCP is only comparable on
the same host. The phase regresses on a view if any of these holds:

- the Lighthouse a11y score drops;
- an a11y audit fails that passed here;
- CLS > min(0.1, baseline + 0.02). The tolerance exists because `/es/wisdom/` measures 0.0000, and a
  strict "≤ baseline" would fail on any shift at all;
- LCP > baseline × 1.2.

Run-to-run evidence: the cold reviewer's independent re-run put LCP within 3 % and `/es/` CLS at
0.0111 against 0.0130 here. Two runs, so the tolerances are a judgement, not a measured spread.

**Lighthouse cannot see the known a11y defects (F9–F12, F38).** All three views score 100, so the
automated score cannot prove those fixes. AA3 must carry targeted tests for them: focus order,
skip link, accessible names and reduced motion. The score only proves that a phase did not make
things worse.

Screenshots: `header-{es,es-wisdom,es-graph-path}-{390,768,1440}.png` and
`view-{…}-390.png`.

## 6. Scope confirmations

- **Phase T stays separate.** AA closes classroom-host readiness. It does **not** authorize public
  release, partner demos or a public GitHub release.
- No file outside this pack changed in AA0, committed or uncommitted. After the review the exit
  gate checks this as an allowlist (pack only) instead of a list of forbidden paths.
- The only live-stack side effect was F27's short Redis stop/start. AOF persistence kept the data,
  and `/health` returned `redis: ok` afterwards.

## 7. What opens when the owner marks AA0 DONE

Per the cascade's parallel rule: **AA1 ∥ AA3 ∥ AA3b ∥ AA5 lane A**. AA2 follows AA1 (and needs O1 answered), AA4 follows AA3 + AA3b, AA5 lane B follows AA1, and AA6 runs last.

Two harness facts constrain parallel execution today:

1. `cascade-harness.sh start` picks the **first** READY row and refuses a second phase in flight in
   the same cascade lane (`.cascade-lane` = the cascade name). It is sequential by design. Parallel
   phases need either a lane-aware harness or manual worktrees. Manual worktrees lose the runner's
   one-lane guarantee, so they need an owner nod per phase.
2. AA1, AA3, AA3b and AA5 have **no exit-gate script yet**. Without one, `verify` refuses. Each
   gate is written by the planner before its phase starts, as AA0's was. The implementer never
   writes its own gate.

## 8. Open items

| # | Item | Owner |
| - | ---- | ----- |
| O1 | Confirm or amend **D7 (b)** (PAT: TTL-only classroom policy + docs note vs `ttod:pat:{jti}` denylist) before AA2 opens | product owner |
| O2 | Choose the parallel mechanism: a lane-aware harness change in the cascade-forge skill, or manual worktrees per phase | product owner |
| O3 | Exit-gate scripts for AA3 and AA3b (AA1 and AA5 lane A are written, on branch `docs/phase-aa-preprod-hardening`) | planner |

## 9. Gate amendments made during the phase (for the cold reviewer)

The gate was written before the work and changed **once** during it. Its final step,
`git diff --check <base>`, failed on the pack's deliberate two-space Markdown hard breaks: pre-existing
pack files, the repo's house style. The check now excludes `*.md`, with the reason recorded as a
comment in the script. Every substantive check is unchanged.

The gate also caught a real deviation, and the **report** was fixed rather than the gate. The
first draft split D7 into "D7a/D7b" rows, while the phase file defines a single D7 row. The report
now has one D7 row with parts (a) and (b).

The first harness `verify` (commit `b11094ca`) **failed**, and rightly. `probe.log` carried trailing
spaces from `probe.sh`'s id and mount lines. The agent's dry run had passed only because the log was
still untracked, so `git diff <base>` could not see it. Two fixes followed. `probe.sh` no longer emits
trailing spaces. The committed log had trailing whitespace stripped, and its content is otherwise
byte-identical: `diff` against the pre-strip copy, ignoring trailing space, is empty. Lesson: run
gates on committed state, which is what the runner does.

## 10. Glossary (for students and new instructors)

| Term | Meaning |
| ---- | ------- |
| Tanit | The instructor's machine that runs the TTOD Compose stack. Students never reach it |
| PAT | Personal access token: a signed token for API or MCP clients |
| `jti` | The token's unique id. A denylist keyed on it can revoke one token |
| AOF | Redis append-only file, the on-disk log that lets Redis restart without data loss |
| Harness, lane | `cascade-harness.sh` opens a worktree per phase and runs its exit gate. A lane is the "one phase at a time" claim it writes |
| A4's second branch | A4 accepts either a denylist **or** an AA0-accepted docs note. The second is the docs note |

## 11. Cold review

Handed to a fresh `cascade-cold-reviewer` session. Its findings go to
`PHASE-AA0-COLD-REVIEW.md`, and any blocking item is amended in this pack in the same session.
