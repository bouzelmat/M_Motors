"""Core SQLAlchemy migration pipeline for legacy users and vehicles.

The module deliberately uses SQLAlchemy Core with the synchronous psycopg driver.
The legacy database is read-only; target writes are protected by one transaction.
"""

from __future__ import annotations

import json
import logging
import re
import sqlite3
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from sqlalchemy import MetaData, Table, create_engine, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

EMAIL_RE = re.compile(r"^[\w.\-+]+@[\w.\-]+\.\w+$")
BCRYPT_RE = re.compile(r"^\$2[aby]?\$\d{2}\$[./A-Za-z0-9]{53}$")
ENERGY_MAP = {
    "GASOLINE": "ESSENCE",
    "PETROL": "ESSENCE",
    "ESSENCE": "ESSENCE",
    "DIESEL": "DIESEL",
    "ELECTRIC": "ELECTRIQUE",
    "ELECTRIQUE": "ELECTRIQUE",
    "HYBRID": "HYBRIDE",
    "HYBRIDE": "HYBRIDE",
}
VALID_STATUSES = {"AVAILABLE", "RENTED", "SOLD", "MAINTENANCE"}
VALID_CATALOG_TYPES = {"SALE", "RENTAL"}


@dataclass
class MigrationResult:
    dry_run: bool
    batch_size: int
    stats: dict[str, dict[str, int]]
    rejected_records: list[dict[str, Any]]
    errors: list[str]


class MigrationError(RuntimeError):
    """Raised for an unsafe or structurally invalid migration."""


def _utc_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        raw = str(value).strip().replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(raw)
        except ValueError as exc:
            raise ValueError(f"date invalide: {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _bool_value(value: Any, default: bool = True) -> bool:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _decimal(value: Any, field: str, *, required: bool = False) -> Decimal | None:
    if value in (None, ""):
        if required:
            raise ValueError(f"{field} obligatoire")
        return None
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field} non numérique: {value!r}") from exc
    if not result.is_finite() or result < 0:
        raise ValueError(f"{field} doit être un nombre fini positif ou nul")
    return result


def _normalise_email(value: Any) -> str:
    email = str(value or "").strip().lower()
    if not email or not EMAIL_RE.fullmatch(email):
        raise ValueError("Email absent ou invalide")
    return email


def _normalise_enum(
    value: Any, field: str, valid: set[str], default: str | None = None
) -> str:
    normalised = str(value or default or "").strip().upper()
    if normalised not in valid:
        raise ValueError(f"{field} invalide: {value!r}")
    return normalised


def _energy(value: Any) -> str:
    key = str(value or "").strip().upper()
    try:
        return ENERGY_MAP[key]
    except KeyError as exc:
        raise ValueError(f"energy_type invalide: {value!r}") from exc


def _reject(
    rejected: list[dict[str, Any]],
    entity: str,
    legacy_id: Any,
    reason: str,
    data: dict[str, Any],
) -> None:
    rejected.append(
        {
            "entity": entity,
            "legacy_id": str(legacy_id),
            "reason": reason,
            "data": data,
        }
    )


def _table_map(conn: Connection) -> Table:
    metadata = MetaData()
    return Table("migration_mapping", metadata, autoload_with=conn)


def ensure_mapping_table(conn: Connection) -> Table:
    """Fail closed if Alembic has not created the technical table."""
    try:
        return _table_map(conn)
    except (SQLAlchemyError, RuntimeError) as exc:
        raise MigrationError(
            "La table migration_mapping est absente ou inaccessible"
        ) from exc


def get_or_create_uuid(
    conn: Connection, mapping: Table, entity_type: str, legacy_id: Any
) -> tuple[str, bool]:
    """Return the stable target UUID and whether a mapping was created."""
    if entity_type not in {"USER", "VEHICLE"}:
        raise MigrationError(f"entity_type interdit: {entity_type}")
    key = str(legacy_id)
    row = conn.execute(
        select(mapping.c.target_uuid).where(
            mapping.c.entity_type == entity_type,
            mapping.c.legacy_id == key,
        )
    ).first()
    if row:
        return str(row.target_uuid), False

    target_uuid = str(uuid.uuid4())
    stmt = (
        pg_insert(mapping)
        .values(
            entity_type=entity_type,
            legacy_id=key,
            target_uuid=target_uuid,
        )
        .on_conflict_do_nothing(index_elements=["entity_type", "legacy_id"])
        .returning(mapping.c.target_uuid)
    )
    inserted = conn.execute(stmt).first()
    if inserted:
        return str(inserted.target_uuid), True
    row = conn.execute(
        select(mapping.c.target_uuid).where(
            mapping.c.entity_type == entity_type,
            mapping.c.legacy_id == key,
        )
    ).one()
    return str(row.target_uuid), False


