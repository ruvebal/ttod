<!--
Cold review of PHASE-AA0 (assignment cut and freeze). Reviewer: fresh cascade-cold-reviewer session,
no implementation context. Reviewed range: 72a76ebe..e97fe079 on cascade/PHASE-AA-PREPROD-HARDENING-0.
This file does not mark AA0 DONE. Only the product owner promotes.
-->

# PHASE-AA0 cold review

**Verdict: PASS-WITH-AMENDMENTS.** There are no P0 findings and four P1 findings. AA0 should stay
VERIFYING until F1–F4 are amended. Acceptance boxes 1, 2 and 5 hold. Box 3 (D1–D7 answered by the
owner) does not hold for D7 (b). Box 4 (baseline cited by later phases) holds only partly, because
the pack now states three different regression rules. Box 6 is this file, and its "amend same
session" half is still open (F3, F4).

**Date:** 2026-11-10 · **Reviewed:** `git log 72a76ebe..HEAD` = `b11094ca`, `28939ee3`, `e97fe079`.

## 1. What I ran (evidence, not prose)

| Check | Command | Result |
| ----- | ------- | ------ |
| Exit gate, own run | `bash PHASES/AA0-assignment-cut-and-freeze.exit-gate.sh` | exit 0, same three lines as the VERIFY-LOG |
| Gate scope base | `git merge-base HEAD origin/main` | `80c6b3be`, so the gate's diff also covers the plan-pack commit |
| Phase scope | `git diff --name-only 72a76ebe..HEAD` | 25 paths, **all** under `docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING/`. No code, Compose, `ttod.yml` or `proposals/` change |
| F-coverage, rows only (stricter than the gate) | python: F ids taken only from lines matching `^\| \*\*[AI]\d+\*\* \|` in ASSIGNMENTS.md, ranges expanded | 56 rows, missing `[]`. FINDINGS has rows F1–F58, nothing above F58 |
| Markdown whitespace hidden by the gate amendment | `git diff --check 72a76ebe..HEAD` incl. `*.md`, plus a grep for trailing whitespace that is not exactly two spaces | only `ASSIGNMENTS.md:8` and `INDEX.md:8`, both exact two-space hard breaks. The exclusion hid nothing in this phase |
| §9 strip claim | `diff -b <(git show b11094ca:…/probe.log) …/probe.log` | identical ignoring whitespace. The claim holds |
| Live headers `/es/` (HEAD and GET) | `curl -sI` / `curl -D -` | only `Content-Type`, `Date`, `Via: 1.1 Caddy` (+ `Transfer-Encoding` on GET). F1 confirmed |
| Slash duplicates | `curl -w %{http_code}` × 8 paths × 2 forms | identical to probe.log:58–65 (7 × 200/200, `/es/library` 302/302) |
| robots/sitemap | same | `/robots.txt` 404, `/sitemap.xml` 404, `/sitemap-index.xml` 404 |
| F57 | `curl /en/wisdom/wis-034/` | HTTP 200, `<title>Wisdom entry not found`. `/es/wisdom/wis-034/` links `href="/en/wisdom/wis-034/"`. `/es/no-such-page/` 404 |
| F23 | `POST /es/login` with matching Host+Origin | `localhost` 200, `tanit.crea-comm.loc` **403**, `evil.example` 403. Cross-checks: see F10 |
| F2 | `curl -sk https://127.0.0.1:18443/`; `curl http://127.0.0.1:18443/es/` | `000`; `200` |
| F32 rendered strings | `curl /es/graph/` and `/es/graph/path/`, then grep for the 6 strings | all 6 on `/es/graph/`, **none** on `/es/graph/path/` (see F7) |
| F3 limiter claim | `grep -rniE "throttl\|limiter\|429\|too_many\|REGISTRATION" services/backend --include=*.py` | no non-test match. The claim holds |
| Lighthouse raw vs JSON | python over `lighthouse/*.json.gz` | requestedUrl = finalUrl, LH 12.6.0, 390×844@2, `simulate`, no runWarnings. Scores match `ux-baseline.json` exactly |
| baseline.sh reproducibility | `baseline.sh http://127.0.0.1:18080 <scratchpad>` (38 s) | `/es/` a11y 100, CLS 0.0111, LCP 4968 · `/es/wisdom/` 100, 0.0000, 2261 · `/es/graph/path` 100, 0.0003, 4816. LCP within 1.6–3 % of the baseline. Reproducible on Tanit |
| Screenshots | `file *.png`, visual read | 9 header crops (366/744/770 × 61 px) and 3 viewport shots (390×900). The 1440 crop is 770 px wide, which confirms the "pill" claim |

