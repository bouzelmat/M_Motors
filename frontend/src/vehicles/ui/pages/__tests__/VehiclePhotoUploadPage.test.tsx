import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useAuthStore } from "../../../../auth/ui/hooks/useAuth";
import { vehiclesClient } from "../../../infrastructure/VehiclesClient";
import { VehiclePhotoUploadPage } from "../VehiclePhotoUploadPage";

vi.mock("../../../../auth/ui/hooks/useAuth", () => ({
  useAuthStore: vi.fn(),
}));

vi.mock("../../../infrastructure/VehiclesClient", () => ({
  vehiclesClient: {
    uploadVehiclePhoto: vi.fn(),
  },
}));

const mockedUseAuthStore = vi.mocked(useAuthStore);
const mockedUploadVehiclePhoto = vi.mocked(vehiclesClient.uploadVehiclePhoto);

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/admin/vehicles/vehicle-1/photos"]}>
      <Routes>
        <Route path="/admin/vehicles/:vehicleId/photos" element={<VehiclePhotoUploadPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("VehiclePhotoUploadPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("refuse l'accès aux utilisateurs qui ne sont pas administrateurs", () => {
    mockedUseAuthStore.mockReturnValue({
      isAuthenticated: true,
      user: { role: "CLIENT" },
    } as never);

    renderPage();

    expect(screen.getByText("Accès réservé aux administrateurs.")).toBeInTheDocument();
  });

  it("téléverse et confirme une photo pour un administrateur", async () => {
    mockedUseAuthStore.mockReturnValue({
      isAuthenticated: true,
      user: { role: "ADMIN" },
    } as never);
    mockedUploadVehiclePhoto.mockResolvedValue({
      photo_id: "photo-1",
      photo_url: "https://s3.example/photo.jpg",
    });

    renderPage();

    const file = new File(["jpeg"], "car.jpg", { type: "image/jpeg" });
    fireEvent.change(screen.getByLabelText("Choisir une photo"), {
      target: { files: [file] },
    });
    fireEvent.click(screen.getByRole("button", { name: "Téléverser la photo" }));

    await waitFor(() => {
      expect(mockedUploadVehiclePhoto).toHaveBeenCalledWith("vehicle-1", file);
    });
    expect(screen.getByText("La photo est maintenant visible dans le catalogue.")).toBeInTheDocument();
  });
});
