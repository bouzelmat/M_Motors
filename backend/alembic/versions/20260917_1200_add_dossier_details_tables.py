"""Add financing_plans, trade_ins, and dossier_services tables.

Revision ID: 20260917_add_dossier_details
Revises: 20260913_create_dossiers_table
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "20260917_add_dossier_details"
down_revision: str | None = "20260913_create_dossiers_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Création des tables annexes pour le financement, la reprise et les services."""
    op.create_table(
        "financing_plans",
        sa.Column(
            "dossier_id",
            UUID(as_uuid=True),
            sa.ForeignKey("dossiers.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("down_payment", sa.Numeric(10, 2), nullable=False),
        sa.Column("duration_months", sa.Integer(), nullable=False),
        sa.Column("monthly_payment", sa.Numeric(10, 2), nullable=False),
        sa.CheckConstraint("down_payment >= 0", name="ck_financing_plans_down_payment_positive"),
        sa.CheckConstraint("duration_months > 0", name="ck_financing_plans_duration_positive"),
        sa.CheckConstraint("monthly_payment >= 0", name="ck_financing_plans_monthly_payment_positive"),
    )

    op.create_table(
        "trade_ins",
        sa.Column(
            "dossier_id",
            UUID(as_uuid=True),
            sa.ForeignKey("dossiers.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("registration", sa.String(length=20), nullable=False),
        sa.Column("mileage", sa.Integer(), nullable=False),
        sa.Column("brand", sa.String(length=100), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("estimated_value", sa.Numeric(10, 2), nullable=True),
        sa.CheckConstraint("mileage >= 0", name="ck_trade_ins_mileage_positive"),
    )

    op.create_table(
        "dossier_services",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "dossier_id",
            UUID(as_uuid=True),
            sa.ForeignKey("dossiers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("service_code", sa.String(length=50), nullable=False),
    )
    op.create_index("ix_dossier_services_dossier_id", "dossier_services", ["dossier_id"])


def downgrade() -> None:
    """Suppression réversible des tables annexes."""
    op.drop_index("ix_dossier_services_dossier_id", table_name="dossier_services")
    op.drop_table("dossier_services")
    op.drop_table("trade_ins")
    op.drop_table("financing_plans")