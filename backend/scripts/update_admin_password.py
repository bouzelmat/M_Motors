"""Script pour mettre à jour le mot de passe d'un utilisateur existant via variables d'environnement."""

import asyncio
import os
import sys
from pathlib import Path

from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError  # ✅ Ajout pour corriger BLE001

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.auth.domain.value_objects.email import Email
from src.auth.infrastructure.orm.user_model import UserModel
from src.auth.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from src.auth.infrastructure.security.password_service import PasswordService
from src.shared.infrastructure.database import get_session_factory


async def update_password() -> str:
    """Met à jour le mot de passe d'un utilisateur existant en base de données."""
    target_email = os.getenv("TARGET_EMAIL")
    new_password = os.getenv("NEW_PASSWORD")

    if not target_email:
        raise ValueError("❌ La variable d'environnement TARGET_EMAIL est obligatoire.")
    if not new_password:
        raise ValueError("❌ La variable d'environnement NEW_PASSWORD est obligatoire.")

    email_vo = Email(target_email)
    session_factory = get_session_factory()

    async with session_factory() as session:
        repository = SQLAlchemyUserRepository(session)
        user = await repository.find_by_email(email_vo)

        if not user:
            print(f"❌ Erreur : L'utilisateur {target_email} n'existe pas.")
            return "échec"

        password_service = PasswordService()
        new_hashed_password = password_service.hash_password(new_password)

        # ✅ CORRECTION CRITIQUE : Mise à jour explicite du modèle ORM pour garantir la persistance
        await session.execute(
            update(UserModel)
            .where(UserModel.id == str(user.id))
            .values(hashed_password=new_hashed_password)
        )

        try:
            await session.commit()
            print(
                f"✅ Succès : Le mot de passe de {target_email} a été mis à jour EN BASE DE DONNÉES."
            )
            return "succès"
        except (
            SQLAlchemyError
        ) as e:  # ✅ Correction de Ruff (Exception -> SQLAlchemyError)
            print(f"❌ Erreur lors de la mise à jour : {e}")
            await session.rollback()
            return "échec"


if __name__ == "__main__":
    asyncio.run(update_password())
