import { apiClient } from "../../shared/infrastructure/http/apiClient";
import axios from "axios";
import {
    ConfirmPhotoUploadDTO,
    CreateVehicleRequestDTO,
    GetCatalogParams,
    PresignedPhotoUploadDTO,
    ServiceDTO,
    VehicleCreatedDTO,
    VehicleDetailDTO,
    VehicleListItemDTO,
    VehicleResponseDTO,
    VehiclePhotoDTO,
} from "./dto/vehicle.dto";

/** Client HTTP du contexte Vehicles. */
export class VehiclesClient {
    private static readonly BASE_URL = "/api/v1/vehicles";

    /**
     * Crée un nouveau véhicule dans le catalogue (Rôle ADMIN).
     */
    async createVehicle(
        payload: CreateVehicleRequestDTO,
    ): Promise<VehicleCreatedDTO> {
        const response = await apiClient.post<VehicleCreatedDTO>(
            VehiclesClient.BASE_URL,
            payload,
        );
        return response.data;
    }

    /**
     * Récupère le catalogue des véhicules avec les filtres optionnels.
     */
    async getCatalog(
        params: GetCatalogParams,
    ): Promise<VehicleListItemDTO[]> {
        const response = await apiClient.get<VehicleListItemDTO[]>(
            VehiclesClient.BASE_URL,
            {
                params,
            },
        );

        return response.data;
    }

    /**
     * Récupère les détails d'un véhicule.
     */
    async getVehicleDetail(
        id: string,
    ): Promise<VehicleDetailDTO> {
        const response = await apiClient.get<VehicleDetailDTO>(
            `${VehiclesClient.BASE_URL}/${id}`,
        );

        return response.data;
    }

    /** Liste tous les véhicules, quel que soit leur statut (administration). */
    async getAdminVehicles(): Promise<VehicleResponseDTO[]> {
        const response = await apiClient.get<VehicleResponseDTO[]>(
            `${VehiclesClient.BASE_URL}/admin`,
        );
        return response.data;
    }

    /** Récupère les détails d'un véhicule sans filtre de disponibilité (administration). */
    async getAdminVehicle(vehicleId: string): Promise<VehicleDetailDTO> {
        const response = await apiClient.get<VehicleDetailDTO>(
            `${VehiclesClient.BASE_URL}/admin/${vehicleId}`,
        );
        return response.data;
    }

    /** Remplace les informations modifiables d'un véhicule existant. */
    async updateVehicle(
        vehicleId: string,
        payload: CreateVehicleRequestDTO,
    ): Promise<VehicleResponseDTO> {
        const response = await apiClient.put<VehicleResponseDTO>(
            `${VehiclesClient.BASE_URL}/admin/${vehicleId}`,
            payload,
        );
        return response.data;
    }

    /** Supprime définitivement un véhicule (administration). */
    async deleteVehicle(vehicleId: string): Promise<void> {
        await apiClient.delete(`${VehiclesClient.BASE_URL}/admin/${vehicleId}`);
    }

    /** Récupère les services configurés pour les offres de location. */
    async getServiceCatalog(): Promise<ServiceDTO[]> {
        const response = await apiClient.get<ServiceDTO[]>(
            `${VehiclesClient.BASE_URL}/services`,
        );
        return response.data;
    }

    /**
     * Bascule le type de catalogue d'un véhicule (SALE <-> RENTAL).
     */
    async changeCatalogType(
        vehicleId: string,
        newPrice: number,
        confirm: boolean,
    ): Promise<VehicleResponseDTO> {
        const response = await apiClient.patch<VehicleResponseDTO>(
            `${VehiclesClient.BASE_URL}/${vehicleId}/catalog-type`,
            {
                new_price: newPrice,
                confirm,
            },
        );
        return response.data;
    }

    /** Réserve une clé S3 pour la photo du véhicule. */
    async requestPhotoUpload(
        vehicleId: string,
        file: File,
    ): Promise<PresignedPhotoUploadDTO> {
        const response = await apiClient.post<PresignedPhotoUploadDTO>(
            `${VehiclesClient.BASE_URL}/${vehicleId}/photos/presigned-url`,
            {
                file_name: file.name,
                file_size: file.size,
                content_type: file.type,
            },
        );

        return response.data;
    }

    /** Dépose la photo directement vers le stockage avec les champs signés. */
    async uploadPhoto(
        upload: PresignedPhotoUploadDTO,
        file: File,
    ): Promise<void> {
        const formData = new FormData();
        Object.entries(upload.fields).forEach(([key, value]) => {
            formData.append(key, value);
        });
        formData.append("file", file);

        await axios.post(upload.url, formData);
    }

    /** Rend la photo visible dans le catalogue après vérification S3. */
    async confirmPhotoUpload(
        vehicleId: string,
        photoId: string,
    ): Promise<ConfirmPhotoUploadDTO> {
        const response = await apiClient.post<ConfirmPhotoUploadDTO>(
            `${VehiclesClient.BASE_URL}/${vehicleId}/photos/${photoId}/confirm`,
        );

        return response.data;
    }

    /** Exécute le flux complet de réservation, upload et confirmation. */
    async uploadVehiclePhoto(
        vehicleId: string,
        file: File,
    ): Promise<ConfirmPhotoUploadDTO> {
        const upload = await this.requestPhotoUpload(vehicleId, file);
        await this.uploadPhoto(upload, file);
        return this.confirmPhotoUpload(vehicleId, upload.photo_id);
    }

    /** Liste toutes les photos confirmées d'un véhicule pour l'administration. */
    async getVehiclePhotos(vehicleId: string): Promise<VehiclePhotoDTO[]> {
        const response = await apiClient.get<VehiclePhotoDTO[]>(
            `${VehiclesClient.BASE_URL}/${vehicleId}/photos`,
        );
        return response.data;
    }

    /** Définit une photo existante comme image principale du véhicule. */
    async setPrimaryVehiclePhoto(vehicleId: string, photoId: string): Promise<void> {
        await apiClient.patch(
            `${VehiclesClient.BASE_URL}/${vehicleId}/photos/${photoId}/primary`,
        );
    }

    /** Supprime une photo du stockage et de la galerie du véhicule. */
    async deleteVehiclePhoto(vehicleId: string, photoId: string): Promise<void> {
        await apiClient.delete(
            `${VehiclesClient.BASE_URL}/${vehicleId}/photos/${photoId}`,
        );
    }
}

export const vehiclesClient = new VehiclesClient();