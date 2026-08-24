import { apiClient } from "../../api/apiClient";
import { VehicleListItemDTO, VehicleDetailDTO, GetCatalogParams } from "./vehicle.types";

/** Client HTTP du contexte Vehicles. */
export class VehiclesClient {
    private static readonly BASE_URL = "/api/v1/vehicles";

    /**
     * Récupère le catalogue des véhicules.
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
}

export const vehiclesClient = new VehiclesClient();
