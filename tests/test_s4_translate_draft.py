"""
Phase S S4' tests — assisted translation drafting.

Covers:
- prompt/response parsing (ttod_core.translation)
- find_active_translations() read-only scan
- build_translation_candidate() payload shape
- structural proof: neither ttod_core/translation.py nor cli.py's translate-draft
  command can allocate a canonical id or set status: active (grep-on-source, not
  just a runtime assertion — the runtime assertion could itself be wrong)
- CLI integration: fail-fast (same-language refusal, duplicate-active warning),
  proposal-only write path, live ttod.yml untouched

The local Ollama model is never called in this suite — `translate_quote` is
monkeypatched so the test suite stays deterministic and does not depend on a
running model server. The real end-to-end / pilot-rubric runs are recorded
separately in docs/DEV_PLAN/PHASE-S4-REPORT.md.
"""

from __future__ import annotations

import inspect
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml
from typer.testing import CliRunner

import cli
from cli import app
from ttod_core.translation import (
    TranslationDraft,
    TranslationError,
    build_translation_candidate,
    build_translation_prompt,
    find_active_translations,
    parse_translation_response,
)
import ttod_core.translation as translation_module

FIXTURE = Path(__file__).parent / "fixtures" / "q3_minimal_ttod.yml"


def _draft(model="test-model", text="Texto traducido.", teaches="Enseñanza traducida."):
    return TranslationDraft(
        model=model,
        text=text,
        teaches=teaches,
        raw_response=f"TEXT: {text}\nTEACHES: {teaches}",
        latency_s=0.01,
    )


class TestParseTranslationResponse(unittest.TestCase):
    def test_basic_two_line(self):
        raw = "TEXT: Hola mundo\nTEACHES: Aprende a saludar"
        parsed = parse_translation_response(raw, expect_teaches=True)
        self.assertEqual(parsed["text"], "Hola mundo")
        self.assertEqual(parsed["teaches"], "Aprende a saludar")

    def test_single_line_when_teaches_not_expected(self):
        raw = "TEXT: Solo texto"
        parsed = parse_translation_response(raw, expect_teaches=False)
        self.assertEqual(parsed["text"], "Solo texto")
        self.assertIsNone(parsed["teaches"])

    def test_strips_markdown_fences(self):
        raw = "```\nTEXT: Hola\nTEACHES: Ensena\n```"
        parsed = parse_translation_response(raw, expect_teaches=True)
        self.assertEqual(parsed["text"], "Hola")
        self.assertEqual(parsed["teaches"], "Ensena")

    def test_multiline_teaches_preserved(self):
        raw = "TEXT: Corto\nTEACHES: linea uno\nlinea dos"
        parsed = parse_translation_response(raw, expect_teaches=True)
        self.assertEqual(parsed["teaches"], "linea uno\nlinea dos")

    def test_missing_text_raises(self):
        with self.assertRaises(TranslationError):
            parse_translation_response("TEACHES: solo esto", expect_teaches=True)

    def test_missing_expected_teaches_raises(self):
        with self.assertRaises(TranslationError):
            parse_translation_response("TEXT: solo texto", expect_teaches=True)

    def test_empty_text_raises(self):
        with self.assertRaises(TranslationError):
            parse_translation_response("TEXT:   \nTEACHES: algo", expect_teaches=True)


class TestBuildTranslationPrompt(unittest.TestCase):
    def test_includes_both_languages_and_intent(self):
        prompt = build_translation_prompt("en", "es", "some text", "some teaches")
        self.assertIn("English", prompt)
        self.assertIn("Spanish", prompt)
        self.assertIn("Preserve ambiguity", prompt)
        self.assertIn("TEXT:", prompt)
        self.assertIn("TEACHES:", prompt)
        self.assertIn("some text", prompt)
        self.assertIn("some teaches", prompt)

    def test_omits_teaches_instruction_when_absent(self):
        prompt = build_translation_prompt("en", "es", "some text", None)
        self.assertNotIn("TEACHES:", prompt)


class TestFindActiveTranslations(unittest.TestCase):
    def test_finds_active_match(self):
        quotes = [
            {"id": "arch-001", "lang": "en"},
            {
                "id": "arch-002",
                "lang": "es",
                "status": "active",
                "relation_edges": [{"target": "arch-001", "relation_type": "translation_of"}],
            },
        ]
        self.assertEqual(find_active_translations(quotes, "arch-001", "es"), ["arch-002"])

    def test_ignores_deprecated_translation(self):
        quotes = [
            {"id": "arch-001", "lang": "en"},
            {
                "id": "arch-002",
                "lang": "es",
                "status": "deprecated",
                "relation_edges": [{"target": "arch-001", "relation_type": "translation_of"}],
            },
        ]
        self.assertEqual(find_active_translations(quotes, "arch-001", "es"), [])

    def test_ignores_different_target_lang(self):
        quotes = [
            {"id": "arch-001", "lang": "en"},
            {
                "id": "arch-003",
                "lang": "fr",
                "relation_edges": [{"target": "arch-001", "relation_type": "translation_of"}],
            },
        ]
        self.assertEqual(find_active_translations(quotes, "arch-001", "es"), [])

    def test_no_matches_returns_empty(self):
        quotes = [{"id": "arch-001", "lang": "en"}]
        self.assertEqual(find_active_translations(quotes, "arch-001", "es"), [])

    def test_status_defaults_to_active_when_absent(self):
        quotes = [
            {"id": "arch-001", "lang": "en"},
            {
                "id": "arch-002",
                "lang": "es",
                "relation_edges": [{"target": "arch-001", "relation_type": "translation_of"}],
            },
        ]
        self.assertEqual(find_active_translations(quotes, "arch-001", "es"), ["arch-002"])


