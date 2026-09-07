# 道 THE TAO OF THE DEVELOPMENT (TTOD)

**by Rubén Vega Balbás, PhD** — `ruvebal@crea-comm.net`

```
═══════════════════════════════════════════════════════════════════════════════
                              道
                    THE TAO OF THE DEVELOPMENT
                              道
         Ancestral Wisdom for the Age of Machine-Assisted Creation
═══════════════════════════════════════════════════════════════════════════════
```

> _"The Tao that can be prompted is not the eternal Tao. The code that can be generated without understanding is not true code."_
> — Lao Tzu, if he had lived to see Stack Overflow

---

> In the ancient scrolls of the silicon age, there existed a sacred text known as [The Tao of Programming](https://www.mit.edu/~xela/tao.html) —a collection of paradoxical wisdom passed down through generations of code warriors. Inspired by its timeless teachings, this book of wisdom is dedicated to the art of machine-assisted creation, revealing the eternal truths of technological intelligence in the digital realm.

---

TTOD is a pedagogical wisdom database — aphorisms for developers walking the path, organized by
section and mastery level, and served outward as content-addressed, human-governed quotes. See
[`AGENTS.md`](AGENTS.md) for the agent contract, data model, and CLI.

**Development status, contract, and phase runbooks** live in one place so they never drift into
two tellings: [`docs/DEV_PLAN/INDEX.md`](docs/DEV_PLAN/INDEX.md). That file is the canonical
source for programme state, the active-phase table, and links to every phase report. This README
does not repeat it.

## Public guide map

The independent Jekyll publication is sourced only from [`docs/public`](docs/public). Its main
index provides a complete menu across the developed and planned teaching surfaces:

- [Project](docs/public/project/index.md) — mission, governance, provenance, and licensing
- [Product areas](docs/public/platform/index.md) — content, quotes, graph, Oracle, operations, and tests
- [Teaching model](docs/public/teaching/index.md) — R3b–R7 at proposed hello-world depth
- [Research](docs/public/research/index.md) — questions, maturity, method, and safeguards
- [Guides](docs/public/guides/index.md) — local setup, product use, and contribution
- [Students](docs/public/audiences/students.md) — provided scaffold and learner-owned work
- [University partners](docs/public/audiences/partners.md) — academic value and release gates
- [Research and venture partners](docs/public/audiences/research-funders.md) — assets, risk, and diligence
- [Roadmap](docs/public/roadmap/index.md) — evidence-backed current and proposed states

The documentation site may be published while the application remains local. That does not by
itself authorize making the whole source repository public.

**Programme status (2026-08-18):** Phase Q **complete** — the live canonical collection has since
advanced to schema **v3.1.0** through the governed bilingual programme. Current phase state lives
only in the development-plan index. Phase Q closed with the collection
strict-valid, and writable only through the CLI/repository. Closeout report:
[`docs/DEV_PLAN/PHASE-Q6-REPORT.md`](docs/DEV_PLAN/PHASE-Q6-REPORT.md).

## Verification

```bash
. .venv/bin/activate
python cli.py validate --strict --json   # must exit 0
python cli.py stats --check              # meta must match recomputed
python -m unittest discover -s tests -p 'test_*.py'   # full suite must pass
```

**License:** code is MIT ([`LICENSE-CODE`](LICENSE-CODE)); content — `ttod.yml` quotes, `docs/`,
`sources/` — is CC BY-NC-SA 4.0 ([`LICENSE-CONTENT`](LICENSE-CONTENT)), per
[`docs/DEV_PLAN/DECISIONS/Q0-2026-08-18-RIGHTS-LICENSE-NC.md`](docs/DEV_PLAN/DECISIONS/Q0-2026-08-18-RIGHTS-LICENSE-NC.md).

**Agent contract:** [`AGENTS.md`](AGENTS.md)
([agentsmd standard](https://github.com/agentsmd/agents.md)).

## Constitutional boundary

The Athanor and WPL development processes may reference the same immutable Athanor evidence
snapshot, including ingested research and governed field-research records. They must not quote,
cite, or summarize each other's draft output as evidence. TTOD quotes are pedagogical material,
not independent corroboration. A quote derived from an Athanor plan, including `arch-052`, must
never be fed back to Athanor or WPL as support for that plan. Full contract:
[`docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md`](docs/DEV_PLAN/PHASE-Q-TTOD-CONTRACT-REPAIR-CASCADE.md).
