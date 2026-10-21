"""PostgreSQL integration tests for migration verification."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from scripts.mock_legacy import init_legacy_db
from src.migration.pipeline import run_etl
from src.migration.verification import run_verification


TARGET_URL = os.getenv("MIGRATION_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not TARGET_URL, reason="MIGRATION_TEST_DATABASE_URL is required")


def _reset_target() -> None:
    engine = create_engine(TARGET_URL)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE migration_mapping, users, vehicles CASCADE"))
    engine.dispose()


def test_verification_returns_ok_after_execute(tmp_path: Path) -> None:
    _reset_target()
    source = init_legacy_db(tmp_path / "legacy.db")
    run_etl(str(source), TARGET_URL, dry_run=False, reports_dir=str(tmp_path / "reports"))
    assert run_verification(str(source), TARGET_URL, str(tmp_path / "reports")) is True
    assert '"status": "OK"' in (tmp_path / "reports" / "verification_report.json").read_text()


def test_verification_detects_orphan_mapping(tmp_path: Path) -> None:
    _reset_target()
    source = init_legacy_db(tmp_path / "legacy.db")
    run_etl(str(source), TARGET_URL, dry_run=False, reports_dir=str(tmp_path / "reports"))
    engine = create_engine(TARGET_URL)
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM users"))
    engine.dispose()
    assert run_verification(str(source), TARGET_URL, str(tmp_path / "reports")) is False
