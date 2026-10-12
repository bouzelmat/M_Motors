import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { LoginPage } from "../LoginPage";
import { useAuthStore } from "../../hooks/useAuth";

vi.mock("../../hooks/useAuth", () => ({
  useAuthStore: vi.fn(),
}));

describe("LoginPage", () => {
  const login = vi.fn();
  const clearError = vi.fn();

  function renderPage(initialEntries: Parameters<typeof MemoryRouter>[0]["initialEntries"] = ["/login"]) {
    return render(
      <MemoryRouter initialEntries={initialEntries}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/dashboard" element={<div>Tableau de bord</div>} />
          <Route path="/admin/dossiers" element={<div>Administration des dossiers</div>} />
          <Route path="/catalogue" element={<div>Catalogue</div>} />
          <Route path="/register" element={<div>Inscription</div>} />
        </Routes>
      </MemoryRouter>,
    );
  }

  beforeEach(() => {
    vi.clearAllMocks();
    login.mockResolvedValue(undefined);
    vi.mocked(useAuthStore).mockReturnValue({
      login,
      isLoading: false,
      error: null,
      clearError,
    } as never);
    useAuthStore.getState = vi.fn(() => ({ user: { role: "CLIENT" } })) as never;
  });

  it("soumet les identifiants et redirige un client vers son tableau de bord", async () => {
    renderPage();
    fireEvent.change(screen.getByRole("textbox", { name: /Adresse email/ }), {
      target: { value: "client@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/Mot de passe/), {
      target: { value: "Secret123!" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Se connecter" }));

    await waitFor(() => {
      expect(login).toHaveBeenCalledWith("client@example.com", "Secret123!");
    });
    expect(await screen.findByText("Tableau de bord")).toBeInTheDocument();
  });

  it("redirige un administrateur vers l'espace d'administration", async () => {
    useAuthStore.getState = vi.fn(() => ({ user: { role: "ADMIN" } })) as never;
    renderPage();
    fireEvent.change(screen.getByRole("textbox", { name: /Adresse email/ }), {
      target: { value: "admin@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/Mot de passe/), {
      target: { value: "Secret123!" },
    });
    fireEvent.submit(screen.getByRole("button", { name: "Se connecter" }).closest("form")!);

    expect(await screen.findByText("Administration des dossiers")).toBeInTheDocument();
  });

  it("respecte la route d'origine fournie par ProtectedRoute", async () => {
    renderPage([
      {
        pathname: "/login",
        state: { from: { pathname: "/catalogue", search: "?mode=sale", hash: "#resultats" } },
      },
    ]);
    fireEvent.change(screen.getByRole("textbox", { name: /Adresse email/ }), {
      target: { value: "client@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/Mot de passe/), {
      target: { value: "Secret123!" },
    });
    fireEvent.submit(screen.getByRole("button", { name: "Se connecter" }).closest("form")!);

    expect(await screen.findByText("Catalogue")).toBeInTheDocument();
  });

  it("efface l'erreur dès que l'utilisateur modifie un champ", () => {
    vi.mocked(useAuthStore).mockReturnValue({
      login,
      isLoading: false,
      error: "Identifiants invalides",
      clearError,
    } as never);
    renderPage();
    expect(screen.getByText("Identifiants invalides")).toBeInTheDocument();
    fireEvent.change(screen.getByRole("textbox", { name: /Adresse email/ }), {
      target: { value: "client@example.com" },
    });
    expect(clearError).toHaveBeenCalledTimes(1);
  });

  it("désactive le formulaire et affiche le chargement pendant la connexion", () => {
    vi.mocked(useAuthStore).mockReturnValue({
      login,
      isLoading: true,
      error: null,
      clearError,
    } as never);
    renderPage();
    expect(screen.getByRole("textbox", { name: /Adresse email/ })).toBeDisabled();
    expect(screen.getByLabelText(/Mot de passe/)).toBeDisabled();
    expect(screen.getByRole("button")).toBeDisabled();
    expect(screen.getByRole("progressbar")).toBeInTheDocument();
  });
});
