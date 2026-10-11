import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { ThemeProvider } from "@mui/material";

import { theme } from "../../shared/ui/theme/theme";
import { useSubscriptionTunnelStore } from "../../vehicles/application/stores/useSubscriptionTunnelStore";
import { useVehicleFilterStore } from "../../vehicles/application/stores/useVehicleFilterStore";
import { useVehiclesQuery } from "../../vehicles/application/hooks/useVehiclesQuery";
import { vehiclesClient } from "../../vehicles/infrastructure/VehiclesClient";
import type { VehicleDetailDTO, VehicleListItemDTO } from "../../vehicles/infrastructure/vehicle.types";
import { CatalogPage } from "../../vehicles/ui/pages/CatalogPage";
import { HomePage } from "../HomePage";

vi.mock("../../vehicles/application/hooks/useVehiclesQuery", () => ({
    useVehiclesQuery: vi.fn(),
}));

const rentalVehicle: VehicleListItemDTO = {
    id: "vehicle-1",
    brand: "Peugeot",
    model: "e-208",
    year: 2024,
    monthly_rent: "329.00",
    photo_url: null,
    included_services: [],
};

const vehicleDetail: VehicleDetailDTO = {
    ...rentalVehicle,
    price: "24800.00",
    mileage: 12000,
    energy_type: "ELECTRIQUE",
    catalog_type: "BOTH",
    description: "Citadine électrique",
    services: [],
};

const LocationDisplay = () => {
    const location = useLocation();
    return <output data-testid="current-location">{`${location.pathname}${location.search}${location.hash}`}</output>;
};

const renderHome = () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    return render(
        <QueryClientProvider client={queryClient}>
            <ThemeProvider theme={theme}>
                <MemoryRouter initialEntries={["/"]}>
                    <LocationDisplay />
                    <Routes>
                        <Route path="/" element={<HomePage />} />
                        <Route path="/catalogue" element={<div>Catalogue filtré</div>} />
                    </Routes>
                </MemoryRouter>
            </ThemeProvider>
        </QueryClientProvider>,
    );
};

describe("HomePage", () => {
    beforeEach(() => {
        vi.clearAllMocks();
        useSubscriptionTunnelStore.getState().resetTunnel();
        useVehicleFilterStore.getState().resetFilters();
        vi.mocked(useVehiclesQuery).mockImplementation(({ mode }) => ({
            data: mode === "rental" ? [rentalVehicle] : [],
            isLoading: false,
            error: null,
        } as ReturnType<typeof useVehiclesQuery>));
        vi.spyOn(vehiclesClient, "getVehicleDetail").mockResolvedValue(vehicleDetail);
    });

    it("affiche les sections d’accueil et les prix de l’annonce reçue de l’API", async () => {
        renderHome();

        expect(screen.getByRole("heading", { name: /Le futur automobile, selon vos règles/i })).toBeInTheDocument();
        expect(screen.getByRole("heading", { name: /Notre Sélection Premium/i })).toBeInTheDocument();
        await waitFor(() => expect(screen.getByText(/Tesla Model 3/i)).toBeInTheDocument());
    });

    it("redirige la recherche express vers le catalogue avec ses critères", async () => {
        const user = userEvent.setup();
        renderHome();

        // 1. Sélection de la Marque
        const brandCombobox = screen.getByRole("combobox", { name: "Marque" });
        await user.click(brandCombobox);
        const brandOption = await screen.findByRole("option", { name: "Tesla" });
        await user.click(brandOption);

        // 2. Sélection du Loyer max
        const budgetCombobox = await screen.findByRole("combobox", { name: "Loyer max (€/mois)" });
        await user.click(budgetCombobox);
        const budgetOption = await screen.findByRole("option", { name: /Moins de 500 € \/ mois|500/i });
        await user.click(budgetOption);

        // 3. Attente du démontage du Popover MUI et clic sur Rechercher
        const searchButton = await waitFor(() => screen.getByRole("button", { name: "Rechercher" }));
        await user.click(searchButton);

        expect(await screen.findByText("Catalogue filtré")).toBeInTheDocument();
    }, 15000);

    it("applique les paramètres transmis lorsque le catalogue s’ouvre", async () => {
        const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
        render(
            <QueryClientProvider client={queryClient}>
                <ThemeProvider theme={theme}>
                    <MemoryRouter initialEntries={["/catalogue?mode=rental&brand=Peugeot&fuel_type=HYBRIDE&max_monthly_rent=450"]}>
                        <Routes><Route path="/catalogue" element={<CatalogPage />} /></Routes>
                    </MemoryRouter>
                </ThemeProvider>
            </QueryClientProvider>,
        );

        await waitFor(() => expect(useVehiclesQuery).toHaveBeenLastCalledWith(expect.objectContaining({
            mode: "rental",
            brand: "Peugeot",
            fuelType: "HYBRIDE",
        })));
    });

    it("enregistre le calcul du mini-simulateur avant de poursuivre", async () => {
        const user = userEvent.setup();
        renderHome();

        const slider = screen.queryByRole("slider");
        if (slider) {
            fireEvent.change(slider, { target: { value: "24" } });
        }
        
        const actionLink = screen.getByRole("link", { name: /Offres LLD dès 299€\/mois/i });
        await user.click(actionLink);

        expect(await screen.findByText("Catalogue filtré")).toBeInTheDocument();
    });
});