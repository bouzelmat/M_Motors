"""Modèle SQLAlchemy ORM pour la table financing_plans."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure.database import Base


class FinancingPlanModel(Base):
    """Représentation relationnelle du plan de financement."""

    __tablename__ = "financing_plans"

    dossier_id: Mapped[UUID] = mapped_column(
        ForeignKey("dossiers.id", ondelete="CASCADE"),
        primary_key=True,
    )
    down_payment: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    duration_months: Mapped[int] = mapped_column(nullable=False)
    monthly_payment: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    dossier: Mapped["DossierModel"] = relationship(back_populates="financing_plan")