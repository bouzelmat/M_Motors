"""Modèle SQLAlchemy ORM pour la table trade_ins."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure.database import Base


class TradeInModel(Base):
    """Représentation relationnelle du véhicule de reprise."""

    __tablename__ = "trade_ins"

    dossier_id: Mapped[UUID] = mapped_column(
        ForeignKey("dossiers.id", ondelete="CASCADE"),
        primary_key=True,
    )
    registration: Mapped[str] = mapped_column(String(20), nullable=False)
    mileage: Mapped[int] = mapped_column(nullable=False)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    estimated_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    dossier: Mapped["DossierModel"] = relationship(back_populates="trade_in")