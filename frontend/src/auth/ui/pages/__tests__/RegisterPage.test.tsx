import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useAuthStore } from "../../hooks/useAuth";
import { RegisterPage } from "../RegisterPage";

vi.mock("../../hooks/useAuth", () => ({
	useAuthStore: vi.fn(),
}));

describe("RegisterPage", () => {
	const register = vi.fn();

	beforeEach(() => {
		vi.clearAllMocks();
		register.mockResolvedValue(undefined);
		vi.mocked(useAuthStore).mockReturnValue({
			register,
			isLoading: false,
			error: null,
			clearError: vi.fn(),
		} as never);
	});

	function renderPage() {
		return render(
			<MemoryRouter initialEntries={["/register"]}>
				<Routes>
					<Route path="/register" element={<RegisterPage />} />
					<Route path="/login" element={<div>Page de connexion</div>} />
				</Routes>
			</MemoryRouter>,
		);
	}

	it("bloque une confirmation différente", () => {
		renderPage();
		fireEvent.change(screen.getByLabelText(/^Mot de passe/), { target: { value: "SecurePass123!" } });
		fireEvent.change(screen.getByLabelText(/^Confirmer le mot de passe/), { target: { value: "SecurePass123?" } });

		expect(screen.getByText("Les mots de passe ne correspondent pas.")).toBeInTheDocument();
		expect(screen.getByRole("button", { name: "S'inscrire" })).toBeDisabled();
		expect(register).not.toHaveBeenCalled();
	});

	it("accepte les mots de passe conformes et identiques", async () => {
		renderPage();
		fireEvent.change(screen.getByLabelText(/^Prénom/), { target: { value: "Jane" } });
		fireEvent.change(screen.getByLabelText(/^Nom/), { target: { value: "Doe" } });
		fireEvent.change(screen.getByLabelText(/^Adresse email/), { target: { value: "jane@example.com" } });
		fireEvent.change(screen.getByLabelText(/^Mot de passe/), { target: { value: "SecurePass123!" } });
		fireEvent.change(screen.getByLabelText(/^Confirmer le mot de passe/), { target: { value: "SecurePass123!" } });
		fireEvent.click(screen.getByRole("button", { name: "S'inscrire" }));

		await waitFor(() => expect(register).toHaveBeenCalledWith("jane@example.com", "SecurePass123!", "Jane", "Doe"));
		expect(await screen.findByText("Page de connexion")).toBeInTheDocument();
	});
});