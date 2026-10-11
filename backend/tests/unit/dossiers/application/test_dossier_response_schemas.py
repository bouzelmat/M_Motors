from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from src.dossiers.application.schemas.dossier_response import (
    AdminDossierDetailResponse,
    DossierListItemResponse,
    DossierStatusResponse,
    FinancingPlanResponse,
    TradeInResponse,
)
from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.value_objects.dossier_status import DossierStatus


def test_client_dossier_list_response_maps_domain_entity() -> None:
    dossier = Dossier.create(user_id=uuid4(), vehicle_id=uuid4())

    response = DossierListItemResponse.model_validate(dossier)

    assert response.id == dossier.id
    assert response.vehicle_id == dossier.vehicle_id

    # L'ensemble des clés attendues est mis à jour pour inclure le champ
    # 'requested_document_types', reflétant l'évolution légitime du schéma.
    assert set(response.model_dump()) == {
        "id",
        "vehicle_id",
        "status",
        "requested_document_types",
        "created_at",
        "updated_at",
    }


def test_status_response_includes_nullable_decision_comment() -> None:
    response = DossierStatusResponse(
        status=DossierStatus.SUBMITTED,
        updated_at=datetime.now(timezone.utc),
        decision_comment=None,
    )

    assert response.model_dump(mode="json")["decision_comment"] is None


def test_admin_dossier_response_serializes_decimal_values_as_strings() -> None:
    now = datetime.now(timezone.utc)
    response = AdminDossierDetailResponse(
        id=uuid4(),
        user_id=uuid4(),
        client_email="client@example.com",
        vehicle_id=uuid4(),
        vehicle_brand="Peugeot",
        vehicle_model="208",
        vehicle_price=Decimal("15000.00"),
        status=DossierStatus.SUBMITTED,
        submitted_at=now,
        financing_plan=FinancingPlanResponse(
            down_payment=Decimal("2000.00"),
            duration_months=48,
            monthly_payment=Decimal("395.00"),
        ),
        trade_in=TradeInResponse(
            registration="AB-123-CD",
            mileage=50000,
            brand=None,
            model=None,
            estimated_value=Decimal("5000.00"),
        ),
        documents=[],
        created_at=now,
        updated_at=now,
    )

    serialized = response.model_dump(mode="json")

    assert isinstance(serialized["vehicle_price"], str)
    assert isinstance(serialized["financing_plan"]["down_payment"], str)
    assert isinstance(serialized["trade_in"]["estimated_value"], str)
