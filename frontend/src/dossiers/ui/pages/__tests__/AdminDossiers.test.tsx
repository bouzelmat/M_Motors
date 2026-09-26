import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { useAuthStore } from "../../../../auth/ui/hooks/useAuth";
import { ProtectedRoute } from "../../../../auth/ui/components/ProtectedRoute";
import { AdminDossiersPage } from "../AdminDossiersPage";
import { DossiersClient } from "../../../../api/clients/DossiersClient";

// Configuration du mock Zustand
vi.mock("../../../../auth/ui/hooks/useAuth", () => {
	const mockFn = vi.fn();
	(mockFn as any).getState = vi.fn();
	return {
		useAuthStore: mockFn,
	};
});

const mockUseAuthStore = vi.mocked(useAuthStore);

const createTestQueryClient = () =>
	new QueryClient({
		defaultOptions: {
			queries: { retry: false },
		},
	});

describe("US-501 — Interface administrateur des dossiers", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		vi.restoreAllMocks();
	});

	const renderPage = () => {
		const queryClient = createTestQueryClient();
		return render(
			<QueryClientProvider client={queryClient}>
				<MemoryRouter initialEntries={["/admin/dossiers"]}>
					<Routes>
						<Route path="/login" element={<div>Page Connexion</div>} />
						<Route path="/dashboard" element={<div>Dashboard Client</div>} />
						<Route
							path="/admin/dossiers"
							element={
								<ProtectedRoute requiredRole="ADMIN">
									<AdminDossiersPage />
								</ProtectedRoute>
							}
						/>
						<Route
							path="/admin/dossiers/:dossierId"
							element={<div>Page Detail Dossier</div>}
						/>
					</Routes>
				</MemoryRouter>
			</QueryClientProvider>
		);
	};

	const setupAuthState = (authState: {
		isAuthenticated: boolean;
		user: any;
		token?: string;
	}) => {
		const state = {
			...authState,
			logout: vi.fn(),
		};
		mockUseAuthStore.mockReturnValue(state as any);
		(mockUseAuthStore.getState as ReturnType<typeof vi.fn>).mockReturnValue(
			state
		);
	};

	it("redirige un utilisateur non-admin vers le dashboard", () => {
		setupAuthState({
			isAuthenticated: true,
			user: { role: "CLIENT", email: "client@test.fr" },
		});

		renderPage();

		expect(screen.getByText("Dashboard Client")).toBeInTheDocument();
	});

	it("affiche la liste des dossiers pour un administrateur", async () => {
		setupAuthState({
			isAuthenticated: true,
			user: { role: "ADMIN", email: "admin@test.fr" },
		});

		// Utilisation de vi.spyOn pour espionner la méthode de l'objet DossiersClient
		vi.spyOn(DossiersClient, "getPendingDossiers").mockResolvedValue([
			{
				id: "dos-123",
				client_email: "client@test.fr",
				vehicle_brand: "Peugeot",
				vehicle_model: "208",
				status: "SUBMITTED",
				submitted_at: "2026-09-20T10:00:00Z",
				created_at: "2026-09-20T09:00:00Z",
			},
		]);

		renderPage();

		expect(screen.getByText("Chargement...")).toBeInTheDocument();

		await waitFor(() => {
			expect(screen.getByText("client@test.fr")).toBeInTheDocument();
			expect(screen.getByText("Peugeot 208")).toBeInTheDocument();
			expect(screen.getByText("SUBMITTED")).toBeInTheDocument();
		});
	});

	it("affiche un état vide lorsqu'aucun dossier n'est en attente", async () => {
		setupAuthState({
			isAuthenticated: true,
			user: { role: "ADMIN", email: "admin@test.fr" },
		});

		vi.spyOn(DossiersClient, "getPendingDossiers").mockResolvedValue([]);

		renderPage();

		await waitFor(() => {
			expect(
				screen.getByText("Aucun dossier en attente pour le moment.")
			).toBeInTheDocument();
		});
	});
});