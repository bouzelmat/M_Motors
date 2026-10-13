import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { SubscriptionConfirmationPage } from "../SubscriptionConfirmationPage";
import { useSubscriptionTunnelStore } from "../../../application/stores/useSubscriptionTunnelStore";
import { DossiersClient } from "../../../infrastructure/DossiersClient";

const mockNavigate = vi.fn();

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock("../../../infrastructure/DossiersClient", () => ({
  DossiersClient: {
    createDossier: vi.fn(),
  },
}));

describe("SubscriptionConfirmationPage", () => {
  const renderPage = () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <SubscriptionConfirmationPage />
        </MemoryRouter>
      </QueryClientProvider>,
    );
  };

  beforeEach(() => {
    vi.clearAllMocks();
    useSubscriptionTunnelStore.getState().resetTunnel();
  });

  it("affiche les données du tunnel et gère le succès du submit", async () => {
    vi.mocked(DossiersClient.createDossier).mockResolvedValueOnce({
      id: "dossier-123",
      vehicle_id: "vehicle-abc",
      status: "DRAFT",
    });

    const store = useSubscriptionTunnelStore.getState();
    store.setVehicle("vehicle-abc", "sale");
    store.setTradeIn({
      registration: "XX-999-YY",
      mileage: 20000,
    });

    renderPage();

    expect(screen.getByText(/ID du véhicule: vehicle-abc/i)).toBeInTheDocument();
    expect(screen.getByText(/XX-999-YY/i)).toBeInTheDocument();

    const confirmBtn = screen.getByRole("button", {
      name: /Confirmer ma demande/i,
    });
    fireEvent.click(confirmBtn);

    await waitFor(() => {
      expect(DossiersClient.createDossier).toHaveBeenCalledWith({
        vehicle_id: "vehicle-abc",
        trade_in: {
          registration: "XX-999-YY",
          mileage: 20000,
          brand: null,
          model: null,
        },
        financing_plan: null,
      });
      expect(mockNavigate).toHaveBeenCalledWith(
        "/dossiers/new?simulationId=confirmation-dossier-123&dossierId=dossier-123&vehicleId=vehicle-abc&mode=sale",
      );
      expect(useSubscriptionTunnelStore.getState().vehicleId).toBe("vehicle-abc");
    });
  });

  it("conserve le contenu du store en cas d'échec API", async () => {
    vi.mocked(DossiersClient.createDossier).mockRejectedValueOnce(
      new Error("API Error"),
    );

    const store = useSubscriptionTunnelStore.getState();
    store.setVehicle("vehicle-abc", "sale");

    renderPage();

    const confirmBtn = screen.getByRole("button", {
      name: /Confirmer ma demande/i,
    });
    fireEvent.click(confirmBtn);

    await waitFor(() => {
      expect(
        screen.getByText(/La création de votre dossier a échoué/i),
      ).toBeInTheDocument();
      expect(useSubscriptionTunnelStore.getState().vehicleId).toBe("vehicle-abc");
    });
  });
});