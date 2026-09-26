"""Cas de lecture pour le détail d'un dossier côté administrateur."""

from src.auth.domain.ports.user_repository import UserRepository
from src.dossiers.application.queries.get_admin_dossier_detail import (
    GetAdminDossierDetailQuery,
)
from src.dossiers.application.queries.read_models import (
    AdminDossierDetailReadModel,
    DocumentReadModel,
)
from src.dossiers.domain.ports.document_repository import DocumentRepository
from src.dossiers.domain.ports.dossier_repository import DossierRepository
from src.shared.domain.exceptions import NotFoundError
from src.vehicles.domain.ports.vehicle_repository import VehicleRepository


class GetAdminDossierDetailUseCase:
    """Assemble le détail complet d'un dossier pour l'administration.

    Ce use case compose les données de plusieurs bounded contexts :
    - Dossier (agrégat principal avec financing_plan et trade_in)
    - User (email du client)
    - Vehicle (marque, modèle, prix)
    - Documents (liste des pièces justificatives)
    """

    def __init__(
        self,
        dossier_repository: DossierRepository,
        user_repository: UserRepository,
        vehicle_repository: VehicleRepository,
        document_repository: DocumentRepository,
    ) -> None:
        self._dossier_repository = dossier_repository
        self._user_repository = user_repository
        self._vehicle_repository = vehicle_repository
        self._document_repository = document_repository

    async def execute(
        self, query: GetAdminDossierDetailQuery
    ) -> AdminDossierDetailReadModel:
        """Exécute la lecture du détail d'un dossier."""
        dossier = await self._dossier_repository.get_by_id(query.dossier_id)
        if dossier is None:
            raise NotFoundError(f"Dossier {query.dossier_id} introuvable.")

        user = await self._user_repository.find_by_id(dossier.user_id)
        if user is None:
            raise NotFoundError(f"Utilisateur {dossier.user_id} introuvable.")

        vehicle = await self._vehicle_repository.find_by_id(dossier.vehicle_id)
        if vehicle is None:
            raise NotFoundError(f"Véhicule {dossier.vehicle_id} introuvable.")

        documents = await self._document_repository.find_by_dossier(dossier.id)
        document_read_models = [
            DocumentReadModel(
                id=doc.id,
                type=doc.type.value if hasattr(doc.type, "value") else str(doc.type),
                status=(
                    doc.status.value
                    if hasattr(doc.status, "value")
                    else str(doc.status)
                ),
                original_filename=doc.original_filename,
                content_type=doc.content_type,
                size=doc.size,
                created_at=doc.created_at,
                uploaded_at=doc.uploaded_at,
            )
            for doc in documents
        ]

        return AdminDossierDetailReadModel(
            id=dossier.id,
            user_id=dossier.user_id,
            client_email=(
                user.email.value if hasattr(user.email, "value") else str(user.email)
            ),
            vehicle_id=dossier.vehicle_id,
            vehicle_brand=vehicle.brand,
            vehicle_model=vehicle.model,
            vehicle_price=vehicle.price if hasattr(vehicle, "price") else None,
            status=dossier.status,
            submitted_at=dossier.submitted_at,
            financing_plan=dossier.financing_plan,
            trade_in=dossier.trade_in,
            documents=document_read_models,
            comment=dossier.comment,
            rejection_reason=dossier.rejection_reason,
            requested_document_types=dossier.requested_document_types,
            rejected_at=dossier.rejected_at,
            created_at=dossier.created_at,
            updated_at=dossier.updated_at,
        )
