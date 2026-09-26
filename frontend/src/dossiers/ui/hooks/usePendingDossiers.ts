import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import {
	DossiersClient,
	type PendingDossierItem,
} from "../../../api/clients/DossiersClient";

const STALE_TIME_MS = 30 * 1000;

export function usePendingDossiers(
	sortBy: string = "submitted_at",
): UseQueryResult<PendingDossierItem[], Error> {
	return useQuery({
		queryKey: ["admin", "dossiers", "pending", sortBy],
		queryFn: () => DossiersClient.getPendingDossiers(sortBy),
		staleTime: STALE_TIME_MS,
		retry: 1,
	});
}

