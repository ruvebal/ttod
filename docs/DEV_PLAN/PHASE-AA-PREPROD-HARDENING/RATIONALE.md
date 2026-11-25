# Why Phase AA exists (product face)

TTOD’s classroom app is **already running**: bilingual shell, wisdom, graph, oracle,
accounts with Redis permanence, open student registration. That is a teaching
success. It is **not** yet a claim that the same Compose file can face a real
web server on the public or even semi-public internet.

Phase AA exists to turn an honest pre-production audit into:

1. a **falsifiable findings ledger** (what is wrong, with evidence);
2. a **gated cascade** so fixes land in the right order (headers before “we’re secure”);
3. a **student assignment list** that maps each finding to a seam students can own
   without touching `ttod.yml` or inventing a second auth system;
4. a **locator contract** ([LOCATORS.md](LOCATORS.md)) so that a quote, a search, a scroll
   chapter or a graph path can be cited by URL in a PR or a lesson. A pedagogical
   database whose places cannot be linked cannot be taught from.

## What AA is not

- Not Phase T (public GitHub release / partner demo / history isolation).
- Not “redesign the brand.” Restyling the header *component* on existing tokens (F56) is in scope. New fonts, palette or logo are not.
- Not Postgres / cloud Redis / new frameworks.
- Not a license change.

## Success looks like

A maintainer can point at a student PR and say: “This closes F3 with a Redis
throttle and a test that would have failed before.” Then Caddy headers, TLS
story, and deploy checklist follow. When AA closes, Phase T’s security gates
have fresher evidence — they still remain separate claims.
