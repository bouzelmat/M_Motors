"""Add submitted_at column to dossiers table.

Revision ID: 20260922_add_submitted_at
Revises: 20260921_add_rejected_at
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260922_add_submitted_at"
down_revision: str | None = "20260921_add_rejected_at"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Ajout de la colonne submitted_at à la table dossiers."""
    op.add_column(
        "dossiers",
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_dossiers_submitted_at", "dossiers", ["submitted_at"])


def downgrade() -> None:
    """Suppression réversible de la colonne submitted_at."""
    op.drop_index("ix_dossiers_submitted_at", table_name="dossiers")
    op.drop_column("dossiers", "submitted_at")
