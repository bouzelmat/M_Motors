"""Create documents table.

Revision ID: 20260918_create_documents
Revises: 20260917_add_dossier_details
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "20260918_create_documents"
down_revision: str | None = "20260917_add_dossier_details"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Création de la table documents."""
    op.create_table(
        "documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "dossier_id",
            UUID(as_uuid=True),
            sa.ForeignKey("dossiers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("s3_key", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_documents_dossier_id", "documents", ["dossier_id"])
    op.create_index("ix_documents_status", "documents", ["status"])


def downgrade() -> None:
    """Suppression réversible de la table documents."""
    op.drop_index("ix_documents_status", table_name="documents")
    op.drop_index("ix_documents_dossier_id", table_name="documents")
    op.drop_table("documents")
