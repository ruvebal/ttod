<!--
Phase U TS3a report — R3b content/i18n hello-world reduction.
Follows cascade-forge evidence-state discipline (status first; claims checked live).
Executed on branch skeleton/ts3a-r3b, worktree ../ttod-skeleton-ts3a, forked from
skeleton/ts1-contracts@47f15da9 (never main).
-->

# Phase U · TS3a Report — R3b content hello-world

**Status:** DONE

**Scope executed:** the keep/cut in the TS3a runbook
(`docs/DEV_PLAN/PHASES/U-TS3a-r3b-content-hello-world.md` §4 — untracked on the main checkout;
not present on `skeleton/ts1-contracts`) and the TS1 subtraction table R3b row
(`docs/DEV_PLAN/PHASE-U-TS1-REPORT.md` §4, also untracked on main): index + one detail, both
locales, live `WisdomEntry` data; three facet-browse route files deleted; `ASSIGNMENT.md` filed;
`frequencies()` left unused but present.

**Date:** 2026-09-09

**Implementer:** TS3a lane session (worktree only)

**Independent verifier:** pending

**Owner:** `@crea-comm.net`

**Branch / worktree:** `skeleton/ts3a-r3b` at `/Users/ruvebal/src/ttod-skeleton-ts3a`
(forked from `skeleton/ts1-contracts`, not `main`)

---

## 1. Pre-flight

- TS1 report status **DONE** — this lane is not BLOCKED.
- TS1 R3b row matches the runbook: delete `sections/`, `tags/`, `levels/` files entirely; keep
  index + detail; do not delete `frequencies()`.
- Worktree created as specified:

  ```text
  cd /Users/ruvebal/src/ttod
  git worktree add ../ttod-skeleton-ts3a -b skeleton/ts3a-r3b skeleton/ts1-contracts
  HEAD 47f15da9 TS1: run CI on skeleton/** branches, not only main.
  ```

No edits under `services/backend/`, `services/mcp/`, `ttod_core/`, `ttod.yml`,
`components/graph/`, or `components/oracle/`.

```text
$ git diff main -- services/backend/ services/mcp/ ttod_core/ ttod.yml \
    services/frontend/src/components/graph/ services/frontend/src/components/oracle/
(empty)
```

---

## 2. Files removed (routes genuinely absent)

Deleted entirely (not commented out). The empty directories were removed as well, so Astro's
file-based router has no facet pages on this branch.

| Removed path | ASSIGNMENT.md deliverable line |
| --- | --- |
| `services/frontend/src/pages/[locale]/wisdom/sections/[section].astro` | section browse |
| `services/frontend/src/pages/[locale]/wisdom/tags/[tag].astro` | tag browse |
| `services/frontend/src/pages/[locale]/wisdom/levels/[level].astro` | level browse |

Confirmed on disk after the cut:

```text
$ find services/frontend/src/pages/[locale]/wisdom -print
services/frontend/src/pages/[locale]/wisdom
services/frontend/src/pages/[locale]/wisdom/index.astro
services/frontend/src/pages/[locale]/wisdom/[slug].astro
services/frontend/src/pages/[locale]/wisdom/ASSIGNMENT.md
```

Live HTTP against the worktree hello-world server (`http://localhost:4321`):

```text
404  /en/wisdom/sections/images/
404  /en/wisdom/tags/optimization/
404  /en/wisdom/levels/beginner/
404  /es/wisdom/sections/architecture/
```

---

## 3. Kept journeys (close to as-is)

`index.astro` still fetches `fetchWisdom(locale)` and lists real entries with locale switch and
empty-state copy. The three `frequencies()` pill clusters that linked at the deleted facet routes
were dropped so `frequencies()` is unused by hello-world routes (runbook §3) and so the index does
not 404 students into missing pages.

`[slug].astro` still fetches by id and renders `text` / `teaches` / `section` / `level`. Tag pills
are `<span>`s rather than `<a href="…/wisdom/tags/…">` (those URLs no longer exist).

`services/frontend/src/content/wisdom.ts` was **not** edited. `frequencies()` remains at line 31.

---

## 4. ASSIGNMENT.md

**Path:** `services/frontend/src/pages/[locale]/wisdom/ASSIGNMENT.md`

