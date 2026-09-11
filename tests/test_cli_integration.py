"""
Q3 CLI integration tests — wiring to Q2V/Q2E/repository.

Uses disposable fixture copies only.
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from typer.testing import CliRunner

from cli import app

FIXTURE = Path(__file__).parent / "fixtures" / "q3_minimal_ttod.yml"


class TestCLIIntegration(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "ttod-test.yml"
        shutil.copy(FIXTURE, self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_validate_json_on_fixture(self):
        result = self.runner.invoke(app, ["validate", "--json", "--file", str(self.path)])
        self.assertEqual(result.exit_code, 0, result.output)
        payload = json.loads(result.output)
        self.assertTrue(payload["is_valid"])

    def test_validate_strict_json(self):
        result = self.runner.invoke(
            app, ["validate", "--strict", "--json", "--file", str(self.path)]
        )
        self.assertEqual(result.exit_code, 0, result.output)

    def test_stats_check_clean(self):
        result = self.runner.invoke(app, ["stats", "--check", "--file", str(self.path)])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("OK", result.output)

    def test_add_requires_reviewer(self):
        result = self.runner.invoke(
            app,
            [
                "add",
                "--section",
                "architecture",
                "--level",
                "advanced",
                "--text",
                "CLI add test.",
                "--tags",
                "boundaries",
                "--file",
                str(self.path),
            ],
        )
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("reviewer", result.output.lower())

    def test_add_via_transaction(self):
        result = self.runner.invoke(
            app,
            [
                "add",
                "--section",
                "architecture",
                "--level",
                "advanced",
                "--text",
                "CLI add test.",
                "--tags",
                "boundaries",
                "--reviewer-id",
                "human-cli-001",
                "--file",
                str(self.path),
            ],
        )
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("arch-002", result.output)

    def test_snapshot_deterministic(self):
        out_a = Path(self.tmp.name) / "snap-a.json"
        out_b = Path(self.tmp.name) / "snap-b.json"
        r1 = self.runner.invoke(
            app, ["snapshot", "--output", str(out_a), "--file", str(self.path)]
        )
        r2 = self.runner.invoke(
            app, ["snapshot", "--output", str(out_b), "--file", str(self.path)]
        )
        self.assertEqual(r1.exit_code, 0, r1.output)
        self.assertEqual(r2.exit_code, 0, r2.output)
        self.assertEqual(out_a.read_bytes(), out_b.read_bytes())

    def test_erase_requires_authority(self):
        result = self.runner.invoke(
            app,
            ["erase", "arch-001", "--file", str(self.path)],
        )
        self.assertNotEqual(result.exit_code, 0)

    def test_stats_no_default_human_for_missing_origin(self):
        """Regression: stats must not default missing origin to human."""
        import yaml

        root = yaml.safe_load(self.path.read_text(encoding="utf-8"))
        root["quotes"].append(
            {
                "id": "arch-099",
                "schema_version": "3.0.0",
                "text": "No origin field.",
                "section": "architecture",
                "level": "beginner",
                "lang": "en",
            }
        )
        self.path.write_text(yaml.dump(root, allow_unicode=True), encoding="utf-8")
        result = self.runner.invoke(app, ["stats", "--file", str(self.path)])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("<missing>", result.output)
        self.assertNotIn("human: 2", result.output)

    def test_bridge_subtyper_registered(self):
        """
        F1 regression (2026-09-10, DevIAC Phase CH0 readiness): the `bridge`
        sub-typer was defined in `cli.py` but never registered via
        `app.add_typer(bridge_app, name="bridge")`, leaving `bridge quote-out`
        and `bridge proposal-in` unreachable from the CLI surface even though
        the underlying `TTODBridge` module worked. See
        deviac/docs/DEV_PLAN/PHASE-CH/PHASE-CH0-READINESS-REPORT.md § F1.

        This test would have failed against the pre-fix code with exit_code 2
        ('No such command bridge'). It fails now if the wiring is dropped again.
        """
        result = self.runner.invoke(app, ["bridge", "--help"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("quote-out", result.output)
        self.assertIn("proposal-in", result.output)
        # And the sub-commands must themselves be reachable (not just listed).
        for sub in ("quote-out", "proposal-in"):
            sub_result = self.runner.invoke(app, ["bridge", sub, "--help"])
            self.assertEqual(sub_result.exit_code, 0, sub_result.output)


if __name__ == "__main__":
    unittest.main()
