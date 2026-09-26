"""Endpoints publics et d'administration pour le catalogue véhicules."""

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

# Remplacement de l'import erroné par le système générique de rôles
from src.api.dependencies import require_role
from src.auth.domain.value_objects import Role
from src.auth.domain.entities.user import User
from src.shared.domain.exceptions import DomainError
from src.vehicles.api.schemas.vehicle_schemas import (
    CreateVehicleRequest,
    ServiceDTO,
    VehicleDetailDTO,
    VehicleListItemDTO,
    VehicleResponse,
)
from src.vehicles.application.commands.add_vehicle import (
    AddVehicleCommand,
    AddVehicleCommandHandler,
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
    get_add_vehicle_command_handler,
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
                vehicle.monthly_rent.value if vehicle.monthly_rent else Decimal("0.00")
            ),
            photo_url=vehicle.photo_url,
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

    if not (vehicle.is_available_for_rental() or vehicle.is_available_for_sale()):
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
            vehicle.monthly_rent.value if vehicle.monthly_rent else Decimal("0.00")
        ),
        price=vehicle.price.value if vehicle.price else None,
        mileage=vehicle.mileage.value,
        energy_type=vehicle.energy_type.value,
        description=vehicle.description,
        photo_url=vehicle.photo_url,
        included_services=[
            service.name for service in vehicle.services if service.included
        ],
        services=services,
    )


@router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un véhicule au catalogue",
    description="Permet à un administrateur d'ajouter un nouveau véhicule.",
)
async def add_vehicle(
    payload: CreateVehicleRequest,
    # Utilisation de require_role(Role.ADMIN) validée par notre architecture globale
    current_user: User = Depends(require_role(Role.ADMIN)),
    handler: AddVehicleCommandHandler = Depends(
        get_add_vehicle_command_handler,
    ),
) -> VehicleResponse:
    """Ajoute un véhicule dans le système."""
    command = AddVehicleCommand(
        brand=payload.brand,
        model=payload.model,
        year=payload.year,
        mileage=payload.mileage,
        energy_type=payload.energy_type,
        catalog_type=payload.catalog_type,
        price=payload.price,
        monthly_rent=payload.monthly_rent,
        description=payload.description,
    )

    try:
        created_vehicle = await handler.handle(command)
        return VehicleResponse.model_validate(created_vehicle)
    except DomainError as err:
        # Aligné sur 422 Unprocessable Entity demandé par le ticket en cas de données invalides
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err),
        ) from err
