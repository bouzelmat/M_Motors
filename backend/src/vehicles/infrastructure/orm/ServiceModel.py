"""Modèles SQLAlchemy pour les services optionnels et la table d'association."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.infrastructure.database import Base
from vehicles.domain.value_objects.ServiceCategory import ServiceCategory


class ServiceModel(Base):
    """Modèle SQLAlchemy représentant la table des services."""

    __tablename__ = "services"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    monthly_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    category: Mapped[ServiceCategory] = mapped_column(Enum(ServiceCategory, name="servicecategory"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relation many-to-many via la table d'association
    vehicles: Mapped[list["VehicleModel"]] = relationship(
        secondary="vehicle_services",
        back_populates="services",
    )


# Table d'association (sans modèle dédié)
vehicle_services = Table(
    "vehicle_services",
    Base.metadata,
    mapped_column("vehicle_id", ForeignKey("vehicles.id", ondelete="CASCADE"), primary_key=True),
    mapped_column("service_id", ForeignKey("services.id", ondelete="CASCADE"), primary_key=True),
)