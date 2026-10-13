import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";

import { DossiersClient } from "../../../infrastructure/DossiersClient";
import { useSubscriptionTunnelStore } from "../../../application/stores/useSubscriptionTunnelStore";
import { useVehicleDetailQuery } from "../../../../vehicles/application/hooks/useVehicleDetailQuery";
import { useDossierStatus } from "../../hooks/useDossierStatus";
import { SimulatorPage } from "../../../../vehicles/ui/pages/SimulatorPage";
import { NewDossierPage } from "../NewDossierPage";
import { AccountDossierPage } from "../AccountDossierPage";

// ============================================================================
// MOCKS
// ============================================================================

vi.mock("../../../../vehicles/application/hooks/useVehicleDetailQuery", () => ({
  useVehicleDetailQuery: vi.fn(),
}));

vi.mock("../../../infrastructure/DossiersClient", () => ({
  DossiersClient: {
    createDossier: vi.fn(),
    cancelDossier: vi.fn(),
    getDocuments: vi.fn(),
    submitDossier: vi.fn(),
  },
}));

vi.mock("../../hooks/useDossierStatus", () => ({
  useDossierStatus: vi.fn(),
}));

vi.mock("../../components/DocumentUploader", () => ({
  DOCUMENT_TYPE_LABELS: {
    IDENTITY_CARD: "Pièce d'identité",
    PROOF_OF_ADDRESS: "Justificatif de domicile",
    PAYSLIP: "Fiche de paie",
    BANK_DETAILS: "Relevé d'identité bancaire",
    DRIVERS_LICENSE: "Permis de conduire",
    REGISTRATION_CERTIFICATE: "Certificat d'immatriculation",
    OTHER: "Autre document",
  },
  DocumentUploader: ({
    onUploadComplete,
    fixedDocumentType,
  }: {
    onUploadComplete: () => void;
    fixedDocumentType?: string;
  }) => (
    <>
      {fixedDocumentType && (
        <output data-testid="requested-document-type">{fixedDocumentType}</output>
      )}
      <button type="button" onClick={onUploadComplete}>
        Téléverser une pièce de test
      </button>
    </>
  ),
}));

// ============================================================================
// DONNÉES DE TEST
// ============================================================================

const mockVehicle = {
  id: "vehicle-flow-1",
  brand: "Peugeot",
  model: "308",
  year: 2025,
  catalog_type: "RENTAL" as const,
  monthly_rent: "399.00",
  photo_url: null,
  included_services: [],
  price: "26000.00",
  mileage: 8000,
  energy_type: "HYBRIDE",
  description: "Véhicule de test",
  services: [],
};

const LocationDisplay = () => {
  const location = useLocation();
  return (
    <output data-testid="current-location">
      {`${location.pathname}${location.search}`}
    </output>
  );
};

// ============================================================================
// SUITES DE TESTS
// ============================================================================

