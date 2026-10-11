import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { apiClient } from "../../../../api/apiClient";
import { useDossierDetail } from "../../hooks/useDossierDetail";
import { AdminDossierDetailPage } from "../AdminDossierDetailPage";

vi.mock("../../hooks/useDossierDetail", () => ({
	useDossierDetail: vi.fn(),
}));

describe("AdminDossierDetailPage", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		vi.mocked(useDossierDetail).mockReturnValue({
			data: {
				id: "dossier-1",
				user_id: "client-1",
				client_email: "client@example.com",
				vehicle_id: "vehicle-1",
				vehicle_brand: "Peugeot",
				vehicle_model: "208",
				vehicle_price: null,
				status: "SUBMITTED",
				submitted_at: "2026-10-09T10:00:00Z",
				created_at: "2026-10-09T09:00:00Z",
				updated_at: "2026-10-09T10:00:00Z",
				financing_plan: null,
				trade_in: null,
				documents: [{
					id: "document-1",
					type: "IDENTITY_CARD",
					status: "UPLOADED",
					original_filename: "identity.pdf",
					content_type: "application/pdf",
					size: 100,
					created_at: "2026-10-09T09:30:00Z",
					uploaded_at: "2026-10-09T09:30:00Z",
				}],
				comment: null,
				rejection_reason: null,
				requested_document_types: null,
				rejected_at: null,
			},
			isLoading: false,
			isError: false,
			error: null,
		} as ReturnType<typeof useDossierDetail>);
	});

	it("requests a document view URL using its dossier ID and opens the returned URL", async () => {
		const getSpy = vi.spyOn(apiClient, "get").mockResolvedValue({
			data: { url: "https://documents.example/identity.pdf", expires_in: 60 },
		});
		const openSpy = vi.spyOn(window, "open").mockImplementation(() => null);

		render(
			<QueryClientProvider client={new QueryClient()}>
				<MemoryRouter initialEntries={["/admin/dossiers/dossier-1"]}>
					<Routes>
						<Route path="/admin/dossiers/:dossierId" element={<AdminDossierDetailPage />} />
					</Routes>
				</MemoryRouter>
			</QueryClientProvider>,
		);

		fireEvent.click(screen.getByRole("button", { name: "Consulter" }));

		await waitFor(() => {
			expect(getSpy).toHaveBeenCalledWith(
				"/api/v1/dossiers/dossier-1/documents/document-1/view-url",
			);
		});
		expect(openSpy).toHaveBeenCalledWith(
			"https://documents.example/identity.pdf",
			"_blank",
			"noopener,noreferrer",
		);
	});
});