class TestBuildTranslationCandidate(unittest.TestCase):
    def test_full_source_copies_optional_fields(self):
        source = {
            "id": "arch-001",
            "section": "architecture",
            "level": "advanced",
            "lang": "en",
            "tags": ["boundaries", "coupling"],
            "subsection": "seams",
            "rights": {"access": "public", "license": "CC-BY-NC-SA-4.0", "holder": "x"},
        }
        candidate = build_translation_candidate(source, "arch-001", "es", _draft())

        self.assertEqual(candidate["lang"], "es")
        self.assertEqual(candidate["section"], "architecture")
        self.assertEqual(candidate["level"], "advanced")
        self.assertEqual(candidate["origin"], "blackbox")
        self.assertEqual(candidate["tags"], ["boundaries", "coupling"])
        self.assertEqual(candidate["subsection"], "seams")
        self.assertEqual(candidate["rights"], source["rights"])
        self.assertEqual(
            candidate["relation_edges"],
            [{"target": "arch-001", "relation_type": "translation_of"}],
        )
        self.assertIn("test-model", candidate["authorship_assertion"])
        self.assertEqual(candidate["teaches"], "Enseñanza traducida.")

        # Rights must be a copy, not the same object (source stays untouched).
        candidate["rights"]["access"] = "restricted"
        self.assertEqual(source["rights"]["access"], "public")

    def test_minimal_source_omits_absent_optional_fields(self):
        source = {"id": "arch-001", "section": "architecture", "level": "advanced", "lang": "en"}
        draft = _draft(teaches=None)
        candidate = build_translation_candidate(source, "arch-001", "es", draft)

        self.assertNotIn("tags", candidate)
        self.assertNotIn("subsection", candidate)
        self.assertNotIn("rights", candidate)
        self.assertNotIn("teaches", candidate)

    def test_never_contains_id_or_status(self):
        """The one property this whole phase exists to guarantee."""
        sources = [
            {"id": "a-1", "section": "s", "level": "advanced", "lang": "en"},
            {
                "id": "a-2",
                "section": "s",
                "level": "beginner",
                "lang": "en",
                "status": "active",
                "tags": ["x"],
                "rights": {"access": "public"},
            },
        ]
        for source in sources:
            candidate = build_translation_candidate(source, source["id"], "es", _draft())
            self.assertNotIn("id", candidate)
            self.assertNotIn("status", candidate)


class TestStructuralNoCanonicalWritePath(unittest.TestCase):
    """
    Grep-on-source proof, not just a runtime assertion: the new code has no
    textual reference to any mechanism capable of allocating a canonical id
    or accepting a proposal into ttod.yml. If someone later "helpfully" wires
    translate-draft into the accept path, this test breaks immediately.
    """

    FORBIDDEN_SUBSTRINGS = (
        "accept_proposal",
        "accept_quote_direct",
        "_allocate_canonical_id",
        ".accept(",
        "TTODRepository(",
    )

    def test_translation_module_has_no_write_path(self):
        source = inspect.getsource(translation_module)
        for forbidden in self.FORBIDDEN_SUBSTRINGS:
            self.assertNotIn(
                forbidden, source, f"ttod_core/translation.py must never reference {forbidden!r}"
            )
        self.assertNotIn('"status": "active"', source)
        self.assertNotIn("'status': 'active'", source)
        # It must not import the repository's write-transaction machinery at all —
        # checked by actual bound names, not text, so a docstring mention of
        # ProposalStore (documentation only) cannot produce a false positive.
        self.assertFalse(hasattr(translation_module, "ProposalStore"))
        self.assertFalse(hasattr(translation_module, "TTODRepository"))
        self.assertFalse(hasattr(translation_module, "create_proposal"))

    def test_cli_translate_draft_command_has_no_accept_call(self):
        source = inspect.getsource(cli.translate_draft)
        for forbidden in self.FORBIDDEN_SUBSTRINGS:
            self.assertNotIn(
                forbidden, source, f"cli.py translate-draft must never reference {forbidden!r}"
            )
        # Only allowed repository interaction is the read-only `_repo(file).load()`.
        self.assertNotIn("repo.accept", source)

    def test_build_translation_candidate_asserts_structurally(self):
        """The function itself refuses to build a candidate carrying id/status."""
        source = inspect.getsource(build_translation_candidate)
        self.assertIn('assert "id" not in candidate', source)
        self.assertIn('assert "status" not in candidate', source)


class TestTranslateDraftCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.tmp = tempfile.TemporaryDirectory()
        self.ttod_path = Path(self.tmp.name) / "ttod-test.yml"
        shutil.copy(FIXTURE, self.ttod_path)
        self.proposals_dir = Path(self.tmp.name) / "proposals"

    def tearDown(self):
        self.tmp.cleanup()

    def _invoke(self, *args):
        with mock.patch.object(cli, "_proposal_store") as store_factory:
            from ttod_core.repository import ProposalStore

            store = ProposalStore(self.proposals_dir)
            store_factory.return_value = store
            result = self.runner.invoke(app, list(args))
        return result

    def test_same_language_refused_before_model_call(self):
        with mock.patch.object(cli, "translate_quote") as mocked:
            result = self._invoke(
                "translate-draft", "arch-001", "--to", "en", "--file", str(self.ttod_path)
            )
        self.assertEqual(result.exit_code, 2, result.output)
        self.assertIn("TRANSLATION_SAME_LANGUAGE", result.output)
        mocked.assert_not_called()

    def test_unknown_source_id_fails_before_model_call(self):
        with mock.patch.object(cli, "translate_quote") as mocked:
            result = self._invoke(
                "translate-draft", "nope-999", "--to", "es", "--file", str(self.ttod_path)
            )
        self.assertEqual(result.exit_code, 1, result.output)
        mocked.assert_not_called()

    def test_invalid_lang_code_rejected(self):
        with mock.patch.object(cli, "translate_quote") as mocked:
            result = self._invoke(
                "translate-draft", "arch-001", "--to", "ESP", "--file", str(self.ttod_path)
            )
        self.assertEqual(result.exit_code, 1, result.output)
        mocked.assert_not_called()

    def test_happy_path_writes_proposal_not_quote(self):
        original_bytes = self.ttod_path.read_bytes()
        with mock.patch.object(cli, "translate_quote", return_value=_draft()) as mocked:
            result = self._invoke(
                "translate-draft", "arch-001", "--to", "es", "--file", str(self.ttod_path)
            )
        self.assertEqual(result.exit_code, 0, result.output)
        mocked.assert_called_once()

        # Live/target ttod.yml byte-identical — never touched.
        self.assertEqual(self.ttod_path.read_bytes(), original_bytes)

        saved = list(self.proposals_dir.glob("*.json"))
        self.assertEqual(len(saved), 1)
        payload = json.loads(saved[0].read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "proposed")
        self.assertNotIn("id", payload["candidate_content"])
        self.assertNotIn("status", payload["candidate_content"])
        self.assertEqual(payload["candidate_content"]["origin"], "blackbox")
        self.assertEqual(payload["candidate_content"]["lang"], "es")
        self.assertEqual(
            payload["candidate_content"]["relation_edges"],
            [{"target": "arch-001", "relation_type": "translation_of"}],
        )
        self.assertIn("test-model", payload["generation_method"])
        self.assertIn("test-model", payload["candidate_content"]["authorship_assertion"])
        self.assertEqual(payload["human_review_activities"], [])
        # Unset accepted_quote_id must be omitted (absent), never JSON null —
        # proposal.schema.json types it as string.
        self.assertNotIn("accepted_quote_id", payload)

    def test_duplicate_active_warns_but_still_calls_model(self):
        root = yaml.safe_load(self.ttod_path.read_text(encoding="utf-8"))
        twin = dict(root["quotes"][0])
        twin["id"] = "arch-002"
        twin["lang"] = "es"
        twin["relation_edges"] = [{"target": "arch-001", "relation_type": "translation_of"}]
        twin.pop("content_digest", None)
        root["quotes"].append(twin)
        self.ttod_path.write_text(yaml.safe_dump(root, allow_unicode=True, sort_keys=False), encoding="utf-8")

        with mock.patch.object(cli, "translate_quote", return_value=_draft()) as mocked:
            result = self._invoke(
                "translate-draft", "arch-001", "--to", "es", "--file", str(self.ttod_path)
            )
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("TRANSLATION_DUPLICATE_ACTIVE", result.output)
        self.assertIn("WARNING", result.output)
        mocked.assert_called_once()  # warn, not hard-block

    def test_model_error_surfaces_cleanly(self):
        with mock.patch.object(cli, "translate_quote", side_effect=TranslationError("boom")):
            result = self._invoke(
                "translate-draft", "arch-001", "--to", "es", "--file", str(self.ttod_path)
            )
        self.assertEqual(result.exit_code, 1, result.output)
        self.assertIn("TRANSLATE-DRAFT FAILED", result.output)
        self.assertIn("boom", result.output)


if __name__ == "__main__":
    unittest.main()
