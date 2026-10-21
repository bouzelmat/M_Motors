bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/docker/docker-compose.staging.yml"
export MIGRATION_DATABASE_URL="postgresql+psycopg://staging_user:staging_password@localhost:5433/mmotors_staging_db"

cd "$ROOT_DIR"
docker compose -f "$COMPOSE_FILE" down -v --remove-orphans
docker compose -f "$COMPOSE_FILE" up -d postgres_staging
until docker compose -f "$COMPOSE_FILE" exec -T postgres_staging pg_isready -U staging_user -d mmotors_staging_db >/dev/null 2>&1; do
  sleep 1
done

docker compose -f "$COMPOSE_FILE" run --rm \
  -e DATABASE_URL="$MIGRATION_DATABASE_URL" \
  etl_staging_runner sh -c 'python scripts/mock_legacy.py && alembic upgrade head && python scripts/03_staging_pilot_runner.py'

