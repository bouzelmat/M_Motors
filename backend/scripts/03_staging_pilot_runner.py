"""Run dry-run, execute, audit and replay against an isolated staging DB."""

from __future__ import annotations

import json
import os
from pathlib import Path

from migration.pipeline import run_etl
from migration.verification import run_verification


def main() -> int:
    source_db = os.getenv("LEGACY_DB_PATH", "/app/legacy.db")
    target_url = os.environ["MIGRATION_DATABASE_URL"]
    reports_dir = os.getenv("REPORTS_DIR", "/app/reports/migration")
    mapping_scope = os.getenv("MAPPING_SCOPE", "us603-users-vehicles")
    summary: dict[str, object] = {"steps": [], "final_status": "FAILED"}
    try:
        dry = run_etl(source_db, target_url, batch_size=2, dry_run=True, reports_dir=reports_dir, mapping_scope=mapping_scope)
        summary["steps"].append({"step": "dry_run", "status": "SUCCESS", "stats": dry.stats})
        first = run_etl(source_db, target_url, batch_size=2, dry_run=False, reports_dir=reports_dir, mapping_scope=mapping_scope)
        summary["steps"].append({"step": "first_execute", "status": "SUCCESS", "stats": first.stats})
        if not run_verification(source_db, target_url, reports_dir):
            raise RuntimeError("Audit après première passe: KO")
        summary["steps"].append({"step": "first_audit", "status": "SUCCESS"})
        second = run_etl(source_db, target_url, batch_size=2, dry_run=False, reports_dir=reports_dir, mapping_scope=mapping_scope)
        summary["steps"].append({"step": "second_execute", "status": "SUCCESS", "stats": second.stats})
        if not run_verification(source_db, target_url, reports_dir):
            raise RuntimeError("Audit après seconde passe: KO")
        summary["steps"].append({"step": "second_audit", "status": "SUCCESS"})
        summary["final_status"] = "SUCCESS_FLUX_VALIDE"
    except Exception as exc:
        summary["error_details"] = str(exc)
    Path(reports_dir).mkdir(parents=True, exist_ok=True)
    Path(reports_dir, "staging_pilot_synthesis.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
    return 0 if summary["final_status"] == "SUCCESS_FLUX_VALIDE" else 1


if __name__ == "__main__":
    raise SystemExit(main())

