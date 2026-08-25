from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from src.vehicles.domain.value_objects.catalog_type import CatalogType


@dataclass(frozen=True)
class VehicleSearchCriteria:
    """
    Critères de recherche pour le catalogue véhicules.
    Utilisé par les Query Handlers (ex: catalogue LLD, catalogue vente).
    """

    mode: Literal["rental", "sale"]  # obligatoire
    max_monthly_rent: Decimal | None = None  # pour la location
    max_price: Decimal | None = None  # pour l'achat
    brand: str | None = None  # marque (filtre approximatif)
    fuel_type: str | None = None  # type d'énergie (ESSENCE, DIESEL…)
    max_mileage: int | None = None  # kilométrage maximum

    @property
    def catalog_type(self) -> CatalogType:
        """Convertit le mode en CatalogType pour l'ORM."""
        return CatalogType.RENTAL if self.mode == "rental" else CatalogType.SALE
