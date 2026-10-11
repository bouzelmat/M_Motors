"""Add decision and requested-document fields to dossiers."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "20261006_dossier_fields"
down_revision: str | None = "20260922_add_submitted_at"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add fields required to record dossier decisions and requested documents."""
    op.add_column("dossiers", sa.Column("comment", sa.Text(), nullable=True))
    op.add_column("dossiers", sa.Column("rejection_reason", sa.Text(), nullable=True))
    op.add_column(
        "dossiers",
        sa.Column("requested_document_types", sa.ARRAY(sa.String()), nullable=True),
    )
    op.add_column(
        "dossiers",
        sa.Column("validated_by_admin_id", UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "dossiers",
        sa.Column("rejected_by_admin_id", UUID(as_uuid=True), nullable=True),
    )
    op.create_index(
        "ix_dossiers_validated_by_admin_id",
        "dossiers",
        ["validated_by_admin_id"],
    )
    op.create_index(
        "ix_dossiers_rejected_by_admin_id",
        "dossiers",
        ["rejected_by_admin_id"],
    )


def downgrade() -> None:
    """Remove the decision and requested-document fields."""
    op.drop_index("ix_dossiers_rejected_by_admin_id", table_name="dossiers")
    op.drop_index("ix_dossiers_validated_by_admin_id", table_name="dossiers")
    op.drop_column("dossiers", "rejected_by_admin_id")
    op.drop_column("dossiers", "validated_by_admin_id")
    op.drop_column("dossiers", "requested_document_types")
    op.drop_column("dossiers", "rejection_reason")
    op.drop_column("dossiers", "comment")
