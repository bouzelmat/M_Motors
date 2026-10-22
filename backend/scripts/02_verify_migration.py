"""CLI for post-migration verification."""

from __future__ import annotations

import argparse
import os

from migration.verification import run_verification


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit users/vehicles migration")
    parser.add_argument("--source-db", default="legacy.db")
    parser.add_argument(
        "--target-url", default=os.getenv("MIGRATION_DATABASE_URL"), required=False
    )
    parser.add_argument("--reports-dir", default="reports/migration")
    args = parser.parse_args()
    if not args.target_url:
        parser.error("--target-url ou MIGRATION_DATABASE_URL est obligatoire")
    return (
        0 if run_verification(args.source_db, args.target_url, args.reports_dir) else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
