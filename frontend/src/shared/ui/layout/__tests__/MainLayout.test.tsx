import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { useAuthStore } from "../../../../auth/ui/hooks/useAuth";
import { MainLayout } from "../MainLayout";

vi.mock("../../../../auth/ui/hooks/useAuth", () => ({
    useAuthStore: vi.fn(),
}));

const renderLayout = (initialEntry = "/") =>
    render(
        <MemoryRouter initialEntries={[initialEntry]}>
            <Routes>
                <Route element={<MainLayout />}>
                    <Route index element={<div>Contenu de la page</div>} />
                    <Route path="admin/dossiers" element={<div>Admin Dossiers</div>} />
                </Route>
            </Routes>
        </MemoryRouter>
    );

describe("MainLayout", () => {
    beforeEach(() => vi.clearAllMocks());

    it("affiche la navigation publique et les actions de connexion", () => {
        vi.mocked(useAuthStore).mockReturnValue({
            isAuthenticated: false,
            user: null,
        } as ReturnType<typeof useAuthStore>);

        renderLayout();

        // 1. Vérification du logo/lien principal
        expect(screen.getByRole("link", { name: "M-MOTORS" })).toHaveAttribute("href", "/");

        // 2. Vérification des liens de navigation principale
        expect(screen.getAllByRole("link", { name: "Catalogue" })).toHaveLength(1);
        expect(screen.getAllByRole("link", { name: "Simulateur LLD" })).toHaveLength(1);

        // 3. Action de connexion pour utilisateur non authentifié
        expect(screen.getByRole("link", { name: "Connexion" })).toBeInTheDocument();
        expect(screen.getByRole("link", { name: "Voir les véhicules" })).toBeInTheDocument();
    });

    it("propose l’espace client et permet la déconnexion", () => {
        const logout = vi.fn();
        vi.mocked(useAuthStore).mockReturnValue({
            isAuthenticated: true,
            user: { first_name: "Camille", role: "CLIENT" },
            logout,
        } as unknown as ReturnType<typeof useAuthStore>);

        renderLayout();

        // Clic direct sur le bouton Déconnexion présent dans la barre d'en-tête
        fireEvent.click(screen.getByRole("button", { name: "Déconnexion" }));

        expect(logout).toHaveBeenCalledOnce();
    });

    it("affiche une navigation réservée à l’administration", () => {
        vi.mocked(useAuthStore).mockReturnValue({
            isAuthenticated: true,
            user: { role: "ADMIN" },
            logout: vi.fn(),
        } as unknown as ReturnType<typeof useAuthStore>);

        renderLayout("/admin/dossiers");

        // Vérification des liens d'administration réels dans le Drawer
        expect(screen.getByRole("link", { name: "Dossiers de souscription" })).toBeInTheDocument();
        expect(screen.getByRole("link", { name: "Gestion des véhicules" })).toBeInTheDocument();

        // Les liens publics standard ne doivent pas figurer dans le menu admin
        expect(screen.queryByRole("link", { name: "Catalogue" })).not.toBeInTheDocument();
    });
});