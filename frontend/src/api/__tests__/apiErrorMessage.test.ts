import { describe, expect, it } from "vitest";

import { getApiErrorMessage } from "./apiErrorMessage";

const axiosError = (status?: number, detail?: unknown) => ({
	isAxiosError: true,
	response: status === undefined ? undefined : { status, data: { detail } },
});

describe("getApiErrorMessage", () => {
	it("returns the backend domain message for a conflict", () => {
		expect(getApiErrorMessage(axiosError(409, "Au moins un justificatif est requis."), "Erreur."))
			.toBe("Au moins un justificatif est requis.");
	});

	it("distinguishes client validation and server failures", () => {
		expect(getApiErrorMessage(axiosError(422), "Erreur.")).toContain("informations transmises");
		expect(getApiErrorMessage(axiosError(503), "Erreur.")).toContain("problème technique");
	});

	it("explains connection failures and preserves non-HTTP fallbacks", () => {
		expect(getApiErrorMessage(axiosError(), "Erreur.")).toContain("connexion");
		expect(getApiErrorMessage(new Error("unexpected"), "Erreur locale.")).toBe("Erreur locale.");
	});
});