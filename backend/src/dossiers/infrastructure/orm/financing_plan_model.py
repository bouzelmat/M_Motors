"""Modèle SQLAlchemy ORM pour la table financing_plans."""

from decimal import Decimal
from typing import TYPE_CHECKING  # 1. Ajout de l'import de typage
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure.database import Base

if TYPE_CHECKING:  # 2. Import masqué pour Ruff
    from src.dossiers.infrastructure.orm.dossier_model import DossierModel


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

    # 3. Ajout de "DossierModel" pour la résolution SQLAlchemy
    dossier: Mapped["DossierModel"] = relationship(
        "DossierModel", back_populates="financing_plan"
    )
