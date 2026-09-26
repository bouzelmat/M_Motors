import { useMutation, useQueryClient } from "@tanstack/react-query";
import { DossiersClient, type DocumentType } from "../../../api/clients/DossiersClient";

export function useValidateDossier(dossierId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (comment?: string) => DossiersClient.validateDossier(dossierId, comment),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["admin", "dossiers", "pending"] });
			queryClient.invalidateQueries({ queryKey: ["admin", "dossiers", dossierId] });
		},
	});
}

export function useRejectDossier(dossierId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (reason: string) => DossiersClient.rejectDossier(dossierId, reason),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["admin", "dossiers", "pending"] });
			queryClient.invalidateQueries({ queryKey: ["admin", "dossiers", dossierId] });
		},
	});
}

export function useRequestDocuments(dossierId: string) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (documentTypes: DocumentType[]) => DossiersClient.requestDocuments(dossierId, documentTypes),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["admin", "dossiers", "pending"] });
			queryClient.invalidateQueries({ queryKey: ["admin", "dossiers", dossierId] });
		},
	});
}