#!/usr/bin/env bash
# Professor-side review queue: everything on this repo that's waiting on a human decision,
# grouped by kind. Read-only — never merges, approves, or comments; it's the "what needs me
# right now" view PHASE-V-...ASSESSMENT.md §4 assumes exists once the cohort's six modules and
# the §2.7 proposal pipeline are both generating PRs in parallel.
#
# Usage: scripts/gh-review-queue.sh
set -euo pipefail

echo "=== Student module PRs awaiting review ==="
gh pr list --search "review-requested:@me" --json number,title,author,updatedAt,statusCheckRollup \
  --template '{{range .}}#{{.number}}  {{.title}}  ({{.author.login}}, updated {{timeago .updatedAt}})
{{end}}' 2>/dev/null || echo "(none, or gh auth lacks scope)"

echo
echo "=== Proposal PRs (proposals/**) open and unreviewed ==="
gh pr list --search "in:title Proposal" --state open \
  --json number,title,author,updatedAt \
  --template '{{range .}}#{{.number}}  {{.title}}  ({{.author.login}}, updated {{timeago .updatedAt}})
{{end}}' 2>/dev/null || echo "(none)"

echo
echo "=== Everything else open, any author ==="
gh pr list --state open --json number,title,author,isDraft \
  --template '{{range .}}#{{.number}}{{if .isDraft}} [draft]{{end}}  {{.title}}  ({{.author.login}})
{{end}}'
