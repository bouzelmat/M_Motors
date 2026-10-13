import { useQuery, type UseQueryResult } from "@tanstack/react-query";

import {
	DossiersClient,
	type DossierStatus,
	type DossierListItem,
} from "../../infrastructure/DossiersClient";

const STALE_TIME_MS = 60 * 1000;
const FINAL_STATUSES: readonly DossierStatus[] = [
	"VALIDATED",
	"REJECTED",
	"EXPIRED",
	"CANCELLED",
];

/**
 * Récupère la liste des dossiers de l'utilisateur connecté.
 */
export function useDossiers(): UseQueryResult<DossierListItem[], Error> {
	return useQuery({
		queryKey: ["dossiers", "me"],
		queryFn: () => DossiersClient.getMyDossiers(),
		staleTime: STALE_TIME_MS,
		refetchInterval: (query) =>
			query.state.data?.some((dossier) => !FINAL_STATUSES.includes(dossier.status))
				? 30_000
				: false,
		retry: 1,
	});
}