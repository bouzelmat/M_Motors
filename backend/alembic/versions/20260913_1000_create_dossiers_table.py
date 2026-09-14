"""Create the dossiers table."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "20260913_create_dossiers_table"
down_revision: str | None = "20260910_vehicle_price_nullable"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the dossier persistence table and its indexes."""
    op.create_table(
        "dossiers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("vehicle_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "SUBMITTED",
                "VALIDATED",
                "REJECTED",
                "EXPIRED",
                native_enum=False,
                create_constraint=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "upload_started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_index("ix_dossiers_user_id", "dossiers", ["user_id"])
    op.create_index("ix_dossiers_vehicle_id", "dossiers", ["vehicle_id"])
    op.create_index("ix_dossiers_status", "dossiers", ["status"])


def downgrade() -> None:
    """Drop the dossier persistence table and its indexes."""
    op.drop_index("ix_dossiers_status", table_name="dossiers")
    op.drop_index("ix_dossiers_vehicle_id", table_name="dossiers")
    op.drop_index("ix_dossiers_user_id", table_name="dossiers")
    op.drop_table("dossiers")
