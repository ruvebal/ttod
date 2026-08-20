"""Phase Q6 migration and rollback tests."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from ttod_core.migration import migrate_root
from ttod_core.repository import RepositoryError, TTODRepository, TransactionHooks
from ttod_core.validation import TTODValidator

LIVE = Path(__file__).resolve().parent.parent / "ttod.yml"
PRE_Q6 = Path(__file__).resolve().parent.parent / "private" / "ttod.yml.pre-q6-backup"


def _pre_migration_source() -> Path:
    if PRE_Q6.exists():
        return PRE_Q6
    return LIVE


class TestMigrationCandidate(unittest.TestCase):
    def test_pre_migration_source_migrates_strict(self):
        root = yaml.safe_load(_pre_migration_source().read_text(encoding="utf-8"))
        migrated, _summary = migrate_root(root)
        result = TTODValidator(strict=True).validate_root(migrated)
        self.assertTrue(result.is_valid, [e.message for e in result.errors[:5]])


class TestMigrationRollback(unittest.TestCase):
    """Failure injection on pre-migration copy — source bytes must survive."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "ttod.yml"
        shutil.copy(_pre_migration_source(), self.path)
        self.original_bytes = self.path.read_bytes()

    def tearDown(self):
        self.tmp.cleanup()

    def _assert_unchanged(self):
        self.assertEqual(self.path.read_bytes(), self.original_bytes)

    def test_rollback_after_lock(self):
        repo = TTODRepository(self.path, hooks=TransactionHooks(fail_after_lock=True))
        with self.assertRaises(RepositoryError):
            repo.apply_v3_migration()
        self._assert_unchanged()

    def test_rollback_after_temp_write(self):
        repo = TTODRepository(self.path, hooks=TransactionHooks(fail_after_temp_write=True))
        with self.assertRaises(RepositoryError):
            repo.apply_v3_migration()
        self._assert_unchanged()

    def test_rollback_before_rename(self):
        repo = TTODRepository(self.path, hooks=TransactionHooks(fail_before_rename=True))
        with self.assertRaises(RepositoryError):
            repo.apply_v3_migration()
        self._assert_unchanged()

    def test_successful_migration_on_copy(self):
        repo = TTODRepository(self.path)
        summary = repo.apply_v3_migration()
        self.assertEqual(summary.quotes_total, 229)
        self.assertNotEqual(self.path.read_bytes(), self.original_bytes)
        result = repo.validate(strict=True)
        self.assertTrue(result.is_valid)


    def test_arch052_live_migrated_adversary(self):
        root = yaml.safe_load(LIVE.read_text(encoding="utf-8"))
        quote = next(q for q in root["quotes"] if q["id"] == "arch-052")
        from ttod_core.sensors.independence import check_evidence_admissibility
        from ttod_core.sensors.types import SELF_DERIVED_NOT_EVIDENCE

        blocked = check_evidence_admissibility("athanor_architecture", quote)
        self.assertFalse(blocked.passed)
        self.assertEqual(blocked.code, SELF_DERIVED_NOT_EVIDENCE)
        self.assertFalse(blocked.details["evidence_admissible"])

        pedagogical = check_evidence_admissibility("pedagogical", quote)
        self.assertTrue(pedagogical.passed)
        self.assertTrue(pedagogical.details["evidence_admissible"])


class TestLiveMigrated(unittest.TestCase):
    def test_live_file_is_strict_valid(self):
        result = TTODValidator(strict=True).validate_root(
            yaml.safe_load(LIVE.read_text(encoding="utf-8"))
        )
        self.assertTrue(result.is_valid)


if __name__ == "__main__":
    unittest.main()
