import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

const mockUseVehicleDetailQuery = vi.fn();

vi.mock(
  "../../../application/hooks/useVehicleDetailQuery",
  () => ({
    useVehicleDetailQuery: (...args: unknown[]) =>
      mockUseVehicleDetailQuery(...args),
  }),
);

import { VehicleDetailPage } from "../VehicleDetailPage";

describe("VehicleDetailPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
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
          <Routes>
            <Route
              path="/catalogue/:vehicleId"
              element={<VehicleDetailPage />}
            />
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
