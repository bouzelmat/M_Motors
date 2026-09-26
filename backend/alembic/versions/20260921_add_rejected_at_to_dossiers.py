"""Add rejected_at column to dossiers table.

Revision ID: 20260921_add_rejected_at
Revises: 20260918_create_documents
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260921_add_rejected_at"
down_revision: str | None = "20260918_create_documents"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Ajout de la colonne rejected_at à la table dossiers."""
    op.add_column(
        "dossiers",
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_dossiers_rejected_at", "dossiers", ["rejected_at"])


def downgrade() -> None:
    """Suppression réversible de la colonne rejected_at."""
    op.drop_index("ix_dossiers_rejected_at", table_name="dossiers")
    op.drop_column("dossiers", "rejected_at")
