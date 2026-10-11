import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { matchRoutes, MemoryRouter, Routes, Route, useLocation } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { useAuthStore } from "../../auth/ui/hooks/useAuth";
import { ProtectedRoute } from "../../auth/ui/components/ProtectedRoute";
import { DossiersPage } from "../../dossiers/ui/pages/DossiersPage";
import { router } from "../router";

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
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={initialEntries}>
          <LocationDisplay />
          <Routes>
            <Route path="/login" element={<div>Page de Connexion</div>} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute requiredRole="CLIENT">
                  <DossiersPage />
                </ProtectedRoute>
              }
            />
            <Route path="/admin/dossiers" element={<div>File de traitement admin</div>} />
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
      </QueryClientProvider>
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
    expect(screen.getByText("ESPACE CLIENT")).toBeInTheDocument();
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

  it("redirige un ADMIN du tableau de bord client vers sa file de traitement", () => {
    (useAuthStore as unknown as ReturnType<typeof vi.fn>).mockReturnValue({
      isAuthenticated: true,
      user: { role: "ADMIN", first_name: "Admin", last_name: "User", email: "admin@test.com" },
    });

    renderWithRouter(["/dashboard"]);

    expect(screen.getByTestId("location-display")).toHaveTextContent("/admin/dossiers");
    expect(screen.getByText("File de traitement admin")).toBeInTheDocument();
    expect(screen.queryByText("ESPACE CLIENT")).not.toBeInTheDocument();
  });

  it("déclare le raccourci profil et redirige les routes inconnues vers l’accueil", () => {
    const profileMatches = matchRoutes(router.routes, "/profil");
    const unknownMatches = matchRoutes(router.routes, "/route-inconnue");

    expect(profileMatches?.[profileMatches.length - 1]?.route.path).toBe("profil");
    expect(unknownMatches?.[unknownMatches.length - 1]?.route.path).toBe("*");
  });
});