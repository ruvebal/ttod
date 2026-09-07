#!/usr/bin/env python3
"""Draft Spanish siblings for docs/public pages via local Ollama.

Never writes ttod.yml. Model output is a draft; a human must review before the
Jekyll source is committed. Uses the same HTTP generate path as Phase S4/S5.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ttod_core.translation import TranslationError, call_ollama_generate  # noqa: E402

SOURCE = ROOT / "docs" / "public"
MODEL = "qwen3.8:27b"

PROMPT = """You are a literary translator working on public pedagogical documentation for software developers.

Translate the following Jekyll markdown page from English to contemporary international Spanish. Prefer Spain usage only where it does not reduce wider intelligibility.

Preserve exactly:
- YAML front-matter keys (translate title, eyebrow, and description values only)
- Liquid tags and filters unchanged
- Canonical quote IDs, commands, paths, URLs, DOIs, license names, and fenced code
- HTML structure and class names
- Hedging and claim boundaries; do not make planned work sound finished
- Do not invent internal development-phase names

Do not add a preamble, title, or commentary. Respond with ONLY the translated markdown file.

SOURCE:
"""


def translate_text(text: str, timeout: float) -> str:
    data = call_ollama_generate(MODEL, PROMPT + text, timeout=timeout, temperature=0.3)
    raw = (data.get("response") or "").strip()
    if not raw:
        raise TranslationError(f"empty response from {MODEL}")
    raw = raw.removeprefix("```markdown").removeprefix("```md").removeprefix("```").removesuffix("```").strip()
    return raw


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="English markdown file under docs/public")
    parser.add_argument("--output", type=Path, help="Write draft here (default stdout)")
    parser.add_argument("--timeout", type=float, default=300.0)
    args = parser.parse_args()
    source = args.source if args.source.is_absolute() else ROOT / args.source
    draft = translate_text(source.read_text(encoding="utf-8"), args.timeout)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(draft + "\n", encoding="utf-8")
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(draft + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except TranslationError as exc:
        print(f"TRANSLATE-PUBLIC-DOCS FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
