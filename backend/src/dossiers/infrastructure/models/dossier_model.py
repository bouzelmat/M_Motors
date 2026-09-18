"""Modèle SQLAlchemy ORM pour la table dossiers."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.dossiers.infrastructure.models.dossier_service_model import DossierServiceModel
from src.dossiers.infrastructure.models.financing_plan_model import FinancingPlanModel
from src.dossiers.infrastructure.models.trade_in_model import TradeInModel
from src.shared.infrastructure.database import Base


class DossierModel(Base):
    """Représentation relationnelle de la table dossiers dans la base de données."""

    __tablename__ = "dossiers"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    vehicle_id: Mapped[UUID] = mapped_column(index=True, nullable=False)
    status: Mapped[DossierStatus] = mapped_column(
        Enum(DossierStatus, native_enum=False),
        nullable=False,
        index=True,
    )
    upload_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    financing_plan: Mapped[FinancingPlanModel | None] = relationship(
        back_populates="dossier",
        uselist=False,
        cascade="all, delete-orphan",
    )
    trade_in: Mapped[TradeInModel | None] = relationship(
        back_populates="dossier",
        uselist=False,
        cascade="all, delete-orphan",
    )
    services: Mapped[list[DossierServiceModel]] = relationship(
        back_populates="dossier",
        cascade="all, delete-orphan",
    )