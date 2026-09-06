"""Mapper entre le modèle ORM Service et l'entité domaine Service."""

from decimal import Decimal

from src.vehicles.domain.entities.service import Service
from src.vehicles.infrastructure.orm.service_model import ServiceModel


class ServiceMapper:
    """Convertit les modèles ORM Service en entités domaine."""

    @staticmethod
    def to_domain(orm: ServiceModel) -> Service:
        """Convertit un ServiceModel en entité Service."""

        return Service(
            id=orm.id,
            name=orm.name,
            monthly_cost=Decimal(str(orm.monthly_cost)),
            category=orm.category,
        )
