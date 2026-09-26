import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import axios from "axios";

import { SwitchCatalogTypeButton } from "../SwitchCatalogTypeButton";
import { vehiclesClient } from "../../../infrastructure/VehiclesClient";
import { useAuthStore } from "../../../../auth/ui/hooks/useAuth";

vi.mock("../../../../auth/ui/hooks/useAuth");
vi.mock("../../../infrastructure/VehiclesClient");

describe("SwitchCatalogTypeButton", () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  beforeEach(() => {
    vi.clearAllMocks();
  });

  function renderComponent(
    catalogType: "SALE" | "RENTAL" | "BOTH" = "SALE",
    newPrice = 399.0,
  ) {
    return render(
      <QueryClientProvider client={queryClient}>
        <SwitchCatalogTypeButton
          vehicleId="vehicle-123"
          catalogType={catalogType}
          newPrice={newPrice}
        />
      </QueryClientProvider>,
    );
  }

  it("n'affiche pas le bouton pour un utilisateur CLIENT", () => {
    vi.mocked(useAuthStore).mockReturnValue({
      user: { id: "1", role: "CLIENT", email: "client@example.com" },
    } as never);

    renderComponent();
    expect(screen.queryByText("Passer en Location")).not.toBeInTheDocument();
  });

  it("affiche 'Passer en Location' pour un ADMIN sur un véhicule SALE", () => {
    vi.mocked(useAuthStore).mockReturnValue({
      user: { id: "1", role: "ADMIN", email: "admin@example.com" },
    } as never);

    renderComponent("SALE");
    expect(screen.getByText("Passer en Location")).toBeInTheDocument();
  });

  it("affiche 'Passer en Vente' pour un ADMIN sur un véhicule RENTAL", () => {
    vi.mocked(useAuthStore).mockReturnValue({
      user: { id: "1", role: "ADMIN", email: "admin@example.com" },
    } as never);

    renderComponent("RENTAL");
    expect(screen.getByText("Passer en Vente")).toBeInTheDocument();
  });

  it("exécute le premier appel avec confirm: false au clic", async () => {
    vi.mocked(useAuthStore).mockReturnValue({
      user: { id: "1", role: "ADMIN", email: "admin@example.com" },
    } as never);

    vi.mocked(vehiclesClient.changeCatalogType).mockResolvedValue({} as never);

    renderComponent("SALE", 399.0);

    const button = screen.getByText("Passer en Location");
    await userEvent.click(button);

    expect(vehiclesClient.changeCatalogType).toHaveBeenCalledWith(
      "vehicle-123",
      399.0,
      false,
    );
  });

  it("ouvre la modale lors d'une réponse 409 et gère l'annulation", async () => {
    vi.mocked(useAuthStore).mockReturnValue({
      user: { id: "1", role: "ADMIN", email: "admin@example.com" },
    } as never);

    const error409 = {
      isAxiosError: true,
      response: { status: 409 },
    };
    vi.spyOn(axios, "isAxiosError").mockReturnValue(true);
    vi.mocked(vehiclesClient.changeCatalogType).mockRejectedValue(error409);

    renderComponent("SALE", 399.0);

    await userEvent.click(screen.getByText("Passer en Location"));

    await waitFor(() => {
      expect(
        screen.getByText("Ce véhicule a un dossier en cours. Confirmer le basculement ?"),
      ).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText("Annuler"));

    await waitFor(() => {
      expect(
        screen.queryByText("Ce véhicule a un dossier en cours. Confirmer le basculement ?"),
      ).not.toBeInTheDocument();
    });

    expect(vehiclesClient.changeCatalogType).toHaveBeenCalledTimes(1);
  });

  it("rappelle l'API avec confirm: true après clic sur Confirmer dans la modale", async () => {
    vi.mocked(useAuthStore).mockReturnValue({
      user: { id: "1", role: "ADMIN", email: "admin@example.com" },
    } as never);

    const error409 = {
      isAxiosError: true,
      response: { status: 409 },
    };
    vi.spyOn(axios, "isAxiosError").mockReturnValue(true);
    vi.mocked(vehiclesClient.changeCatalogType)
      .mockRejectedValueOnce(error409)
      .mockResolvedValueOnce({} as never);

    renderComponent("SALE", 399.0);

    await userEvent.click(screen.getByText("Passer en Location"));

    await waitFor(() => {
      expect(screen.getByText("Confirmation requise")).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText("Confirmer"));

    await waitFor(() => {
      expect(vehiclesClient.changeCatalogType).toHaveBeenLastCalledWith(
        "vehicle-123",
        399.0,
        true,
      );
    });
  });
});