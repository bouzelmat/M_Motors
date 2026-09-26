from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.dossiers.domain.entities.dossier import Dossier
from src.dossiers.domain.value_objects.dossier_status import DossierStatus
from src.dossiers.infrastructure.repository.sqlalchemy_dossier_repository import (
    SQLAlchemyDossierRepository,
)


@pytest.mark.asyncio
async def test_find_rejected_since_filters_correctly(db_session: AsyncSession):
    repo = SQLAlchemyDossierRepository(db_session)
    now = datetime.now(timezone.utc)

    # Dossiers de test
    d_29 = Dossier(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.REJECTED,
        rejected_at=now - timedelta(days=29),
    )
    d_30 = Dossier(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.REJECTED,
        rejected_at=now - timedelta(days=30),
    )
    d_31 = Dossier(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.REJECTED,
        rejected_at=now - timedelta(days=31),
    )
    d_validated = Dossier(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.VALIDATED,
        rejected_at=now - timedelta(days=40),
    )
    d_no_rejected_at = Dossier(
        id=uuid4(),
        user_id=uuid4(),
        vehicle_id=uuid4(),
        status=DossierStatus.REJECTED,
        rejected_at=None,
    )

    await repo.save(d_29)
    await repo.save(d_30)
    await repo.save(d_31)
    await repo.save(d_validated)
    await repo.save(d_no_rejected_at)
    await db_session.commit()

    results = await repo.find_rejected_since(30)
    result_ids = [d.id for d in results]

    assert d_30.id in result_ids
    assert d_31.id in result_ids
    assert d_29.id not in result_ids
    assert d_validated.id not in result_ids
    assert d_no_rejected_at.id not in result_ids
