# Instructor PR merge sequence — post-defense queue (2026-11-07)

**Audience:** instructor only (not students).  
**Trigger:** five open PRs (#88–#92) after oral defense; laptop cannot run host Ollama.  
**Deferred:** `make review-pr` hybrid bot (needs Metal Ollama `:11434` + `qwen2.5-coder:32b` on a machine that can run it — Tanit).  
**Canonical guide:** [`docs/public/guides/reviewing-cohort-prs.md`](../../public/guides/reviewing-cohort-prs.md).  
**Shore map:** [`docs/DEV_PLAN/PHASE-Z-REDIS-RUNTIME-PERSISTENCE/REDIS-SHORE-MAP.md`](../PHASE-Z-REDIS-RUNTIME-PERSISTENCE/REDIS-SHORE-MAP.md).

This file is the frozen runbook. Execute it later on a machine with `gh` as `ruvebal`, SSH push to `origin`, and (optionally) Ollama for the bot pass.

---

## 0. Snapshot of the queue (as of 2026-11-07)

| Order | PR | Author / branch | Required CI (`typecheck-and-build`) | Ambient | Hybrid brief | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | [#91](https://github.com/ruvebal/ttod/pull/91) `fix/icon_deletion_revert` | PRNovoa | ✅ | pwa ✅ | `brief=none` | **PWA gate** — restore `icon-192.png` / `icon-512.png` |
| 2 | [#88](https://github.com/ruvebal/ttod/pull/88) `oracle-terminal-mejoras` | nbfrodri | ✅ | pwa ❌ | `brief=none` | Closest merge; Copilot recommended approve |
| 3 | [#89](https://github.com/ruvebal/ttod/pull/89) `accounts-task10-post-defense` | alexxblaro16 | ✅ | pwa ❌ | `ASSIGNMENT-accounts-task10.md` | Land **before** #92 (`auth.server.ts` overlap) |
| 4 | [#92](https://github.com/ruvebal/ttod/pull/92) `accounts-task11-user-persistence` | alexxblaro16 | ✅ | pwa ❌; docs build ❌ | `brief=missing` (oral task11) | Hold until registration policy answered |
| 5 | [#90](https://github.com/ruvebal/ttod/pull/90) `graph-task11-post-defense-changes` | gpfc-git | ✅ | pwa ❌; ~14 behind | `brief=missing` | Rebase after earlier lands |

**Branch protection on `main` (strict):**

| Gate | Blocks `gh pr merge`? |
| --- | --- |
| `typecheck-and-build` | **Yes** |
| 1 approving review | **Yes** |
| Branch up to date with `main` (`strict: true`) | **Yes** |
| `pwa-compatibility` | No (signal) |
| Public documentation `build` | No (signal; already red on `main` via `sync_visual_system.py --check`) |

Nothing in this queue had an approval yet on 2026-11-07. Ambient PWA red is from `875db85` deleting manifest icons; #91 is the unblocker for that signal.

---

## 1. Preconditions (before any checkout)

```bash
cd ~/src/ttod/ttod   # or your clone root

# Identity: must be ruvebal, not ruvebal-udit
gh api user --jq .login          # expect: ruvebal
git remote -v                    # prefer git@github.com:ruvebal/ttod.git
# If HTTPS still says Permission denied to ruvebal-udit:
#   git remote set-url origin git@github.com:ruvebal/ttod.git
#   printf 'protocol=https\nhost=github.com\n\n' | git credential-osxkeychain erase

git fetch origin
git status -sb                   # instructor main clone may be dirty — that is OK
make review-queue                # read-only inventory
```

**Do not** `gh pr checkout` in the dirty instructor clone. Use a review worktree:

```bash
# once
git worktree add ../ttod-review main
cd ../ttod-review
git fetch origin && git checkout main && git pull --ff-only origin main
```

All `gh pr checkout`, `npm`, and Redis probes below run from `../ttod-review` unless noted.

---

## 2. Optional bot pass (skip on this laptop; do on Tanit)

```bash
# On Tanit / any host with Metal Ollama:
curl -s http://localhost:11434/api/tags | python3 -c 'import sys,json; print([m["name"] for m in json.load(sys.stdin)["models"]])'
# need qwen2.5-coder:32b — not the Compose teaching port :11435

cd ../ttod-review
make review-pr PR=89            # has real brief — read terminal output first
make review-pr PR=89 POST=1     # only if the draft looks sane

# Generic-only (still useful as a diff skim, not as acceptance grade):
make review-pr PR=88
make review-pr PR=91
make review-pr PR=90
make review-pr PR=92
# stderr brief=none|missing → do not treat as full task grade
```

Elevate **MUST FIX** only when requesting changes. NITs stay comments.

---

## 3. Git merge sequence (detailed)

Protection forces: **approve → update branch → squash merge → next PR updates**. Never merge two PRs that share a file without refreshing the second.

### 3.1 Decision before #91 — icons vs visual-system sync

`site.webmanifest` declares `visual-system/icon-192.png` and `icon-512.png`.  
`scripts/sync_visual_system.py` copies **only top-level files** from `shared/visual-system/` → `docs/public/assets/visual-system/` and `services/frontend/public/visual-system/`.  
`main` already drifts (frontend has extras such as `CREDITOS.md`). Public-docs CI has been failing on that check.

Pick one before merging #91:

| Option | Action |
| --- | --- |
| **A — PWA first (fast)** | Merge #91 as-is. Accept deeper sync drift; schedule a follow-up that either adds icons to `shared/visual-system` + `python3 scripts/sync_visual_system.py`, or moves icon paths out of the synced tree. |
| **B — Contract-clean** | Ask PRNovoa (or land a tiny follow-up) to put icons in `shared/visual-system/` and run sync so docs + frontend match before/with #91. |

### 3.2 Per-PR loop (repeat for 91 → 88 → 89 → 92 → 90)

```bash
cd ../ttod-review
git checkout main && git pull --ff-only origin main

PR=<n>   # set each time

make pr-status PR=$PR
gh pr checks $PR
gh pr view $PR --json files,mergeable,mergeStateStatus,reviewDecision,url

# Checkout student branch into the worktree only
gh pr checkout $PR

# Frontend signal (always)
npm --prefix services/frontend run check
npm --prefix services/frontend run build

# If behavioral AC: make up / click through from this worktree — not from dirty main clone

# Approve (or request-changes with MUST FIX cite)
gh pr review $PR --approve --body "…one line why…"
# or: gh pr review $PR --request-changes --body "MUST FIX: …"

# Strict: branch must include latest main
gh pr merge $PR --squash --delete-branch
# If "must be up to date": GitHub UI "Update branch", or:
#   git fetch origin && git merge origin/main && git push
# then retry merge. Do not --admin unless you know why.
```

After each successful merge:

```bash
git checkout main && git pull --ff-only origin main
```

Then start the next PR's loop (its author may need to click **Update branch** if you merge from the UI).

### 3.3 Overlap rule — #89 before #92

Both touch `services/frontend/src/lib/auth.server.ts`.

```text
merge #89 (squash) → main
→ update #92 onto new main (student or you in review worktree)
→ resolve auth.server.ts if conflicted
→ re-run frontend check/build + backend tests
→ approve #92 → squash
```

```bash
# If you update #92 yourself in the review worktree:
cd ../ttod-review
gh pr checkout 92
git fetch origin
git merge origin/main          # or: git rebase origin/main (prefer merge if student is mid-flight)
# fix conflicts, especially auth.server.ts
npm --prefix services/frontend run check
cd services/backend && python -m pytest -q   # or the repo's usual backend test invocation
git push
```

### 3.4 #90 — rebase after the queue shrinks

```bash
gh pr checkout 90
git fetch origin
git rebase origin/main         # ~14 commits behind as of 2026-11-07
# fix conflicts → push --force-with-lease (student branch; confirm with author if unsure)
npm --prefix services/frontend run check && npm --prefix services/frontend run build
gh pr review 90 --approve
gh pr merge 90 --squash --delete-branch
```

### 3.5 Push / workflow-scope gotchas

- Instructor `origin` must push as **`ruvebal`** (SSH). HTTPS keychain may still be `ruvebal-udit` → 403 / Cursor “create a fork?” — **refuse the fork**.
- If a PR edits `.github/workflows/*`, `gh pr merge` needs OAuth **`workflow`** scope (`gh auth refresh -h github.com -s workflow`). `--admin` does not bypass that.

---

## 4. Redis-specific user config (for reviewing / verifying #92)

Phase Z already put sessions, favorites, and proposal drafts on the Redis shore. #92 adds **real multi-user registration** on top of `RedisUserStore` already sketched in the shore map.

### 4.1 Env the stack must have (`make up` / `.env`)

From `.env.example` (Compose network — do not invent a second DB):

| Variable | Role for #92 |
| --- | --- |
| `REDIS_URL=redis://redis:6379/0` | Shore client. Empty → memory/filesystem backends (unit tests only). |
| `TTOD_SESSION_SECRET` | Stable ≥32 bytes so sessions survive backend restart. Distinct from PAT. |
| `TTOD_PAT_SECRET` | Must **≠** `TTOD_SESSION_SECRET` (auth constructor refuses equality). |
| `TTOD_SESSION_TTL_SECONDS` | Session TTL (default 3600). |
| `TTOD_ADMIN_EMAIL` | Seeded admin email (default `admin@ttod.local`). |
| `TTOD_ADMIN_PASSWORD_HASH` | bcrypt hash; empty ⇒ admin login disabled. Seeded into Redis via `ensure_admin` on boot when hash set. |

Generate secrets / admin hash (host, never commit values):

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"   # session
python3 -c "import secrets; print(secrets.token_urlsafe(32))"   # pat — different value
python3 -c "from getpass import getpass; from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash(getpass()))"
```

Redis service: Compose `redis:7-alpine`, conf bind-mount, AOF under `./data/redis`, **no host port** — only `redis:6379` on the Compose network. Probe from a backend container or `docker compose exec redis redis-cli …`.

### 4.2 Key taxonomy (#92 must obey)

| Key | Type | Contents |
| --- | --- | --- |
| `ttod:user:{id}` | hash | `user_id`, `email`, `password_hash` (bcrypt only), `roles` (JSON list), `display_name` |
| `ttod:user:email:{email}` | string | → `user_id` (email casefolded); reserved with **SET NX** on register |
| `ttod:session:{sid}` | hash + TTL | opaque session (Phase Z) |
| `ttod:favorites:{user_id}` | hash | quoteId → savedAt (ids only) |

Hard rules (unchanged): never put quote bodies in Redis; never accept proposals into `ttod.yml` from Redis alone; fail closed → **503** when `REDIS_URL` set and Redis errors.

### 4.3 What #92 claims to add

- `POST /api/v1/auth/register` + `/{locale}/register` page.
- New users: role always **`student`**; password bcrypt; Redis profile written **before** email SET NX; profile deleted if reservation lost (no orphan reserved emails).
- Responses: **201** + session cookie, **409** email taken, **422** invalid, **503** Redis down.
- `POST /api/v1/favorites`: **401** if signed session has no backing user (deleted user / forged cookie).
- Favorites remain keyed by **session user**, not a client-supplied `userId`.

### 4.4 Instructor policy gates (answer on the PR before merge)

Student asked you to confirm:

1. **Open registration** (anyone, no email verify) vs admin-provisioned only.  
2. **Auto-login on register** (current PR).  
3. **No rate limit** + **409 reveals email existence**.

Until those are explicit in a review comment, do not squash-merge #92.

### 4.5 Live Redis probes (after `gh pr checkout 92` + `make up`)

```bash
# From repo root with Compose up:
docker compose exec redis redis-cli PING

# After one web registration (replace id/email):
docker compose exec redis redis-cli HGETALL 'ttod:user:usr-…'
docker compose exec redis redis-cli GET 'ttod:user:email:ana@ttod.local'
docker compose exec redis redis-cli HGETALL 'ttod:favorites:usr-…'

# Expect password_hash to start with $2b$ — never plaintext
# Expect a second user's favorites key empty / missing when isolating users
```

Student already reported (believe, then spot-check): concurrent same-email register → one 201 + nine 409; Redis restart keeps user + favorites; deleted user session → favorites POST 401; Redis down → API 503 + honest UI.

Unit path (no live Redis): empty `REDIS_URL` → memory stores; `services/backend/tests/test_user_persistence.py` on the PR branch.

---

## 5. Suggested comment templates

**Approve #88 (after update):**

```text
Stream cancel + Escape scoping look correct; tests cover the failure and focus paths.
Ambient pwa-compatibility red is pre-existing (missing icons) — not blocking; tracked via #91.
```

**#92 policy reply (example — edit to taste):**

```text
Policy for this cohort drop:
- Open self-registration OK for the lab (student role only); no email verification required yet.
- Auto-login on register OK.
- Accept 409 email enumeration for now; rate limit deferred (shore map).
Merge after #89 is on main and this branch is updated / conflict-free on auth.server.ts.
```

**#91 sync caveat (if choosing option A):**

```text
Landing icons to unblock PWA. Follow-up: either add icon-192/512 to shared/visual-system and run scripts/sync_visual_system.py, or relocate manifest icon paths outside the synced top-level set — public-docs build is already red on sync drift.
```

---

## 6. Checklist (tick when executing)

- [ ] `gh` / `git` identity = `ruvebal` (SSH origin)
- [ ] Review worktree `../ttod-review` on fresh `main`
- [ ] (Optional, Tanit) Ollama bot pass; `POST=1` only for #89+sane drafts
- [ ] Decide #91 option A vs B (icons vs sync)
- [ ] Merge #91 → pull main
- [ ] Merge #88 → pull main
- [ ] `make review-pr PR=89` (when Ollama available) → approve → merge #89 → pull main
- [ ] Comment #92 policy → update branch onto main → Redis probes → approve → merge #92
- [ ] Rebase/update #90 → approve → merge
- [ ] Tear down: `git worktree remove ../ttod-review` when the wave is done

---

## 7. Out of scope this runbook

- Fixing public-docs `sync_visual_system` drift on `main` (except as decided under §3.1).
- Reactivating cloud `.github/workflows/pr-review.yml` (cost-gated; leave inactive).
- Hand-editing `ttod.yml` or accepting proposals from Redis.
