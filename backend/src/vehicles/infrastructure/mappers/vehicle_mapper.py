from decimal import Decimal

from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.domain.value_objects.service_inclusion import ServiceInclusion
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus
from src.vehicles.infrastructure.orm.service_model import VehicleServiceAssociation
from src.vehicles.infrastructure.orm.vehicle_model import VehicleModel


class VehicleMapper:
    """Mapper statique entre Vehicle et VehicleModel."""

    @staticmethod
    def to_domain(orm: VehicleModel) -> Vehicle:
        """Convertit un modèle SQLAlchemy en entité domaine Vehicle."""

        services = [
            ServiceInclusion(
                service_id=association.service.id,
                name=association.service.name,
                monthly_cost=Decimal(str(association.service.monthly_cost)),
                category=association.service.category,
                included=association.included,
            )
            for association in orm.service_associations
        ]

        return Vehicle(
            id=orm.id,
            brand=orm.brand,
            model=orm.model,
            year=orm.year,
            price=Price(float(orm.price)),
            mileage=Mileage(orm.mileage),
            energy_type=EnergyType(orm.energy_type),
            status=VehicleStatus(orm.status),
            catalog_type=CatalogType(orm.catalog_type),
            monthly_rent=(
                Price(float(orm.monthly_rent))
                if orm.monthly_rent is not None
                else None
            ),
            description=orm.description,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            services=services,
        )

    @staticmethod
    def to_orm(
        entity: Vehicle, existing_orm: VehicleModel | None = None
    ) -> VehicleModel:
        """Convertit une entité domaine Vehicle en modèle SQLAlchemy."""

        orm = existing_orm if existing_orm is not None else VehicleModel()

        if existing_orm is None:
            orm.id = entity.id

        orm.brand = entity.brand
        orm.model = entity.model
        orm.year = entity.year
        orm.price = Decimal(str(entity.price.value))
        orm.mileage = entity.mileage.value
        orm.energy_type = entity.energy_type.value
        orm.status = entity.status.value
        orm.catalog_type = entity.catalog_type.value
        orm.monthly_rent = (
            Decimal(str(entity.monthly_rent.value))
            if entity.monthly_rent
            else None
        )
        orm.description = entity.description
        orm.created_at = entity.created_at
        orm.updated_at = entity.updated_at

        existing_associations = {
            association.service_id: association
            for association in orm.service_associations
        }

        domain_service_ids = {
            service.service_id for service in entity.services
        }

        orm.service_associations = [
            association
            for association in orm.service_associations
            if association.service_id in domain_service_ids
        ]

        for service in entity.services:
            association = existing_associations.get(service.service_id)

            if association is None:
                association = VehicleServiceAssociation(
                    vehicle_id=orm.id,
                    service_id=service.service_id,
                    included=service.included,
                )
                orm.service_associations.append(association)
            else:
                association.included = service.included

        return orm