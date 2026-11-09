<!--
PHASE-Z — Redis shore for accounts, sessions, favorites, proposal drafts (Compose + bind mount).
Amended 2026-10-27: broadened beyond favorites-only. Author: Rubén Vega Balbás PhD
-->

# Phase Z — Redis runtime permanence (shore store)

**Status:** AUTHORIZED 2026-10-27 · **Z0–Z6 DONE** · post-cohort completeness recovered 2026-11-09 ([COMPLETENESS-2026-11-09.md](COMPLETENESS-2026-11-09.md)).
**Depends on:** Phase R stack on `main`; Phase V Accounts/Library/Proposals API live; tip [#87](https://github.com/ruvebal/ttod/pull/87) superseded by Phase Z.
**Programme letter:** Z.
**Author:** Rubén Vega Balbás PhD · drafted 2026-10-27 · **amended same day** (accounts + proposals + shared Redis module) · **amended 2026-11-09** (Equipo merges #89/#92 register + F2 close).

## One-sentence claims

- **Product:** Student logins, profiles, library, and proposal drafts survive Compose restarts without touching `ttod.yml`.
- **Engineering:** One Redis microservice (AOF on a host bind mount) + one shared backend Redis client; Protocol stores per domain; proposals **dual-write** so CLI accept stays file-based.
- **Pedagogy:** Accounts team uses the same shore as favorites — Redis is the database for *runtime identity and drafts*, not a second corpus.

## How to read this pack

| Face | File |
| ---- | ---- |
| Index (this) | entry + live snapshot |
| Shore map (what else?) | [REDIS-SHORE-MAP.md](REDIS-SHORE-MAP.md) |
| Completeness (post-#92) | [COMPLETENESS-2026-11-09.md](COMPLETENESS-2026-11-09.md) |
| Evidence | [FINDINGS-2026-10-27.md](FINDINGS-2026-10-27.md) |
| Orchestrator | [PHASE-Z-REDIS-RUNTIME-PERSISTENCE-CASCADE.md](PHASE-Z-REDIS-RUNTIME-PERSISTENCE-CASCADE.md) |
| Phases | [PHASES/](PHASES/) Z0→Z6 |

## Live snapshot (2026-11-09)

| Fact | Value | Where checked |
| ---- | ----- | ------------- |
| Open tip PRs | **0** (train #91→#88→#90→#89→#92 merged) | `gh pr list` |
| Auth today | Redis/Memory `UserStore` + opaque `SessionStore`; open `POST /api/v1/auth/register` always `student`; env admin seed = reviewer+instructor | `auth.py`, #92 |
| Favorites today | `ttod:favorites:{userId}` (Redis when `REDIS_URL` set); POST requires user exists | `favorites.py`, `main.py` |
| Proposals today | Dual-write file + Redis; CLI accept still file-based | `proposal_drafts.py` |
| `main` Compose Redis | present — AOF bind `./data/redis`, no host ports, healthy gate | `docker-compose.yml`, Z1 exit-gate OK today |
| Register roles | **always `student`** (server-forced; client cannot elevate) | `test_a_client_cannot_choose_its_own_roles_or_id` |

## Decision

**Yes — Redis is the classroom DB for shore state**, including Accounts (profiles/login/sessions) and proposal drafts. Not Postgres. Not “Redis for favorites only.”

Authorize **Z0** to freeze the shore map + improved Compose knobs before code. **2026-11-09:** plan recovered; Compose permanence + student register path are complete for classroom use (set stable session/PAT secrets in `.env` before relying on PATs across restarts).
