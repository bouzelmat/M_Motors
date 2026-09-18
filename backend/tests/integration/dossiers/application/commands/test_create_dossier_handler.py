"""Tests unitaires du handler de création de dossier."""

from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.dossiers.application.ports.vehicle_availability_port import VehicleAvailabilityPort
from src.dossiers.application.use_cases.create_dossier import (
    CreateDossierCommand,
    CreateDossierCommandHandler,
    FinancingPlanDTO,
    TradeInDTO,
)
from src.dossiers.domain.events.dossier_initialized import DossierInitialized
from src.dossiers.domain.exceptions import (
    VehicleNotAvailableException,
    VehicleNotFoundException,
)
from src.dossiers.domain.value_objects.dossier_status import DossierStatus


@pytest.fixture
def mock_uow() -> AsyncMock:
    uow = AsyncMock()
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow


@pytest.fixture
def mock_vehicle_port() -> AsyncMock:
    port = AsyncMock(spec=VehicleAvailabilityPort)
    port.exists.return_value = True
    port.is_available.return_value = True
    return port


@pytest.fixture
def mock_event_bus() -> AsyncMock:
    return AsyncMock()


@pytest.mark.asyncio
async def test_create_minimal_dossier_success(
    mock_uow: AsyncMock,
    mock_vehicle_port: AsyncMock,
    mock_event_bus: AsyncMock,
) -> None:
    handler = CreateDossierCommandHandler(mock_uow, mock_vehicle_port, mock_event_bus)
    user_id = uuid4()
    vehicle_id = uuid4()
    command = CreateDossierCommand(user_id=user_id, vehicle_id=vehicle_id)

    dossier = await handler(command)

    assert dossier.user_id == user_id
    assert dossier.vehicle_id == vehicle_id
    assert dossier.status == DossierStatus.DRAFT
    assert dossier.trade_in is None
    assert dossier.financing_plan is None

    mock_uow.dossiers.save.assert_called_once_with(dossier)
    mock_uow.commit.assert_called_once()
    mock_event_bus.publish.assert_called_once()
    event = mock_event_bus.publish.call_args[0][0]
    assert isinstance(event, DossierInitialized)
    assert event.dossier_id == dossier.id


@pytest.mark.asyncio
async def test_create_dossier_with_trade_in_and_financing(
    mock_uow: AsyncMock,
    mock_vehicle_port: AsyncMock,
    mock_event_bus: AsyncMock,
) -> None:
    handler = CreateDossierCommandHandler(mock_uow, mock_vehicle_port, mock_event_bus)
    command = CreateDossierCommand(
        user_id=uuid4(),
        vehicle_id=uuid4(),
        trade_in=TradeInDTO(registration="AB-123-CD", mileage=10000),
        financing_plan=FinancingPlanDTO(
            down_payment=Decimal("100.00"),
            duration_months=12,
            monthly_payment=Decimal("50.00"),
        ),
    )

    dossier = await handler(command)

    assert dossier.trade_in is not None
    assert dossier.trade_in.registration == "AB-123-CD"
    assert dossier.financing_plan is not None
    assert dossier.financing_plan.duration_months == 12


@pytest.mark.asyncio
async def test_create_dossier_vehicle_not_found_raises(
    mock_uow: AsyncMock,
    mock_vehicle_port: AsyncMock,
    mock_event_bus: AsyncMock,
) -> None:
    mock_vehicle_port.exists.return_value = False
    handler = CreateDossierCommandHandler(mock_uow, mock_vehicle_port, mock_event_bus)
    command = CreateDossierCommand(user_id=uuid4(), vehicle_id=uuid4())

    with pytest.raises(VehicleNotFoundException):
        await handler(command)

    mock_uow.dossiers.save.assert_not_called()


@pytest.mark.asyncio
async def test_create_dossier_vehicle_not_available_raises(
    mock_uow: AsyncMock,
    mock_vehicle_port: AsyncMock,
    mock_event_bus: AsyncMock,
) -> None:
    mock_vehicle_port.is_available.return_value = False
    handler = CreateDossierCommandHandler(mock_uow, mock_vehicle_port, mock_event_bus)
    command = CreateDossierCommand(user_id=uuid4(), vehicle_id=uuid4())

    with pytest.raises(VehicleNotAvailableException):
        await handler(command)

    mock_uow.dossiers.save.assert_not_called()