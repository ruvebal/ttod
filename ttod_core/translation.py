"""
TTOD Assisted Translation Drafting (Phase S S4')

Calls a local Ollama model to draft a sister-language version of a quote and
assembles it into a proposal `candidate_content` payload.

Hard boundary (do not weaken): this module never allocates a canonical quote
`id`, never sets `status: active`, and never writes ttod.yml. It only builds
data structures that flow into `ttod_core.proposals.create_proposal()` and
`ttod_core.repository.ProposalStore`. Reaching `status: active` remains a
separate, human-run `cli.py proposal accept --reviewer-id ...` transaction —
this module has no path to that transaction at all.

See docs/DEV_PLAN/PHASE-S-TTOD-BILINGUAL-CONTENT-MODEL.md §S4' and
docs/DEV_PLAN/DECISIONS/S0-2026-09-04-BILINGUAL-CONTENT-MODEL.md decision 4.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

OLLAMA_DEFAULT_HOST = "http://localhost:11434"

# Display names for the prompt only — lang itself stays an open ISO 639-1
# pattern per S0 decision 1/8; this map is cosmetic, never a closed enum.
_LANGUAGE_NAMES = {"en": "English", "es": "Spanish"}


class TranslationError(Exception):
    """Raised when the local model cannot be reached or its output cannot be parsed."""


@dataclass
class TranslationDraft:
    """A single model translation attempt — data only, never a proposal or quote."""

    model: str
    text: str
    teaches: Optional[str]
    raw_response: str
    latency_s: float


def _language_name(code: str) -> str:
    return _LANGUAGE_NAMES.get(code, code)


def build_translation_prompt(
    source_lang: str,
    target_lang: str,
    text: str,
    teaches: Optional[str],
) -> str:
    """
    Build the translation prompt.

    Adapts the draft system-prompt from PHASE-S-TTOD-BILINGUAL-CONTENT-MODEL.md
    §S4' (explicitly marked "not final" in that document) — intent preserved:
    preserve ambiguity/silence/rhetorical structure rather than resolving or
    expanding it; match aphoristic register, not technical prose; preserve
    line breaks/syllabic economy where the form is haiku-shaped.
    """
    src_name = _language_name(source_lang)
    tgt_name = _language_name(target_lang)

    instructions = (
        "You are a literary translator working on a pedagogical wisdom database for "
        "software developers — short aphorisms, koans, and haiku-style maxims.\n"
        f"Translate the following record from {src_name} to {tgt_name}.\n"
        "Preserve ambiguity, silence, and rhetorical structure — do not resolve or "
        "explain what the original leaves open. Match the register of a pedagogical "
        "aphorism, not technical prose. Preserve line breaks and syllabic economy "
        "where the form is haiku-shaped. Do not add content that is not present in "
        "(or a direct implication of) the source. Do not add a preamble, title, or "
        "commentary of your own.\n\n"
    )

    if teaches is not None:
        instructions += (
            "Respond with EXACTLY these two lines, in this order, no markdown fences, "
            "no extra commentary:\n"
            "TEXT: <translated text>\n"
            "TEACHES: <translated teaches>\n\n"
            f"text: {text}\n"
            f"teaches: {teaches}\n"
        )
    else:
        instructions += (
            "Respond with EXACTLY this one line, no markdown fences, no extra commentary:\n"
            "TEXT: <translated text>\n\n"
            f"text: {text}\n"
        )

    return instructions


def parse_translation_response(raw: str, expect_teaches: bool) -> Dict[str, Optional[str]]:
    """Parse the model's TEXT:/TEACHES: response into a dict. Raises TranslationError on failure."""
    cleaned = raw.strip()
    # Strip stray markdown fences some models add despite instructions.
    cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
    cleaned = re.sub(r"\n?```$", "", cleaned).strip()

    text_match = re.search(r"TEXT:[ \t]*(.*?)(?:\nTEACHES:|\Z)", cleaned, re.DOTALL)
    if not text_match or not text_match.group(1).strip():
        raise TranslationError(
            f"could not parse TEXT: field from model response: {raw!r}"
        )
    translated_text = text_match.group(1).strip()

    translated_teaches: Optional[str] = None
    if expect_teaches:
        teaches_match = re.search(r"TEACHES:\s*(.*)", cleaned, re.DOTALL)
        if not teaches_match or not teaches_match.group(1).strip():
            raise TranslationError(
                f"could not parse TEACHES: field from model response: {raw!r}"
            )
        translated_teaches = teaches_match.group(1).strip()

    return {"text": translated_text, "teaches": translated_teaches}


