"""make photo_url nullable

Revision ID: make_photo_url_nullable_001
Revises: 20261018_photo_url_text
Create Date: 2026-10-18 21:30:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20261018_make_photo_url_nullable"
down_revision = "20261018_photo_url_text"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Rend la colonne photo_url nullable."""
    op.alter_column(
        "vehicle_photos", "photo_url", existing_type=sa.Text(), nullable=True
    )


def downgrade() -> None:
    """Restaure la contrainte NOT NULL."""
    op.alter_column(
        "vehicle_photos", "photo_url", existing_type=sa.Text(), nullable=False
    )
