"""Generate the read-only SQLite fixture used by migration tests."""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent.parent / "legacy.db"
FIXED_DATE = "2026-01-15T10:00:00+00:00"
BCRYPT_HASH = "$2b$12$eImiTXuWVxfM37uY4JANjO5E/w929k1N3/19dG3g8k5R6lG"


def init_legacy_db(db_file: str | Path = DB_FILE) -> Path:
    path = Path(db_file)
    if path.exists():
        path.unlink()
    connection = sqlite3.connect(path)
    try:
        cursor = connection.cursor()
        cursor.executescript("""
            CREATE TABLE old_users (
                usr_id INTEGER PRIMARY KEY,
                usr_mail TEXT UNIQUE,
                usr_pwd TEXT NOT NULL,
                usr_firstname TEXT,
                usr_lastname TEXT,
                usr_role TEXT DEFAULT 'CLIENT',
                usr_active INTEGER DEFAULT 1,
                usr_created_at TEXT
            );
            CREATE TABLE old_vehicles (
                veh_id INTEGER PRIMARY KEY,
                veh_brand TEXT,
                veh_model TEXT,
                veh_year INTEGER NOT NULL,
                veh_price REAL,
                veh_monthly_rent REAL,
                veh_kms INTEGER,
                veh_energy TEXT,
                veh_status TEXT,
                veh_catalog_type TEXT NOT NULL,
                veh_desc TEXT,
                veh_created_at TEXT
            );
            """)
        cursor.executemany(
            """INSERT INTO old_users
            (usr_id, usr_mail, usr_pwd, usr_firstname, usr_lastname,
             usr_role, usr_active, usr_created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    1,
                    "jean.dupont@email.com",
                    BCRYPT_HASH,
                    "Jean",
                    "DUPONT",
                    "CLIENT",
                    1,
                    FIXED_DATE,
                ),
                (
                    2,
                    "marie.curie@email.com",
                    BCRYPT_HASH,
                    "Marie",
                    "CURIE",
                    "ADMIN",
                    1,
                    FIXED_DATE,
                ),
                (
                    3,
                    "invalide-email-sans-at",
                    BCRYPT_HASH,
                    "John",
                    "DOE",
                    "CLIENT",
                    1,
                    FIXED_DATE,
                ),
                (
                    4,
                    "pierre.martin@email.com",
                    "not-a-bcrypt-hash",
                    None,
                    "MARTIN",
                    "CLIENT",
                    1,
                    FIXED_DATE,
                ),
            ],
        )
        cursor.executemany(
            """INSERT INTO old_vehicles
            (veh_id, veh_brand, veh_model, veh_year, veh_price, veh_monthly_rent,
             veh_kms, veh_energy, veh_status, veh_catalog_type, veh_desc, veh_created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    1,
                    "Peugeot",
                    "208",
                    2021,
                    15000.0,
                    None,
                    35000,
                    "GASOLINE",
                    "AVAILABLE",
                    "SALE",
                    "Super état.",
                    FIXED_DATE,
                ),
                (
                    2,
                    "Tesla",
                    "Model 3",
                    2022,
                    None,
                    699.0,
                    12000,
                    "ELECTRIC",
                    "AVAILABLE",
                    "RENTAL",
                    "Location longue durée.",
                    FIXED_DATE,
                ),
                (
                    3,
                    "Renault",
                    "Clio",
                    2018,
                    9500.0,
                    None,
                    85000,
                    "DIESEL",
                    "SOLD",
                    "SALE",
                    "Ancienne voiture.",
                    FIXED_DATE,
                ),
                (
                    4,
                    None,
                    "Inconnu",
                    2020,
                    10000.0,
                    None,
                    50000,
                    "GASOLINE",
                    "AVAILABLE",
                    "SALE",
                    "Sans marque.",
                    FIXED_DATE,
                ),
                (
                    5,
                    "BMW",
                    "X1",
                    2023,
                    None,
                    None,
                    10000,
                    "HYBRID",
                    "AVAILABLE",
                    "RENTAL",
                    "Location sans loyer : rejet attendu.",
                    FIXED_DATE,
                ),
            ],
        )
        connection.commit()
    finally:
        connection.close()
    return path


if __name__ == "__main__":
    print(f"Base legacy générée : {init_legacy_db()}")
