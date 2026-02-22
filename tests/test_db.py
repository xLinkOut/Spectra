"""Unit tests for the bookmark database."""

from pathlib import Path

import pytest

from prism.db import BookmarkDB


@pytest.fixture
def db(tmp_path: Path) -> BookmarkDB:
    return BookmarkDB(tmp_path / "test.db")


class TestSeenTransactions:
    """Transaction deduplication tests."""

    def test_unseen_returns_false(self, db: BookmarkDB) -> None:
        assert db.is_seen("tx-001") is False

    def test_mark_seen_then_is_seen(self, db: BookmarkDB) -> None:
        db.mark_seen("tx-001")
        assert db.is_seen("tx-001") is True

    def test_mark_seen_idempotent(self, db: BookmarkDB) -> None:
        db.mark_seen("tx-001")
        db.mark_seen("tx-001")  # Should not raise
        assert db.is_seen("tx-001") is True

    def test_mark_seen_batch(self, db: BookmarkDB) -> None:
        db.mark_seen_batch(["tx-001", "tx-002", "tx-003"])
        assert db.is_seen("tx-001") is True
        assert db.is_seen("tx-002") is True
        assert db.is_seen("tx-003") is True
        assert db.is_seen("tx-999") is False

    def test_count(self, db: BookmarkDB) -> None:
        assert db.count() == 0
        db.mark_seen_batch(["a", "b", "c"])
        assert db.count() == 3


class TestContextManager:
    def test_context_manager(self, tmp_path: Path) -> None:
        with BookmarkDB(tmp_path / "ctx.db") as db:
            db.mark_seen("tx-001")
            assert db.is_seen("tx-001") is True
