import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { ThemeProvider } from "@mui/material/styles";
import { theme } from "../../../../shared/ui/theme/theme";
import { AdminDossiersList } from "../AdminDossiersList";
import { DocumentList } from "../DocumentList";
import { DossierStatusCard } from "../DossierStatusCard";
import { TradeInForm } from "../TradeInForm";
import { useSubscriptionTunnelStore } from "../../../../dossiers/application/stores/useSubscriptionTunnelStore";
import type { DocumentListItem, PendingDossierItem } from "../../../infrastructure/DossiersClient";

const pendingItem: PendingDossierItem = {
  id: "dossier-1",
  user_id: "user-1",
  client_email: "client@example.com",
  vehicle_id: "vehicle-1",
  vehicle_brand: "Peugeot",
  vehicle_model: "208",
  status: "SUBMITTED",
  submitted_at: "2026-01-10T10:00:00.000Z",
  created_at: "2026-01-09T10:00:00.000Z",
  updated_at: "2026-01-10T10:00:00.000Z",
};

const documents: DocumentListItem[] = [
  {
    id: "document-1",
    type: "IDENTITY_CARD",
    status: "UPLOADED",
    original_filename: "identite.pdf",
    content_type: "application/pdf",
    size: 1000,
    created_at: "2026-01-01T10:00:00.000Z",
    uploaded_at: "2026-01-02T10:00:00.000Z",
  },
  {
    id: "document-2",
    type: "PROOF_OF_ADDRESS",
    status: "VALIDATED",
    original_filename: "domicile.pdf",
    content_type: "application/pdf",
    size: 1000,
    created_at: "2026-01-01T10:00:00.000Z",
    uploaded_at: null,
  },
  {
    id: "document-3",
    type: "PAYSLIP",
    status: "REJECTED",
    original_filename: "salaire.pdf",
    content_type: "application/pdf",
    size: 1000,
    created_at: "2026-01-01T10:00:00.000Z",
    uploaded_at: null,
  },
];

function renderTradeIn() {
  return render(
    <ThemeProvider theme={theme}>
      <TradeInForm />
    </ThemeProvider>,
  );
}

describe("Dossier UI components", () => {
  beforeEach(() => {
    useSubscriptionTunnelStore.getState().resetTunnel();
  });

  it("affiche un tableau de dossiers et navigue vers le détail", () => {
    render(
      <MemoryRouter initialEntries={["/admin/dossiers"]}>
        <Routes>
          <Route path="/admin/dossiers" element={<AdminDossiersList items={[pendingItem]} />} />
          <Route path="/admin/dossiers/:id" element={<div>Détail du dossier</div>} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText("client@example.com")).toBeInTheDocument();
    expect(screen.getByText("En cours d’étude")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Voir" }));
    expect(screen.getByText("Détail du dossier")).toBeInTheDocument();
  });

  it("affiche l'état vide de la liste de documents", () => {
    render(<DocumentList documents={[]} />);
    expect(screen.getByText("Aucun document téléversé")).toBeInTheDocument();
  });

  it("affiche les documents et leurs statuts", () => {
    render(<DocumentList documents={documents} />);
    expect(screen.getByText("identite.pdf")).toBeInTheDocument();
    expect(screen.getByText("domicile.pdf")).toBeInTheDocument();
    expect(screen.getByText("salaire.pdf")).toBeInTheDocument();
    expect(screen.getAllByText("UPLOADED")).toHaveLength(1);
    expect(screen.getAllByText("VALIDATED")).toHaveLength(1);
    expect(screen.getAllByText("REJECTED")).toHaveLength(1);
  });

  it("affiche le commentaire d'un dossier rejeté", () => {
    render(
      <DossierStatusCard
        status="REJECTED"
        updatedAt="2026-01-10T10:00:00.000Z"
        decisionComment="Pièce justificative illisible"
      />,
    );
    expect(screen.getByText("Dossier refusé")).toBeInTheDocument();
    expect(screen.getByText("Motif du refus :")).toBeInTheDocument();
    expect(screen.getByText("Pièce justificative illisible")).toBeInTheDocument();
  });

  it("permet d'activer la reprise et affiche les erreurs de validation", () => {
    renderTradeIn();
    fireEvent.click(screen.getByRole("checkbox", { name: "Toggle reprise véhicule" }));
    expect(screen.getByRole("textbox", { name: /Immatriculation/ })).toBeInTheDocument();
    expect(screen.getByText("L'immatriculation est obligatoire.")).toBeInTheDocument();
    expect(screen.getByText("Le kilométrage doit être un nombre positif ou nul.")).toBeInTheDocument();
    expect(useSubscriptionTunnelStore.getState().tradeIn).toBeNull();
  });

  it("enregistre une reprise valide et la supprime quand le toggle est désactivé", () => {
    renderTradeIn();
    fireEvent.click(screen.getByRole("checkbox", { name: "Toggle reprise véhicule" }));
    fireEvent.change(screen.getByRole("textbox", { name: /Immatriculation/ }), { target: { value: " AB-123-CD " } });
    fireEvent.change(screen.getByRole("spinbutton", { name: /Kilométrage/ }), { target: { value: "42000" } });
    fireEvent.change(screen.getByRole("textbox", { name: /^Marque/ }), { target: { value: "Peugeot" } });
    fireEvent.change(screen.getByRole("textbox", { name: /^Modèle/ }), { target: { value: "208" } });
    expect(useSubscriptionTunnelStore.getState().tradeIn).toEqual({
      registration: "AB-123-CD",
      mileage: 42000,
      brand: "Peugeot",
      model: "208",
    });
    fireEvent.click(screen.getByRole("checkbox", { name: "Toggle reprise véhicule" }));
    expect(useSubscriptionTunnelStore.getState().tradeIn).toBeNull();
  });
});
