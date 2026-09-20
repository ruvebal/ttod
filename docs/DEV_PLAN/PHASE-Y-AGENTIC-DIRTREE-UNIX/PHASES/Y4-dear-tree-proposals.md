# Y4 — Dear Tree proposals (human gate)

## Already staged (2026-09-20) — review these first

Under `~/src/.cursor/skills/ttod-bridge/pending/`:

| File stem | Theme |
| --- | --- |
| `…-architecture-a-dirtree-is-a-cathedral-of-names-and-a-` | cathedral/bazaar dirtree |
| `…-code-craft-name-a-folder-as-if-you-were-baptising-a` | naming / one star |
| `…-architecture-when-packs-and-leaves-share-a-parent-wit` | deer lost in forest |
| `…-wisdom-wu-wei-in-a-repository-remove-the-wrong-` | non-forcing layout |
| `…-devops-release-early-the-layout-you-can-defend-` | ESR release-early → README |

All `origin: blackbox`, no `validated_by`.

## What the agent may do here — and only this

- Read the five staged files; confirm each is well-formed and still `origin: blackbox` with no
  `validated_by`.
- Dry-run the import on a **disposable copy** of `ttod.yml` (never the live file) to show they
  would pass `validate --strict`.
- Write `PHASE-Y4-REPORT.md` and leave the exact accept commands for the named human.

The agent does **not** run `proposal accept`, does not supply a `--reviewer-id`, and does not
edit `collections`. Accepting is the human act; the collection edit is only valid after it.

## Human steps

1. `proposal import` / review / `proposal accept --reviewer-id …` (or studio accept path).
2. Add collection only after IDs exist:

```yaml
dear_tree:
  name: The Tao of the Dear Tree
  description: >-
    Quotes on dirtree coherence — naming homes, packs vs leaves,
    non-forcing structure (cathedral of names, bazaar of packs).
  ids: [/* accepted ids */]
```

3. `python cli.py validate --strict` + `stats --check`.
