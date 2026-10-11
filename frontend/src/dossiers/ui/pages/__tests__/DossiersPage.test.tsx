import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, useLocation } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useAuthStore } from "../../../../auth/ui/hooks/useAuth";
import { useDossiers } from "../../hooks/useDossiers";
import { DossiersPage } from "../DossiersPage";

vi.mock("../../../../auth/ui/hooks/useAuth", () => ({
	useAuthStore: vi.fn(),
}));

vi.mock("../../hooks/useDossiers", () => ({
	useDossiers: vi.fn(),
}));

function CurrentLocation() {
	const location = useLocation();
	return <output data-testid="current-location">{`${location.pathname}${location.search}`}</output>;
}

describe("DossiersPage", () => {
	beforeEach(() => {
		vi.mocked(useAuthStore).mockReturnValue({
			user: { first_name: "Camille", last_name: "Martin", email: "camille@example.com", role: "CLIENT" },
			isAuthenticated: true,
			logout: vi.fn(),
		} as never);
		vi.mocked(useDossiers).mockReturnValue({
			data: [],
			isLoading: false,
			isError: false,
		} as never);
	});

	it("affiche un état vide utile et dirige vers le catalogue LLD", () => {
		render(
			<MemoryRouter initialEntries={["/dashboard"]}>
				<DossiersPage />
				<CurrentLocation />
			</MemoryRouter>,
		);

		expect(screen.getByText("Vous trouverez ici le suivi de vos demandes.")).toBeInTheDocument();
		expect(screen.queryByText("Le service rencontre un problème technique. Réessayez plus tard.")).not.toBeInTheDocument();
		fireEvent.click(screen.getByRole("button", { name: "Offres LLD" }));
		expect(screen.getByTestId("current-location")).toHaveTextContent("/catalogue?mode=rental");
	});

	it("conserve les dossiers annulés dans l'historique du tableau de bord", () => {
		vi.mocked(useDossiers).mockReturnValue({
			data: [
				{ id: "draft-1", status: "DRAFT", updated_at: "2026-10-01T10:00:00Z" },
				{ id: "cancelled-1", status: "CANCELLED", updated_at: "2026-10-02T10:00:00Z" },
				{ id: "validated-1", status: "VALIDATED", updated_at: "2026-10-03T10:00:00Z" },
			],
			isLoading: false,
			isError: false,
		} as never);

		render(
			<MemoryRouter initialEntries={["/dashboard"]}>
				<DossiersPage />
			</MemoryRouter>,
		);

		expect(screen.getByText("Dossier de financement")).toBeInTheDocument();
		expect(screen.getByText(/Historique de mes dossiers/)).toBeInTheDocument();
		expect(screen.getByText(/ANNULÉ/)).toBeInTheDocument();
		expect(screen.getByText(/#validate — VALIDÉ/)).toBeInTheDocument();
	});

	it("signale les pièces demandées et dirige le client vers leur téléversement", () => {
		vi.mocked(useDossiers).mockReturnValue({
			data: [
				{
					id: "dossier-submitted-1",
					status: "SUBMITTED",
					requested_document_types: null,
					updated_at: "2026-09-30T10:00:00Z",
				},
				{
					id: "dossier-documents-1",
					status: "DOCUMENTS_PENDING",
					requested_document_types: ["IDENTITY_CARD", "PAYSLIP"],
					updated_at: "2026-10-01T10:00:00Z",
				},
			],
			isLoading: false,
			isError: false,
		} as never);

		render(
			<MemoryRouter initialEntries={["/dashboard"]}>
				<DossiersPage />
				<CurrentLocation />
			</MemoryRouter>,
		);

		expect(screen.getByText("Pièces complémentaires demandées")).toBeInTheDocument();
		expect(screen.getByText("Pièce d'identité, Fiche de paie")).toBeInTheDocument();
		fireEvent.click(screen.getByRole("button", { name: "Transmettre les pièces" }));
		expect(screen.getByTestId("current-location")).toHaveTextContent(
			"/account/dossiers/dossier-documents-1",
		);
	});
});