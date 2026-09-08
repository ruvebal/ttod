"""Regression tests for the public-privacy watcher (report-steward harness)."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "agentic" / "report-steward" / "scripts" / "check_public_privacy.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_public_privacy", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PublicPrivacyWatcherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_module()

    def test_rejects_phase_id_on_public_surface(self) -> None:
        path = Path("/tmp/docs/public/assets/diagrams/x.html")
        hits = self.mod.findings(path, "R6 ships public/sw.js\n", [])
        self.assertTrue(any("phase identifier" in reason for _, reason in hits))

    def test_rejects_docker_internal_hostname(self) -> None:
        path = Path("/tmp/docs/public/page.md")
        hits = self.mod.findings(path, "via host.docker.internal\n", [])
        self.assertTrue(any("internal hostname" in reason for _, reason in hits))

    def test_rejects_empty_anchor_on_public_markup(self) -> None:
        path = Path("/tmp/docs/public/teaching/index.md")
        hits = self.mod.findings(path, '<a id="ref-garcia-2025"></a>Garcia\n', [])
        self.assertTrue(any("missing href" in reason for _, reason in hits))

    def test_allows_span_citation_anchor(self) -> None:
        path = Path("/tmp/docs/public/teaching/index.md")
        hits = self.mod.findings(path, '<span id="ref-garcia-2025"></span>Garcia\n', [])
        self.assertEqual(hits, [])

    def test_allows_repository_anchor_with_href(self) -> None:
        path = Path("/tmp/docs/public/assets/diagrams/x.html")
        line = (
            '<a class="semantic-passport-repository" id="focus-repository" '
            'href="https://github.com/ruvebal/ttod" target="_blank"></a>\n'
        )
        hits = self.mod.findings(path, line, [])
        self.assertEqual(hits, [])

    def test_phase_id_allowed_outside_public(self) -> None:
        path = Path("/tmp/docs/DEV_PLAN/INDEX.md")
        hits = self.mod.findings(path, "R6 remains student-owned\n", [])
        self.assertFalse(any("phase identifier" in reason for _, reason in hits))

    def test_cli_fails_on_fixture_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            public = root / "docs" / "public" / "assets" / "diagrams"
            public.mkdir(parents=True)
            (public / "bad.html").write_text(
                '<a id="focus-repository" target="_blank"></a>\nR6 note\n',
                encoding="utf-8",
            )
            old = sys.argv
            try:
                sys.argv = [
                    "check_public_privacy.py",
                    str(public),
                    "--root",
                    str(root),
                    "--quiet",
                ]
                exit_code = self.mod.main()
            finally:
                sys.argv = old
            self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