def _validate_target_tables(conn: Connection) -> tuple[Table, Table, Table]:
    metadata = MetaData()
    try:
        users = Table("users", metadata, autoload_with=conn)
        vehicles = Table("vehicles", metadata, autoload_with=conn)
        mapping = ensure_mapping_table(conn)
    except (SQLAlchemyError, RuntimeError) as exc:
        raise MigrationError(
            "Le schéma cible users/vehicles/migration_mapping est incomplet"
        ) from exc
    return users, vehicles, mapping


def _write_report(reports_dir: Path, name: str, payload: Any) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / name).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )


def _upsert_user(conn: Connection, table: Table, values: dict[str, Any]) -> str:
    existing = conn.execute(
        select(table.c.id).where(table.c.email == values["email"])
    ).first()
    if existing and str(existing.id) != str(values["id"]):
        raise MigrationError(
            f"Email {values['email']} déjà lié à un UUID différent ({existing.id} != {values['id']})"
        )
    stmt = pg_insert(table).values(values)
    stmt = stmt.on_conflict_do_update(
        index_elements=["email"],
        set_={
            "hashed_password": stmt.excluded.hashed_password,
            "first_name": stmt.excluded.first_name,
            "last_name": stmt.excluded.last_name,
            "role": stmt.excluded.role,
            "is_active": stmt.excluded.is_active,
        },
    )
    conn.execute(stmt)
    return "updated" if existing else "inserted"


def _upsert_vehicle(conn: Connection, table: Table, values: dict[str, Any]) -> str:
    existing = conn.execute(
        select(table.c.id).where(table.c.id == values["id"])
    ).first()
    stmt = pg_insert(table).values(values)
    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={
            "brand": stmt.excluded.brand,
            "model": stmt.excluded.model,
            "year": stmt.excluded.year,
            "price": stmt.excluded.price,
            "mileage": stmt.excluded.mileage,
            "energy_type": stmt.excluded.energy_type,
            "status": stmt.excluded.status,
            "catalog_type": stmt.excluded.catalog_type,
            "monthly_rent": stmt.excluded.monthly_rent,
            "description": stmt.excluded.description,
        },
    )
    conn.execute(stmt)
    return "updated" if existing else "inserted"


