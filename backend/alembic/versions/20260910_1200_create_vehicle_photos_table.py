"""Create vehicle photos table."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260910_vehicle_photos"
down_revision: Union[str, None] = "c9f8a7b6e5d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vehicle_photos",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("vehicle_id", sa.UUID(), nullable=False),
        sa.Column("object_key", sa.String(length=500), nullable=False),
        sa.Column("photo_url", sa.String(length=1000), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("uploaded_by", sa.UUID(), nullable=False),
        sa.Column(
            "is_uploaded", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column(
            "is_primary", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("object_key"),
    )
    op.create_index("ix_vehicle_photos_vehicle_id", "vehicle_photos", ["vehicle_id"])


def downgrade() -> None:
    op.drop_index("ix_vehicle_photos_vehicle_id", table_name="vehicle_photos")
    op.drop_table("vehicle_photos")
