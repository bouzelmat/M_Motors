"""Routes de l'API REST pour le contexte Véhicules."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from src.shared.domain.exceptions import DomainError
from src.vehicles.api.dependencies import (
    check_toggle_feature_enabled,
    get_current_admin_user,
    get_toggle_vehicle_type_handler,
)
from src.vehicles.api.schemas.vehicle_schemas import (
    ToggleCatalogTypeRequest,
    VehicleResponse,
)
from src.vehicles.application.commands.toggle_vehicle_type import (
    ToggleVehicleTypeCommand,
    ToggleVehicleTypeCommandHandler,
)
from src.vehicles.application.exceptions import ActiveDossierWarningException

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.patch(
    "/{vehicle_id}/catalog-type",
    response_model=VehicleResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(get_current_admin_user),
        Depends(check_toggle_feature_enabled),
    ],
    summary="Bascule le mode commercial d'un véhicule (Vente <-> Location)",
)
async def toggle_catalog_type(
    vehicle_id: UUID,
    request: ToggleCatalogTypeRequest,
    handler: ToggleVehicleTypeCommandHandler = Depends(get_toggle_vehicle_type_handler),
) -> VehicleResponse:
    """Bascule automatiquement le mode commercial d'un véhicule.

    - Exige un compte administrateur.
    - Désactivé en production tant que le Feature Flag n'est pas activé.
    - Retourne un statut HTTP 409 si un dossier actif bloque la bascule sans confirmation.
    """
    command = ToggleVehicleTypeCommand(
        vehicle_id=vehicle_id,
        new_price=request.new_price,
        bypass_warning=request.confirm,
    )

    try:
        updated_vehicle = await handler.handle(command)
        return VehicleResponse.model_validate(updated_vehicle)

    except ActiveDossierWarningException as exc:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": str(exc),
                "vehicle_id": str(exc.vehicle_id),
                "requires_confirmation": True,
            },
        )
    except DomainError as exc:
        if "introuvable" in str(exc).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
