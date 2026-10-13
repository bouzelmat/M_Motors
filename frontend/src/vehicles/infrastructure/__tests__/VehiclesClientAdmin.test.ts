import axios from "axios";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "../../../shared/infrastructure/http/apiClient";
import { VehiclesClient } from "../VehiclesClient";

vi.mock("../../../shared/infrastructure/http/apiClient", () => ({
  apiClient: { get: vi.fn(), post: vi.fn(), put: vi.fn(), patch: vi.fn(), delete: vi.fn() },
}));

describe("VehiclesClient - administration et photos", () => {
  const client = new VehiclesClient();
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(axios, "post").mockResolvedValue({} as never);
  });

  it("crée, met à jour, liste et supprime un véhicule", async () => {
    vi.mocked(apiClient.post).mockResolvedValueOnce({ data: { id: "v1" } } as never);
    vi.mocked(apiClient.put).mockResolvedValueOnce({ data: { id: "v1", brand: "BMW" } } as never);
    vi.mocked(apiClient.get)
      .mockResolvedValueOnce({ data: [{ id: "v1" }] } as never)
      .mockResolvedValueOnce({ data: { id: "v1", brand: "BMW" } } as never);
    const payload = { brand: "BMW", model: "X3", year: 2024, mileage: 1000, energy_type: "ESSENCE" as const, catalog_type: "SALE" as const, services: [] };
    await client.createVehicle(payload);
    await client.updateVehicle("v1", payload);
    expect(await client.getAdminVehicles()).toHaveLength(1);
    expect(await client.getAdminVehicle("v1")).toHaveProperty("brand", "BMW");
    await client.deleteVehicle("v1");
    expect(apiClient.post).toHaveBeenCalledWith("/api/v1/vehicles", payload);
    expect(apiClient.put).toHaveBeenCalledWith("/api/v1/vehicles/admin/v1", payload);
    expect(apiClient.delete).toHaveBeenCalledWith("/api/v1/vehicles/admin/v1");
  });

  it("gère le catalogue de services et les actions photo", async () => {
    vi.mocked(apiClient.get)
      .mockResolvedValueOnce({ data: [{ id: "s1", name: "GPS" }] } as never)
      .mockResolvedValueOnce({ data: [{ id: "p1", photo_url: "url" }] } as never);
    vi.mocked(apiClient.post)
      .mockResolvedValueOnce({ data: { photo_id: "p1", url: "https://s3", fields: { key: "k" } } } as never)
      .mockResolvedValueOnce({ data: { photo_id: "p1", photo_url: "url" } } as never);
    expect(await client.getServiceCatalog()).toHaveLength(1);
    const file = new File(["data"], "car.jpg", { type: "image/jpeg" });
    const upload = await client.requestPhotoUpload("v1", file);
    await client.uploadPhoto(upload, file);
    expect(await client.confirmPhotoUpload("v1", "p1")).toHaveProperty("photo_url", "url");
    expect(await client.getVehiclePhotos("v1")).toHaveLength(1);
    await client.setPrimaryVehiclePhoto("v1", "p1");
    await client.deleteVehiclePhoto("v1", "p1");
    expect(apiClient.post).toHaveBeenCalledWith("/api/v1/vehicles/v1/photos/presigned-url", { file_name: "car.jpg", file_size: file.size, content_type: "image/jpeg" });
    expect(apiClient.patch).toHaveBeenCalledWith("/api/v1/vehicles/v1/photos/p1/primary");
    expect(apiClient.delete).toHaveBeenCalledWith("/api/v1/vehicles/v1/photos/p1");
  });
});
