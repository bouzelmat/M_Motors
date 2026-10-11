from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.vehicles.domain.entities.vehicle import Vehicle
from src.vehicles.domain.value_objects.catalog_type import CatalogType
from src.vehicles.domain.value_objects.energy_type import EnergyType
from src.vehicles.domain.value_objects.mileage import Mileage
from src.vehicles.domain.value_objects.price import Price
from src.vehicles.infrastructure.repositories.sqlalchemy_vehicle_repository import (
    SQLAlchemyVehicleRepository,
)


@pytest.mark.asyncio
async def test_manage_multiple_vehicle_photos_and_primary_promotion(
    db_session: AsyncSession,
) -> None:
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

    first_photo = await repository.create_pending_photo(
        vehicle_id=vehicle.id,
        object_key=f"vehicles/{vehicle.id}/first.jpg",
        photo_url="https://photos/first.jpg",
        content_type="image/jpeg",
        uploaded_by=uuid4(),
    )
    await repository.confirm_photo(first_photo)
    second_photo = await repository.create_pending_photo(
        vehicle_id=vehicle.id,
        object_key=f"vehicles/{vehicle.id}/second.jpg",
        photo_url="https://photos/second.jpg",
        content_type="image/jpeg",
        uploaded_by=uuid4(),
    )
    await repository.confirm_photo(second_photo)
    await db_session.commit()

    assert await repository.set_primary_photo(vehicle.id, second_photo.id)
    await db_session.commit()
    photos = await repository.list_uploaded_photos(vehicle.id)
    assert len(photos) == 2
    assert next(photo for photo in photos if photo.id == second_photo.id).is_primary

    deleted_key = await repository.delete_photo(vehicle.id, second_photo.id)
    await db_session.commit()
    remaining = await repository.list_uploaded_photos(vehicle.id)

    assert deleted_key == f"vehicles/{vehicle.id}/second.jpg"
    assert len(remaining) == 1
    assert remaining[0].id == first_photo.id
    assert remaining[0].is_primary
