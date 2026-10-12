import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
	DossiersClient,
	type CreateDossierRequest,
	type DocumentType,
} from "../../infrastructure/DossiersClient";

export function useCreateDossier() {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (data: CreateDossierRequest) => DossiersClient.createDossier(data),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["dossiers", "me"] });
		},
	});
}

export function useSubmitDossier(dossierId: string | undefined) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: () => {
			if (!dossierId) throw new Error("Identifiant de dossier manquant.");
			return DossiersClient.submitDossier(dossierId);
		},
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["dossiers", "me"] });
			queryClient.invalidateQueries({ queryKey: ["dossiers", dossierId] });
			queryClient.invalidateQueries({ queryKey: ["dossiers", dossierId, "status"] });
		},
	});
}

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