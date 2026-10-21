from src.migration.pipeline import _energy, _normalise_enum, _decimal, VALID_CATALOG_TYPES


def test_legacy_energy_is_mapped_to_real_enum():
    assert _energy("GASOLINE") == "ESSENCE"
    assert _energy("electric") == "ELECTRIQUE"


def test_rental_requires_monthly_rent():
    try:
        _decimal(None, "monthly_rent", required=True)
    except ValueError as exc:
        assert "obligatoire" in str(exc)
    else:
        raise AssertionError("A missing RENTAL rent must be rejected")


def test_catalog_type_is_strict():
    assert _normalise_enum(" rental ", "catalog_type", VALID_CATALOG_TYPES) == "RENTAL"

