from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.main import app
from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.infrastructure.dependencies import get_storage_service
from src.vehicles.infrastructure.repositories.sqlalchemy_vehicle_repository import (
    SQLAlchemyVehicleRepository,
)


class FakePhotoStorage:
    def __init__(self) -> None:
        self.deleted_keys: list[str] = []

    async def get_object_url(self, object_name: str) -> str:
        return f"https://signed.example/{object_name}"

    async def delete_object(self, object_name: str) -> None:
        self.deleted_keys.append(object_name)


@pytest.mark.asyncio
async def test_admin_can_manage_vehicle_photo_gallery(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_admin_token: str,
) -> None:
    storage = FakePhotoStorage()
    app.dependency_overrides[get_storage_service] = lambda: storage

    repository = SQLAlchemyVehicleRepository(db_session)
    vehicle = Vehicle.create(
        brand="Peugeot",
        model="208",
        year=2024,
        mileage=Mileage(1000),
        energy_type=EnergyType.ESSENCE,
        catalog_type=CatalogType.SALE,
        price=Price(18000),
    )
    await repository.save(vehicle)
    await db_session.commit()

    # ✅ CORRECTION : Suppression de l'argument photo_url (3ème paramètre)
    first = await repository.create_pending_photo(
        vehicle.id,
        f"vehicles/{vehicle.id}/first.jpg",
        "image/jpeg",
        uuid4(),
    )
    await repository.confirm_photo(first)

    # ✅ CORRECTION : Suppression de l'argument photo_url (3ème paramètre)
    second = await repository.create_pending_photo(
        vehicle.id,
        f"vehicles/{vehicle.id}/second.jpg",
        "image/jpeg",
        uuid4(),
    )
    await repository.confirm_photo(second)
    await db_session.commit()

    headers = {"Authorization": f"Bearer {test_admin_token}"}
    gallery_response = await async_client.get(
        f"/api/v1/vehicles/{vehicle.id}/photos", headers=headers
    )
    assert gallery_response.status_code == 200
    assert all(
        photo["photo_url"].startswith("https://signed.example/")
        for photo in gallery_response.json()
    )

    csrf_response = await async_client.get("/api/v1/auth/csrf")
    headers["X-CSRF-Token"] = csrf_response.json()["csrf_token"]
    primary_response = await async_client.patch(
        f"/api/v1/vehicles/{vehicle.id}/photos/{second.id}/primary",
        headers=headers,
    )
    assert primary_response.status_code == 204

    delete_response = await async_client.delete(
        f"/api/v1/vehicles/{vehicle.id}/photos/{second.id}",
        headers=headers,
    )
    assert delete_response.status_code == 204
    assert storage.deleted_keys == [f"vehicles/{vehicle.id}/second.jpg"]

    remaining = await repository.list_uploaded_photos(vehicle.id)
    assert len(remaining) == 1
    assert remaining[0].id == first.id
    assert remaining[0].is_primary
