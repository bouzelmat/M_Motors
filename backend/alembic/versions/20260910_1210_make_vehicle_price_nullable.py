"""Allow rental vehicles to omit a sale price.

Revision ID: 20260910_vehicle_price_nullable
Revises: 20260910_vehicle_photos
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260910_vehicle_price_nullable"
down_revision: Union[str, None] = "20260910_vehicle_photos"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Allow ``price`` to be null for rental vehicles."""
    op.alter_column(
        "vehicles",
        "price",
        existing_type=sa.Numeric(precision=10, scale=2),
        nullable=True,
    )


def downgrade() -> None:
    """Restore the previous non-null sale price column."""
    op.alter_column(
        "vehicles",
        "price",
        existing_type=sa.Numeric(precision=10, scale=2),
        nullable=False,
    )
