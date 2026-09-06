"""Modèles SQLAlchemy pour les services optionnels et la table d'association."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure.database import Base
from src.vehicles.domain.value_objects.service_category import ServiceCategory

if TYPE_CHECKING:
    from src.vehicles.infrastructure.orm.vehicle_model import VehicleModel


class VehicleServiceAssociation(Base):
    """Modèle ORM d'association entre un véhicule et un service (Association Object)."""

    __tablename__ = "vehicle_services"

    vehicle_id: Mapped[UUID] = mapped_column(
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    service_id: Mapped[UUID] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"),
        primary_key=True,
    )
    included: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # Navigation vers les entités
    vehicle: Mapped[VehicleModel] = relationship(
        back_populates="service_associations",
    )
    service: Mapped[ServiceModel] = relationship(
        back_populates="vehicle_associations",
    )


class ServiceModel(Base):
    """Modèle SQLAlchemy représentant la table des services."""

    __tablename__ = "services"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    monthly_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    category: Mapped[ServiceCategory] = mapped_column(
        Enum(ServiceCategory, name="servicecategory"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relation vers la table d'association
    vehicle_associations: Mapped[list[VehicleServiceAssociation]] = relationship(
        back_populates="service",
        cascade="all, delete-orphan",
    )
