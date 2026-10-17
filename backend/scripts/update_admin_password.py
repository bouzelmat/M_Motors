"""Script pour mettre à jour le mot de passe d'un utilisateur existant via variables d'environnement."""

import asyncio
import os
import sys
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from src.auth.infrastructure.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from src.auth.infrastructure.security.password_service import PasswordService
from src.auth.domain.value_objects.email import Email
from src.shared.infrastructure.database import get_session_factory


async def update_password() -> str:
    """Met à jour le mot de passe d'un utilisateur existant."""
    # --- 1. Récupération des variables d'environnement (OBLIGATOIRES) ---
    target_email = os.getenv("TARGET_EMAIL")
    new_password = os.getenv("NEW_PASSWORD")

    if not target_email:
        raise ValueError("❌ La variable d'environnement TARGET_EMAIL est obligatoire.")
    if not new_password:
        raise ValueError("❌ La variable d'environnement NEW_PASSWORD est obligatoire.")

    # --- 2. Validation de l'email ---
    email_vo = Email(target_email)
    session_factory = get_session_factory()

    # --- 3. Recherche de l'utilisateur ---
    async with session_factory() as session:
        repository = SQLAlchemyUserRepository(session)
        user = await repository.find_by_email(email_vo)

        if not user:
            print(f"❌ Erreur : L'utilisateur {target_email} n'existe pas.")
            return "échec"

        # --- 4. Hachage et mise à jour ---
        password_service = PasswordService()
        new_hashed_password = password_service.hash_password(new_password)
        user.hashed_password = new_hashed_password

        try:
            await session.commit()
            print(f"✅ Succès : Le mot de passe de {target_email} a été mis à jour.")
            return "succès"
        except SQLAlchemyError as e:
            print(f"❌ Erreur lors de la mise à jour : {e}")
            await session.rollback()
            return "échec"


if __name__ == "__main__":
    asyncio.run(update_password())
