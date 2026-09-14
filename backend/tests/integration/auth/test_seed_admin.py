"""Tests d'intégration pour le seed idempotent de l'administrateur."""

import os
import pytest
from sqlalchemy import select

from scripts.seed_admin import seed_admin
from src.auth.domain.value_objects import Email, Role
from src.auth.infrastructure.orm.user_model import UserModel
from src.auth.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from src.auth.infrastructure.security.password_service import PasswordService


@pytest.mark.asyncio
async def test_seed_admin_is_idempotent_and_creates_valid_admin(db_session):
    test_email = "test.admin.seed@example.com"
    test_password = "Password123!Test"

    # Injection des variables d'environnement de test
    os.environ["SEED_ADMIN_EMAIL"] = test_email
    os.environ["SEED_ADMIN_PASSWORD"] = test_password
    os.environ["SEED_ADMIN_FIRST_NAME"] = "Test"
    os.environ["SEED_ADMIN_LAST_NAME"] = "Admin"

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
