from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field

# Imports de sécurité globaux corrigés
from src.api.dependencies import require_role
from src.auth.domain.value_objects import Role
from src.auth.domain.entities.user import User
from src.shared.infrastructure.dependencies import SessionDep

from src.vehicles.application.use_cases.generate_presigned_url import (
    GeneratePresignedUploadUrlUseCase,
)
from src.vehicles.domain.exceptions import (
    FileSizeExceededError,
    InvalidImageFormatError,
    VehicleNotFoundError,
)
from src.vehicles.domain.entities.vehicle_photo import VehiclePhoto

# CORRECTION DE L'IMPORT : On cible le fichier dependencies du module vehicles
from src.vehicles.infrastructure.dependencies import (
    get_storage_service,
    get_vehicle_repository,
)
from src.vehicles.infrastructure.storage.s3_storage_service import S3StorageService

router = APIRouter(prefix="/api/v1/vehicles", tags=["Vehicle Photos"])


class PresignedUrlRequest(BaseModel):
    file_name: str = Field(..., json_schema_extra={"example": "front_view.jpg"})
    file_size: int = Field(..., gt=0, json_schema_extra={"example": 2048000})
    content_type: str = Field(..., json_schema_extra={"example": "image/jpeg"})


class PresignedUrlResponse(BaseModel):
    photo_id: UUID
    url: str
    fields: Dict[str, Any]


class ConfirmPhotoResponse(BaseModel):
    photo_id: UUID
    photo_url: str


class VehiclePhotoResponse(BaseModel):
    id: UUID
    photo_url: str
    is_primary: bool
    created_at: datetime
    uploaded_at: datetime | None


@router.get(
    "/{vehicle_id}/photos",
    response_model=list[VehiclePhotoResponse],
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def list_vehicle_photos(
    vehicle_id: UUID,
    storage_service: S3StorageService = Depends(get_storage_service),
    vehicle_repository=Depends(get_vehicle_repository),
) -> list[VehiclePhotoResponse]:
    """Retourne les photos confirmées d'un véhicule avec des URL de lecture fraîches."""
    if await vehicle_repository.find_by_id(vehicle_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Véhicule non trouvé"
        )

    photos: list[VehiclePhoto] = await vehicle_repository.list_uploaded_photos(
        vehicle_id
    )
    return [
        VehiclePhotoResponse(
            id=photo.id,
            photo_url=await storage_service.get_object_url(photo.object_key),
            is_primary=photo.is_primary,
            created_at=photo.created_at,
            uploaded_at=photo.uploaded_at,
        )
        for photo in photos
    ]


@router.patch(
    "/{vehicle_id}/photos/{photo_id}/primary",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def set_primary_vehicle_photo(
    vehicle_id: UUID,
    photo_id: UUID,
    session: SessionDep,
    vehicle_repository=Depends(get_vehicle_repository),
) -> Response:
    """Définit une photo confirmée comme couverture du véhicule."""
    if not await vehicle_repository.set_primary_photo(vehicle_id, photo_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo non trouvée"
        )
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/{vehicle_id}/photos/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
async def delete_vehicle_photo(
    vehicle_id: UUID,
    photo_id: UUID,
    session: SessionDep,
    storage_service: S3StorageService = Depends(get_storage_service),
    vehicle_repository=Depends(get_vehicle_repository),
) -> Response:
    """Supprime le fichier S3 et les métadonnées d'une photo du véhicule."""
    object_key = await vehicle_repository.delete_photo(vehicle_id, photo_id)
    if object_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo non trouvée"
        )
    await storage_service.delete_object(object_key)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{vehicle_id}/photos/presigned-url",
    response_model=PresignedUrlResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_photo_upload_url(
    vehicle_id: UUID,
    payload: PresignedUrlRequest,
    session: SessionDep,
    current_user: User = Depends(require_role(Role.ADMIN)),
    storage_service: S3StorageService = Depends(get_storage_service),
    # FastAPI injectera automatiquement la SessionDep requise par get_vehicle_repository
    vehicle_repository=Depends(get_vehicle_repository),
) -> PresignedUrlResponse:
    """Génère une URL pré-signée POST et ses signatures pour l'upload S3 (ADMIN uniquement)."""

    use_case = GeneratePresignedUploadUrlUseCase(
        storage_service=storage_service,
        vehicle_repository=vehicle_repository,
    )

    try:
        presigned_data = await use_case.execute(
            vehicle_id=vehicle_id,
            file_name=payload.file_name,
            file_size=payload.file_size,
            content_type=payload.content_type,
        )
        object_key = presigned_data["fields"]["key"]
        photo_url = await storage_service.get_object_url(object_key)
        photo = await vehicle_repository.create_pending_photo(
            vehicle_id=vehicle_id,
            object_key=object_key,
            photo_url=photo_url,
            content_type=payload.content_type,
            uploaded_by=current_user.id,
        )
        await session.commit()
        return PresignedUrlResponse(
            photo_id=photo.id,
            url=presigned_data["url"],
            fields=presigned_data["fields"],
        )
    except VehicleNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except InvalidImageFormatError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except FileSizeExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=str(exc),
        ) from exc


@router.post(
    "/{vehicle_id}/photos/{photo_id}/confirm",
    response_model=ConfirmPhotoResponse,
    status_code=status.HTTP_200_OK,
)
async def confirm_photo_upload(
    vehicle_id: UUID,
    photo_id: UUID,
    session: SessionDep,
    current_user: User = Depends(require_role(Role.ADMIN)),
    storage_service: S3StorageService = Depends(get_storage_service),
    vehicle_repository=Depends(get_vehicle_repository),
) -> ConfirmPhotoResponse:
    """Vérifie l'upload S3 et rend la photo visible dans le catalogue."""
    photo = await vehicle_repository.get_photo(vehicle_id, photo_id)
    if photo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photo non trouvée"
        )

    if not await storage_service.object_exists(photo.object_key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La photo n'est pas encore disponible dans le stockage.",
        )

    photo.photo_url = await storage_service.get_object_url(photo.object_key)
    await vehicle_repository.confirm_photo(photo)
    await session.commit()
    return ConfirmPhotoResponse(photo_id=photo.id, photo_url=photo.photo_url)
