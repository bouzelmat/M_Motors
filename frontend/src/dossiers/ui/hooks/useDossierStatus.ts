import { useQuery, type UseQueryResult } from "@tanstack/react-query";

import {
	DossiersClient,
	type DossierStatus,
	type DossierStatusResponse,
} from "../../infrastructure/DossiersClient";

const FINAL_STATUSES: readonly DossierStatus[] = [
	"VALIDATED",
	"REJECTED",
	"EXPIRED",
	"CANCELLED",
];

/**
 * Récupère le statut d'un dossier et le rafraîchit automatiquement tant que le dossier est en cours.
 */
export function useDossierStatus(
	dossierId: string | null,
): UseQueryResult<DossierStatusResponse, Error> {
	return useQuery({
		queryKey: ["dossiers", dossierId, "status"],
		queryFn: () => {
			if (!dossierId) {
				throw new Error("Un dossierId est requis pour consulter son statut.");
			}

			return DossiersClient.getDossierStatus(dossierId);
		},
		enabled: Boolean(dossierId),
		staleTime: 30 * 1000,
		refetchInterval: (query) => {
			const status = query.state.data?.status;
			return status && !FINAL_STATUSES.includes(status) ? 30_000 : false;
		},
		retry: 1,
	});
}