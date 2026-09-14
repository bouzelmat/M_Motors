import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";

import { AddVehiclePage } from "../AddVehiclePage";
import { vehiclesClient } from "../../../infrastructure/VehiclesClient";
import { useAuthStore } from "../../../../auth/ui/hooks/useAuth";

const mockedNavigate = vi.fn();

vi.mock("react-router-dom", async () => {
    const actual = await vi.importActual("react-router-dom");
    return {
        ...actual,
        useNavigate: () => mockedNavigate,
    };
});

vi.mock("../../../../auth/ui/hooks/useAuth", () => ({
    useAuthStore: vi.fn(),
}));

vi.mock("../../../infrastructure/VehiclesClient", () => ({
    vehiclesClient: {
        createVehicle: vi.fn(),
    },
}));

describe("AddVehiclePage", () => {
    beforeEach(() => {
        vi.clearAllMocks();
        (useAuthStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
            isAuthenticated: true,
            user: { role: "ADMIN" },
        });
    });

    it("bloque l'accès si l'utilisateur n'est pas ADMIN", () => {
        (useAuthStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
            isAuthenticated: true,
            user: { role: "CLIENT" },
        });

        render(
            <MemoryRouter>
                <AddVehiclePage />
            </MemoryRouter>
        );

        expect(screen.getByText("Accès réservé aux administrateurs.")).toBeInTheDocument();
    });

    it("affiche des erreurs de validation locales en français pour la location sans loyer", async () => {
        render(
            <MemoryRouter>
                <AddVehiclePage />
            </MemoryRouter>
        );

        fireEvent.change(screen.getByLabelText(/Marque/i), { target: { value: "Peugeot" } });
        fireEvent.change(screen.getByLabelText(/Modèle/i), { target: { value: "208" } });

        fireEvent.click(screen.getByRole("button", { name: /Créer le véhicule/i }));

        await waitFor(() => {
            expect(screen.getByText("Le loyer mensuel est obligatoire et doit être strictement positif.")).toBeInTheDocument();
        });
    });

    it("soumet un véhicule en RENTAL sans transmettre le champ price", async () => {
        (vehiclesClient.createVehicle as ReturnType<typeof vi.fn>).mockResolvedValue({
            id: "v-rental-123",
            brand: "Peugeot",
            model: "208",
        });

        render(
            <MemoryRouter>
                <AddVehiclePage />
            </MemoryRouter>
        );

        fireEvent.change(screen.getByLabelText(/Marque/i), { target: { value: "Peugeot" } });
        fireEvent.change(screen.getByLabelText(/Modèle/i), { target: { value: "208" } });
        fireEvent.change(screen.getByLabelText(/Année/i), { target: { value: 2024 } });
        fireEvent.change(screen.getByLabelText(/Kilométrage/i), { target: { value: 10000 } });
        fireEvent.change(screen.getByLabelText(/Loyer mensuel/i), { target: { value: 350 } });

        fireEvent.click(screen.getByRole("button", { name: /Créer le véhicule/i }));

        await waitFor(() => {
            const callArg = (vehiclesClient.createVehicle as ReturnType<typeof vi.fn>).mock.calls[0][0];
            expect(callArg).toEqual({
                brand: "Peugeot",
                model: "208",
                year: 2024,
                mileage: 10000,
                energy_type: "GASOLINE",
                catalog_type: "RENTAL",
                monthly_rent: 350,
                description: null,
            });
            expect(callArg).not.toHaveProperty("price");
            expect(mockedNavigate).toHaveBeenCalledWith("/admin/vehicles/v-rental-123/photos");
        });
    });

    it("soumet un véhicule en SALE sans transmettre le champ monthly_rent", async () => {
        (vehiclesClient.createVehicle as ReturnType<typeof vi.fn>).mockResolvedValue({
            id: "v-sale-456",
            brand: "Tesla",
            model: "Model 3",
        });

        render(
            <MemoryRouter>
                <AddVehiclePage />
            </MemoryRouter>
        );

        fireEvent.change(screen.getByLabelText(/Marque/i), { target: { value: "Tesla" } });
        fireEvent.change(screen.getByLabelText(/Modèle/i), { target: { value: "Model 3" } });

        // Sélection du mode Vente dans le Select MUI
        const selectCatalog = screen.getByLabelText(/Type de catalogue/i);
        fireEvent.mouseDown(selectCatalog);
        const optionSale = await screen.findByRole("option", { name: "Vente" });
        fireEvent.click(optionSale);

        fireEvent.change(screen.getByLabelText(/Prix de vente/i), { target: { value: 42000 } });

        fireEvent.click(screen.getByRole("button", { name: /Créer le véhicule/i }));

        await waitFor(() => {
            const callArg = (vehiclesClient.createVehicle as ReturnType<typeof vi.fn>).mock.calls[0][0];
            expect(callArg).toEqual({
                brand: "Tesla",
                model: "Model 3",
                year: new Date().getFullYear(),
                mileage: 0,
                energy_type: "GASOLINE",
                catalog_type: "SALE",
                price: 42000,
                description: null,
            });
            expect(callArg).not.toHaveProperty("monthly_rent");
            expect(mockedNavigate).toHaveBeenCalledWith("/admin/vehicles/v-sale-456/photos");
        });
    });

    it("soumet un véhicule en BOTH en exigeant et transmettant à la fois price et monthly_rent", async () => {
        (vehiclesClient.createVehicle as ReturnType<typeof vi.fn>).mockResolvedValue({
            id: "v-both-789",
            brand: "BMW",
            model: "i4",
        });

        render(
            <MemoryRouter>
                <AddVehiclePage />
            </MemoryRouter>
        );

        fireEvent.change(screen.getByLabelText(/Marque/i), { target: { value: "BMW" } });
        fireEvent.change(screen.getByLabelText(/Modèle/i), { target: { value: "i4" } });

        const selectCatalog = screen.getByLabelText(/Type de catalogue/i);
        fireEvent.mouseDown(selectCatalog);
        const optionBoth = await screen.findByRole("option", { name: "Vente et Location" });
        fireEvent.click(optionBoth);

        fireEvent.change(screen.getByLabelText(/Prix de vente/i), { target: { value: 55000 } });
        fireEvent.change(screen.getByLabelText(/Loyer mensuel/i), { target: { value: 650 } });

        fireEvent.click(screen.getByRole("button", { name: /Créer le véhicule/i }));

        await waitFor(() => {
            const callArg = (vehiclesClient.createVehicle as ReturnType<typeof vi.fn>).mock.calls[0][0];
            expect(callArg).toEqual({
                brand: "BMW",
                model: "i4",
                year: new Date().getFullYear(),
                mileage: 0,
                energy_type: "GASOLINE",
                catalog_type: "BOTH",
                price: 55000,
                monthly_rent: 650,
                description: null,
            });
            expect(mockedNavigate).toHaveBeenCalledWith("/admin/vehicles/v-both-789/photos");
        });
    });

    it("affiche une erreur de l'API en cas d'échec de la requête", async () => {
        (vehiclesClient.createVehicle as ReturnType<typeof vi.fn>).mockRejectedValue(new Error("API Error"));

        render(
            <MemoryRouter>
                <AddVehiclePage />
            </MemoryRouter>
        );

        fireEvent.change(screen.getByLabelText(/Marque/i), { target: { value: "Renault" } });
        fireEvent.change(screen.getByLabelText(/Modèle/i), { target: { value: "Clio" } });
        fireEvent.change(screen.getByLabelText(/Loyer mensuel/i), { target: { value: 300 } });

        fireEvent.click(screen.getByRole("button", { name: /Créer le véhicule/i }));

        await waitFor(() => {
            expect(screen.getByText(/Une erreur est survenue lors de la création du véhicule/i)).toBeInTheDocument();
        });
    });
});