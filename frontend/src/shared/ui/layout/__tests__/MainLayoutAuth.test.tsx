import { act, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { useAuthStore } from "../../../../auth/ui/hooks/useAuth";
import { MainLayout } from "../MainLayout";

describe("MainLayout avec le store d’authentification réel", () => {
    beforeEach(() => {
        useAuthStore.getState().logout();
    });

    it("actualise immédiatement le menu après la mise à jour du jeton et du profil", () => {
        render(
            <MemoryRouter initialEntries={["/"]}>
                <Routes>
                    <Route element={<MainLayout />}>
                        <Route index element={<div>Accueil</div>} />
                        <Route path="admin/dossiers" element={<div>Admin Dossiers</div>} />
                    </Route>
                </Routes>
            </MemoryRouter>
        );

        // 1. État anonyme : Vérification du lien de connexion
        expect(screen.getByRole("link", { name: "Connexion" })).toBeInTheDocument();

        // 2. Passage du jeton : Mise à jour de l'état authentifié et présence de l'action de déconnexion
        act(() => {
            useAuthStore.getState().setToken("token-test");
        });
        expect(screen.getByRole("button", { name: "Déconnexion" })).toBeInTheDocument();

        // 3. Attribution du rôle ADMIN : Affichage synchrone des accès d'administration
        act(() => {
            useAuthStore.getState().setUser({
                id: "user-test",
                email: "admin@example.com",
                first_name: "Admin",
                last_name: "Test",
                role: "ADMIN",
                is_active: true,
            });
        });
        expect(screen.getByRole("link", { name: "Dossiers de souscription" })).toBeInTheDocument();
    });
});