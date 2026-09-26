from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import asyncio

from src.shared.infrastructure.scheduler import (
    JOB_ID_PURGE,
    ApplicationScheduler,
    run_purge_job,
)


def test_scheduler_job_registration():
    scheduler_mgr = ApplicationScheduler()
    scheduler_mgr.configure_jobs()

    job = scheduler_mgr.scheduler.get_job(JOB_ID_PURGE)
    assert job is not None
    assert str(job.trigger) == "cron[hour='3', minute='0']"


@pytest.mark.asyncio
async def test_scheduler_start_stop_and_no_double_registration():
    scheduler_mgr = ApplicationScheduler()
    scheduler_mgr.start()
    assert scheduler_mgr.scheduler.running

    scheduler_mgr.configure_jobs()
    jobs = scheduler_mgr.scheduler.get_jobs()
    assert len([j for j in jobs if j.id == JOB_ID_PURGE]) == 1

    scheduler_mgr.shutdown()
    await asyncio.sleep(0)  # Laisse le temps à l'event loop d'enregistrer l'arrêt
    assert not scheduler_mgr.scheduler.running


@pytest.mark.asyncio
@patch("src.shared.infrastructure.scheduler.get_session_factory")
@patch("src.shared.infrastructure.scheduler.PurgeRejectedDossiersUseCase")
async def test_run_purge_job_orchestration(mock_use_case_cls, mock_get_session_factory):
    # 1. Création du mock de session SQLAlchemy
    mock_session = AsyncMock()

    # 2. Mock du context manager async (`async with session_factory() as session:`)
    mock_factory_instance = MagicMock()
    mock_factory_instance.return_value.__aenter__.return_value = mock_session
    mock_get_session_factory.return_value = mock_factory_instance

    # 3. Mock de l'instance du cas d'usage
    mock_use_case_instance = AsyncMock()
    mock_use_case_cls.return_value = mock_use_case_instance

    # Exécution de la fonction à tester
    await run_purge_job()

    # Vérifications
    mock_get_session_factory.assert_called_once()
    mock_use_case_cls.assert_called_once()
    mock_use_case_instance.execute.assert_called_once_with(days=30)
