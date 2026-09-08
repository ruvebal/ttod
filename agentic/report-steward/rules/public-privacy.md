# Public-output privacy rule

Public, partner, and student-facing artifacts must not contain:

- local absolute, tilde-expanded, mounted-volume, or temporary paths;
- private-network addresses;
- internal-only hostname suffixes (`*.loc`, `*.local`, `*.lan`, `*.internal`, `*.home`) —
  including Docker host gateways written as `host.docker.internal`;
- names of private machines or infrastructure supplied through a local denylist; or
- personal email addresses outside `@crea-comm.net`;
- internal development phase names, numbers, or shorthand in public documentation
  (`R6`, `Q4`, `Phase Q`, `RC0`, `TS1`, …).

Use repository-relative paths and role labels such as “instructor workstation,” “local container,”
“Docker host gateway,” or “future staging environment.” Run `scripts/check_public_privacy.py`
over the exact candidate artifact. Findings block release; do not hide them with a broad
allowlist. Historical/internal archives must be excluded from the candidate explicitly if they
retain operational details.

Public documentation describes capabilities, learner responsibilities, maturity, and next work in
reader-facing language. Internal roadmap identifiers belong only in engineering plans and evidence
reports; they must not leak into navigation, prose, metadata, generated HTML, Archify JSON labels,
source-evidence labels, guided-view notes, or asset text under `docs/public/`.

## Markup that must not reach Pages (htmlproofer)

Shipped failures (2026-09-08): `htmlproofer` Links check — `'a' tag is missing a reference`.

- Citation fragment targets: use `<span id="ref-…"></span>`, never empty `<a id="ref-…"></a>`.
- Archify interactive HTML: every `<a>` needs an `href` before publish. The
  `#focus-repository` shell must ship with a real repository URL (e.g.
  `https://github.com/ruvebal/ttod`); JS may overwrite it at runtime.
- After copying Archify HTML into `docs/public/assets/diagrams/`, run the privacy watcher on
  that directory **and** `bundle exec htmlproofer` on a local `_site-public` build before claiming
  done.
