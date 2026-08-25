from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from src.vehicles.domain.entities.Vehicle import Vehicle
from src.vehicles.domain.value_objects.CatalogType import CatalogType
from src.vehicles.domain.value_objects.EnergyType import EnergyType
from src.vehicles.domain.value_objects.Mileage import Mileage
from src.vehicles.domain.value_objects.Price import Price
from src.vehicles.domain.value_objects.VehicleStatus import VehicleStatus
from src.vehicles.infrastructure.mappers.VehicleMapper import VehicleMapper
from src.vehicles.infrastructure.orm.VehicleModel import VehicleModel


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
