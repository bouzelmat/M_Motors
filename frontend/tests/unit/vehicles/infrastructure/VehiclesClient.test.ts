import { beforeEach, describe, expect, it, vi } from "vitest";
import axios from "axios";

import { apiClient } from "../../../../src/api/apiClient";
import { VehiclesClient } from "../../../../src/vehicles/infrastructure/VehiclesClient";
import { GetCatalogParams } from "../../../../src/vehicles/infrastructure/vehicle.types";

describe("VehiclesClient", () => {
    beforeEach(() => {
        vi.restoreAllMocks();
    });

    it("récupère le catalogue des véhicules avec l'ensemble des filtres optionnels", async () => {
        const responseData = [
            {
                id: "vehicle-1",
                brand: "BMW",
                model: "Série 3",
                year: 2023,
                monthly_rent: "450.00",
                photo_url: null,
                included_services: [],
            },
        ];

        vi.spyOn(apiClient, "get").mockResolvedValue({
            data: responseData,
        } as never);

        const client = new VehiclesClient();
        const filters: GetCatalogParams = {
            mode: "sale",
            brand: "BMW",
            max_price: 35000,
            max_mileage: 50000,
            fuel_type: "ESSENCE",
        };

        const result = await client.getCatalog(filters);

        expect(apiClient.get).toHaveBeenCalledWith("/api/v1/vehicles", {
            params: {
                mode: "sale",
                brand: "BMW",
                max_price: 35000,
                max_mileage: 50000,
                fuel_type: "ESSENCE",
            },
        });

        expect(result).toEqual(responseData);
    });

    it("retourne les détails d'un véhicule avec ses services", async () => {
        const vehicleId = "vehicle-123";

        const responseData = {
            id: vehicleId,
            brand: "Peugeot",
            model: "308",
            year: 2024,
            monthly_rent: "399.00",
            photo_url: null,
            included_services: ["Assistance"],
            price: "25000.00",
            mileage: 10000,
            energy_type: "ESSENCE",
            catalog_type: "RENTAL",
            description: "Véhicule avec services",
            services: [
                {
                    id: "service-1",
                    name: "Assistance",
                    monthly_cost: "15.00",
                    category: "ASSISTANCE",
                    included: true,
                },
                {
                    id: "service-2",
                    name: "Extension de garantie",
                    monthly_cost: "29.90",
                    category: "MAINTENANCE",
                    included: false,
                },
            ],
        };

        vi.spyOn(apiClient, "get").mockResolvedValue({
            data: responseData,
        } as never);

        const client = new VehiclesClient();

        const result = await client.getVehicleDetail(vehicleId);

        expect(apiClient.get).toHaveBeenCalledWith(
            `/api/v1/vehicles/${vehicleId}`,
        );

        expect(result.services).toHaveLength(2);
    });

    it("effectue la requête PATCH pour changer le type de catalogue d'un véhicule", async () => {
        const vehicleId = "vehicle-123";
        const responseData = {
            id: vehicleId,
            brand: "Peugeot",
            model: "308",
            year: 2024,
            price: "25000.00",
            monthly_rent: "399.00",
            mileage: 10000,
            energy_type: "ESSENCE",
            status: "AVAILABLE",
            catalog_type: "RENTAL",
            description: "Véhicule modifié",
        };

        vi.spyOn(apiClient, "patch").mockResolvedValue({
            data: responseData,
        } as never);

        const client = new VehiclesClient();
        const result = await client.changeCatalogType(vehicleId, 399.0, false);

        expect(apiClient.patch).toHaveBeenCalledWith(
            `/api/v1/vehicles/${vehicleId}/catalog-type`,
            {
                new_price: 399.0,
                confirm: false,
            },
        );
        expect(result).toEqual(responseData);
    });

    it("réserve, téléverse et confirme une photo de véhicule", async () => {
        const file = new File(["jpeg"], "car.jpg", { type: "image/jpeg" });
        const upload = {
            photo_id: "photo-1",
            url: "https://s3.example/upload",
            fields: { key: "vehicles/vehicle-1/photo.jpg", policy: "signed" },
        };

        vi.spyOn(apiClient, "post")
            .mockResolvedValueOnce({ data: upload } as never)
            .mockResolvedValueOnce({
                data: { photo_id: "photo-1", photo_url: "https://s3.example/car.jpg" },
            } as never);
        const axiosPost = vi.spyOn(axios, "post").mockResolvedValue({} as never);

        const result = await new VehiclesClient().uploadVehiclePhoto("vehicle-1", file);

        expect(apiClient.post).toHaveBeenNthCalledWith(
            1,
            "/api/v1/vehicles/vehicle-1/photos/presigned-url",
            { file_name: "car.jpg", file_size: file.size, content_type: "image/jpeg" },
        );
        expect(axiosPost).toHaveBeenCalledWith(
            "https://s3.example/upload",
            expect.any(FormData),
        );
        expect(apiClient.post).toHaveBeenNthCalledWith(
            2,
            "/api/v1/vehicles/vehicle-1/photos/photo-1/confirm",
        );
        expect(result.photo_url).toBe("https://s3.example/car.jpg");
    });
});