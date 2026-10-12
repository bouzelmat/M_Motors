import axios from "axios";

type ApiErrorBody = {
	detail?: unknown;
};

export function getApiErrorMessage(error: unknown, fallbackMessage: string): string {
	if (!axios.isAxiosError<ApiErrorBody>(error)) {
		return fallbackMessage;
	}

	const response = error.response;
	if (!response) {
		return "Le service est injoignable. Vérifiez votre connexion puis réessayez.";
	}
	const status = response.status;
	if (status >= 500) {
		return "Le service rencontre un problème technique. Réessayez plus tard.";
	}
	if (status === 401) {
		return "Votre session a expiré. Reconnectez-vous pour poursuivre.";
	}
	if (status === 403) {
		return "Vous n’êtes pas autorisé à effectuer cette action.";
	}
	if (status === 404) {
		return "La ressource demandée est introuvable ou indisponible.";
	}
	if (status === 409 && typeof response.data?.detail === "string") {
		return response.data.detail;
	}
	if (status === 400 || status === 422) {
		return "Les informations transmises ne sont pas valides. Vérifiez-les puis réessayez.";
	}
	if (status === 429) {
		return "Trop de tentatives. Patientez un instant puis réessayez.";
	}
	if (status >= 400) {
		return `La demande n’a pas abouti (HTTP ${status}). Vérifiez les informations puis réessayez.`;
	}

	return fallbackMessage;
}