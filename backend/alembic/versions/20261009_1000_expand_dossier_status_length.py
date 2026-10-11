"""Allow the DOCUMENTS_PENDING dossier status."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261009_expand_dossier_status"
down_revision: str | None = "20261006_dossier_fields"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Expand the dossier status column for all supported status values."""
    op.alter_column(
        "dossiers",
        "status",
        existing_type=sa.String(length=9),
        type_=sa.String(length=32),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Restore the previous dossier status column size."""
    op.alter_column(
        "dossiers",
        "status",
        existing_type=sa.String(length=32),
        type_=sa.String(length=9),
        existing_nullable=False,
    )
