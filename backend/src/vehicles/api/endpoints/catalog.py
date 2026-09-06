"""Endpoints publics pour le catalogue véhicules."""

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.vehicles.api.schemas.vehicle_schemas import (
    ServiceDTO,
    VehicleDetailDTO,
    VehicleListItemDTO,
)
from src.vehicles.application.queries.get_vehicle_detail_query import (
    GetVehicleDetailQuery,
    GetVehicleDetailQueryHandler,
)
from src.vehicles.application.queries.search_vehicles_query import (
    SearchVehiclesQuery,
    SearchVehiclesQueryHandler,
)
from src.vehicles.domain.value_objects.vehicle_search_criteria import (
    VehicleSearchCriteria,
)
from src.vehicles.infrastructure.dependencies import (
    get_search_vehicles_query_handler,
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
    summary="Catalogue des véhicules disponibles",
    description=(
        "Retourne la liste des véhicules disponibles selon "
        "les critères de recherche."
    ),
)
async def list_vehicles(
    mode: str = Query(
        default="rental",
        pattern="^(rental|sale)$",
        description="Mode de catalogue : rental ou sale",
    ),
    brand: str | None = Query(
        default=None,
        description="Marque du véhicule",
    ),
    max_price: Decimal | None = Query(
        default=None,
        description="Prix de vente maximum",
    ),
    max_mileage: int | None = Query(
        default=None,
        description="Kilométrage maximum",
    ),
    fuel_type: str | None = Query(
        default=None,
        description="Type d'énergie",
    ),
    max_monthly_rent: Decimal | None = Query(
        default=None,
        description="Loyer mensuel maximum",
    ),
    handler: SearchVehiclesQueryHandler = Depends(
        get_search_vehicles_query_handler,
    ),
) -> list[VehicleListItemDTO]:
    """Retourne les véhicules disponibles selon les critères."""

    criteria = VehicleSearchCriteria(
        mode=mode,
        brand=brand,
        max_price=max_price,
        max_mileage=max_mileage,
        fuel_type=fuel_type,
        max_monthly_rent=max_monthly_rent,
    )

    vehicles = await handler.handle(
        SearchVehiclesQuery(criteria=criteria),
    )

    return [
        VehicleListItemDTO(
            id=vehicle.id,
            brand=vehicle.brand,
            model=vehicle.model,
            year=vehicle.year,
            monthly_rent=(
                vehicle.monthly_rent.value
                if vehicle.monthly_rent
                else Decimal("0.00")
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
            id=service.service_id,
            name=service.name,
            monthly_cost=service.monthly_cost,
            category=service.category.value,
            included=service.included,
        )
        for service in vehicle.services
    ]

    return VehicleDetailDTO(
        id=vehicle.id,
        brand=vehicle.brand,
        model=vehicle.model,
        year=vehicle.year,
        monthly_rent=(
            vehicle.monthly_rent.value
            if vehicle.monthly_rent
            else Decimal("0.00")
        ),
        price=vehicle.price.value,
        mileage=vehicle.mileage.value,
        energy_type=vehicle.energy_type.value,
        description=vehicle.description,
        photo_url=None,
        included_services=[
            service.name
            for service in vehicle.services
            if service.included
        ],
        services=services,
    )