I did not run `probe.sh --with-redis-down` and did not stop any container (per the review brief).

## 2. Acceptance, box by box

| Box | Holds? | Evidence |
| --- | ------ | -------- |
| Live probes recorded with dates/commands | **Yes** | `probe.log:1` dated `2026-11-10T16:52:09Z`; `probe.sh` committed; every value I re-probed matched. Caveats: F7, F11 |
| Every F1–F58 mapped | **Yes** | row-strict check above; I16 owns F48 |
| D1–D7 answered by the owner, not inferred | **No (D7 b)** | F1, F2 |
| UX baselines stored; later phases cite them | **Partly** | stored and reproducible; AA3:105 cites it with a rule that contradicts report §5 (F4); AA3b/AA4 do not cite it, and the graph view moves (F8) |
| LOCATORS.md FROZEN | **Yes** | `LOCATORS.md:9` `**Status:** FROZEN 2026-11-10` |
| Cold review filed; blocking surprises amended same session | **Open** | this file is filed; F3/F4 amendments to ASSIGNMENTS/AA3/AA4 are not yet made |

## 3. Findings

| ID | Sev | Blocks DONE | Finding | Evidence | Fix |
| -- | --- | ----------- | ------- | -------- | --- |
| F1 | P1 | yes | **D7 (b) (PAT policy) is not an owner answer, and the pack in two places says it is.** The report is honest in its D7 row and in O1. But `INDEX.md:8` still says "owner accepted the recommended D1–D7". AA2's status line lets AA2 open on AA0 alone, so the report's "AA2 waits for AA1 anyway" is not guaranteed. The "denylist deferred to **Phase T**" is the agent's own addition: FINDINGS F5 names no target phase. D7 (a) (noindex) is also an inference: the AA0 table gave no D7 default, and the value came from AA4's "prefer noindex". That inference is disclosed and defensible, but it is still not the owner's words | `PHASE-AA0-REPORT.md:32`, `:136`; `INDEX.md:8`; `PHASES/AA2-auth-throttle-and-fallback.md:4` "BLOCKED until AA1 DONE (preferred; AA0 minimum)"; `FINDINGS-2026-11-10.md:35` | Preferred: ask the owner one question ("D7: noindex on classroom hosts, and PAT = TTL-only + docs note, denylist later? yes/amend") and record the reply verbatim in §1. Otherwise, the owner explicitly amends AA0 Acceptance box 3 to allow "D7 (b) deferred to AA2 entry, owner: product owner". If you take that route, add `and AA0 O1 (D7 b) answered` to the AA2 status line, and change INDEX.md:8 to "D1–D6 + D7 (a) accepted; D7 (b) open (O1)" |
| F2 | P1 | yes | **The owner quote is labelled "verbatim" but is cut short.** The real message ends "…go, paralel running?". The dropped clause is the owner's question that §7/§8 O2 answer, and nothing links the two. The gate checks only for the literal phrase `Owner answer (verbatim)`, so it cannot catch this | `PHASE-AA0-REPORT.md:17-18` ends at `go".`. The owner message (given by the human): "Then lets switch to ttod AA (D1-D7) I decide the defaults are ok, go, paralel running?" | Quote the full message, typos included. In §7, add one line: "Owner asked 'paralel running?' → answered here; mechanism is O2" |
| F3 | P1 | yes | **The frozen ASSIGNMENTS and AA4 still tell students to make the index decision that D7 (a) took away from them** ("decide here so students do not"). A student reading frozen A12 would choose index or noindex in their own PR. Separately, AA4 should know that a robots.txt `Disallow: /` stops crawlers from ever seeing the `noindex` meta. This is harmless on a LAN host, but AA4 should pick one mechanism on purpose | `ASSIGNMENTS.md:55` A12 "index/noindex decision in PR"; `PHASES/AA4-seo-robots-and-meta.md:8` "Index vs noindex decision", `:35` "may be noindex", `:47` "prefer noindex unless owner says otherwise"; `PHASE-AA0-REPORT.md:32` | Amend A12's acceptance to "noindex per AA0 D7 (a): robots.txt + meta; no sitemap while noindex". Amend AA4:8/35/47 to cite D7 (a) as decided. Do it in the same session (Acceptance box 6, "amend on surprise") |
| F4 | P1 | yes | **There are three incompatible "no regression" rules.** Report §5 says CLS ≤ max(0.1, baseline) and LCP ≤ +20 %. AA3 Acceptance and A31 say CLS ≤ the AA0 baseline, strictly. The baseline.sh header says CLS ≤ max(0.1, baseline) and has no LCP clause. A later phase cannot tell which one binds. Under the strict rule, `/es/wisdom/` (CLS 0.0000) fails on any shift at all. My re-run moved `/es/` CLS from 0.0130 to 0.0111, so noise is real | `PHASE-AA0-REPORT.md:92-98`; `PHASES/AA3-nav-a11y-and-url-hygiene.md:105`; `ASSIGNMENTS.md:70` ("CLS ≤ AA0 baseline"); `baselines/aa0-2026-11-10/baseline.sh:3-5` | Pick one rule (report §5 is the sensible one). Write it once, for example as a `baselines/aa0-2026-11-10/README.md` or as report §5 with an anchor. Make AA3:105, A31 and the baseline.sh header cite it instead of restating it. Also say that the LCP clause is valid only when measured on the same host (Tanit), because students run on their own machines |
| F5 | P2 | no | **The gate's scope check is a denylist that misses top-level application code.** It does not cover `cli.py`, `ttod_core/`, `schema/`, `shared/`, `scripts/`, `tests/`, `Makefile`, `pyproject.toml`, `ttod.yml.lock`, `data/` or `sources/`. It lists `backend`, which does not exist at repo root. `git diff --quiet <base>` also cannot see untracked files, which is the same blind spot §9 reports for probe.log. The scope rule did hold in fact (§1) | `exit-gate.sh:63`; `ls` of the worktree root | Replace it with an allowlist: `git diff --name-only "$start" HEAD -- . ':(exclude)docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING' ':(exclude)docs/DEV_PLAN/INDEX.md'` must be empty, and `git status --porcelain` outside the pack must be empty. Apply the same pattern to the AA1+ gates now being drafted |
| F6 | P2 | no | **The gate's checks are real but shallow.** It passes when a D row says OPEN. It does not check that ASSIGNMENTS.md is FROZEN. It does not check that probe.log contains each required section (F1, F2, F22, F23, F25, F27, F3, F14, F32, F8, F50/51, F57). Its screenshot check passes if any one view exists at a given width. Excluding `*.md` from `git diff --check` hid nothing this time, but it also drops conflict-marker detection for every Markdown file. The gate does not check "Cold review filed". That is defensible, because the review comes after verify, but then the promotion step must check it | `exit-gate.sh:17-19`, `:40`, `:43-44`, `:57-59`, `:67` | Add: `grep -Eq '^\*\*Status:\*\* FROZEN' ASSIGNMENTS.md`; a loop over the required `## F…` headings in probe.log; a check for all 9 `header-{es,es-wisdom,es-graph-path}-{390,768,1440}.png`; and a check that no D row contains `OPEN` unless the report names an owner-approved deferral. Instead of the `*.md` pathspec exclusion, add `docs/DEV_PLAN/**/*.md whitespace=-blank-at-eol` to `.gitattributes` so `--check` still covers Markdown |
| F7 | P2 | no | **The F32 probe evidence points at the wrong page.** The probe reads `lang` from `/es/graph/path/` but greps the English strings in the **source** of GraphIsland. Live, those strings render on `/es/graph/`, not on `/es/graph/path/`. The finding stands (I confirmed all 6 strings in `/es/graph/` HTML), but report row F32 does not name the page, and probe.log:49 says "(rendered on /es/ too)" | `probe.sh:72-76`; `probe.log:47-55`; `PHASE-AA0-REPORT.md:69`; live: `curl /es/graph/` finds 6 strings, `/es/graph/path/` finds 0 | Make the probe curl `/es/graph/` and grep the rendered HTML. Change the report row to "`/es/graph/` (2D, future `/graph/plano/`) renders 6 English strings" |
| F8 | P2 | no | **The graph baseline view will change identity.** After AA3b, `/es/graph/path` 301s to `/es/graph/` (3D, LOCATORS:98). A re-run of baseline.sh would then measure redirect + 3D page against a baseline taken without the redirect. The 2D page (`/es/graph/` today, `/graph/plano/` later), where A20 works, has no baseline at all. AA3b and AA4 do not cite the baseline | `baseline.sh:15`; `LOCATORS.md:93-98`; `grep -n baseline PHASES/AA3b* PHASES/AA4*` returns nothing | In AA3b, name the successor view (`/es/graph/` replaces `/es/graph/path`, compare against AA0's `/es/graph/path` numbers) and add `/es/graph/` (2D) to the next baseline run. Point AA3b and AA4 Acceptance at the single regression rule from F4 |
| F9 | P2 | no | **baseline.sh can clobber the reference, and it is tied to one host.** The default out-dir is the script's own folder, so a bare `baseline.sh` overwrites `ux-baseline.json` and the `.gz` reports. `CHROME_PATH` is a macOS path, and `FE_PKG` points at the main checkout's `node_modules`. Each view gets a single Lighthouse run. The "±10 % between runs" claim had no recorded evidence. My one re-run is consistent with it (≤3 %) | `baseline.sh:9`, `:10-11`, `:16-21`; `PHASE-AA0-REPORT.md:98` | Make out-dir mandatory, or refuse to run if `$OUT/ux-baseline.json` exists. Document the host prerequisites in the header. Store the AA0 re-run numbers (or 3 runs and their median) as the variance evidence |
| F10 | P2 | no | **The F23 report row leaves out the variable that decides the result.** The 403 tracks the **Origin** header checked against the host Astro resolves (localhost), not the Host header alone. Host=tanit with Origin=localhost returns **200**; Host=localhost with Origin=tanit returns 403; no Origin returns 403. A browser on the LAN sends a matching Origin, so F23 is real. But an AA2/A17 test that sets only Host would be misleading | my curls: `tanit no-origin: 403`, `tanit origin=localhost: 200`, `localhost origin=tanit: 403`; `probe.sh:37-38` sets Origin = Host; `PHASE-AA0-REPORT.md:64` mentions only Host | In report row F23, say "Host and Origin both `tanit.crea-comm.loc` (as a LAN browser sends)". In A17's acceptance, require the matching Host+Origin pair |
| F11 | P2 | no | **The probe log does not say which build was probed.** It records the worktree HEAD (`72a76ebe`), and the code greps (F22, F23, F32, F3) run against the worktree. The live containers have been up 21 h, and their image IDs are not recorded, so nothing ties the live answers to that commit | `probe.log:1`; `docker compose -p ttod_oracle ps` shows image sha256 ids, not commits | Add `docker compose -p ttod_oracle images` (or image IDs + created times) to the probe header |
| F12 | P2 | no | **Legibility for a student or a new instructor.** Unexplained terms: "Tanit", "PAT", "`jti`", "AOF", "runner/harness/cascade lane", "A4's second branch". The probe time is given as "16:5x UTC". Report §6 lists gate paths without `backend`. ASSIGNMENTS I16's note still says "AA0 may defer it", which is stale. A7 says "One policy (AA0 D1)" without naming the policy | `PHASE-AA0-REPORT.md:12`, `:32`, `:51`, `:113-114`, `:122-127`; `ASSIGNMENTS.md:43`, `:100` | Add a 5-line glossary at the end of the report (Tanit = instructor-only host; PAT = personal access token; jti = token id; harness = `cascade-harness.sh`). Use `16:52:09Z`. Change A7 to "always-slash + 301 (AA0 D1)" and I16 to "instructor-owned (AA0)" |

## 4. Questions the brief asked, answered directly

- **D7 handling.** The report is honest. It does not pretend D7 (b) was answered, and it scopes the gap to AA2. It still does not meet Acceptance box 3 as written, and the AA2 status line plus INDEX.md undercut "AA2 waits anyway". That is why F1 is P1, not P0: it costs one owner question, and it does not invalidate AA1, AA3, AA3b or AA5 lane A.
- **Gate amendment (`*.md` excluded).** It hid nothing in this phase (verified above). In principle it weakens the gate a little: it loses conflict-marker and stray-whitespace detection for Markdown. The `.gitattributes` route in F6 restores that. The gate is a faithful, non-trivial encoding of boxes 1, 2, 4 and 5 and of the scope rule. It does not encode box 3 beyond the presence of the rows, and it does not encode box 6 (F5, F6).
- **Lighthouse a11y = 100.** Report §5 correctly says the score cannot see F9–F12/F38. AA3 needs targeted tests for those, and the score is only a floor. I agree with that wording, and it is the most useful sentence in §5.
- **Scope.** Confirmed: no application code, Compose, `ttod.yml` or proposals changed in `72a76ebe..HEAD`.

## 5. Downstream phase files to amend (amend on surprise)

- `PHASES/AA2-auth-throttle-and-fallback.md:4`: entry condition on O1 / D7 (b) (F1).
- `PHASES/AA4-seo-robots-and-meta.md:8,35,47` and `ASSIGNMENTS.md:55`: D7 (a) decided (F3).
- `PHASES/AA3-nav-a11y-and-url-hygiene.md:105` and `ASSIGNMENTS.md:70`: one regression rule (F4).
- `PHASES/AA3b-locators-wisdom-and-graph-ia.md`: successor graph view + cite baseline (F8).
