import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { MemoryRouter, Routes, Route, useLocation } from "react-router-dom";

import { useAuthStore } from "../../auth/ui/hooks/useAuth";
import { ProtectedRoute } from "../../auth/ui/components/ProtectedRoute";
import { DossiersPage } from "../../dossiers/ui/pages/DossiersPage";

vi.mock("../../auth/ui/hooks/useAuth", () => ({
  useAuthStore: vi.fn(),
}));

vi.mock("../../vehicles/ui/pages/AddVehiclePage", () => ({
  AddVehiclePage: () => <div>Formulaire Création Véhicule Page</div>,
}));

// Composant pour vérifier la route courante dans les assertions
const LocationDisplay = () => {
  const location = useLocation();
  return <div data-testid="location-display">{location.pathname}</div>;
};

describe("Tâche 8 — Sécurité des routes et navigation Back-Office", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const renderWithRouter = (initialEntries: string[]) => {
    return render(
      <MemoryRouter initialEntries={initialEntries}>
        <LocationDisplay />
        <Routes>
          <Route path="/login" element={<div>Page de Connexion</div>} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DossiersPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/vehicles/new"
            element={
              <ProtectedRoute requiredRole="ADMIN">
                <div>Formulaire Création Véhicule Page</div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </MemoryRouter>
    );
  };

  it("redirige un visiteur non authentifié accédant à /admin/vehicles/new vers /login", () => {
    (useAuthStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
      isAuthenticated: false,
      user: null,
    });

    renderWithRouter(["/admin/vehicles/new"]);

    expect(screen.getByTestId("location-display")).toHaveTextContent("/login");
    expect(screen.getByText("Page de Connexion")).toBeInTheDocument();
  });

  it("redirige un utilisateur CLIENT accédant à /admin/vehicles/new vers /dashboard", () => {
    (useAuthStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
      isAuthenticated: true,
      user: { role: "CLIENT", first_name: "Jean", last_name: "Dupont", email: "jean@test.com" },
    });

    renderWithRouter(["/admin/vehicles/new"]);

    expect(screen.getByTestId("location-display")).toHaveTextContent("/dashboard");
    expect(screen.getByText("Tableau de bord")).toBeInTheDocument();
    expect(screen.queryByText("Formulaire Création Véhicule Page")).not.toBeInTheDocument();
  });

  it("autorise un utilisateur ADMIN à accéder à /admin/vehicles/new", () => {
    (useAuthStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
      isAuthenticated: true,
      user: { role: "ADMIN", first_name: "Admin", last_name: "User", email: "admin@test.com" },
    });

    renderWithRouter(["/admin/vehicles/new"]);

    expect(screen.getByTestId("location-display")).toHaveTextContent("/admin/vehicles/new");
    expect(screen.getByText("Formulaire Création Véhicule Page")).toBeInTheDocument();
  });

  it("masque le bouton 'Ajouter un véhicule' dans le tableau de bord pour un CLIENT", () => {
    (useAuthStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
      isAuthenticated: true,
      user: { role: "CLIENT", first_name: "Jean", last_name: "Dupont", email: "jean@test.com" },
    });

    renderWithRouter(["/dashboard"]);

    expect(screen.queryByRole("button", { name: /Ajouter un véhicule/i })).not.toBeInTheDocument();
  });

  it("affiche le bouton 'Ajouter un véhicule' dans le tableau de bord pour un ADMIN et permet la navigation", () => {
    (useAuthStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
      isAuthenticated: true,
      user: { role: "ADMIN", first_name: "Admin", last_name: "User", email: "admin@test.com" },
    });

    renderWithRouter(["/dashboard"]);

    const addButton = screen.getByRole("button", { name: /Ajouter un véhicule/i });
    expect(addButton).toBeInTheDocument();

    fireEvent.click(addButton);

    expect(screen.getByTestId("location-display")).toHaveTextContent("/admin/vehicles/new");
    expect(screen.getByText("Formulaire Création Véhicule Page")).toBeInTheDocument();
  });
});