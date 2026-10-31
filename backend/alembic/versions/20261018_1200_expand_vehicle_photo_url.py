"""Expand vehicle photo URL column to support long presigned S3 URLs."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261018_photo_url_text"
down_revision: str | None = "20261009_expand_dossier_status"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Change vehicle_photos.photo_url from VARCHAR(1000) to PostgreSQL TEXT."""
    op.alter_column(
        "vehicle_photos",
        "photo_url",
        existing_type=sa.String(length=1000),
        type_=sa.Text(),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Restore the previous VARCHAR(1000) type."""
    op.alter_column(
        "vehicle_photos",
        "photo_url",
        existing_type=sa.Text(),
        type_=sa.String(length=1000),
        existing_nullable=False,
    )