def call_ollama_generate(
    model: str,
    prompt: str,
    *,
    host: str = OLLAMA_DEFAULT_HOST,
    timeout: float = 180.0,
    temperature: float = 0.3,
) -> Dict[str, Any]:
    """Raw call to Ollama's /api/generate (stream disabled). Stdlib only, no new dependency."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "think": False,  # ignored harmlessly by non-thinking models; avoids wasted reasoning tokens
        "options": {"temperature": temperature},
    }
    req = urllib.request.Request(
        host.rstrip("/") + "/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise TranslationError(
            f"cannot reach Ollama at {host} (model={model}): {exc}"
        ) from exc
    except TimeoutError as exc:
        raise TranslationError(
            f"Ollama call timed out after {timeout}s (model={model}): {exc}"
        ) from exc


def translate_quote(
    model: str,
    source_lang: str,
    target_lang: str,
    text: str,
    teaches: Optional[str] = None,
    *,
    host: str = OLLAMA_DEFAULT_HOST,
    timeout: float = 180.0,
) -> TranslationDraft:
    """Call the local model once and return a parsed TranslationDraft."""
    prompt = build_translation_prompt(source_lang, target_lang, text, teaches)
    t0 = time.time()
    data = call_ollama_generate(model, prompt, host=host, timeout=timeout)
    latency = time.time() - t0

    raw_response = data.get("response", "")
    if not raw_response:
        raise TranslationError(
            f"empty response from model={model!r} (done_reason={data.get('done_reason')!r}); "
            "the model may have exhausted its token budget on internal reasoning"
        )

    parsed = parse_translation_response(raw_response, expect_teaches=teaches is not None)

    return TranslationDraft(
        model=model,
        text=parsed["text"],
        teaches=parsed["teaches"],
        raw_response=raw_response,
        latency_s=latency,
    )


def find_active_translations(
    quotes: List[Dict[str, Any]],
    source_id: str,
    target_lang: str,
) -> List[str]:
    """
    Return IDs of quotes that are already an `active` translation_of `source_id`
    into `target_lang` — i.e. quotes that would collide with TRANSLATION_DUPLICATE_ACTIVE
    if a newly-accepted draft joined them. Read-only; never mutates.
    """
    matches: List[str] = []
    for quote in quotes:
        if not isinstance(quote, dict):
            continue
        status = quote.get("status") or "active"
        if status != "active":
            continue
        if quote.get("lang") != target_lang:
            continue
        edges = quote.get("relation_edges") or []
        if not isinstance(edges, list):
            continue
        for edge in edges:
            if (
                isinstance(edge, dict)
                and edge.get("relation_type") == "translation_of"
                and edge.get("target") == source_id
            ):
                matches.append(str(quote.get("id")))
                break
    return matches


def build_translation_candidate(
    source: Dict[str, Any],
    source_id: str,
    target_lang: str,
    draft: TranslationDraft,
) -> Dict[str, Any]:
    """
    Build a proposal `candidate_content` payload from a source quote and a model draft.

    Structural guarantee: this function never writes an `id` key (create_proposal()
    rejects one anyway) and never writes a `status` key — the resulting proposal can
    therefore never be mistaken for an already-active canonical quote. Reaching
    `status: active` requires a separate, human-run `proposal accept` transaction that
    this module has no call path to.
    """
    candidate: Dict[str, Any] = {
        "text": draft.text,
        "section": source.get("section"),
        "level": source.get("level"),
        "lang": target_lang,
        "origin": "blackbox",
        "relation_edges": [
            {"target": source_id, "relation_type": "translation_of"}
        ],
        "authorship_assertion": (
            f"machine-translated from '{source_id}' (lang={source.get('lang')}) "
            f"via ollama:{draft.model} — human review required before acceptance"
        ),
    }

    if draft.teaches is not None:
        candidate["teaches"] = draft.teaches

    if source.get("tags"):
        candidate["tags"] = list(source["tags"])

    if source.get("subsection"):
        candidate["subsection"] = source["subsection"]

    if source.get("rights"):
        candidate["rights"] = dict(source["rights"])

    assert "id" not in candidate  # structural guard, not just a comment
    assert "status" not in candidate  # structural guard: never asserts active/deprecated/erased

    return candidate
