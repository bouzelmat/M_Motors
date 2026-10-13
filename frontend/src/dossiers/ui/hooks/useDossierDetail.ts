import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import {
	DossiersClient,
	type AdminDossierDetailResponse,
} from "../../infrastructure/DossiersClient";

const STALE_TIME_MS = 60 * 1000;

export function useDossierDetail(
	dossierId: string | undefined,
): UseQueryResult<AdminDossierDetailResponse, Error> {
	return useQuery({
		queryKey: ["admin", "dossiers", dossierId],
		queryFn: () => {
			if (!dossierId) throw new Error("Identifiant de dossier manquant.");
			return DossiersClient.getDossierDetail(dossierId);
		},
		enabled: Boolean(dossierId),
		staleTime: STALE_TIME_MS,
		retry: 1,
	});
}