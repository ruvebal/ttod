# Source — The Tao of Human-Centered Design

**Status:** parked for merge into `ttod.yml`. Do not treat this file as the
quote database. The YAML remains the source of truth for IDs.

| File    | Language | Origin                                                                 |
| ------- | -------- | ---------------------------------------------------------------------- |
| `es.md` | Spanish  | Ported 2026-08-28 from `hc-app-design/docs/tao/index.md`               |

Jekyll frontmatter is preserved so the move is lossless. Strip it when
extracting quotes.

## Why it is here

*El Tao del Diseño Centrado en las Personas* is the pedagogical wisdom layer
for the hc-app-design Studio course (Diseño Centrado en las Personas). It
collects haiku, koan, and máxima forms across ten chapters — personas,
problema, investigación, accesibilidad, prototipo, test, evidencia, IA,
código, exhibición — plus a generative note and academic references.

TTOD is the teaching layer that already stores aphorisms with IDs, tags, and
`origin`. This text belongs here until distilled into quote records.

hc-app-design keeps the published Jekyll page at `/tao/` for students. The
canonical prose copy lives here until merge.

## Merge later (do not do it in the same session as a lesson forge)

1. Distill durable lines into quotes (`origin: human`, `source: tao-of-human-centered-design`).
2. Assign IDs from `meta.last_id_by_section`. Likely sections: `ux`, `a11y`,
   `wisdom`, `code-craft`. Add tags to `tag_taxonomy` first if needed
   (`hcd`, `research`, `usability`, `evidence`, `studio`, …).
3. Map chapter → subsection where useful (e.g. cap. IV → `a11y`, cap. III → `ux`).
4. Bidirectional `related` where a koan already has a cousin in `ttod.yml`.
5. Bump `meta.total_quotes`. Run `python cli.py validate` (zero errors).
6. Teaching surfaces quote **by ID** only. hc-app-design lessons consume IDs;
   they do not copy the chapter.

Priority distill (lines other artefacts are waiting on):

- «El tao que puede ser procesado por un modelo no es el tao eterno.»
- «La frustración de la usuaria no es un problema de la usuaria.»
- «La IA puede escribir la síntesis de la investigación que hiciste. No puede hacer la investigación que no hiciste.»
- «Accesibilidad añadida después del diseño no es accesibilidad — es compensación.»
- «Codificar es diseñar. Diseñar es elegir quién puede y quién no puede.»

## License

- **Chapter prose:** CC BY-NC-SA 4.0 — see repo [`LICENSE-CONTENT`](../../LICENSE-CONTENT).
- **TTOD tooling/code:** MIT — see [`LICENSE-CODE`](../../LICENSE-CODE).
- **TTOD database quotes:** CC BY-NC-SA 4.0 per quote `rights.license`; reconcile on merge — do not silently relicense.
