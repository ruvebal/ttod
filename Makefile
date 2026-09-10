# 道 TTOD — The Tao of Development
# Root task surface for a polyglot teaching repo (Compose · CLI · Jekyll · Astro).
# Author: ruvebal@crea-comm.net · Pattern: DevIAC `make help` + lean ## targets.

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help
.ONESHELL:

ROOT     := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHON   := $(shell if [ -x "$(ROOT)/.venv/bin/python" ]; then echo "$(ROOT)/.venv/bin/python"; else echo python3; fi)
CLI      := $(PYTHON) $(ROOT)/cli.py
COMPOSE  := docker compose
FE       := services/frontend
DOCS     := docs/public
HTTP_PORT ?= 8080

# Prefer npm when present; never introduce a second package manager at the root.
NPM := npm --prefix $(FE)

.PHONY: help env venv \
	up down rebuild ps logs ollama-pull \
	validate stats snapshot export test check \
	docs docs-serve docs-clean docs-setup docs-privacy \
	fe-dev fe-build fe-check \
	review-queue pr-status \
	clean

# ─────────────────────────────────────────────────────────
# Discovery
# ─────────────────────────────────────────────────────────

help: ## Show this help
	@printf '\n  道  TTOD — make targets\n'
	@printf '  %s\n\n' 'https://github.com/ruvebal/ttod'
	@awk 'BEGIN {FS = ":.*## "; section = ""} \
		/^# ─/ { next } \
		/^# [A-Z]/ { section = substr($$0, 3); next } \
		/^[a-zA-Z0-9_-]+:.*## / { \
			if (section != prev) { printf "  \033[1m%s\033[0m\n", section; prev = section } \
			printf "    \033[36m%-14s\033[0m %s\n", $$1, $$2 \
		}' $(MAKEFILE_LIST)
	@printf '\n  Stack URL (default): http://localhost:$(HTTP_PORT)\n'
	@printf '  Corpus CLI:          $(CLI) <command>\n\n'

env: ## Show toolchain resolutions (python, ruby, docker, bundle, npm)
	@printf 'PYTHON=%s\n' '$(PYTHON)'
	@$(PYTHON) --version
	@docker --version
	@$(COMPOSE) version
	@command -v ruby >/dev/null && ruby -v || echo 'ruby: missing'
	@command -v bundle >/dev/null && bundle --version || echo 'bundle: (not on PATH — run make docs-setup)'
	@command -v npm >/dev/null && npm --version || echo 'npm: missing'
	@test -f $(ROOT)/.env && echo 'env: .env present' || echo 'env: copy .env.example → .env'
	@grep -E '^OLLAMA_MODE=' $(ROOT)/.env 2>/dev/null || echo 'OLLAMA_MODE: (.env missing)'

venv: ## Create .venv (idempotent) and install the editable CLI + service deps
	@test -d $(ROOT)/.venv || python3 -m venv $(ROOT)/.venv
	@$(ROOT)/.venv/bin/pip install -q -e $(ROOT)
	@$(ROOT)/.venv/bin/pip install -q \
		-r $(ROOT)/services/backend/requirements.txt \
		-r $(ROOT)/services/mcp/requirements.txt
	@printf 'venv ready → %s\n' '$(ROOT)/.venv/bin/python'

# ─────────────────────────────────────────────────────────
# Stack (Docker Compose)
# ─────────────────────────────────────────────────────────

up: ## Start the app — its own Ollama included, nothing to install first
	@test -f $(ROOT)/.env || cp $(ROOT)/.env.example $(ROOT)/.env
	@$(COMPOSE) up --build -d
	@$(COMPOSE) ps
	@port=$$(grep -E '^HTTP_PORT=' $(ROOT)/.env | tail -1 | cut -d= -f2); \
	printf 'Open http://localhost:%s (see compose ps for mapped ports)\n' "$${port:-$(HTTP_PORT)}"
	@printf 'First run on an empty Ollama volume? Pull chat + embed models: make ollama-pull\n'

down: ## Stop containers (keeps named volumes)
	@$(COMPOSE) down

rebuild: ## Rebuild images and recreate the stack
	@$(COMPOSE) up --build -d --force-recreate
	@$(COMPOSE) ps

ps: ## Show compose service status
	@$(COMPOSE) ps

logs: ## Tail recent compose logs (n=100)
	@$(COMPOSE) logs --tail=$${n:-100}

