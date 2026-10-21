"""CLI for the legacy users and vehicles migration."""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path

from src.migration.pipeline import run_etl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Migration legacy users/vehicles")
    parser.add_argument("--source-db", default="legacy.db", help="SQLite legacy database")
    parser.add_argument("--target-url", default=os.getenv("MIGRATION_DATABASE_URL"), help="postgresql+psycopg DSN")
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--execute", action="store_true", help="commit target writes; default is dry-run")
    parser.add_argument("--reports-dir", default="reports/migration")
    parser.add_argument("--mapping-scope", default="us603-users-vehicles")
    return parser


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = build_parser().parse_args()
    if not args.target_url:
        raise SystemExit("--target-url ou MIGRATION_DATABASE_URL est obligatoire")
    result = run_etl(
        source_db=args.source_db,
        target_url=args.target_url,
        batch_size=args.batch_size,
        dry_run=not args.execute,
        reports_dir=args.reports_dir,
        mapping_scope=args.mapping_scope,
    )
    print(json.dumps({
        "dry_run": result.dry_run,
        "stats": result.stats,
        "rejected_records": result.rejected_records,
        "errors": result.errors,
    }, indent=2, ensure_ascii=False, default=str))
    logging.info("Migration terminée: %s", result.stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

