from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.vehicles.api.schemas.vehicle_schemas import ToggleCatalogTypeRequest


def test_toggle_catalog_type_request_valid_default_confirm() -> None:
    """Scénario : Requête valide, confirmation par défaut (confirm=False)."""
    dto = ToggleCatalogTypeRequest(new_price=Decimal("600.00"))

    assert dto.new_price == Decimal("600.00")
    assert dto.confirm is False


def test_toggle_catalog_type_request_valid_explicit_confirm() -> None:
    """Scénario : Requête valide, confirmation explicite (confirm=True)."""
    dto = ToggleCatalogTypeRequest(new_price=Decimal("25000.00"), confirm=True)

    assert dto.new_price == Decimal("25000.00")
    assert dto.confirm is True


def test_toggle_catalog_type_request_missing_new_price() -> None:
    """Scénario : new_price manquant -> ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        ToggleCatalogTypeRequest.model_validate({})

    errors = exc_info.value.errors()
    assert any(err["loc"] == ("new_price",) for err in errors)


@pytest.mark.parametrize("invalid_price", [Decimal("0"), Decimal("-100.00")])
def test_toggle_catalog_type_request_zero_or_negative_price(
    invalid_price: Decimal,
) -> None:
    """Scénario : new_price nul ou négatif (contrainte gt=0) -> ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        ToggleCatalogTypeRequest(new_price=invalid_price)

    errors = exc_info.value.errors()
    assert any(err["loc"] == ("new_price",) for err in errors)


def test_toggle_catalog_type_request_non_numeric_price() -> None:
    """Scénario : new_price non numérique ("abc") -> ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        ToggleCatalogTypeRequest.model_validate({"new_price": "abc"})

    errors = exc_info.value.errors()
    assert any(err["loc"] == ("new_price",) for err in errors)
