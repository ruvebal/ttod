# Source — The Tao of AI Development

**Status:** parked for merge into `ttod.yml`. Do not treat these files as the
quote database. The YAML remains the source of truth for IDs.

| File | Language | Origin |
| --- | --- | --- |
| `en.md` | English | Moved 2026-08-13 from Web Atelier `methodology/en/tao-of-ai-development/` |
| `es.md` | Spanish | Moved 2026-08-13 from `methodology/es/ai-practical-guide/tao-of-ai-development/` |

Jekyll frontmatter is still on the files so the move is lossless. Strip it
when extracting quotes.

## Why it is here

The chapter is a voice piece (Craftsman's Oath, Weight of Tokens, README
covenant, koans). It does not belong on the student protocol page and it is
not a journal article. TTOD is the teaching layer that already stores
aphorisms with IDs, tags, and `origin`.

Web Atelier keeps **permalink stubs** so existing URLs do not 404. The full
text lives here until merge.

## Merge later (do not do it in the same session as a student-guide forge)

1. Distill durable lines into quotes (`origin: human`, `source: tao-of-ai-development`).
2. Assign IDs from `meta.last_id_by_section`. Likely sections: `wisdom`,
   `code-craft`, `architecture`. Add tags to `tag_taxonomy` first if needed.
3. Bidirectional `related` where a koan already has a cousin in `ttod.yml`
   (the chapter already cites `cc-001`, `img-064`).
4. Bump `meta.total_quotes`. Run `python cli.py validate` (zero errors).
5. Teaching surfaces quote **by ID** only
   (`lesson-publishing-integrity.mdc` §7). Tribune and student protocol
   consume IDs; they do not copy the chapter.

Priority distill (the lines other artefacts are waiting on):

- Craftsman's Oath ("I am the human in the loop…")
- The first sin (it compiled; the developer did not understand)
- Weight of Tokens
- README covenant / Koan 4 Attribution
- "The Tao that can be prompted is not the eternal Tao"

## License

Chapter prose: CC BY-NC-SA 4.0 (Web Atelier teaching content).
TTOD database: CC BY-SA 4.0. Reconcile on merge — do not silently relicense.
