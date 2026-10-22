"""Create the technical mapping table used by the legacy migration."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "20261018_migration_mapping"
down_revision: str | None = "20261018_make_photo_url_nullable"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "migration_mapping",
        sa.Column("entity_type", sa.String(length=32), nullable=False),
        sa.Column("legacy_id", sa.String(length=255), nullable=False),
        sa.Column("target_uuid", UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("entity_type", "legacy_id"),
        sa.UniqueConstraint("target_uuid", name="uq_migration_mapping_target_uuid"),
    )
    op.create_check_constraint(
        "ck_migration_mapping_entity_type",
        "migration_mapping",
        "entity_type IN ('USER', 'VEHICLE')",
    )


def downgrade() -> None:
    op.drop_table("migration_mapping")