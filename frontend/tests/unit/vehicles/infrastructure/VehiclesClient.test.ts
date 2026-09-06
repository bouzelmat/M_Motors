import { beforeEach, describe, expect, it, vi } from "vitest";

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

        expect(result.services[0]).toEqual({
            id: "service-1",
            name: "Assistance",
            monthly_cost: "15.00",
            category: "ASSISTANCE",
            included: true,
        });

        expect(result.services[1]).toEqual({
            id: "service-2",
            name: "Extension de garantie",
            monthly_cost: "29.90",
            category: "MAINTENANCE",
            included: false,
        });
    });
});