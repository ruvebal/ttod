# Public-output privacy rule

Public, partner, and student-facing artifacts must not contain:

- local absolute, tilde-expanded, mounted-volume, or temporary paths;
- private-network addresses;
- internal-only hostname suffixes;
- names of private machines or infrastructure supplied through a local denylist; or
- personal email addresses outside `@crea-comm.net`;
- internal development phase names, numbers, or shorthand in public documentation.

Use repository-relative paths and role labels such as “instructor workstation,” “local container,”
or “future staging environment.” Run `scripts/check_public_privacy.py` over the exact candidate
artifact. Findings block release; do not hide them with a broad allowlist. Historical/internal
archives must be excluded from the candidate explicitly if they retain operational details.

Public documentation describes capabilities, learner responsibilities, maturity, and next work in
reader-facing language. Internal roadmap identifiers belong only in engineering plans and evidence
reports; they must not leak into navigation, prose, metadata, generated HTML, or asset text.
