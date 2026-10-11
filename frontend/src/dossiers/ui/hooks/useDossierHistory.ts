import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import {
	DossiersClient,
	type PendingDossierItem,
} from "../../../api/clients/DossiersClient";

export function useDossierHistory(): UseQueryResult<PendingDossierItem[], Error> {
	return useQuery({
		queryKey: ["admin", "dossiers", "history"],
		queryFn: () => DossiersClient.getDossierHistory(),
		staleTime: 30_000,
		retry: 1,
	});
}
