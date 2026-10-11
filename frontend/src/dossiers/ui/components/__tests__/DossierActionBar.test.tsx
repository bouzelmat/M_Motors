import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DossierActionBar } from "../DossierActionBar";
import { DossiersClient } from "../../../../api/clients/DossiersClient";


vi.mock("../../../../api/clients/DossiersClient", () => ({
	DossiersClient: {
		validateDossier: vi.fn(),
		rejectDossier: vi.fn(),
		requestDocuments: vi.fn(),
	},
}));

const createTestQueryClient = () =>
	new QueryClient({
		defaultOptions: {
			queries: { retry: false },
			mutations: { retry: false },
		},
	});

const renderWithClient = (ui: React.ReactElement) => {
	const queryClient = createTestQueryClient();
	return render(
		<QueryClientProvider client={queryClient}>
			{ui}
		</QueryClientProvider>
	);
};

describe("US-502 — DossierActionBar", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("n'affiche aucune action pour un dossier VALIDATED", () => {
		renderWithClient(<DossierActionBar dossierId="test-id" status="VALIDATED" />);
		expect(screen.queryByRole("button", { name: "Valider le dossier" })).not.toBeInTheDocument();
		expect(screen.queryByRole("button", { name: "Rejeter le dossier" })).not.toBeInTheDocument();
		expect(screen.queryByRole("button", { name: "Demander des documents" })).not.toBeInTheDocument();
	});

	it("n'affiche aucune action pour un dossier REJECTED", () => {
		renderWithClient(<DossierActionBar dossierId="test-id" status="REJECTED" />);
		expect(screen.queryByRole("button", { name: "Valider le dossier" })).not.toBeInTheDocument();
	});

	it("affiche les actions pour un dossier SUBMITTED", () => {
		renderWithClient(<DossierActionBar dossierId="test-id" status="SUBMITTED" />);
		expect(screen.getByRole("button", { name: "Valider le dossier" })).toBeInTheDocument();
		expect(screen.getByRole("button", { name: "Rejeter le dossier" })).toBeInTheDocument();
		expect(screen.getByRole("button", { name: "Demander des documents" })).toBeInTheDocument();
	});

	it("ouvre la modale de rejet et valide le motif (min 10 caractères)", async () => {
		renderWithClient(<DossierActionBar dossierId="test-id" status="SUBMITTED" />);
		
		// CORRECTION 1 : getByRole cible uniquement le bouton, pas le titre <h2>
		fireEvent.click(screen.getByRole("button", { name: "Rejeter le dossier" }));
		
		// CORRECTION 2 : Le titre de la modale (DialogTitle) est un <h2>, donc rôle "heading"
		await waitFor(() => {
			expect(screen.getByRole("heading", { name: "Rejeter le dossier" })).toBeInTheDocument();
		});

		const reasonInput = screen.getByLabelText(/Motif du rejet/i);
		fireEvent.change(reasonInput, { target: { value: "Court" } });
		
		fireEvent.click(screen.getByRole("button", { name: "Rejeter" }));
		
		await waitFor(() => {
			expect(screen.getByText("Le motif de rejet doit contenir au moins 10 caractères.")).toBeInTheDocument();
		});

		fireEvent.change(reasonInput, { target: { value: "Ce motif est largement assez long pour passer" } });
		vi.mocked(DossiersClient.rejectDossier).mockResolvedValue({
			message: "OK",
			dossier_id: "test-id",
			status: "REJECTED",
		});

		fireEvent.click(screen.getByRole("button", { name: "Rejeter" }));

		await waitFor(() => {
			expect(DossiersClient.rejectDossier).toHaveBeenCalledWith("test-id", "Ce motif est largement assez long pour passer");
		});
	});

	it("ouvre la modale de demande de documents et valide la sélection", async () => {
		renderWithClient(<DossierActionBar dossierId="test-id" status="SUBMITTED" />);
		
		fireEvent.click(screen.getByRole("button", { name: "Demander des documents" }));
		
		// Tenter de soumettre sans sélection
		fireEvent.click(screen.getByRole("button", { name: "Envoyer la demande" }));
		
		await waitFor(() => {
			// CORRECTION 3 : Le texte apparaît 2 fois (dans l'Alert ET dans le FormHelperText).
			// Testing Library exige getAllByText quand c'est intentionnel.
			const errorMessages = screen.getAllByText("Vous devez sélectionner au moins un document.");
			expect(errorMessages.length).toBeGreaterThanOrEqual(1);
		});

		const checkbox = screen.getByRole("checkbox", { name: /Pièce d'identité/i });
		fireEvent.click(checkbox);

		vi.mocked(DossiersClient.requestDocuments).mockResolvedValue({
			message: "OK",
			dossier_id: "test-id",
			status: "DOCUMENTS_PENDING",
		});

		fireEvent.click(screen.getByRole("button", { name: "Envoyer la demande" }));

		await waitFor(() => {
			expect(DossiersClient.requestDocuments).toHaveBeenCalledWith("test-id", ["IDENTITY_CARD"]);
		});
	});

	it("garde la modale ouverte et affiche l'erreur si la demande de documents échoue", async () => {
		vi.mocked(DossiersClient.requestDocuments).mockRejectedValue(new Error("Request failed"));
		renderWithClient(<DossierActionBar dossierId="test-id" status="SUBMITTED" />);

		fireEvent.click(screen.getByRole("button", { name: "Demander des documents" }));
		fireEvent.click(screen.getByRole("checkbox", { name: /Pièce d'identité/i }));
		fireEvent.click(screen.getByRole("button", { name: "Envoyer la demande" }));

		expect(await screen.findByText("Une erreur est survenue lors de l’action.")).toBeInTheDocument();
		expect(screen.getByRole("heading", {
			name: "Demander des documents complémentaires",
		})).toBeInTheDocument();
	});

	it("désactive les boutons pendant l'appel réseau", async () => {
		// CORRECTION 4 : Utilisation d'une promesse contrôlée pour éviter les fuites asynchrones 
		// et l'erreur "window is not defined" en fin de test.
		let resolvePromise: (value: any) => void;
		const mockPromise = new Promise((resolve) => {
			resolvePromise = resolve;
		});
		vi.mocked(DossiersClient.validateDossier).mockReturnValue(mockPromise as any);

		renderWithClient(<DossierActionBar dossierId="test-id" status="SUBMITTED" />);
		
		fireEvent.click(screen.getByRole("button", { name: "Valider le dossier" }));
		
		await waitFor(() => {
			expect(screen.getByRole("button", { name: "Valider" })).toBeInTheDocument();
		});
		
		fireEvent.click(screen.getByRole("button", { name: "Valider" }));

		// Vérifier que le bouton est désactivé et affiche "Traitement..."
		await waitFor(() => {
			const submittingButton = screen.getByRole("button", { name: "Traitement..." });
			expect(submittingButton).toBeDisabled();
		});
		
		// Résoudre la promesse pour terminer proprement la mutation et éviter l'erreur React en fin de test
		resolvePromise!({ message: "OK", dossier_id: "test-id", status: "VALIDATED" });
		
		await waitFor(() => {
			expect(DossiersClient.validateDossier).toHaveBeenCalled();
		});
	});  
});