import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { FinancialSummaryPanel } from "../FinancialSummaryPanel";
import type { AdminDossierDetailResponse } from "../../../infrastructure/DossiersClient";

const createMockDossier = (
	overrides: Partial<AdminDossierDetailResponse> = {}
): AdminDossierDetailResponse => ({
	id: "test-id",
	user_id: "user-id",
	client_email: "test@example.com",
	vehicle_id: "vehicle-id",
	vehicle_brand: "Peugeot",
	vehicle_model: "208",
	vehicle_price: "15000",
	status: "SUBMITTED",
	submitted_at: "2026-09-18T10:00:00Z",
	created_at: "2026-09-18T09:00:00Z",
	updated_at: "2026-09-18T10:00:00Z",
	financing_plan: null,
	trade_in: null,
	documents: [],
	comment: null,
	rejection_reason: null,
	requested_document_types: null,
	rejected_at: null,
	...overrides,
});

describe("FinancialSummaryPanel", () => {
	it("affiche le financement et la reprise lorsqu'ils sont présents", () => {
		const dossier = createMockDossier({
			financing_plan: {
				down_payment: "2000",
				duration_months: 48,
				monthly_payment: "395",
			},
			trade_in: {
				registration: "AB-123-CD",
				mileage: 50000,
				brand: "Renault",
				model: "Clio",
				estimated_value: "5000",
			},
		});

		render(<FinancialSummaryPanel dossier={dossier} />);

		expect(screen.getByText("Financement")).toBeInTheDocument();
		expect(screen.getByText("Reprise")).toBeInTheDocument();
		expect(screen.getByText("AB-123-CD")).toBeInTheDocument();
	});

	it("affiche l'apport initial correctement", () => {
		const dossier = createMockDossier({
			financing_plan: {
				down_payment: "2500",
				duration_months: 60,
				monthly_payment: "300",
			},
		});

		render(<FinancialSummaryPanel dossier={dossier} />);

		expect(screen.getByText("Apport initial")).toBeInTheDocument();
		expect(screen.getByText("2 500,00 €")).toBeInTheDocument();
	});

	it("calcule correctement le capital à financer", () => {
		const dossier = createMockDossier({
			vehicle_price: "20000",
			financing_plan: {
				down_payment: "3000",
				duration_months: 48,
				monthly_payment: "400",
			},
		});

		render(<FinancialSummaryPanel dossier={dossier} />);

		expect(screen.getByText("Capital à financer")).toBeInTheDocument();
		expect(screen.getByText("17 000,00 €")).toBeInTheDocument();
	});

	it("affiche la durée et la mensualité", () => {
		const dossier = createMockDossier({
			financing_plan: {
				down_payment: "2000",
				duration_months: 48,
				monthly_payment: "395",
			},
		});

		render(<FinancialSummaryPanel dossier={dossier} />);

		expect(screen.getByText("48 mois")).toBeInTheDocument();
		expect(screen.getByText("395,00 €")).toBeInTheDocument();
	});

	it("affiche les informations de reprise", () => {
		const dossier = createMockDossier({
			trade_in: {
				registration: "XY-987-ZW",
				mileage: 75000,
				brand: "Citroën",
				model: "C3",
				estimated_value: "4500",
			},
		});

		render(<FinancialSummaryPanel dossier={dossier} />);

		expect(screen.getByText("XY-987-ZW")).toBeInTheDocument();
		expect(screen.getByText("Citroën C3")).toBeInTheDocument();
		expect(screen.getByText("75 000 km")).toBeInTheDocument();
		expect(screen.getByText("4 500,00 €")).toBeInTheDocument();
	});

	it("affiche 'Aucun financement renseigné' quand financing_plan est null", () => {
		const dossier = createMockDossier({
			financing_plan: null,
		});

		render(<FinancialSummaryPanel dossier={dossier} />);

		expect(screen.getByText("Aucun financement renseigné")).toBeInTheDocument();
	});

	it("affiche 'Aucune reprise demandée' quand trade_in est null", () => {
		const dossier = createMockDossier({
			trade_in: null,
		});

		render(<FinancialSummaryPanel dossier={dossier} />);

		expect(screen.getByText("Aucune reprise demandée")).toBeInTheDocument();
	});

	it("affiche 'En attente d'évaluation' quand estimated_value est null", () => {
		const dossier = createMockDossier({
			trade_in: {
				registration: "AB-123-CD",
				mileage: 50000,
				brand: "Peugeot",
				model: "208",
				estimated_value: null,
			},
		});

		render(<FinancialSummaryPanel dossier={dossier} />);

		expect(screen.getByText("En attente d'évaluation")).toBeInTheDocument();
	});

	it("n'affiche pas le capital à financer quand vehicle_price est absent", () => {
		const dossier = createMockDossier({
			vehicle_price: null,
			financing_plan: {
				down_payment: "2000",
				duration_months: 48,
				monthly_payment: "395",
			},
		});

		render(<FinancialSummaryPanel dossier={dossier} />);

		expect(screen.getByText("Non calculable")).toBeInTheDocument();
	});
});