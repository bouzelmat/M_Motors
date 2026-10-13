import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { VehicleSlugPage } from "../VehicleSlugPage";
import { vehiclesClient } from "../../../infrastructure/VehiclesClient";

vi.mock("../../../infrastructure/VehiclesClient", () => ({ vehiclesClient: { getCatalog: vi.fn() } }));
vi.mock("../VehicleDetailPage", () => ({ VehicleDetailPage: ({ vehicleIdOverride }: { vehicleIdOverride: string }) => <div>Détail {vehicleIdOverride}</div> }));

function renderPage(slug: string) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={queryClient}><MemoryRouter initialEntries={[`/vehicles/${slug}`]}><Routes><Route path="/vehicles/:vehicleId" element={<VehicleSlugPage />} /></Routes></MemoryRouter></QueryClientProvider>);
}

describe("VehicleSlugPage", () => {
  it("redirige un UUID legacy vers le détail", () => {
    renderPage("123e4567-e89b-12d3-a456-426614174000");
    expect(screen.getByText("Détail 123e4567-e89b-12d3-a456-426614174000")).toBeInTheDocument();
    expect(vehiclesClient.getCatalog).not.toHaveBeenCalled();
  });

  it("affiche un véhicule retrouvé dans les catalogues", async () => {
    vi.mocked(vehiclesClient.getCatalog).mockResolvedValue([
      { id: "abcdefgh-1234-1234-1234-12345678abcd", brand: "Peugeot", model: "208", year: 2024, monthly_rent: null, photo_url: null, included_services: [] },
    ]);
    renderPage("peugeot-208-2024-5678abcd");
    expect(await screen.findByText("Détail abcdefgh-1234-1234-1234-12345678abcd")).toBeInTheDocument();
  });

  it("affiche un avertissement si le slug est absent", async () => {
    vi.mocked(vehiclesClient.getCatalog).mockResolvedValue([]);
    renderPage("vehicule-inexistant");
    expect(await screen.findByText("Ce véhicule n’est plus disponible dans le catalogue.")).toBeInTheDocument();
  });

  it("affiche une erreur si un catalogue échoue", async () => {
    vi.mocked(vehiclesClient.getCatalog).mockRejectedValue(new Error("network"));
    renderPage("peugeot-208-2024-unknown");
    expect(await screen.findByText("Impossible de retrouver ce véhicule dans le catalogue.")).toBeInTheDocument();
  });
});
