#!/usr/bin/env bash
# Generates skeleton/ts5-fresh-history: a brand-new orphan root commit (no shared Git objects,
# remotes, or history with `main`) containing exactly what a student needs to run the app and
# complete their assignment — nothing from the instructor's internal dev-plan, worktree paths, or
# machine names.
#
# Scope decided per docs/DEV_PLAN/PHASE-U-FEII-TEACHING-SKELETON-CASCADE.md's own TS5 definition:
# "Create a new-history artifact containing the governed core, backend walking skeleton, R3a shell,
# and TS3/TS4 hello-world slices. Include only the assignment briefs, student guide, licenses, and
# public-safe documentation needed for the course." This script IS that decision, explicit and
# re-runnable — an allowlist of what's copied IN, not a denylist of what's deleted, because starting
# from nothing and adding only what's named is the only way an orphan commit can't accidentally
# carry something forgotten.
#
# Source: skeleton/ts5-hello-world (the merge-assembled minimum exit — see PHASE-U-TS5-REPORT.md).
# Never touches main. Never pushes. Safe to re-run (refuses if the target branch already exists).
#
# Usage: bash scripts/generate-ts5-teaching-baseline.sh

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

SRC_BRANCH=skeleton/ts5-hello-world
OUT_BRANCH=skeleton/ts5-fresh-history
STAGE=$(mktemp -d)

if git show-ref --verify --quiet "refs/heads/$OUT_BRANCH"; then
  echo "REFUSED: branch '$OUT_BRANCH' already exists locally." >&2
  echo "Delete it first if you intend to regenerate: git branch -D $OUT_BRANCH" >&2
  exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
  echo "REFUSED: working tree is not clean. Commit or stash before generating." >&2
  exit 1
fi

echo "== Exporting $SRC_BRANCH's tree into a clean staging dir =="
git archive "$SRC_BRANCH" | (cd "$STAGE" && tar -xf -)

echo "== Building the allowlisted student tree =="
DEST=$(mktemp -d)
copy() { mkdir -p "$(dirname "$DEST/$1")"; cp -R "$STAGE/$1" "$DEST/$1"; }

# Governed core + its own test suite
copy ttod.yml
copy ttod.yml.lock
copy ttod_core
copy schema
copy cli.py
copy pyproject.toml
copy tests
copy proposals

# The working app: backend (R1), MCP (R2), frontend (R3a shell + TS3/TS4 hello-world slices +
# every module's ASSIGNMENT.md, already embedded under services/frontend/**)
copy services

# Local operation, licenses, agent contract
copy docker-compose.yml
copy .env.example
copy .gitignore
copy .gitattributes
copy AGENTS.md
copy CLAUDE.md
copy LICENSE-CODE
copy LICENSE-CONTENT
copy Makefile

# Reviewer/student PR workflow — the same CI gate and rubric-as-checklist students' own PRs run
# against, not instructor-only tooling
mkdir -p "$DEST/.github/workflows"
copy .github/workflows/ci.yml
copy .github/workflows/proposal-accept.yml
copy .github/pull_request_template.md

# Curated, already privacy-reviewed student-facing documentation (not the internal dev plan)
copy docs/public/teaching
copy docs/public/audiences/students.md
copy docs/public/es/teaching
copy docs/public/es/audiences/students.md

echo "== Patching AGENTS.md: drop the instructor's absolute repository path =="
sed -i.bak "s#\`/Users/ruvebal/src/ttod\`#the repository root#" "$DEST/AGENTS.md"
rm -f "$DEST/AGENTS.md.bak"

