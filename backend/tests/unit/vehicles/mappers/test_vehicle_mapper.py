from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus
from src.vehicles.domain.value_objects.service_inclusion import ServiceInclusion
from src.vehicles.infrastructure.mappers.vehicle_mapper import VehicleMapper
from src.vehicles.infrastructure.orm.vehicle_model import VehicleModel
from src.vehicles.infrastructure.orm.service_model import (
    ServiceModel,
    VehicleServiceAssociation,
)


class TestVehicleMapper:
    """Tests unitaires du mapper VehicleMapper."""

    def test_to_domain_from_orm(self):
        """Vérifie la conversion d'un modèle ORM vers une entité domaine."""

        # Création d'un modèle ORM factice
        vehicle_id = uuid4()
        now = datetime.now(timezone.utc)

        orm = VehicleModel(
            id=vehicle_id,
            brand="Tesla",
            model="Model 3",
            year=2023,
            price=Decimal("45990.00"),
            mileage=15000,
            energy_type=EnergyType.ELECTRIQUE.value,
            status=VehicleStatus.AVAILABLE.value,
            catalog_type=CatalogType.RENTAL.value,
            monthly_rent=Decimal("350.00"),  # Ajouté pour respecter la validation
            description="Superbe voiture électrique",
            created_at=now,
            updated_at=now,
        )

        # Conversion vers domaine
        entity = VehicleMapper.to_domain(orm)

        # Vérifications
        assert entity.id == vehicle_id
        assert entity.brand == "Tesla"
        assert entity.model == "Model 3"
        assert entity.year == 2023
        assert entity.price.value == 45990.00
        assert entity.mileage.value == 15000
        assert entity.energy_type == EnergyType.ELECTRIQUE
        assert entity.status == VehicleStatus.AVAILABLE
        assert entity.catalog_type == CatalogType.RENTAL
        assert entity.monthly_rent is not None
        assert entity.monthly_rent.value == 350.00
        assert entity.description == "Superbe voiture électrique"
        assert entity.created_at == now
        assert entity.updated_at == now

    def test_to_orm_from_entity(self):
        """Vérifie la conversion d'une entité domaine vers un modèle ORM."""

        # Création d'une entité domaine
        vehicle_id = uuid4()
        now = datetime.now(timezone.utc)

        entity = Vehicle(
            id=vehicle_id,
            brand="Renault",
            model="Clio",
            year=2022,
            price=Price(18990.99),
            mileage=Mileage(25000),
            energy_type=EnergyType.DIESEL,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.RENTAL,
            monthly_rent=Price(350.00),  # Ajouté
            description="Petite citadine économique",
            created_at=now,
            updated_at=now,
        )

        # Conversion vers ORM
        orm = VehicleMapper.to_orm(entity)

        # Vérifications
        assert orm.id == vehicle_id
        assert orm.brand == "Renault"
        assert orm.model == "Clio"
        assert orm.year == 2022
        assert orm.price == Decimal("18990.99")
        assert orm.mileage == 25000
        assert orm.energy_type == EnergyType.DIESEL.value
        assert orm.status == VehicleStatus.AVAILABLE.value
        assert orm.catalog_type == CatalogType.RENTAL.value
        assert orm.monthly_rent == Decimal("350.00")
        assert orm.description == "Petite citadine économique"
        assert orm.created_at == now
        assert orm.updated_at == now

    def test_roundtrip_conversion(self):
        """Vérifie que to_domain(to_orm(entity)) restitue l'entité d'origine."""

        now = datetime.now(timezone.utc)

        original_entity = Vehicle(
            id=uuid4(),
            brand="Peugeot",
            model="208",
            year=2021,
            price=Price(15990.50),
            mileage=Mileage(32000),
            energy_type=EnergyType.ESSENCE,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.RENTAL,
            monthly_rent=Price(350.00),  # Déjà présent
            description="Idéale pour la ville",
            created_at=now,
            updated_at=now,
        )

        # Domaine → ORM → Domaine
        orm = VehicleMapper.to_orm(original_entity)
        reconstructed = VehicleMapper.to_domain(orm)

        # Vérifications
        assert reconstructed.id == original_entity.id
        assert reconstructed.brand == original_entity.brand
        assert reconstructed.model == original_entity.model
        assert reconstructed.year == original_entity.year
        assert reconstructed.price.value == original_entity.price.value
        assert reconstructed.mileage.value == original_entity.mileage.value
        assert reconstructed.energy_type == original_entity.energy_type
        assert reconstructed.status == original_entity.status
        assert reconstructed.catalog_type == original_entity.catalog_type
        assert reconstructed.monthly_rent == original_entity.monthly_rent
        assert reconstructed.description == original_entity.description
        assert reconstructed.created_at == original_entity.created_at
        assert reconstructed.updated_at == original_entity.updated_at

    def test_update_existing_orm(self):
        """Vérifie la mise à jour d'un modèle ORM existant."""

        # Création d'un ORM existant
        existing_id = uuid4()
        existing_orm = VehicleModel(id=existing_id)

        # Création d'une entité avec un autre identifiant
        now = datetime.now(timezone.utc)

        entity = Vehicle(
            id=uuid4(),
            brand="Citroën",
            model="C3",
            year=2020,
            price=Price(12900.00),
            mileage=Mileage(45000),
            energy_type=EnergyType.DIESEL,
            status=VehicleStatus.MAINTENANCE,
            catalog_type=CatalogType.RENTAL,
            monthly_rent=Price(350.00),  # Ajouté
            description=None,
            created_at=now,
            updated_at=now,
        )

        # Mise à jour de l'ORM existant
        updated_orm = VehicleMapper.to_orm(entity, existing_orm)

        # Vérifications
        assert updated_orm is existing_orm
        assert updated_orm.id == existing_id
        assert updated_orm.brand == "Citroën"
        assert updated_orm.model == "C3"
        assert updated_orm.year == 2020
        assert updated_orm.price == Decimal("12900.00")
        assert updated_orm.mileage == 45000
        assert updated_orm.energy_type == EnergyType.DIESEL.value
        assert updated_orm.status == VehicleStatus.MAINTENANCE.value
        assert updated_orm.catalog_type == CatalogType.RENTAL.value
        assert updated_orm.monthly_rent == Decimal("350.00")
        assert updated_orm.description is None
        assert updated_orm.created_at == now
        assert updated_orm.updated_at == now

    def test_to_domain_with_services(self):
        """Vérifie la conversion des associations ORM vers les services du domaine."""

        vehicle_id = uuid4()
        service_id = uuid4()
        now = datetime.now(timezone.utc)

        service = ServiceModel(
            id=service_id,
            name="Assurance tous risques",
            monthly_cost=Decimal("49.90"),
            category="insurance",
        )

        association = VehicleServiceAssociation(
            vehicle_id=vehicle_id,
            service_id=service_id,
            included=True,
            service=service,
        )

        orm = VehicleModel(
            id=vehicle_id,
            brand="Tesla",
            model="Model 3",
            year=2023,
            price=Decimal("45990.00"),
            mileage=15000,
            energy_type=EnergyType.ELECTRIQUE.value,
            status=VehicleStatus.AVAILABLE.value,
            catalog_type=CatalogType.RENTAL.value,
            monthly_rent=Decimal("350.00"),
            description="Superbe voiture électrique",
            created_at=now,
            updated_at=now,
            service_associations=[association],
        )

        entity = VehicleMapper.to_domain(orm)

        assert len(entity.services) == 1
        assert entity.services[0].service_id == service_id
        assert entity.services[0].name == "Assurance tous risques"
        assert entity.services[0].monthly_cost == Decimal("49.90")
        assert entity.services[0].included is True

    def test_to_orm_with_services(self):
        """Vérifie la conversion des services du domaine vers les associations ORM."""

        vehicle_id = uuid4()
        service_id = uuid4()
        now = datetime.now(timezone.utc)

        entity = Vehicle(
            id=vehicle_id,
            brand="Renault",
            model="Clio",
            year=2022,
            price=Price(18990.99),
            mileage=Mileage(25000),
            energy_type=EnergyType.DIESEL,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.RENTAL,
            monthly_rent=Price(350.00),
            description="Petite citadine économique",
            created_at=now,
            updated_at=now,
            services=[
                ServiceInclusion(
                    service_id=service_id,
                    name="Assistance dépannage",
                    monthly_cost=Decimal("19.90"),
                    category="assistance",
                    included=False,
                )
            ],
        )

        orm = VehicleMapper.to_orm(entity)

        assert len(orm.service_associations) == 1

        association = orm.service_associations[0]

        assert association.vehicle_id == vehicle_id
        assert association.service_id == service_id
        assert association.included is False

    def test_to_orm_updates_existing_service_association(self):
        """Vérifie la mise à jour du statut included d'une association existante."""

        vehicle_id = uuid4()
        service_id = uuid4()
        now = datetime.now(timezone.utc)

        existing_association = VehicleServiceAssociation(
            vehicle_id=vehicle_id,
            service_id=service_id,
            included=True,
        )

        existing_orm = VehicleModel(
            id=vehicle_id,
            service_associations=[existing_association],
        )

        entity = Vehicle(
            id=vehicle_id,
            brand="Citroën",
            model="C3",
            year=2020,
            price=Price(12900.00),
            mileage=Mileage(45000),
            energy_type=EnergyType.DIESEL,
            status=VehicleStatus.MAINTENANCE,
            catalog_type=CatalogType.RENTAL,
            monthly_rent=Price(350.00),
            description=None,
            created_at=now,
            updated_at=now,
            services=[
                ServiceInclusion(
                    service_id=service_id,
                    name="Assurance",
                    monthly_cost=Decimal("49.90"),
                    category="insurance",
                    included=False,
                )
            ],
        )

        updated_orm = VehicleMapper.to_orm(entity, existing_orm)

        assert updated_orm is existing_orm
        assert len(updated_orm.service_associations) == 1
        assert updated_orm.service_associations[0] is existing_association
        assert updated_orm.service_associations[0].included is False

    def test_to_orm_removes_services_not_present_in_entity(self):
        """Vérifie la suppression des associations absentes du domaine."""

        vehicle_id = uuid4()
        existing_service_id = uuid4()
        now = datetime.now(timezone.utc)

        existing_association = VehicleServiceAssociation(
            vehicle_id=vehicle_id,
            service_id=existing_service_id,
            included=True,
        )

        existing_orm = VehicleModel(
            id=vehicle_id,
            service_associations=[existing_association],
        )

        entity = Vehicle(
            id=vehicle_id,
            brand="Peugeot",
            model="208",
            year=2021,
            price=Price(15990.50),
            mileage=Mileage(32000),
            energy_type=EnergyType.ESSENCE,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.RENTAL,
            monthly_rent=Price(350.00),
            description="Idéale pour la ville",
            created_at=now,
            updated_at=now,
            services=[],
        )

        updated_orm = VehicleMapper.to_orm(entity, existing_orm)

        assert updated_orm.service_associations == []