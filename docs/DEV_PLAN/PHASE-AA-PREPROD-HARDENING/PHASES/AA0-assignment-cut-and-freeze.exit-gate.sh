#!/usr/bin/env bash
# AA0 exit gate: the Gate + Acceptance of AA0-assignment-cut-and-freeze.md, made runnable.
# Written before the phase ran (planner, not implementer). Docs + measurements only.
# Amended after the cold review (F5, F6): allowlist scope, frozen cut, probe sections, all
# screenshots, cold-review file, and .gitattributes instead of excluding Markdown.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
pack="docs/DEV_PLAN/PHASE-AA-PREPROD-HARDENING"
report="$pack/PHASE-AA0-REPORT.md"
base_dir="$pack/baselines/aa0-2026-11-10"

fail() { echo "AA0 GATE FAIL: $*" >&2; exit 1; }

# 1. Report exists and records the owner's words, not the agent's inference.
test -f "$report" || fail "missing $report"
grep -Fq 'Owner answer (verbatim)' "$report" || fail "report lacks the verbatim owner answer"
for d in 1 2 3 4 5 6 7; do
  grep -Eq "^\| D${d} \|" "$report" || fail "report lacks a D${d} row"
done

# 2. Every finding F1–F58 maps to an A*/I* row (ranges like F42–F44 expand).
python3 - "$pack/ASSIGNMENTS.md" <<'PY'
import re, sys
text = open(sys.argv[1], encoding="utf-8").read()
seen = set()
for a, b in re.findall(r"\bF(\d+)\s*[–-]\s*F(\d+)\b", text):
    seen.update(range(int(a), int(b) + 1))
seen.update(int(n) for n in re.findall(r"\bF(\d+)\b", text))
missing = [n for n in range(1, 59) if n not in seen]
rows = set(re.findall(r"^\| \*\*([AI]\d+)\*\* \|", text, flags=re.M))
need = {f"A{i}" for i in range(1, 41)} | {f"I{i}" for i in range(1, 17)}
if missing:
    sys.exit(f"AA0 GATE FAIL: findings without an owner row: {missing}")
if need - rows:
    sys.exit(f"AA0 GATE FAIL: assignment rows missing: {sorted(need - rows)}")
print(f"coverage: F1–F58 mapped; {len(rows & need)} A*/I* rows")
PY

# 3. Locator contract and assignment cut frozen.
grep -Eq '^\*\*Status:\*\* FROZEN' "$pack/LOCATORS.md" || fail "LOCATORS.md status is not FROZEN"
grep -Eq '^\*\*Status:\*\* FROZEN' "$pack/ASSIGNMENTS.md" || fail "ASSIGNMENTS.md status is not FROZEN"

# 4. Live re-probe and UX baseline stored with the report.
test -s "$base_dir/probe.log" || fail "missing live probe log"
grep -Eq '^# probe run: 20[0-9]{2}-' "$base_dir/probe.log" || fail "probe log is undated"
for sec in "F1 " "F2 " "F22 " "F23 " "F25 " "F27 " "F3 " "F14 " "F32 " "F8 " "F50/F51 " "F57 "; do
  grep -q "^## $sec" "$base_dir/probe.log" || fail "probe log lacks the ## ${sec}section"
done
grep -q 'redis stopped → /health' "$base_dir/probe.log" || fail "F27 was not probed with Redis down"
test -s "$base_dir/ux-baseline.json" || fail "missing ux-baseline.json"
python3 - "$base_dir/ux-baseline.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
views = {v["path"]: v for v in data["views"]}
for path in ("/es/", "/es/wisdom/", "/es/graph/path"):
    v = views.get(path) or sys.exit(f"AA0 GATE FAIL: no baseline for {path}")
    for key in ("a11y_violations", "cls", "lcp_ms"):
        if v.get(key) is None:
            sys.exit(f"AA0 GATE FAIL: {path} lacks {key}")
print("ux baseline: 3 views with a11y/CLS/LCP")
PY
for v in es es-wisdom es-graph-path; do
  for w in 390 768 1440; do
    test -s "$base_dir/header-$v-$w.png" || fail "missing header-$v-$w.png"
  done
done

# 5. Scope as an allowlist: nothing outside the pack changed, committed or not.
# Base = the commit that created the pack (AA0 starts there), not origin/main.
start="$(git log --diff-filter=A --format=%H -1 -- "$pack/INDEX.md")"
[ -n "$start" ] || fail "cannot find the commit that created the pack"
outside="$(git diff --name-only "$start" -- . ":(exclude)$pack/**")"
[ -z "$outside" ] || fail "AA0 changed files outside the pack: $outside"
dirty="$(git status --porcelain -- . ":(exclude)$pack/**" ':(exclude).cascade-lane')"
[ -z "$dirty" ] || fail "uncommitted or untracked files outside the pack: $dirty"

# 6. Cold review filed with a verdict.
grep -Eq 'PASS|FAIL' "$pack/PHASE-AA0-COLD-REVIEW.md" 2>/dev/null || fail "no cold review with a verdict"

# The pack's .gitattributes allows two-space Markdown hard breaks; all other checks apply.
git diff --check "$start"
echo "AA0 exit gate passed: owner decisions recorded, cut + locators frozen, probe + baseline stored, no code touched."
