"""Endpoints publics pour le catalogue véhicules."""

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.vehicles.api.schemas.vehicle_schemas import (
    ServiceDTO,
    VehicleDetailDTO,
    VehicleListItemDTO,
)
from src.vehicles.application.queries.GetRentalCatalogQuery import (
    GetRentalCatalogQuery,
    GetRentalCatalogQueryHandler,
)
from src.vehicles.application.queries.GetVehicleDetailQuery import (
    GetVehicleDetailQuery,
    GetVehicleDetailQueryHandler,
)
from src.vehicles.infrastructure.dependencies import (
    get_rental_catalog_query_handler,
    get_vehicle_detail_handler,
)

router = APIRouter(
    prefix="/api/v1/vehicles",
    tags=["vehicles"],
)


@router.get(
    "",
    response_model=list[VehicleListItemDTO],
    status_code=status.HTTP_200_OK,
    summary="Catalogue des véhicules disponibles en location (LLD)",
    description="Retourne la liste des véhicules disponibles avec leurs loyers mensuels.",
)
async def list_vehicles(
    mode: str = Query(
        default="rental",
        pattern="^(rental|sale)$",
        description="Mode de catalogue : rental ou sale",
    ),
    max_monthly_rent: Decimal | None = Query(
        default=None,
        description="Loyer mensuel maximum (pour rental)",
    ),
    handler: GetRentalCatalogQueryHandler = Depends(
        get_rental_catalog_query_handler,
    ),
) -> list[VehicleListItemDTO]:
    """Retourne les véhicules disponibles selon le mode de catalogue demandé."""

    if mode == "rental":
        query = GetRentalCatalogQuery(
            max_monthly_rent=max_monthly_rent,
        )
    else:
        # Un QueryHandler dédié sera implémenté pour le catalogue de vente.
        return []

    vehicles = await handler.handle(query)

    return [
        VehicleListItemDTO(
            id=vehicle.id,
            brand=vehicle.brand,
            model=vehicle.model,
            year=vehicle.year,
            monthly_rent=(
                vehicle.monthly_rent.value if vehicle.monthly_rent else Decimal("0.00")
            ),
            photo_url=None,
            included_services=[],
        )
        for vehicle in vehicles
    ]


@router.get(
    "/{vehicle_id}",
    response_model=VehicleDetailDTO,
    status_code=status.HTTP_200_OK,
    summary="Détails d'un véhicule",
)
async def get_vehicle_detail(
    vehicle_id: UUID,
    handler: GetVehicleDetailQueryHandler = Depends(
        get_vehicle_detail_handler,
    ),
) -> VehicleDetailDTO:
    """Retourne les informations détaillées d'un véhicule."""

    query = GetVehicleDetailQuery(
        vehicle_id=vehicle_id,
    )

    result = await handler.handle(query)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Véhicule non trouvé",
        )

    vehicle, service_orms = result

    if not vehicle.is_available_for_rental():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Véhicule non disponible",
        )

    services = [
        ServiceDTO(
            id=service.id,
            name=service.name,
            monthly_cost=service.monthly_cost,
            category=service.category.value,
        )
        for service in service_orms
    ]

    return VehicleDetailDTO(
        id=vehicle.id,
        brand=vehicle.brand,
        model=vehicle.model,
        year=vehicle.year,
        monthly_rent=(
            vehicle.monthly_rent.value if vehicle.monthly_rent else Decimal("0.00")
        ),
        price=vehicle.price.value,
        mileage=vehicle.mileage.value,
        energy_type=vehicle.energy_type.value,
        description=vehicle.description,
        photo_url=None,
        included_services=[service.name for service in service_orms],
        services=services,
    )
