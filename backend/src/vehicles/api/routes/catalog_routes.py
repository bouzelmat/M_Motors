"""Endpoints publics et d'administration pour le catalogue véhicules."""

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from src.auth.api.dependencies import require_role
from src.auth.domain.value_objects import Role
from src.auth.domain.entities.user import User
from src.shared.domain.exceptions import DomainError, NotFoundError
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
    VehicleServiceSelection,
)
from src.vehicles.application.commands.manage_vehicles import (
    DeleteVehicleCommand,
    DeleteVehicleCommandHandler,
    UpdateVehicleCommand,
    UpdateVehicleCommandHandler,
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
    get_delete_vehicle_command_handler,
    get_search_vehicles_query_handler,
    get_vehicle_detail_handler,
    get_vehicle_repository,
    get_update_vehicle_command_handler,
)
from src.vehicles.domain.ports.vehicle_repository import VehicleRepository

router = APIRouter(prefix="/api/v1/vehicles", tags=["vehicles"])


@router.get(
    "/admin",
    response_model=list[VehicleResponse],
    dependencies=[Depends(require_role(Role.ADMIN))],
    summary="Lister tous les véhicules pour l'administration",
)
async def list_all_vehicles(
    repository: VehicleRepository = Depends(get_vehicle_repository),
) -> list[VehicleResponse]:
    """Retourne les véhicules de tous les statuts au back-office."""
    vehicles = await repository.list_all()
    return [VehicleResponse.model_validate(vehicle) for vehicle in vehicles]


@router.get(
    "/admin/{vehicle_id}",
    response_model=VehicleDetailDTO,
    dependencies=[Depends(require_role(Role.ADMIN))],
    summary="Consulter un véhicule dans l'administration",
)
async def get_admin_vehicle(
    vehicle_id: UUID,
    repository: VehicleRepository = Depends(get_vehicle_repository),
) -> VehicleDetailDTO:
    """Retourne les détails d'un véhicule, même s'il n'est pas disponible."""
    result = await repository.find_by_id_with_services(vehicle_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Véhicule non trouvé"
        )
    vehicle, _ = result
    return VehicleDetailDTO(
        id=vehicle.id,
        brand=vehicle.brand,
        model=vehicle.model,
        year=vehicle.year,
        catalog_type=vehicle.catalog_type,
        monthly_rent=vehicle.monthly_rent.value if vehicle.monthly_rent else None,
        price=vehicle.price.value if vehicle.price else None,
        mileage=vehicle.mileage.value,
        energy_type=vehicle.energy_type.value,
        description=vehicle.description,
        photo_url=vehicle.photo_url,
        included_services=[
            service.name for service in vehicle.services if service.included
        ],
        services=[
            ServiceDTO(
                id=service.service_id,
                name=service.name,
                monthly_cost=service.monthly_cost,
                category=service.category.value,
                included=service.included,
            )
            for service in vehicle.services
        ],
    )


@router.put(
    "/admin/{vehicle_id}",
    response_model=VehicleResponse,
    dependencies=[Depends(require_role(Role.ADMIN))],
    summary="Modifier un véhicule",
)
async def update_vehicle(
    vehicle_id: UUID,
    payload: CreateVehicleRequest,
    handler: UpdateVehicleCommandHandler = Depends(get_update_vehicle_command_handler),
) -> VehicleResponse:
    """Remplace les caractéristiques modifiables d'un véhicule existant."""
    command = UpdateVehicleCommand(
        vehicle_id=vehicle_id,
        brand=payload.brand,
        model=payload.model,
        year=payload.year,
        mileage=payload.mileage,
        energy_type=payload.energy_type,
        catalog_type=payload.catalog_type,
        price=payload.price,
        monthly_rent=payload.monthly_rent,
        description=payload.description,
        services=tuple(
            VehicleServiceSelection(service_id=item.service_id, included=item.included)
            for item in payload.services
        ),
    )
    try:
        vehicle = await handler.handle(command)
        return VehicleResponse.model_validate(vehicle)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        ) from exc
    except DomainError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid vehicle data",
        ) from exc


@router.delete(
    "/admin/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(Role.ADMIN))],
    summary="Supprimer un véhicule",
)
async def delete_vehicle(
    vehicle_id: UUID,
    handler: DeleteVehicleCommandHandler = Depends(get_delete_vehicle_command_handler),
) -> Response:
    """Supprime un véhicule existant et ses photos/services associés."""
    try:
        await handler.handle(DeleteVehicleCommand(vehicle_id=vehicle_id))
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
        pattern="^(rental|sale|purchase)$",
        description="Mode de catalogue : rental ou sale (purchase est accepté comme alias)",
    ),
    brand: str | None = Query(default=None, description="Marque du véhicule"),
    max_price: Decimal | None = Query(
        default=None, description="Prix de vente maximum"
    ),
    max_mileage: int | None = Query(default=None, description="Kilométrage maximum"),
    fuel_type: str | None = Query(default=None, description="Type d'énergie"),
    max_monthly_rent: Decimal | None = Query(
        default=None, description="Loyer mensuel maximum"
    ),
    handler: SearchVehiclesQueryHandler = Depends(get_search_vehicles_query_handler),
) -> list[VehicleListItemDTO]:
    """Retourne les véhicules disponibles selon les critères."""
    search_mode = "sale" if mode == "purchase" else mode
    criteria = VehicleSearchCriteria(
        mode=search_mode,
        brand=brand,
        max_price=max_price,
        max_mileage=max_mileage,
        fuel_type=fuel_type,
        max_monthly_rent=max_monthly_rent,
    )
    vehicles = await handler.handle(SearchVehiclesQuery(criteria=criteria))
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
    "/services",
    response_model=list[ServiceDTO],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def list_service_options(
    repository: VehicleRepository = Depends(get_vehicle_repository),
) -> list[ServiceDTO]:
    """Retourne le catalogue de services sélectionnable par un administrateur."""
    services = await repository.list_service_catalog()
    return [
        ServiceDTO(
            id=service.service_id,
            name=service.name,
            monthly_cost=service.monthly_cost,
            category=service.category.value,
            included=False,
        )
        for service in services
    ]


@router.get(
    "/{vehicle_id}",
    response_model=VehicleDetailDTO,
    status_code=status.HTTP_200_OK,
    summary="Détails d'un véhicule",
)
async def get_vehicle_detail(
    vehicle_id: UUID,
    handler: GetVehicleDetailQueryHandler = Depends(get_vehicle_detail_handler),
) -> VehicleDetailDTO:
    """Retourne les informations détaillées d'un véhicule."""
    query = GetVehicleDetailQuery(vehicle_id=vehicle_id)
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
        catalog_type=vehicle.catalog_type,
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
    current_user: User = Depends(require_role(Role.ADMIN)),
    handler: AddVehicleCommandHandler = Depends(get_add_vehicle_command_handler),
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
        services=tuple(
            VehicleServiceSelection(
                service_id=service.service_id,
                included=service.included,
            )
            for service in payload.services
        ),
    )
    try:
        created_vehicle = await handler.handle(command)
        return VehicleResponse.model_validate(created_vehicle)
    except DomainError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid vehicle data",
        ) from err
