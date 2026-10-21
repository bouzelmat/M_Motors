"""PostgreSQL integration tests for the migration pipeline.

Set MIGRATION_TEST_DATABASE_URL to run these tests against a dedicated database
already initialized with ``alembic upgrade head``. They are skipped otherwise so
ordinary application tests never mutate their database.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from scripts.mock_legacy import init_legacy_db
from src.migration.pipeline import run_etl


TARGET_URL = os.getenv("MIGRATION_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not TARGET_URL, reason="MIGRATION_TEST_DATABASE_URL is required")


def _reset_target() -> None:
    engine = create_engine(TARGET_URL)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE migration_mapping, users, vehicles CASCADE"))
    engine.dispose()


def test_execute_is_idempotent_and_rejects_invalid_rental(tmp_path: Path) -> None:
    _reset_target()
    source = init_legacy_db(tmp_path / "legacy.db")
    first = run_etl(str(source), TARGET_URL, batch_size=2, dry_run=False, reports_dir=str(tmp_path / "reports"))
    second = run_etl(str(source), TARGET_URL, batch_size=2, dry_run=False, reports_dir=str(tmp_path / "reports"))

    assert first.stats["vehicles"]["rejected"] >= 2  # missing brand + RENTAL without rent
    assert first.stats["vehicles"]["accepted"] == second.stats["vehicles"]["accepted"]
    assert first.stats["users"]["accepted"] == second.stats["users"]["accepted"]
    assert any("monthly_rent obligatoire" in item["reason"] for item in first.rejected_records)

    engine = create_engine(TARGET_URL)
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM users")).scalar_one() == first.stats["users"]["accepted"]
        assert conn.execute(text("SELECT COUNT(*) FROM vehicles")).scalar_one() == first.stats["vehicles"]["accepted"]
        assert conn.execute(text("SELECT monthly_rent FROM vehicles WHERE catalog_type = 'RENTAL'")).scalar_one() == 699
    engine.dispose()


def test_dry_run_leaves_no_rows_or_mappings(tmp_path: Path) -> None:
    _reset_target()
    source = init_legacy_db(tmp_path / "legacy.db")
    run_etl(str(source), TARGET_URL, batch_size=2, dry_run=True, reports_dir=str(tmp_path / "reports"))

    engine = create_engine(TARGET_URL)
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM migration_mapping")).scalar_one() == 0
        assert conn.execute(text("SELECT COUNT(*) FROM users")).scalar_one() == 0
        assert conn.execute(text("SELECT COUNT(*) FROM vehicles")).scalar_one() == 0
    engine.dispose()

