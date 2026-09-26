import { useQuery, type UseQueryResult } from "@tanstack/react-query";

import {
	DossiersClient,
	type DossierListItem,
} from "../../../api/clients/DossiersClient";

const STALE_TIME_MS = 60 * 1000;

/**
 * Récupère la liste des dossiers de l'utilisateur connecté.
 */
export function useDossiers(): UseQueryResult<DossierListItem[], Error> {
	return useQuery({
		queryKey: ["dossiers", "me"],
		queryFn: () => DossiersClient.getMyDossiers(),
		staleTime: STALE_TIME_MS,
		retry: 1,
	});
}