from __future__ import annotations

import sqlite3

from scripts.mock_legacy import init_legacy_db


def test_fixture_contains_rental_success_and_rejection_cases(tmp_path):
    db_path = init_legacy_db(tmp_path / "legacy.db")
    connection = sqlite3.connect(db_path)
    try:
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(old_vehicles)")
        }
        assert "veh_catalog_type" in columns
        assert "veh_monthly_rent" in columns
        assert (
            connection.execute(
                "SELECT COUNT(*) FROM old_vehicles WHERE veh_catalog_type = 'RENTAL' AND veh_monthly_rent > 0"
            ).fetchone()[0]
            >= 1
        )
        assert (
            connection.execute(
                "SELECT COUNT(*) FROM old_vehicles WHERE veh_catalog_type = 'RENTAL' AND veh_monthly_rent IS NULL"
            ).fetchone()[0]
            >= 1
        )
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE name = 'old_dossiers'"
            ).fetchone()
            is None
        )
    finally:
        connection.close()
