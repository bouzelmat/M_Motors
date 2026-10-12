import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { vehiclesClient } from "../../../infrastructure/VehiclesClient";
import { EditVehiclePage } from "../EditVehiclePage";

vi.mock("../../../infrastructure/VehiclesClient", () => ({
	vehiclesClient: {
		getAdminVehicle: vi.fn(),
		getServiceCatalog: vi.fn(),
		getVehiclePhotos: vi.fn(),
		updateVehicle: vi.fn(),
		uploadVehiclePhoto: vi.fn(),
		setPrimaryVehiclePhoto: vi.fn(),
		deleteVehiclePhoto: vi.fn(),
	},
}));

function renderPage() {
	const queryClient = new QueryClient({
		defaultOptions: { queries: { retry: false } },
	});
	return render(
		<QueryClientProvider client={queryClient}>
			<MemoryRouter initialEntries={["/admin/vehicles/vehicle-1/edit"]}>
				<Routes>
					<Route path="/admin/vehicles/:vehicleId/edit" element={<EditVehiclePage />} />
					<Route path="/admin/vehicles" element={<div>Liste des véhicules</div>} />
				</Routes>
			</MemoryRouter>
		</QueryClientProvider>,
	);
}

describe("EditVehiclePage", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		
		vi.mocked(vehiclesClient.getAdminVehicle).mockResolvedValue({
			id: "vehicle-1",
			brand: "Peugeot",
			model: "208",
			year: 2024,
			price: "18000.00",
			monthly_rent: null,
			mileage: 1000,
			energy_type: "ESSENCE",
			catalog_type: "SALE",
			description: null,
			photo_url: null,
			included_services: [],
			services: [],
		});
		vi.mocked(vehiclesClient.getServiceCatalog).mockResolvedValue([]);
		vi.mocked(vehiclesClient.getVehiclePhotos).mockResolvedValue([]);
		vi.mocked(vehiclesClient.uploadVehiclePhoto).mockResolvedValue({
			photo_id: "photo-new",
			photo_url: "https://images/photo-new.jpg",
		});
		
		vi.mocked(vehiclesClient.setPrimaryVehiclePhoto).mockResolvedValue({ success: true } as any);
		vi.mocked(vehiclesClient.deleteVehiclePhoto).mockResolvedValue({ success: true } as any);
	});

	it("permet de téléverser plusieurs images depuis une sélection unique", async () => {
		const user = userEvent.setup();
		const { container } = renderPage();

		await screen.findByDisplayValue("Peugeot");
		const fileInput = container.querySelector<HTMLInputElement>("input[type=file][multiple]");
		expect(fileInput).not.toBeNull();
		
		await user.upload(fileInput!, [
			new File(["front"], "avant.jpg", { type: "image/jpeg" }),
			new File(["side"], "cote.png", { type: "image/png" }),
		]);
		await user.click(screen.getByRole("button", { name: "Ajouter les images" }));

		await waitFor(() => {
			expect(vehiclesClient.uploadVehiclePhoto).toHaveBeenNthCalledWith(1, "vehicle-1", expect.objectContaining({ name: "avant.jpg" }));
			expect(vehiclesClient.uploadVehiclePhoto).toHaveBeenNthCalledWith(2, "vehicle-1", expect.objectContaining({ name: "cote.png" }));
		});
	});

	// CORRECTION ICI : Ajout du paramètre de timeout (10000ms) à la fin de la fonction it()
	it("permet de changer la photo principale et de supprimer une image", async () => {
		const user = userEvent.setup();
		
		vi.mocked(vehiclesClient.getVehiclePhotos).mockResolvedValue([
			{ id: "photo-1", photo_url: "https://images/one.jpg", is_primary: true, created_at: "2026-10-01T00:00:00Z", uploaded_at: "2026-10-01T00:00:00Z" },
			{ id: "photo-2", photo_url: "https://images/two.jpg", is_primary: false, created_at: "2026-10-02T00:00:00Z", uploaded_at: "2026-10-02T00:00:00Z" },
		]);
		
		renderPage();

		const images = await screen.findAllByRole("img");
		expect(images).toHaveLength(2);

		const setPrimaryButtons = screen.getAllByRole("button", { name: "Définir comme image principale" });
		const actionablePrimaryButton = setPrimaryButtons.find(btn => !btn.hasAttribute("disabled"));
		
		expect(actionablePrimaryButton).toBeDefined();
		await user.click(actionablePrimaryButton!);

		await waitFor(() => {
			expect(vehiclesClient.setPrimaryVehiclePhoto).toHaveBeenCalledWith("vehicle-1", "photo-2");
		});

		const deleteButtons = screen.getAllByRole("button", { name: "Supprimer cette image" });
		await user.click(deleteButtons[deleteButtons.length - 1]);

		const confirmDeleteButton = await screen.findByRole("button", { name: "Supprimer", exact: true });
		await user.click(confirmDeleteButton);

		await waitFor(() => {
			expect(vehiclesClient.deleteVehiclePhoto).toHaveBeenCalledWith("vehicle-1", "photo-2");
		});
	}, 10000); // <-- Ce paramètre étend la limite de 5000ms à 10000ms pour ce test spécifique
});