def run_etl(
    source_db: str = "legacy.db",
    target_url: str | None = None,
    batch_size: int = 1000,
    dry_run: bool = True,
    reports_dir: str = "reports/migration",
    mapping_scope: str = "us603-users-vehicles",
) -> MigrationResult:
    if batch_size <= 0:
        raise ValueError("batch_size doit être strictement positif")
    if target_url is None:
        raise ValueError(
            "target_url doit être fourni explicitement pour éviter une écriture accidentelle"
        )

    reports_path = Path(reports_dir)
    started_at = datetime.now(timezone.utc)
    started_clock = time.monotonic()
    stats = {
        "users": {
            "extracted": 0,
            "accepted": 0,
            "inserted": 0,
            "updated": 0,
            "rejected": 0,
            "mapping_created": 0,
            "mapping_reused": 0,
        },
        "vehicles": {
            "extracted": 0,
            "accepted": 0,
            "inserted": 0,
            "updated": 0,
            "rejected": 0,
            "mapping_created": 0,
            "mapping_reused": 0,
        },
    }
    rejected: list[dict[str, Any]] = []
    errors: list[str] = []

    source = sqlite3.connect(f"file:{Path(source_db).resolve()}?mode=ro", uri=True)
    source.row_factory = sqlite3.Row
    engine: Engine = create_engine(target_url, future=True)
    try:
        with engine.begin() as conn:
            users, vehicles, mapping = _validate_target_tables(conn)
            user_cursor = source.execute(
                "SELECT usr_id, usr_mail, usr_pwd, usr_firstname, usr_lastname, usr_role, usr_active, usr_created_at FROM old_users"
            )
            while rows := user_cursor.fetchmany(batch_size):
                for row in rows:
                    stats["users"]["extracted"] += 1
                    try:
                        created_at = _utc_datetime(row["usr_created_at"])
                        if created_at is None:
                            raise ValueError("usr_created_at obligatoire")
                        password = str(row["usr_pwd"] or "")
                        is_active = _bool_value(row["usr_active"])
                        if not BCRYPT_RE.fullmatch(password):
                            is_active = False
                        values = {
                            "email": _normalise_email(row["usr_mail"]),
                            "hashed_password": password,
                            "first_name": str(row["usr_firstname"] or "Inconnu"),
                            "last_name": str(row["usr_lastname"] or "Inconnu"),
                            "role": str(row["usr_role"] or "CLIENT").strip().upper(),
                            "is_active": is_active,
                            "created_at": created_at,
                        }
                        target_id, created = get_or_create_uuid(
                            conn, mapping, "USER", row["usr_id"]
                        )
                        values["id"] = target_id
                        action = _upsert_user(conn, users, values)
                        stats["users"]["accepted"] += 1
                        stats["users"][action] += 1
                        stats["users"][
                            "mapping_created" if created else "mapping_reused"
                        ] += 1
                    except (ValueError, MigrationError, SQLAlchemyError) as exc:
                        stats["users"]["rejected"] += 1
                        _reject(rejected, "user", row["usr_id"], str(exc), dict(row))

            vehicle_cursor = source.execute(
                """SELECT veh_id, veh_brand, veh_model, veh_year, veh_price,
                   veh_monthly_rent, veh_kms, veh_energy, veh_status,
                   veh_catalog_type, veh_desc, veh_created_at
                   FROM old_vehicles"""
            )
            while rows := vehicle_cursor.fetchmany(batch_size):
                for row in rows:
                    stats["vehicles"]["extracted"] += 1
                    try:
                        catalog_type = _normalise_enum(
                            row["veh_catalog_type"], "catalog_type", VALID_CATALOG_TYPES
                        )
                        price = _decimal(
                            row["veh_price"], "price", required=catalog_type == "SALE"
                        )
                        monthly_rent = _decimal(
                            row["veh_monthly_rent"],
                            "monthly_rent",
                            required=catalog_type == "RENTAL",
                        )
                        if not row["veh_brand"] or not str(row["veh_brand"]).strip():
                            raise ValueError("brand obligatoire")
                        if not row["veh_model"] or not str(row["veh_model"]).strip():
                            raise ValueError("model obligatoire")
                        year = int(row["veh_year"])
                        mileage = int(row["veh_kms"] or 0)
                        if mileage < 0:
                            raise ValueError("mileage ne peut pas être négatif")
                        values = {
                            "brand": str(row["veh_brand"]).strip(),
                            "model": str(row["veh_model"]).strip(),
                            "year": year,
                            "price": price,
                            "mileage": mileage,
                            "energy_type": _energy(row["veh_energy"]),
                            "status": _normalise_enum(
                                row["veh_status"], "status", VALID_STATUSES, "AVAILABLE"
                            ),
                            "catalog_type": catalog_type,
                            "monthly_rent": monthly_rent,
                            "description": row["veh_desc"],
                        }
                        target_id, created = get_or_create_uuid(
                            conn, mapping, "VEHICLE", row["veh_id"]
                        )
                        values["id"] = target_id
                        action = _upsert_vehicle(conn, vehicles, values)
                        stats["vehicles"]["accepted"] += 1
                        stats["vehicles"][action] += 1
                        stats["vehicles"][
                            "mapping_created" if created else "mapping_reused"
                        ] += 1
                    except (ValueError, MigrationError, SQLAlchemyError) as exc:
                        stats["vehicles"]["rejected"] += 1
                        _reject(rejected, "vehicle", row["veh_id"], str(exc), dict(row))

            if dry_run:
                # engine.begin commits on exit; explicitly force rollback by raising a private sentinel.
                raise _DryRunRollback()
    except _DryRunRollback:
        logger.info("Dry-run terminé : transaction cible annulée")
    finally:
        source.close()
        engine.dispose()

    summary = {
        "run_started_at": started_at.isoformat(),
        "duration_seconds": round(time.monotonic() - started_clock, 3),
        "source_db": str(source_db),
        "mapping_scope": mapping_scope,
        "dry_run": dry_run,
        "batch_size": batch_size,
        "stats": stats,
        "rejected_count": len(rejected),
        "errors": errors,
    }
    _write_report(reports_path, "rejected_records.json", rejected)
    _write_report(reports_path, "migration_summary.json", summary)
    return MigrationResult(dry_run, batch_size, stats, rejected, errors)


class _DryRunRollback(Exception):
    """Internal control-flow exception used to rollback the target transaction."""


__all__ = ["MigrationError", "MigrationResult", "get_or_create_uuid", "run_etl"]