echo "== Trimming Makefile: docs-* targets assume the full docs/public Jekyll scaffold, which this artifact does not carry =="
python3 - "$DEST/Makefile" <<'PYEOF'
import re, sys
path = sys.argv[1]
text = open(path).read()
# Drop each docs-*: recipe block (target line through the next blank line or next target)
text = re.sub(r"\ndocs-setup:.*?(?=\n[a-z][\w-]*:|\Z)", "\n", text, flags=re.S)
text = re.sub(r"\ndocs:.*?(?=\n[a-z][\w-]*:|\Z)", "\n", text, flags=re.S)
text = re.sub(r"\ndocs-serve:.*?(?=\n[a-z][\w-]*:|\Z)", "\n", text, flags=re.S)
text = re.sub(r"\ndocs-clean:.*?(?=\n[a-z][\w-]*:|\Z)", "\n", text, flags=re.S)
text = re.sub(r"\ndocs-privacy:.*?(?=\n[a-z][\w-]*:|\Z)", "\n", text, flags=re.S)
text = text.replace("clean: docs-clean ## Remove local caches (Jekyll site + Python bytecode)",
                     "clean: ## Remove local caches (Python bytecode)")
open(path, "w").write(text)
PYEOF

echo "== Writing the student-facing README (main's own README assumes docs/DEV_PLAN, not present here) =="
cat > "$DEST/README.md" <<'EOF'
# 道 THE TAO OF THE DEVELOPMENT (TTOD) — FE II teaching baseline

This is the **hello-world teaching skeleton**, not the instructor's rich reference. Every seam
(content, graph, oracle, PWA, auth, testing) is present end to end but deliberately incomplete —
your assignment is the gap between what runs and what a finished feature would do. Each module
names its own acceptance criteria in its `ASSIGNMENT.md`:

- `services/frontend/src/pages/[locale]/wisdom/ASSIGNMENT.md` — content, i18n, proposals UI
- `services/frontend/src/components/graph/ASSIGNMENT.md` — knowledge graph
- `services/frontend/src/components/oracle/ASSIGNMENT.md` — Oracle terminal
- `services/frontend/public/ASSIGNMENT.md` — PWA & local operations
- `services/frontend/src/auth/ASSIGNMENT.md` — auth, favorites library, public API
- `services/frontend/ASSIGNMENT-testing.md` — testing strategy

## Start here

- [`docs/public/teaching/index.md`](docs/public/teaching/index.md) — how this maps to FE II
  Units 1–7, and how a class session runs (theory → team meeting → lab time)
- [`docs/public/audiences/students.md`](docs/public/audiences/students.md) — what you're expected
  to build and defend
- [`AGENTS.md`](AGENTS.md) — the governed-data contract: how quote proposals get reviewed and
  accepted, and the one rule that never changes — only a named human accepts a proposal into
  `ttod.yml`

## Run it locally

```bash
cp .env.example .env   # fill in required values
make up                # starts backend, MCP, frontend, and the app's own Ollama
```

See `Makefile` (`make help`) for the full command list — validation, tests, local dev servers.

## Contributing

Every PR follows [`.github/pull_request_template.md`](.github/pull_request_template.md) — it's
your module's grading rubric as a checklist, not a separate hoop. `.github/workflows/ci.yml` is
the required check your PRs run against.
EOF

echo "== Creating the orphan commit =="
rm -rf "$STAGE"
cd "$DEST"
git init -q -b "$OUT_BRANCH"
git add -A
git commit -q -m "$(cat <<'EOF'
TTOD FE II teaching baseline — fresh history, no shared objects with main

Orphan root commit. Generated by scripts/generate-ts5-teaching-baseline.sh
from skeleton/ts5-hello-world's tree — governed core, the working app
(backend/mcp/frontend with every module's ASSIGNMENT.md), local-operation
config, licenses, the agent contract, the reviewer/student PR workflow, and
curated student-facing docs (docs/public/teaching, docs/public/audiences/
students.md, es/ mirrors) only. No docs/DEV_PLAN, no instructor tooling, no
absolute local paths, no machine names — verified by the public-privacy
watcher before this commit was trusted (see PHASE-U-TS5-REPORT.md).

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"

cd - > /dev/null
echo "== Importing the orphan commit into this repository as $OUT_BRANCH =="
git fetch "$DEST" "$OUT_BRANCH:$OUT_BRANCH"
rm -rf "$DEST"

echo "== Done. Branch: $OUT_BRANCH =="
git log --oneline -1 "$OUT_BRANCH"
echo "Nothing was pushed. Run the privacy watcher and isolation probe next."
