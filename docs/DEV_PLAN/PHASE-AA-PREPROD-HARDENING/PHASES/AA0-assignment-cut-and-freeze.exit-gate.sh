#!/usr/bin/env bash
# AA0 exit gate: the Gate + Acceptance of AA0-assignment-cut-and-freeze.md, made runnable.
# Written before the phase ran (planner, not implementer). Docs + measurements only.
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

# 3. Locator contract frozen.
grep -Eq '^\*\*Status:\*\* FROZEN' "$pack/LOCATORS.md" || fail "LOCATORS.md status is not FROZEN"

# 4. Live re-probe and UX baseline stored with the report.
test -s "$base_dir/probe.log" || fail "missing live probe log"
grep -Eq '^# probe run: 20[0-9]{2}-' "$base_dir/probe.log" || fail "probe log is undated"
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
for w in 390 768 1440; do
  ls "$base_dir"/header-*-"$w".png >/dev/null 2>&1 || fail "no header screenshot at ${w}px"
done

# 5. Scope: no application code, Compose or canonical-store changes in this phase.
start="$(git merge-base HEAD origin/main)"
git diff --quiet "$start" -- services backend caddy redis docker-compose.yml ttod.yml proposals \
  || fail "AA0 touched code, Compose or the canonical stores"

git diff --check "$start"
echo "AA0 exit gate passed: owner decisions recorded, cut + locators frozen, probe + baseline stored, no code touched."