describe("Parcours de souscription", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Réinitialisation sécurisée du store
    const store = useSubscriptionTunnelStore.getState();
    if (typeof store.resetTunnel === "function") {
      store.resetTunnel();
    }

    vi.mocked(useVehicleDetailQuery).mockReturnValue({
      data: mockVehicle,
      isLoading: false,
      error: null,
    } as unknown as ReturnType<typeof useVehicleDetailQuery>);

    vi.mocked(DossiersClient.createDossier).mockResolvedValue({
      id: "dossier-flow-1",
      vehicle_id: mockVehicle.id,
      status: "DRAFT",
    });

    vi.mocked(DossiersClient.getDocuments).mockResolvedValue([
      {
        id: "document-flow-1",
        type: "IDENTITY_CARD",
        status: "UPLOADED",
        original_filename: "identite.pdf",
        content_type: "application/pdf",
        size: 100,
        created_at: "2026-09-29T10:00:00Z",
        uploaded_at: "2026-09-29T10:00:00Z",
      },
    ]);

    vi.mocked(DossiersClient.submitDossier).mockResolvedValue({
      id: "dossier-flow-1",
      vehicle_id: mockVehicle.id,
      status: "SUBMITTED",
    });

    vi.mocked(DossiersClient.cancelDossier).mockResolvedValue({
      id: "dossier-flow-1",
      vehicle_id: mockVehicle.id,
      status: "CANCELLED",
    });

    vi.mocked(useDossierStatus).mockReturnValue({
      data: {
        status: "SUBMITTED",
        updated_at: "2026-09-29T10:00:00Z",
        decision_comment: null,
      },
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useDossierStatus>);
  });

  it("va de la simulation au dossier soumis et à son suivi client", async () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/simulator?vehicleId=vehicle-flow-1"]}>
          <LocationDisplay />
          <Routes>
            <Route path="/simulator" element={<SimulatorPage />} />
            <Route path="/dossiers/new" element={<NewDossierPage />} />
            <Route
              path="/account/dossiers/:dossierId"
              element={<AccountDossierPage />}
            />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(
      await screen.findByRole("heading", { name: "Peugeot 308" })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("spinbutton", { name: "Montant de référence (€)" })
    ).toHaveValue(26000);
    
    fireEvent.click(
      screen.getByRole("button", { name: "Valider la simulation" })
    );

    const dossierCreateButton = await screen.findByRole("button", {
      name: "Créer le dossier et déposer mes pièces",
    });
    
    expect(screen.getByTestId("current-location").textContent).toMatch(
      /^\/dossiers\/new\?simulationId=/
    );
    expect(screen.getByTestId("current-location")).toHaveTextContent(
      `vehicleId=${mockVehicle.id}&mode=rental`
    );
    expect(
      screen.getByText("Votre demande de location longue durée · Peugeot 308")
    ).toBeInTheDocument();
    expect(useSubscriptionTunnelStore.getState().vehicleId).toBe(mockVehicle.id);
    expect(
      useSubscriptionTunnelStore.getState().financingPlan?.monthly_payment
    ).toBeGreaterThan(0);

    fireEvent.click(dossierCreateButton);
    
    expect(
      await screen.findByRole("button", { name: "Téléverser une pièce de test" })
    ).toBeInTheDocument();
    
    fireEvent.click(
      screen.getByRole("button", { name: "Téléverser une pièce de test" })
    );
    
    await waitFor(() =>
      expect(
        screen.getByRole("button", { name: "Soumettre mon dossier" })
      ).toBeEnabled()
    );
    
    fireEvent.click(
      screen.getByRole("button", { name: "Soumettre mon dossier" })
    );

    expect(
      await screen.findByRole("heading", { name: "Suivi de votre dossier" })
    ).toBeInTheDocument();
    expect(screen.getByText("En cours d’étude")).toBeInTheDocument();
    expect(screen.getByText("identite.pdf")).toBeInTheDocument();
    
    expect(DossiersClient.createDossier).toHaveBeenCalledWith(
      expect.objectContaining({ vehicle_id: mockVehicle.id })
    );
    expect(DossiersClient.submitDossier).toHaveBeenCalledWith("dossier-flow-1");
    expect(screen.getByTestId("current-location")).toHaveTextContent(
      "/account/dossiers/dossier-flow-1"
    );
  });

  it("reprend la création depuis l’URL sans dépendre du store mémoire", async () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter
          initialEntries={[
            `/dossiers/new?simulationId=resume-1&vehicleId=${mockVehicle.id}&mode=rental`,
          ]}
        >
          <Routes>
            <Route path="/dossiers/new" element={<NewDossierPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    fireEvent.click(
      await screen.findByRole("button", {
        name: "Créer le dossier et déposer mes pièces",
      })
    );

    await waitFor(() =>
      expect(DossiersClient.createDossier).toHaveBeenCalledWith(
        expect.objectContaining({ vehicle_id: mockVehicle.id })
      )
    );
  });

  it("bloque la soumission et affiche un état vide sans pièce téléversée", async () => {
    vi.mocked(DossiersClient.getDocuments).mockResolvedValue([]);
    
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter
          initialEntries={[
            `/dossiers/new?simulationId=resume-1&dossierId=dossier-flow-1&vehicleId=${mockVehicle.id}&mode=rental`,
          ]}
        >
          <Routes>
            <Route path="/dossiers/new" element={<NewDossierPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(
      await screen.findByText(/Aucune pièce téléversée/)
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Soumettre mon dossier" })
    ).toBeDisabled();
  });

  it("permet au client d’annuler un dossier encore en préparation", async () => {
    vi.mocked(useDossierStatus).mockReturnValue({
      data: {
        status: "DRAFT",
        updated_at: "2026-09-29T10:00:00Z",
        decision_comment: null,
      },
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useDossierStatus>);

    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/account/dossiers/dossier-flow-1"]}>
          <Routes>
            <Route
              path="/account/dossiers/:dossierId"
              element={<AccountDossierPage />}
            />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    fireEvent.click(
      await screen.findByRole("button", { name: "Annuler ma demande" })
    );
    
    expect(
      await screen.findByRole("heading", { name: "Annuler cette demande ?" })
    ).toBeInTheDocument();
    
    fireEvent.click(
      screen.getByRole("button", { name: "Confirmer l’annulation" })
    );

    await waitFor(() =>
      expect(DossiersClient.cancelDossier).toHaveBeenCalledWith("dossier-flow-1")
    );
  });

  it("affiche les types demandés, permet leur téléversement et retransmet le dossier", async () => {
    vi.mocked(useDossierStatus).mockReturnValue({
      data: {
        status: "DOCUMENTS_PENDING",
        updated_at: "2026-09-29T10:00:00Z",
        decision_comment: null,
        requested_document_types: ["IDENTITY_CARD", "PAYSLIP"],
      },
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useDossierStatus>);

    vi.mocked(DossiersClient.getDocuments).mockResolvedValue([
      {
        id: "identity-1",
        type: "IDENTITY_CARD",
        status: "UPLOADED",
        original_filename: "identite.pdf",
        content_type: "application/pdf",
        size: 100,
        created_at: "2026-09-29T10:00:00Z",
        uploaded_at: "2026-09-29T10:00:00Z",
      },
      {
        id: "payslip-1",
        type: "PAYSLIP",
        status: "UPLOADED",
        original_filename: "fiche-paie.pdf",
        content_type: "application/pdf",
        size: 100,
        created_at: "2026-09-29T10:00:00Z",
        uploaded_at: "2026-09-29T10:00:00Z",
      },
    ]);

    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/account/dossiers/dossier-flow-1"]}>
          <Routes>
            <Route
              path="/account/dossiers/:dossierId"
              element={<AccountDossierPage />}
            />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(
      (await screen.findAllByText("Pièces complémentaires demandées")).length
    ).toBeGreaterThan(0);
    expect(screen.getByText("Pièce d'identité")).toBeInTheDocument();
    expect(screen.getByText("Fiche de paie")).toBeInTheDocument();
    
    expect(
      screen.getAllByTestId("requested-document-type").map((item) => item.textContent)
    ).toEqual(["IDENTITY_CARD", "PAYSLIP"]);

    const resubmitButton = await screen.findByRole("button", {
      name: "Transmettre les pièces à l’étude",
    });
    
    await waitFor(() => expect(resubmitButton).toBeEnabled());
    fireEvent.click(resubmitButton);

    await waitFor(() =>
      expect(DossiersClient.submitDossier).toHaveBeenCalledWith("dossier-flow-1")
    );
  });

  it("signale une demande de pièces même si la liste des types n’est pas disponible", async () => {
    vi.mocked(useDossierStatus).mockReturnValue({
      data: {
        status: "DOCUMENTS_PENDING",
        updated_at: "2026-09-29T10:00:00Z",
        decision_comment: null,
        requested_document_types: null,
      },
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useDossierStatus>);

    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/account/dossiers/dossier-flow-1"]}>
          <Routes>
            <Route
              path="/account/dossiers/:dossierId"
              element={<AccountDossierPage />}
            />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    );

    expect(
      (await screen.findAllByText("Pièces complémentaires demandées")).length
    ).toBeGreaterThan(0);
    expect(
      screen.getByText(/L’étude attend des pièces complémentaires/)
    ).toBeInTheDocument();
  });
});