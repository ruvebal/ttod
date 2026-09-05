"""
Q3 repository tests — rollback, concurrency, accept transaction.

All tests use disposable copies under tests/fixtures or tempfile; never live ttod.yml.
"""

from __future__ import annotations

import shutil
import tempfile
import threading
import unittest
from pathlib import Path

from ttod_core.proposals import create_proposal
from ttod_core.repository import RepositoryError, TransactionHooks, TTODRepository

FIXTURE = Path(__file__).parent / "fixtures" / "q3_minimal_ttod.yml"

CANDIDATE = {
    "text": "Boundaries are where systems learn their shape.",
    "section": "architecture",
    "level": "advanced",
    "lang": "en",
    "origin": "human",
    "tags": ["boundaries"],
}


def _copy_fixture(tmp_dir: Path) -> Path:
    target = tmp_dir / "ttod-test.yml"
    shutil.copy(FIXTURE, target)
    return target


class TestRepositoryAccept(unittest.TestCase):
    """Successful accept updates quote + derived meta atomically."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = _copy_fixture(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_accept_updates_quote_and_meta(self):
        repo = TTODRepository(self.path)
        result = repo.accept_quote_direct(CANDIDATE, "reviewer-human-001")
        self.assertEqual(result.quote_id, "arch-002")

        root = repo.load()
        self.assertEqual(root["meta"]["total_quotes"], 2)
        self.assertEqual(root["meta"]["last_id_by_section"]["arch"], 2)
        ids = [q["id"] for q in root["quotes"]]
        self.assertIn("arch-002", ids)

    def test_unknown_tags_rejected(self):
        repo = TTODRepository(self.path)
        bad = {**CANDIDATE, "tags": ["nonexistent-tag-xyz"]}
        with self.assertRaises(RepositoryError) as ctx:
            repo.accept_quote_direct(bad, "reviewer-human-001")
        self.assertIn("unknown tags", str(ctx.exception).lower())

    def test_proposal_accept_resumable_on_validation_failure(self):
        """Pre-lock validation failure leaves file and proposal state clean."""
        repo = TTODRepository(self.path)
        proposal = create_proposal(
            candidate_content={**CANDIDATE, "tags": ["bad-tag"]},
            proposer_kind="human",
            proposer_id="p1",
            generation_method="test",
        )
        original = repo.read_bytes()
        with self.assertRaises(RepositoryError):
            repo.accept_proposal(proposal, "reviewer-1")
        self.assertEqual(repo.read_bytes(), original)
        self.assertEqual(proposal.status.value, "proposed")


class TestRepositoryRollback(unittest.TestCase):
    """Induced failures leave target byte-identical."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = _copy_fixture(Path(self.tmp.name))
        self.original_bytes = self.path.read_bytes()

    def tearDown(self):
        self.tmp.cleanup()

    def _assert_unchanged(self):
        self.assertEqual(self.path.read_bytes(), self.original_bytes)

    def test_rollback_after_lock_injection(self):
        hooks = TransactionHooks(fail_after_lock=True)
        repo = TTODRepository(self.path, hooks=hooks)
        with self.assertRaises(RepositoryError):
            repo.accept_quote_direct(CANDIDATE, "reviewer-1")
        self._assert_unchanged()

    def test_rollback_after_temp_write_injection(self):
        hooks = TransactionHooks(fail_after_temp_write=True)
        repo = TTODRepository(self.path, hooks=hooks)
        with self.assertRaises(RepositoryError):
            repo.accept_quote_direct(CANDIDATE, "reviewer-1")
        self._assert_unchanged()

    def test_rollback_before_rename_injection(self):
        hooks = TransactionHooks(fail_before_rename=True)
        repo = TTODRepository(self.path, hooks=hooks)
        with self.assertRaises(RepositoryError):
            repo.accept_quote_direct(CANDIDATE, "reviewer-1")
        self._assert_unchanged()

    def test_no_orphan_id_on_rollback(self):
        hooks = TransactionHooks(fail_before_rename=True)
        repo = TTODRepository(self.path, hooks=hooks)
        with self.assertRaises(RepositoryError):
            repo.accept_quote_direct(CANDIDATE, "reviewer-1")
        root = repo.load()
        self.assertEqual(len(root["quotes"]), 1)
        self.assertEqual(root["meta"]["total_quotes"], 1)


class TestRepositoryConcurrency(unittest.TestCase):
    """Two acceptors serialize and receive distinct IDs."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = _copy_fixture(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_two_acceptors_distinct_ids(self):
        barrier = threading.Barrier(2)
        results: list[str] = []
        errors: list[Exception] = []

        def accept_worker(suffix: str):
            try:
                barrier.wait(timeout=5)
                repo = TTODRepository(self.path)
                candidate = {**CANDIDATE, "text": f"Quote {suffix}."}
                out = repo.accept_quote_direct(candidate, f"reviewer-{suffix}")
                results.append(out.quote_id)
            except Exception as exc:
                errors.append(exc)

        t1 = threading.Thread(target=accept_worker, args=("a",))
        t2 = threading.Thread(target=accept_worker, args=("b",))
        t1.start()
        t2.start()
        t1.join(timeout=30)
        t2.join(timeout=30)

        self.assertEqual(errors, [], f"unexpected errors: {errors}")
        self.assertEqual(len(results), 2)
        self.assertNotEqual(results[0], results[1])
        self.assertEqual(set(results), {"arch-002", "arch-003"})

        root = TTODRepository(self.path).load()
        self.assertEqual(root["meta"]["total_quotes"], 3)
        self.assertEqual(root["meta"]["last_id_by_section"]["arch"], 3)


class TestStatsCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = _copy_fixture(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_stats_check_clean_on_fresh_fixture(self):
        result = TTODRepository(self.path).stats_check()
        self.assertTrue(result.is_clean)

    def test_stats_check_detects_drift(self):
        root = TTODRepository(self.path).load()
        root["meta"]["total_quotes"] = 999
        self.path.write_text(
            __import__("yaml").dump(root, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )
        result = TTODRepository(self.path).stats_check()
        self.assertFalse(result.is_clean)
        self.assertTrue(any(d.field == "meta.total_quotes" for d in result.drifts))


if __name__ == "__main__":
    unittest.main()
