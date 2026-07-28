"""SQLAlchemy ORM model for Vehicle."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Index, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.infrastructure.database import Base
from vehicles.domain.value_objects.CatalogType import CatalogType
from vehicles.domain.value_objects.EnergyType import EnergyType
from vehicles.domain.value_objects.VehicleStatus import VehicleStatus


class VehicleModel(Base):
    """SQLAlchemy ORM model representing the vehicles table."""

    __tablename__ = "vehicles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    mileage: Mapped[int] = mapped_column(Integer, nullable=False)
    energy_type: Mapped[EnergyType] = mapped_column(Enum(EnergyType, name="energytype"), nullable=False)
    status: Mapped[VehicleStatus] = mapped_column(Enum(VehicleStatus, name="vehiclestatus"), nullable=False)
    catalog_type: Mapped[CatalogType] = mapped_column(Enum(CatalogType, name="catalogtype"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_vehicles_catalog_status", "catalog_type", "status"),
    )