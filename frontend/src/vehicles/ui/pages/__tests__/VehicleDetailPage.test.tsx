import { fireEvent, render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useSubscriptionTunnelStore } from "../../../application/stores/useSubscriptionTunnelStore";

const mockUseVehicleDetailQuery = vi.fn();

vi.mock(
  "../../../application/hooks/useVehicleDetailQuery",
  () => ({
    useVehicleDetailQuery: (...args: unknown[]) =>
      mockUseVehicleDetailQuery(...args),
  }),
);

import { VehicleDetailPage } from "../VehicleDetailPage";

const CurrentPath = () => {
  const location = useLocation();
  return <output data-testid="current-path">{`${location.pathname}${location.search}`}</output>;
};

describe("VehicleDetailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useSubscriptionTunnelStore.getState().resetTunnel();
  });

  function renderPage() {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/catalogue/vehicle-123"]}>
          <CurrentPath />
          <Routes>
            <Route path="/catalogue" element={<div>Catalogue</div>} />
            <Route
              path="/catalogue/:vehicleId"
              element={<VehicleDetailPage />}
            />
            <Route path="/simulator" element={<div>Simulateur LLD</div>} />
            <Route path="/dossiers/new" element={<div>Nouveau dossier</div>} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    );
  }

  it("affiche les services disponibles avec leur statut inclus", () => {
    mockUseVehicleDetailQuery.mockReturnValue({
      data: {
        id: "vehicle-123",
        brand: "Peugeot",
        model: "308",
        year: 2024,
        catalog_type: "RENTAL",
        monthly_rent: "399.00",
        photo_url: null,
        included_services: ["Assistance"],
        price: "25000.00",
        mileage: 10000,
        energy_type: "ESSENCE",
        description: "Véhicule de test",
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
            name: "Maintenance",
            monthly_cost: "29.90",
            category: "MAINTENANCE",
            included: false,
          },
        ],
      },
      isLoading: false,
      error: null,
    });

    renderPage();

    expect(
      screen.getByText("Peugeot 308"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Services disponibles"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Assistance"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("15.00 €/mois"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Inclus"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Maintenance"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("29.90 €/mois"),
    ).toBeInTheDocument();
  });

  it("explique l’absence d’options sur une offre Achat et ouvre le catalogue LLD", () => {
    mockUseVehicleDetailQuery.mockReturnValue({
      data: {
        id: "vehicle-sale-1",
        brand: "Peugeot",
        model: "208",
        year: 2023,
        catalog_type: "SALE",
        monthly_rent: null,
        photo_url: null,
        included_services: [],
        price: "19900.00",
        mileage: 12500,
        energy_type: "ESSENCE",
        description: "Citadine récente",
        services: [],
      },
      isLoading: false,
      error: null,
    });

    renderPage();

    expect(screen.getByText(/services mensuels.*offres de location longue durée/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Voir les offres LLD" }));
    expect(screen.getByTestId("current-path")).toHaveTextContent("/catalogue?mode=rental");
  });

  it("affiche un état de chargement", () => {
    mockUseVehicleDetailQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    });

    renderPage();

    expect(
      screen.getByTestId("vehicle-detail-loading"),
    ).toBeInTheDocument();
  });

  it("montre les caractéristiques complètes et prépare une simulation LLD", () => {
    mockUseVehicleDetailQuery.mockReturnValue({
      data: {
        id: "vehicle-123",
        brand: "Peugeot",
        model: "308",
        year: 2024,
        monthly_rent: "399.00",
        photo_url: null,
        included_services: [],
        price: "25000.00",
        mileage: 10000,
        energy_type: "ESSENCE",
        catalog_type: "BOTH",
        description: "Confort et sobriété",
        services: [],
      },
      isLoading: false,
      error: null,
    });

    renderPage();

    expect(screen.getByText("Énergie : ESSENCE")).toBeInTheDocument();
    expect(screen.getByText((_, element) =>
      element?.classList.contains("tabular-nums") && element.textContent?.replace(/\D/g, "") === "10000",
    )).toBeInTheDocument();
    expect(screen.getByText((_, element) =>
      element?.classList.contains("tabular-nums") && element.textContent?.replace(/\D/g, "") === "399",
    )).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Simuler en LLD" }));

    expect(screen.getByTestId("current-path")).toHaveTextContent("/simulator?vehicleId=vehicle-123");
    expect(useSubscriptionTunnelStore.getState().vehicleId).toBe("vehicle-123");
    expect(useSubscriptionTunnelStore.getState().vehicleMode).toBe("rental");
  });

  it("ouvre le démarrage du dossier en mode achat", () => {
    mockUseVehicleDetailQuery.mockReturnValue({
      data: {
        id: "vehicle-123",
        brand: "Peugeot",
        model: "308",
        year: 2024,
        monthly_rent: "399.00",
        photo_url: null,
        included_services: [],
        price: "25000.00",
        mileage: 10000,
        energy_type: "ESSENCE",
        catalog_type: "BOTH",
        description: null,
        services: [],
      },
      isLoading: false,
      error: null,
    });

    renderPage();
    fireEvent.click(screen.getByRole("button", { name: "Acheter" }));

    expect(screen.getByTestId("current-path")).toHaveTextContent("/dossiers/new?simulationId=achat-vehicle-123&vehicleId=vehicle-123&mode=sale");
    expect(useSubscriptionTunnelStore.getState().vehicleMode).toBe("sale");
  });

  it("affiche une erreur lorsque le chargement échoue", () => {
    mockUseVehicleDetailQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error("Erreur API"),
    });

    renderPage();

    expect(
      screen.getByTestId("vehicle-detail-error"),
    ).toBeInTheDocument();
  });
});
