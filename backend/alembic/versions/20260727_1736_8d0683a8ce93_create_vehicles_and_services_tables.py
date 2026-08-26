"""create vehicles and services tables

Revision ID: 8d0683a8ce93
Revises: 001
Create Date: 2026-07-27 17:36:04.148052

"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM, UUID

from alembic import op

# Identifiants uniques de révision Alembic pour votre projet
revision: str = "8d0683a8ce93"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Création sécurisée des enums manquants
    ENUM(
        "INSURANCE",
        "ASSISTANCE",
        "MAINTENANCE",
        "INSPECTION",
        name="servicecategory",
    ).create(op.get_bind(), checkfirst=True)

    ENUM(
        "RENTAL",
        "SALE",
        name="catalogtype",
    ).create(op.get_bind(), checkfirst=True)

    ENUM(
        "ESSENCE",
        "DIESEL",
        "ELECTRIQUE",
        "HYBRIDE",
        name="energytype",
    ).create(op.get_bind(), checkfirst=True)

    ENUM(
        "AVAILABLE",
        "RENTED",
        "SOLD",
        "MAINTENANCE",
        name="vehiclestatus",
    ).create(op.get_bind(), checkfirst=True)

    # 2. Table vehicles
    op.create_table(
        "vehicles",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "brand",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "model",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "year",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "price",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
        sa.Column(
            "mileage",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "energy_type",
            ENUM(
                "ESSENCE",
                "DIESEL",
                "ELECTRIQUE",
                "HYBRIDE",
                name="energytype",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            ENUM(
                "AVAILABLE",
                "RENTED",
                "SOLD",
                "MAINTENANCE",
                name="vehiclestatus",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "catalog_type",
            ENUM(
                "RENTAL",
                "SALE",
                name="catalogtype",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "monthly_rent",
            sa.Numeric(precision=10, scale=2),
            nullable=True,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_vehicles_catalog_status",
        "vehicles",
        ["catalog_type", "status"],
        unique=False,
    )

    # 3. Table services
    op.create_table(
        "services",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "monthly_cost",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
        sa.Column(
            "category",
            ENUM(
                "INSURANCE",
                "ASSISTANCE",
                "MAINTENANCE",
                "INSPECTION",
                name="servicecategory",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # 4. Table d'association vehicle_services
    op.create_table(
        "vehicle_services",
        sa.Column(
            "vehicle_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "vehicles.id",
                ondelete="CASCADE",
            ),
            primary_key=True,
        ),
        sa.Column(
            "service_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "services.id",
                ondelete="CASCADE",
            ),
            primary_key=True,
        ),
    )

    # 5. Injection des données initiales (Seed)
    services_table = sa.table(
        "services",
        sa.column(
            "id",
            UUID(as_uuid=True),
        ),
        sa.column(
            "name",
            sa.String,
        ),
        sa.column(
            "monthly_cost",
            sa.Numeric,
        ),
        sa.column(
            "category",
            ENUM(
                "INSURANCE",
                "ASSISTANCE",
                "MAINTENANCE",
                "INSPECTION",
                name="servicecategory",
                create_type=False,
            ),
        ),
    )

    op.bulk_insert(
        services_table,
        [
            {
                "id": uuid.uuid4(),
                "name": "Assurance Tous Risques",
                "monthly_cost": 49.99,
                "category": "INSURANCE",
            },
            {
                "id": uuid.uuid4(),
                "name": "Assistance Panne 24/7",
                "monthly_cost": 14.99,
                "category": "ASSISTANCE",
            },
            {
                "id": uuid.uuid4(),
                "name": "Entretien Périodique Inclus",
                "monthly_cost": 29.99,
                "category": "MAINTENANCE",
            },
            {
                "id": uuid.uuid4(),
                "name": "Contrôle Technique Annuel",
                "monthly_cost": 9.99,
                "category": "INSPECTION",
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("vehicle_services")
    op.drop_table("services")

    op.drop_index(
        "ix_vehicles_catalog_status",
        table_name="vehicles",
    )

    op.drop_table("vehicles")

    ENUM(
        name="servicecategory",
    ).drop(
        op.get_bind(),
        checkfirst=True,
    )

    ENUM(
        name="catalogtype",
    ).drop(
        op.get_bind(),
        checkfirst=True,
    )

    ENUM(
        name="energytype",
    ).drop(
        op.get_bind(),
        checkfirst=True,
    )

    ENUM(
        name="vehiclestatus",
    ).drop(
        op.get_bind(),
        checkfirst=True,
    )
