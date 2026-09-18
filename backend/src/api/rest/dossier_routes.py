"""Routes HTTP FastAPI pour l'API dossiers."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_current_user
from src.dossiers.application.use_cases.create_dossier import (
    CreateDossierCommand,
    CreateDossierCommandHandler,
    FinancingPlanDTO,
    TradeInDTO,
)
from src.dossiers.domain.exceptions import (
    VehicleNotAvailableException,
    VehicleNotFoundException,
)
from src.dossiers.application.schemas.dossier_schemas import (
    CreateDossierRequest,
    DossierResponse,
)
from src.auth.domain.entities.user import User

router = APIRouter(prefix="/api/v1/dossiers", tags=["dossiers"])


@router.post(
    "",
    response_model=DossierResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_dossier(
    request: CreateDossierRequest,
    current_user: User = Depends(get_current_user),
) -> DossierResponse:
    """Endpoint de création d'un dossier véhicule."""
    trade_in_dto = None
    if request.trade_in is not None:
        trade_in_dto = TradeInDTO(
            registration=request.trade_in.registration,
            mileage=request.trade_in.mileage,
            brand=request.trade_in.brand,
            model=request.trade_in.model,
        )

    financing_dto = None
    if request.financing_plan is not None:
        financing_dto = FinancingPlanDTO(
            down_payment=request.financing_plan.down_payment,
            duration_months=request.financing_plan.duration_months,
            monthly_payment=request.financing_plan.monthly_payment,
        )

    command = CreateDossierCommand(
        user_id=current_user.id,
        vehicle_id=request.vehicle_id,
        trade_in=trade_in_dto,
        financing_plan=financing_dto,
    )

    # TODO: Implement handler dependency injection
    # dossier = await handler(command)
    # return DossierResponse.model_validate(dossier)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Dossier creation not yet implemented",
    )
