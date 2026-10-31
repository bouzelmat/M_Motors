from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.domain.value_objects.service_category import ServiceCategory
from src.vehicles.domain.value_objects.vehicle_status import VehicleStatus
from src.vehicles.infrastructure.orm.service_model import (
    ServiceModel,
    VehicleServiceAssociation,
)
from src.vehicles.infrastructure.repositories.sqlalchemy_vehicle_repository import (
    SQLAlchemyVehicleRepository,
)


@pytest.mark.asyncio
async def test_list_vehicles_rental_returns_available_vehicles(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Vérifie que le catalogue LLD ne retourne que les véhicules disponibles."""
    repo = SQLAlchemyVehicleRepository(db_session)

    vehicle_1 = Vehicle(
        id=uuid4(),
        brand="Peugeot",
        model="208",
        year=2023,
        price=Price(20000.0),
        mileage=Mileage(10000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(350.0),
    )

    vehicle_2 = Vehicle(
        id=uuid4(),
        brand="Renault",
        model="Clio",
        year=2022,
        price=Price(18000.0),
        mileage=Mileage(15000),
        energy_type=EnergyType.DIESEL,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(400.0),
    )

    vehicle_3 = Vehicle(
        id=uuid4(),
        brand="Tesla",
        model="Model 3",
        year=2023,
        price=Price(45000.0),
        mileage=Mileage(5000),
        energy_type=EnergyType.ELECTRIQUE,
        status=VehicleStatus.RENTED,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(600.0),
    )

    for vehicle in (vehicle_1, vehicle_2, vehicle_3):
        await repo.save(vehicle)

    await db_session.commit()

    response = await async_client.get(
        "/api/v1/vehicles?mode=rental",
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")

    data = response.json()

    assert len(data) == 2

    returned_models = {f"{item['brand']} {item['model']}" for item in data}

    assert returned_models == {
        "Peugeot 208",
        "Renault Clio",
    }

    for item in data:
        assert "id" in item
        assert "brand" in item
        assert "model" in item
        assert "year" in item
        assert "price" in item
        assert "mileage" in item
        assert "energy_type" in item
        assert "catalog_type" in item
        assert "monthly_rent" in item
        assert "photo_url" in item
        assert "included_services" in item


@pytest.mark.asyncio
async def test_list_vehicles_rental_filter_by_max_monthly_rent(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Vérifie le filtrage des véhicules par loyer mensuel maximal."""
    repo = SQLAlchemyVehicleRepository(db_session)

    vehicle_1 = Vehicle(
        id=uuid4(),
        brand="A",
        model="A1",
        year=2023,
        price=Price(10000.0),
        mileage=Mileage(20000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(300.0),
    )

    vehicle_2 = Vehicle(
        id=uuid4(),
        brand="B",
        model="B1",
        year=2023,
        price=Price(15000.0),
        mileage=Mileage(10000),
        energy_type=EnergyType.DIESEL,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(450.0),
    )

    for vehicle in (vehicle_1, vehicle_2):
        await repo.save(vehicle)

    await db_session.commit()

    response = await async_client.get(
        "/api/v1/vehicles?mode=rental&max_monthly_rent=400",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["brand"] == "A"
    assert data[0]["monthly_rent"] == "300.00"


@pytest.mark.parametrize("mode", ["sale", "purchase"])
@pytest.mark.asyncio
async def test_list_vehicles_sale_returns_available_vehicles(
    async_client: AsyncClient,
    db_session: AsyncSession,
    mode: str,
) -> None:
    """Vérifie que le mode achat retourne uniquement les véhicules disponibles."""
    repo = SQLAlchemyVehicleRepository(db_session)

    available_vehicle = Vehicle(
        id=uuid4(),
        brand="Peugeot",
        model="308",
        year=2024,
        price=Price(25000.0),
        mileage=Mileage(10000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.SALE,
        monthly_rent=None,
    )

    rented_vehicle = Vehicle(
        id=uuid4(),
        brand="Renault",
        model="Austral",
        year=2024,
        price=Price(30000.0),
        mileage=Mileage(8000),
        energy_type=EnergyType.DIESEL,
        status=VehicleStatus.RENTED,
        catalog_type=CatalogType.SALE,
        monthly_rent=None,
    )

    await repo.save(available_vehicle)
    await repo.save(rented_vehicle)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/vehicles?mode={mode}",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["brand"] == "Peugeot"
    assert data[0]["model"] == "308"


@pytest.mark.asyncio
async def test_list_vehicles_sale_filter_by_brand(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Vérifie le filtrage par marque en mode achat."""
    repo = SQLAlchemyVehicleRepository(db_session)

    vehicles = [
        Vehicle(
            id=uuid4(),
            brand="Peugeot",
            model="208",
            year=2023,
            price=Price(20000.0),
            mileage=Mileage(10000),
            energy_type=EnergyType.ESSENCE,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.SALE,
        ),
        Vehicle(
            id=uuid4(),
            brand="Peugeot",
            model="308",
            year=2024,
            price=Price(25000.0),
            mileage=Mileage(12000),
            energy_type=EnergyType.DIESEL,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.SALE,
        ),
        Vehicle(
            id=uuid4(),
            brand="Renault",
            model="Clio",
            year=2023,
            price=Price(18000.0),
            mileage=Mileage(15000),
            energy_type=EnergyType.DIESEL,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.SALE,
        ),
    ]

    for vehicle in vehicles:
        await repo.save(vehicle)

    await db_session.commit()

    response = await async_client.get(
        "/api/v1/vehicles?mode=sale&brand=peug",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    returned_models = {item["model"] for item in data}

    assert returned_models == {
        "208",
        "308",
    }


@pytest.mark.asyncio
async def test_list_vehicles_sale_filter_by_max_price(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Vérifie le filtrage par prix maximum en mode achat."""
    repo = SQLAlchemyVehicleRepository(db_session)

    vehicles = [
        Vehicle(
            id=uuid4(),
            brand="A",
            model="A1",
            year=2023,
            price=Price(20000.0),
            mileage=Mileage(10000),
            energy_type=EnergyType.ESSENCE,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.SALE,
        ),
        Vehicle(
            id=uuid4(),
            brand="B",
            model="B1",
            year=2023,
            price=Price(30000.0),
            mileage=Mileage(10000),
            energy_type=EnergyType.DIESEL,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.SALE,
        ),
    ]

    for vehicle in vehicles:
        await repo.save(vehicle)

    await db_session.commit()

    response = await async_client.get(
        "/api/v1/vehicles?mode=sale&max_price=25000",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["brand"] == "A"


@pytest.mark.asyncio
async def test_list_vehicles_sale_filter_by_max_mileage(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Vérifie le filtrage par kilométrage maximum en mode achat."""
    repo = SQLAlchemyVehicleRepository(db_session)

    vehicles = [
        Vehicle(
            id=uuid4(),
            brand="A",
            model="A1",
            year=2023,
            price=Price(20000.0),
            mileage=Mileage(10000),
            energy_type=EnergyType.ESSENCE,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.SALE,
        ),
        Vehicle(
            id=uuid4(),
            brand="B",
            model="B1",
            year=2023,
            price=Price(22000.0),
            mileage=Mileage(30000),
            energy_type=EnergyType.DIESEL,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.SALE,
        ),
    ]

    for vehicle in vehicles:
        await repo.save(vehicle)

    await db_session.commit()

    response = await async_client.get(
        "/api/v1/vehicles?mode=sale&max_mileage=15000",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["brand"] == "A"


@pytest.mark.asyncio
async def test_list_vehicles_sale_filter_by_fuel_type(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Vérifie le filtrage par motorisation en mode achat."""
    repo = SQLAlchemyVehicleRepository(db_session)

    vehicles = [
        Vehicle(
            id=uuid4(),
            brand="Peugeot",
            model="208",
            year=2023,
            price=Price(20000.0),
            mileage=Mileage(10000),
            energy_type=EnergyType.ESSENCE,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.SALE,
        ),
        Vehicle(
            id=uuid4(),
            brand="Renault",
            model="Clio",
            year=2023,
            price=Price(18000.0),
            mileage=Mileage(12000),
            energy_type=EnergyType.DIESEL,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.SALE,
        ),
    ]

    for vehicle in vehicles:
        await repo.save(vehicle)

    await db_session.commit()

    response = await async_client.get(
        "/api/v1/vehicles?mode=sale&fuel_type=ESSENCE",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["brand"] == "Peugeot"
    assert data[0]["model"] == "208"


@pytest.mark.asyncio
async def test_list_vehicles_sale_combines_multiple_filters(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Vérifie la combinaison de plusieurs filtres en mode achat."""
    repo = SQLAlchemyVehicleRepository(db_session)

    vehicles = [
        Vehicle(
            id=uuid4(),
            brand="Peugeot",
            model="208",
            year=2023,
            price=Price(20000.0),
            mileage=Mileage(10000),
            energy_type=EnergyType.ESSENCE,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.SALE,
        ),
        Vehicle(
            id=uuid4(),
            brand="Peugeot",
            model="308",
            year=2024,
            price=Price(30000.0),
            mileage=Mileage(8000),
            energy_type=EnergyType.ESSENCE,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.SALE,
        ),
        Vehicle(
            id=uuid4(),
            brand="Renault",
            model="Clio",
            year=2023,
            price=Price(19000.0),
            mileage=Mileage(9000),
            energy_type=EnergyType.ESSENCE,
            status=VehicleStatus.AVAILABLE,
            catalog_type=CatalogType.SALE,
        ),
    ]

    for vehicle in vehicles:
        await repo.save(vehicle)

    await db_session.commit()

    response = await async_client.get(
        "/api/v1/vehicles"
        "?mode=sale"
        "&brand=peugeot"
        "&max_price=25000"
        "&max_mileage=15000"
        "&fuel_type=ESSENCE",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["brand"] == "Peugeot"
    assert data[0]["model"] == "208"


@pytest.mark.asyncio
async def test_list_vehicles_sale_returns_empty_when_no_vehicle_matches_filters(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Vérifie qu'une recherche sans résultat retourne une liste vide."""
    repo = SQLAlchemyVehicleRepository(db_session)

    vehicle = Vehicle(
        id=uuid4(),
        brand="Peugeot",
        model="308",
        year=2024,
        price=Price(30000.0),
        mileage=Mileage(10000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.SALE,
    )

    await repo.save(vehicle)
    await db_session.commit()

    response = await async_client.get(
        "/api/v1/vehicles?mode=sale&max_price=10000",
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_vehicle_detail_returns_200_when_available(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Retourne le détail d'un véhicule disponible."""
    repo = SQLAlchemyVehicleRepository(db_session)

    vehicle = Vehicle(
        id=uuid4(),
        brand="Peugeot",
        model="208",
        year=2023,
        price=Price(20000.0),
        mileage=Mileage(10000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(350.0),
        description="Une voiture compacte",
    )

    await repo.save(vehicle)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/vehicles/{vehicle.id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(vehicle.id)
    assert data["brand"] == "Peugeot"
    assert data["catalog_type"] == "RENTAL"
    assert data["monthly_rent"] == "350.00"
    assert data["price"] == "20000.00"
    assert data["mileage"] == 10000
    assert data["energy_type"] == "ESSENCE"
    assert data["description"] == "Une voiture compacte"
    assert data["services"] == []


@pytest.mark.asyncio
async def test_get_vehicle_detail_returns_200_for_available_sale_vehicle(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A vehicle listed for sale also has an accessible detail page."""
    repo = SQLAlchemyVehicleRepository(db_session)
    vehicle = Vehicle(
        id=uuid4(),
        brand="Peugeot",
        model="308",
        year=2024,
        price=Price(25000.0),
        mileage=Mileage(10000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.SALE,
    )
    await repo.save(vehicle)
    await db_session.commit()

    response = await async_client.get(f"/api/v1/vehicles/{vehicle.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(vehicle.id)
    assert response.json()["price"] == "25000.00"


@pytest.mark.asyncio
async def test_get_vehicle_detail_returns_services_with_inclusion(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Vérifie que le détail retourne les services avec leur statut included."""
    repo = SQLAlchemyVehicleRepository(db_session)

    vehicle_id = uuid4()
    included_service_id = uuid4()
    optional_service_id = uuid4()

    vehicle = Vehicle(
        id=vehicle_id,
        brand="Peugeot",
        model="308",
        year=2024,
        price=Price(25000.0),
        mileage=Mileage(10000),
        energy_type=EnergyType.ESSENCE,
        status=VehicleStatus.AVAILABLE,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(399.0),
        description="Véhicule avec services",
    )

    await repo.save(vehicle)

    included_service = ServiceModel(
        id=included_service_id,
        name="Assistance",
        monthly_cost=Decimal("15.00"),
        category=ServiceCategory.ASSISTANCE,
    )

    optional_service = ServiceModel(
        id=optional_service_id,
        name="Extension de garantie",
        monthly_cost=Decimal("29.90"),
        category=ServiceCategory.MAINTENANCE,
    )

    included_association = VehicleServiceAssociation(
        vehicle_id=vehicle_id,
        service_id=included_service_id,
        included=True,
        service=included_service,
    )

    optional_association = VehicleServiceAssociation(
        vehicle_id=vehicle_id,
        service_id=optional_service_id,
        included=False,
        service=optional_service,
    )

    db_session.add_all(
        [
            included_service,
            optional_service,
            included_association,
            optional_association,
        ]
    )

    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/vehicles/{vehicle_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert "services" in data
    assert len(data["services"]) == 2

    services_by_id = {service["id"]: service for service in data["services"]}

    included_service_data = services_by_id[str(included_service_id)]

    assert included_service_data["name"] == "Assistance"
    assert included_service_data["monthly_cost"] == "15.00"
    assert included_service_data["category"] == "ASSISTANCE"
    assert included_service_data["included"] is True

    optional_service_data = services_by_id[str(optional_service_id)]

    assert optional_service_data["name"] == "Extension de garantie"
    assert optional_service_data["monthly_cost"] == "29.90"
    assert optional_service_data["category"] == "MAINTENANCE"
    assert optional_service_data["included"] is False

    assert data["included_services"] == ["Assistance"]


@pytest.mark.asyncio
async def test_admin_can_create_rental_vehicle_with_included_and_optional_services(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_admin_token: str,
) -> None:
    included_service = ServiceModel(
        id=uuid4(),
        name="Assurance tous risques",
        monthly_cost=Decimal("49.99"),
        category=ServiceCategory.INSURANCE,
    )
    optional_service = ServiceModel(
        id=uuid4(),
        name="Contrôle technique annuel",
        monthly_cost=Decimal("9.99"),
        category=ServiceCategory.INSPECTION,
    )
    db_session.add_all([included_service, optional_service])

    csrf_response = await async_client.get("/api/v1/auth/csrf")
    headers = {
        "Authorization": f"Bearer {test_admin_token}",
        "X-CSRF-Token": csrf_response.json()["csrf_token"],
    }
    catalog_response = await async_client.get(
        "/api/v1/vehicles/services",
        headers=headers,
    )
    assert catalog_response.status_code == 200
    assert {item["category"] for item in catalog_response.json()} >= {
        "INSURANCE",
        "INSPECTION",
    }

    response = await async_client.post(
        "/api/v1/vehicles",
        headers=headers,
        json={
            "brand": "Peugeot",
            "model": "208",
            "year": 2024,
            "mileage": 10000,
            "energy_type": "ESSENCE",
            "catalog_type": "RENTAL",
            "monthly_rent": 350,
            "services": [
                {"service_id": str(included_service.id), "included": True},
                {"service_id": str(optional_service.id), "included": False},
            ],
        },
    )

    assert response.status_code == 201, response.text
    vehicle_id = response.json()["id"]
    detail_response = await async_client.get(f"/api/v1/vehicles/{vehicle_id}")
    assert detail_response.status_code == 200, detail_response.text
    services = {
        service["id"]: service for service in detail_response.json()["services"]
    }
    assert services[str(included_service.id)]["included"] is True
    assert services[str(optional_service.id)]["included"] is False


@pytest.mark.asyncio
async def test_get_vehicle_detail_returns_404_when_not_found(
    async_client: AsyncClient,
) -> None:
    """Retourne 404 lorsqu'aucun véhicule ne correspond à l'identifiant demandé."""
    response = await async_client.get(
        f"/api/v1/vehicles/{uuid4()}",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Véhicule non trouvé",
    }


@pytest.mark.asyncio
async def test_get_vehicle_detail_returns_404_when_vehicle_is_not_available(
    async_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Retourne 404 lorsqu'un véhicule existe mais n'est pas disponible."""
    repo = SQLAlchemyVehicleRepository(db_session)

    vehicle = Vehicle(
        id=uuid4(),
        brand="Tesla",
        model="Model 3",
        year=2023,
        price=Price(45000.0),
        mileage=Mileage(5000),
        energy_type=EnergyType.ELECTRIQUE,
        status=VehicleStatus.RENTED,
        catalog_type=CatalogType.RENTAL,
        monthly_rent=Price(600.0),
    )

    await repo.save(vehicle)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/vehicles/{vehicle.id}",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Véhicule non disponible",
    }