Required sections are all present:

| Section | What it names |
| --- | --- |
| Learning outcomes | dynamic file-based routes; mandatory `en`/`es` i18n; content collections vs live corpus; semantic HTML for humanities content |
| Constraints | reuse `fetchWisdom` + frozen `WisdomEntry`; both locales; no backend edits; prefer `frequencies()`; do not read `ttod.yml` |
| Acceptance criteria | section / tag / level browse routes exist and are reachable in both locales; breadcrumbs; one accessibility check per new route; index/detail stay live |
| Prohibited shortcuts | no hardcoded locale; no static JSON replacing `fetchWisdom`; no parallel wisdom collection; no restoring from instructor-only history; no `domain.ts` / backend / `ttod.yml` edits |

The three removed files are named in that brief as the assessed deliverables, not as defects.

---

## 5. Gate evidence (runbook §5)

Compose (`ttod_oracle-*`) was already up from the main checkout: reverse-proxy
`http://localhost:18080`, backend healthy. `GET /api/v1/wisdom/sample` returned **460** entries
(`en`: 230, `es`: 230). No fixtures were invented.

The Docker **frontend** image on `:18080` is still the pre-subtraction build (facet links present).
Hello-world routes were therefore verified from this worktree with:

```text
cd /Users/ruvebal/src/ttod-skeleton-ts3a/services/frontend
BACKEND_URL=http://localhost:18080 npm run dev
# Astro 5.18.2 → http://localhost:4321
```

Caddy on `:18080` proxies `/api/*` to the live backend, so SSR `fetchWisdom` round-trips the real
sample endpoint.

| Gate | Result |
| --- | --- |
| Both locales render real content | **PASS** — see curl matrix below; neither empty-state string appeared |
| One detail page works | **PASS** — `/en/wisdom/img-001/` and `/es/wisdom/arch-060/` |
| Facet routes absent | **PASS** — files gone; those URLs 404 |
| `ASSIGNMENT.md` present | **PASS** — four required sections |
| No backend edits | **PASS** — empty `git diff main -- services/backend/` |

`npm run check` in the worktree frontend: **0 errors, 0 warnings, 0 hints** (27 files; three facet
pages no longer in the graph).

### Curl transcript (worktree `:4321` → live backend)

```text
200  /en/wisdom/                 html lang=en  title=Wisdom
     quote: The wise developer knows: the smallest image carries the heaviest meaning.
     id img-001 present; /wisdom/sections/ absent from HTML
     empty-state strings absent

200  /es/wisdom/                 html lang=es  title=Sabiduría
     quote: El acoplamiento fuerte es un préstamo con interés compuesto. El acoplamiento flojo es un ahorro que se multiplica.
     id arch-060 present; /wisdom/sections/ absent from HTML
     empty-state strings absent

200  /en/wisdom/img-001/         title=img-001 · Wisdom
     text, Teaches, meta: img-001 · images · beginner · legacy-unknown · en

200  /es/wisdom/arch-060/        title=arch-060 · Sabiduría
     text, Enseña, meta: arch-060 · architecture · beginner · blackbox · es

404  /en/wisdom/sections/images/
404  /en/wisdom/tags/optimization/
404  /en/wisdom/levels/beginner/
404  /es/wisdom/sections/architecture/
```

Live sample IDs used above (`img-001`, `arch-060`) were taken from the running
`/api/v1/wisdom/sample` payload, not from a committed fixture.

---

## 6. Explicit non-claims

This report does **not** claim:

- The Compose frontend container was rebuilt from this branch (it was not; `:18080` still serves
  the rich reference UI).
- TS3b / TS3c have been opened.
- The assignment brief is the implemented browse UI (it is the student seam).
- This branch should be merged to `main`.

---

## 7. Resume rule

| Status | Meaning | Next action |
| --- | --- | --- |
| **DONE (current)** | Hello-world index+detail live in `en`/`es`; facet files gone; `ASSIGNMENT.md` filed; no backend edits | Independent second reader (§8 of the runbook). TS3b/TS3c may proceed per TS1's resume rule once they confirm this filing. |
| **PARTIAL** | Named §5 gate unmet | Finish that gate before later content lanes |
| **BLOCKED** | TS1 not DONE | Do not open this lane |
