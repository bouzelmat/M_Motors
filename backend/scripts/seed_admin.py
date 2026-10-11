"""Script de seed idempotent pour créer un compte administrateur de développement/test.

Exécution :
    python scripts/seed_admin.py

Variables d'environnement optionnelles :
    SEED_ADMIN_EMAIL       (Défaut : admin@example.com)
    SEED_ADMIN_PASSWORD    (Défaut : Admin123!Secure)
    SEED_ADMIN_FIRST_NAME  (Défaut : Admin)
    SEED_ADMIN_LAST_NAME   (Défaut : System)
"""

import asyncio
import os
import sys
import uuid
from pathlib import Path

from sqlalchemy import update

# Ajouter la racine du backend au PYTHONPATH pour autoriser les imports src.*
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.auth.domain.entities.user import User
from src.auth.domain.value_objects.role import Role
from src.auth.domain.value_objects.email import Email
from src.auth.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from src.auth.infrastructure.orm.user_model import UserModel
from src.auth.infrastructure.security.password_service import PasswordService
from src.shared.infrastructure.database import get_session_factory


async def seed_admin() -> str:
    """Crée un compte utilisateur ADMIN de manière idempotente.

    Returns:
        str: Status de l'opération ('créé' ou 'déjà existant').
    """
    admin_email = os.getenv("SEED_ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("SEED_ADMIN_PASSWORD", "Admin123!Secure")
    first_name = os.getenv("SEED_ADMIN_FIRST_NAME", "Admin")
    last_name = os.getenv("SEED_ADMIN_LAST_NAME", "System")

    email_vo = Email(admin_email)
    session_factory = get_session_factory()

    async with session_factory() as session:
        repository = SQLAlchemyUserRepository(session)
        existing_user = await repository.find_by_email(email_vo)

        if existing_user is not None:
            if existing_user.role != Role.ADMIN:
                await session.execute(
                    update(UserModel)
                    .where(UserModel.id == str(existing_user.id))
                    .values(role=Role.ADMIN.value)
                )
                await session.commit()
                print(
                    f"Administrateur {admin_email} : rôle administrateur attribué au compte existant."
                )
                return "promu"

            print(f"Administrateur {admin_email} : déjà existant.")
            return "déjà existant"

        password_service = PasswordService()
        hashed_password = password_service.hash_password(admin_password)

        # Correction : Instanciation directe avec génération de l'UUID obligatoire
        admin_user = User(
            id=uuid.uuid4(),
            email=email_vo,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            role=Role.ADMIN,
        )

        await repository.save(admin_user)
        await session.commit()

        print(f"Administrateur {admin_email} : créé.")
        return "créé"


if __name__ == "__main__":
    asyncio.run(seed_admin())