ollama-pull: ## Pull Oracle chat + embed models (model= / embed_model= to override)
	@$(COMPOSE) exec ollama ollama pull $${model:-llama3.2:1b}
	@$(COMPOSE) exec ollama ollama pull $${embed_model:-nomic-embed-text}

# ─────────────────────────────────────────────────────────
# Corpus (ttod.yml · cli.py)
# ─────────────────────────────────────────────────────────

validate: ## Strict validate of live ttod.yml
	@$(CLI) validate --strict

stats: ## Recompute and check derived meta
	@$(CLI) stats --check

snapshot: ## Write a C14N snapshot export (out=exports/snapshot.json)
	@$(CLI) snapshot --output $${out:-$(ROOT)/exports/snapshot.json}

export: ## Export canonical JSON and graph projections
	@$(CLI) export --format json
	@$(CLI) export --format graph

test: ## Full Python unittest suite
	@$(PYTHON) -m unittest discover -s $(ROOT)/tests -p 'test_*.py'

check: validate stats test ## Corpus gate: validate + stats + tests
	@printf 'check ok\n'

# ─────────────────────────────────────────────────────────
# Public docs (Jekyll · docs/public)
# ─────────────────────────────────────────────────────────

docs-setup: ## bundle install for the public docs Gemfile
	@cd $(DOCS) && bundle install

docs: ## Build the public Jekyll site
	@cd $(DOCS) && bundle exec jekyll build

docs-serve: ## Serve public docs with livereload
	@cd $(DOCS) && bundle exec jekyll serve --livereload

docs-clean: ## Remove Jekyll _site under docs/public
	@cd $(DOCS) && bundle exec jekyll clean || rm -rf $(DOCS)/_site

docs-privacy: ## Public-privacy watcher on docs/public (phase IDs, hosts, empty <a>)
	@$(PYTHON) $(ROOT)/agentic/report-steward/scripts/check_public_privacy.py $(ROOT)/docs/public --root $(ROOT)

# ─────────────────────────────────────────────────────────
# Frontend package (Astro · services/frontend)
# ─────────────────────────────────────────────────────────

fe-dev: ## Astro dev server (host 0.0.0.0)
	@$(NPM) run dev

fe-build: ## Astro production build
	@$(NPM) run build

fe-check: ## Astro type/content check
	@$(NPM) run check

# ─────────────────────────────────────────────────────────
# GitHub review surface (read-only — approve/merge stay human)
# Privileged git (approve, merge, force-push, protection) is never a Make target.
# ─────────────────────────────────────────────────────────

review-queue: ## Read-only open PR queue (uses scripts/gh-review-queue.sh when present)
	@if [ -x "$(ROOT)/scripts/gh-review-queue.sh" ]; then \
		"$(ROOT)/scripts/gh-review-queue.sh"; \
	else \
		printf 'scripts/gh-review-queue.sh not on this branch yet — falling back to gh pr list\n'; \
		gh pr list --state open --json number,title,isDraft,mergeStateStatus,reviewDecision,headRefName,url \
			--jq '.[] | "#\(.number) [\(.mergeStateStatus // "?")/\(.reviewDecision // "none")] \(.headRefName)\n  \(.title)\n  \(.url)\(if .isDraft then " (draft)" else "" end)\n"'; \
	fi

pr-status: ## Show one PR's merge/check state (PR=2)
	@test -n "$(PR)" || { printf 'usage: make pr-status PR=<n>\n' >&2; exit 2; }
	@gh pr view "$(PR)" --json number,title,url,isDraft,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup,baseRefName,headRefName \
		--jq '"#\(.number) \(.title)\n\(.url)\nbase=\(.baseRefName) head=\(.headRefName) draft=\(.isDraft)\nmergeable=\(.mergeable) state=\(.mergeStateStatus) review=\(.reviewDecision)\nchecks:\n" + ((.statusCheckRollup // []) | map("  \(.name): \(.status)/\(.conclusion // "-")") | join("\n"))'

# ─────────────────────────────────────────────────────────
# Housekeeping
# ─────────────────────────────────────────────────────────

clean: docs-clean ## Remove local caches (Jekyll site + Python bytecode)
	@find $(ROOT) -type d -name '__pycache__' -not -path '*/.venv/*' -exec rm -rf {} + 2>/dev/null || true
	@find $(ROOT) -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	@printf 'clean ok\n'
