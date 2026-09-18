"""Modèle SQLAlchemy ORM pour la table dossier_services."""

from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure.database import Base


class DossierServiceModel(Base):
    """Représentation relationnelle des services souscrits dans un dossier."""

    __tablename__ = "dossier_services"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    dossier_id: Mapped[UUID] = mapped_column(
        ForeignKey("dossiers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service_code: Mapped[str] = mapped_column(String(50), nullable=False)

    dossier: Mapped["DossierModel"] = relationship(back_populates="services")