"""Tests d'intégration pour le seed idempotent de l'administrateur."""

import os
from contextlib import asynccontextmanager
from uuid import uuid4

import pytest
from sqlalchemy import select

import scripts.seed_admin as seed_admin_script
from scripts.seed_admin import seed_admin
from src.auth.domain.value_objects import Email, Role
from src.auth.infrastructure.orm.user_model import UserModel
from src.auth.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from src.auth.infrastructure.security.password_service import PasswordService


def bind_seed_to_test_session(monkeypatch, db_session):
    @asynccontextmanager
    async def session_context():
        yield db_session

    monkeypatch.setattr(
        seed_admin_script, "get_session_factory", lambda: session_context
    )


@pytest.mark.asyncio
async def test_seed_admin_is_idempotent_and_creates_valid_admin(
    db_session, monkeypatch
):
    test_email = "test.admin.seed@example.com"
    test_password = "Password123!Test"

    # Injection des variables d'environnement de test
    os.environ["SEED_ADMIN_EMAIL"] = test_email
    os.environ["SEED_ADMIN_PASSWORD"] = test_password
    os.environ["SEED_ADMIN_FIRST_NAME"] = "Test"
    os.environ["SEED_ADMIN_LAST_NAME"] = "Admin"
    bind_seed_to_test_session(monkeypatch, db_session)

    try:
        # Première exécution du seed -> Création du compte
        result_first_run = await seed_admin()
        assert result_first_run == "créé"

        # Seconde exécution du seed -> Idempotence (ne crée rien)
        result_second_run = await seed_admin()
        assert result_second_run == "déjà existant"

        # Vérification en base de données qu'un seul utilisateur existe avec cet email
        db_result = await db_session.execute(
            select(UserModel).where(UserModel.email == test_email)
        )
        users = db_result.scalars().all()
        assert len(users) == 1

        # Vérification du rôle et du mot de passe
        repo = SQLAlchemyUserRepository(db_session)
        user = await repo.find_by_email(Email(test_email))
        assert user is not None
        assert user.role == Role.ADMIN

        password_service = PasswordService()
        assert password_service.verify_password(test_password, user.hashed_password)

    finally:
        # Nettoyage des variables d'environnement modifiées
        os.environ.pop("SEED_ADMIN_EMAIL", None)
        os.environ.pop("SEED_ADMIN_PASSWORD", None)
        os.environ.pop("SEED_ADMIN_FIRST_NAME", None)
        os.environ.pop("SEED_ADMIN_LAST_NAME", None)


@pytest.mark.asyncio
async def test_seed_admin_promotes_existing_client_account(db_session, monkeypatch):
    test_email = "test.admin.promote@example.com"
    client = UserModel(
        id=uuid4(),
        email=test_email,
        hashed_password="existing-password-hash",
        first_name="Existing",
        last_name="Client",
        role="CLIENT",
        is_active=True,
    )
    db_session.add(client)
    await db_session.commit()
    os.environ["SEED_ADMIN_EMAIL"] = test_email
    bind_seed_to_test_session(monkeypatch, db_session)

    try:
        result = await seed_admin()
        assert result == "promu"

        db_result = await db_session.execute(
            select(UserModel).where(UserModel.email == test_email)
        )
        user = db_result.scalar_one()
        assert user.role == Role.ADMIN.value
        assert user.hashed_password == "existing-password-hash"
    finally:
        os.environ.pop("SEED_ADMIN_EMAIL", None)
