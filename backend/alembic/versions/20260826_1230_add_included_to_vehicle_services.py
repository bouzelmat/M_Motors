"""Add included flag to vehicle_services association."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# Identifiant unique de cette révision (ex: généré via `alembic revision`)
revision: str = "c9f8a7b6e5d4"
down_revision: Union[str, None] = "8d0683a8ce93"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the included flag to vehicle_services."""
    op.add_column(
        "vehicle_services",
        sa.Column(
            "included",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    """Remove the included flag from vehicle_services."""
    op.drop_column("vehicle_services", "included")
