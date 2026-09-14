"""Modèle SQLAlchemy ORM pour la table dossiers."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from src.dossiers.domain.value_objects.dossier_status import DossierStatus
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
