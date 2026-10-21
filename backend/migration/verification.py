"""Post-migration checks for users, vehicles and migration mappings."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from sqlalchemy import MetaData, Table, create_engine, text

from .pipeline import EMAIL_RE, ENERGY_MAP, VALID_CATALOG_TYPES, VALID_STATUSES


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def run_verification(source_db: str, target_url: str, reports_dir: str = "reports/migration") -> bool:
    report: dict[str, Any] = {"status": "OK", "checks": {}, "errors": []}
    source = sqlite3.connect(f"file:{Path(source_db).resolve()}?mode=ro", uri=True)
    source.row_factory = sqlite3.Row
    engine = create_engine(target_url, future=True)
    try:
        with engine.connect() as conn:
            metadata = MetaData()
            try:
                mapping = Table("migration_mapping", metadata, autoload_with=conn)
                users = Table("users", metadata, autoload_with=conn)
                vehicles = Table("vehicles", metadata, autoload_with=conn)
            except Exception as exc:
                report["status"] = "KO"
                report["errors"].append(f"Schéma cible incomplet: {exc}")
                _write(Path(reports_dir) / "verification_report.json", report)
                return False

            legacy_users = source.execute("SELECT * FROM old_users").fetchall()
            valid_users = [r for r in legacy_users if r["usr_mail"] and EMAIL_RE.fullmatch(str(r["usr_mail"]).strip().lower())]
            legacy_vehicles = source.execute("SELECT * FROM old_vehicles").fetchall()
            valid_vehicles = []
            for row in legacy_vehicles:
                try:
                    catalog = str(row["veh_catalog_type"] or "").strip().upper()
                    has_price = row["veh_price"] not in (None, "")
                    has_rent = row["veh_monthly_rent"] not in (None, "")
                    if row["veh_brand"] and row["veh_model"] and catalog in VALID_CATALOG_TYPES and ((catalog == "SALE" and has_price) or (catalog == "RENTAL" and has_rent)):
                        valid_vehicles.append(row)
                except Exception:
                    continue

            mapping_users = conn.execute(text("SELECT COUNT(*) FROM migration_mapping WHERE entity_type = 'USER'")).scalar_one()
            mapping_vehicles = conn.execute(text("SELECT COUNT(*) FROM migration_mapping WHERE entity_type = 'VEHICLE'")).scalar_one()
            pg_users = conn.execute(text("SELECT COUNT(*) FROM users")).scalar_one()
            pg_vehicles = conn.execute(text("SELECT COUNT(*) FROM vehicles")).scalar_one()
            report["checks"]["counts"] = {
                "users": {"legacy_valid": len(valid_users), "mapped": mapping_users, "postgres": pg_users, "match": len(valid_users) == mapping_users == pg_users},
                "vehicles": {"legacy_valid": len(valid_vehicles), "mapped": mapping_vehicles, "postgres": pg_vehicles, "match": len(valid_vehicles) == mapping_vehicles == pg_vehicles},
            }
            if not report["checks"]["counts"]["users"]["match"] or not report["checks"]["counts"]["vehicles"]["match"]:
                report["status"] = "KO"
                report["errors"].append("Divergence des volumes validés, mappés et importés")

            duplicates = conn.execute(text("SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1")).all()
            report["checks"]["duplicate_emails"] = {"count": len(duplicates), "details": [row[0] for row in duplicates]}
            if duplicates:
                report["status"] = "KO"
                report["errors"].append("Emails en doublon")

            orphan_mappings = conn.execute(text("""
                SELECT m.entity_type, m.legacy_id, m.target_uuid
                FROM migration_mapping m
                LEFT JOIN users u ON m.entity_type = 'USER' AND u.id = m.target_uuid
                LEFT JOIN vehicles v ON m.entity_type = 'VEHICLE' AND v.id = m.target_uuid
                WHERE (m.entity_type = 'USER' AND u.id IS NULL)
                   OR (m.entity_type = 'VEHICLE' AND v.id IS NULL)
            """)).mappings().all()
            report["checks"]["orphan_mappings"] = {"count": len(orphan_mappings), "details": [dict(row) for row in orphan_mappings]}
            if orphan_mappings:
                report["status"] = "KO"
                report["errors"].append("Mappings orphelins")

            invalid_vehicles = conn.execute(text("""
                SELECT id FROM vehicles
                WHERE brand IS NULL OR trim(brand) = ''
                   OR model IS NULL OR trim(model) = ''
                   OR (catalog_type = 'SALE' AND (price IS NULL OR price < 0))
                   OR (catalog_type = 'RENTAL' AND (monthly_rent IS NULL OR monthly_rent < 0))
                   OR energy_type NOT IN ('ESSENCE','DIESEL','ELECTRIQUE','HYBRIDE')
                   OR status NOT IN ('AVAILABLE','RENTED','SOLD','MAINTENANCE')
                   OR catalog_type NOT IN ('SALE','RENTAL')
            """)).all()
            report["checks"]["invalid_vehicles"] = {"count": len(invalid_vehicles), "details": [str(row[0]) for row in invalid_vehicles]}
            if invalid_vehicles:
                report["status"] = "KO"
                report["errors"].append("Véhicules non conformes")

            unmapped_users = conn.execute(text("""
                SELECT u.id FROM users u LEFT JOIN migration_mapping m
                ON m.entity_type = 'USER' AND m.target_uuid = u.id
                WHERE m.target_uuid IS NULL
            """)).all()
            unmapped_vehicles = conn.execute(text("""
                SELECT v.id FROM vehicles v LEFT JOIN migration_mapping m
                ON m.entity_type = 'VEHICLE' AND m.target_uuid = v.id
                WHERE m.target_uuid IS NULL
            """)).all()
            report["checks"]["unmapped_targets"] = {"users": len(unmapped_users), "vehicles": len(unmapped_vehicles)}
            if unmapped_users or unmapped_vehicles:
                report["status"] = "KO"
                report["errors"].append("Lignes cibles sans mapping")
    finally:
        source.close()
        engine.dispose()

    _write(Path(reports_dir) / "verification_report.json", report)
    return report["status"] == "OK"


__all__ = ["run_verification"]

