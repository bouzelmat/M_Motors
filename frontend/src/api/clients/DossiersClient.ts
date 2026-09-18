import { apiClient } from "../apiClient";

export type TradeInRequest = {
	readonly registration: string;
	readonly mileage: number;
	readonly brand?: string | null;
	readonly model?: string | null;
};

export type FinancingPlanRequest = {
	readonly down_payment: number;
	readonly duration_months: number;
	readonly monthly_payment: number;
};

export type CreateDossierRequest = {
	readonly vehicle_id: string;
	readonly trade_in: TradeInRequest | null;
	readonly financing_plan: FinancingPlanRequest | null;
};

export type DossierResponse = {
	readonly id: string;
	readonly vehicle_id: string;
	readonly status: string;
};

export const DossiersClient = {
	async createDossier(
		data: CreateDossierRequest,
	): Promise<DossierResponse> {
		const response = await apiClient.post<DossierResponse>(
			"/api/v1/dossiers",
			data,
		);

		return response.data;
	},
};
