import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Alert, Box, Button, Chip, CircularProgress, Container, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Paper, Stack, Typography } from "@mui/material";
import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";
import { useParams } from "react-router-dom";

import type { DossierStatus, DocumentStatus, DocumentType } from "../../../api/clients/DossiersClient";
import { useDossierStatus } from "../hooks/useDossierStatus";
import { useQuery } from "@tanstack/react-query";
import { DossiersClient } from "../../../api/clients/DossiersClient";
import { getApiErrorMessage } from "../../../api/apiErrorMessage";
import { DOCUMENT_TYPE_LABELS, DocumentUploader } from "../components/DocumentUploader";

const STATUS_LABELS: Record<DossierStatus, string> = {
	DRAFT: "En préparation",
	SUBMITTED: "En cours d’étude",
	VALIDATED: "Dossier validé",
	REJECTED: "Dossier refusé",
	EXPIRED: "Dossier expiré",
	CANCELLED: "Demande annulée",
	DOCUMENTS_PENDING: "Pièces complémentaires demandées",
};

const DOCUMENT_STATUS_LABELS: Record<DocumentStatus, string> = {
	PENDING: "En attente de téléversement",
	UPLOADED: "Reçue, en attente de vérification",
	REJECTED: "À remplacer",
	VALIDATED: "Pièce validée",
	PENDING_PURGE: "Suppression en cours",
	PURGED: "Supprimée",
};

const statusColor = (status: DossierStatus) => {
	if (status === "VALIDATED") return "success";
	if (status === "REJECTED" || status === "EXPIRED") return "error";
	if (status === "CANCELLED") return "default";
	if (status === "DOCUMENTS_PENDING") return "warning";
	return "primary";
};

export const AccountDossierPage = () => {
	const { dossierId } = useParams<{ dossierId: string }>();
	const queryClient = useQueryClient();
	const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
	const statusQuery = useDossierStatus(dossierId ?? null);
	const documentsQuery = useQuery({
		queryKey: ["dossiers", dossierId, "documents"],
		queryFn: () => DossiersClient.getDocuments(dossierId!),
		enabled: Boolean(dossierId),
		retry: 1,
	});
	const cancelMutation = useMutation({
		mutationFn: () => DossiersClient.cancelDossier(dossierId!),
		onSuccess: async () => {
			setCancelDialogOpen(false);
			await queryClient.invalidateQueries({ queryKey: ["dossiers"] });
		},
	});
	const resubmitMutation = useMutation({
		mutationFn: () => DossiersClient.submitDossier(dossierId!),
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: ["dossiers"] });
		},
	});

	if (statusQuery.isLoading) return <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}><CircularProgress aria-label="Chargement du statut" /></Box>;
	if (statusQuery.isError || !statusQuery.data) return <Container maxWidth="md" sx={{ py: 5 }}><Alert severity="error">{getApiErrorMessage(statusQuery.error, "Impossible de charger le statut de ce dossier.")}</Alert></Container>;

	const status = statusQuery.data.status;
	const color = statusColor(status);
	const requestedDocumentTypes = statusQuery.data.requested_document_types ?? [];
	const requestedDocumentsUploaded = requestedDocumentTypes.length > 0 && requestedDocumentTypes.every((type) =>
		documentsQuery.data?.some((document) => document.type === type && ["UPLOADED", "VALIDATED"].includes(document.status)),
	);

	return (
		<Container maxWidth="md" sx={{ py: { xs: 4, md: 7 } }}>
			<Typography variant="overline" color="primary.main" fontWeight={800}>ESPACE CLIENT</Typography>
			<Typography variant="h3" component="h1" fontWeight={800} sx={{ mb: 1 }}>Suivi de votre dossier</Typography>
			<Typography color="text.secondary" sx={{ mb: 4, overflowWrap: "anywhere" }}>Référence : {dossierId}</Typography>

			<Paper variant="outlined" sx={{ p: { xs: 2.5, md: 4 }, borderRadius: 1, mb: 3 }}>
				<Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" spacing={2} alignItems={{ sm: "center" }}>
					<Box>
						<Typography variant="h6" fontWeight={750} gutterBottom>État de la demande</Typography>
						<Typography color="text.secondary">Le statut est actualisé automatiquement pendant l’étude.</Typography>
					</Box>
					<Chip color={color} label={STATUS_LABELS[status]} />
				</Stack>
				{statusQuery.data.decision_comment && <Alert severity={status === "REJECTED" ? "error" : "info"} sx={{ mt: 3 }}>{statusQuery.data.decision_comment}</Alert>}
				<Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 2 }}>
					Dernière actualisation : {new Date(statusQuery.data.updated_at).toLocaleString("fr-FR")}
				</Typography>
			</Paper>

			{status === "DOCUMENTS_PENDING" ? (
				<Paper variant="outlined" sx={{ p: { xs: 2.5, md: 3 }, mb: 3, borderRadius: 1 }}>
					<Typography variant="h6" component="h2" fontWeight={750}>
						Pièces complémentaires demandées
					</Typography>
					{requestedDocumentTypes.length ? (
						<>
							<Typography color="text.secondary" sx={{ mt: 0.5, mb: 2 }}>
								Veuillez transmettre les documents suivants pour reprendre l’étude de votre dossier.
							</Typography>
							<Stack spacing={2}>
								{requestedDocumentTypes.map((documentType) => (
									<Box key={documentType}>
										<Typography variant="subtitle2" sx={{ mb: 1 }}>
											{DOCUMENT_TYPE_LABELS[documentType]}
										</Typography>
										<DocumentUploader
											dossierId={dossierId!}
											fixedDocumentType={documentType}
											onUploadComplete={() => { void documentsQuery.refetch(); }}
										/>
									</Box>
								))}
							</Stack>
						</>
					) : (
						<Typography color="text.secondary" sx={{ mt: 0.5 }}>
							L’étude attend des pièces complémentaires. Si leur liste ne s’affiche pas, actualisez la page ou contactez notre équipe.
						</Typography>
					)}
				</Paper>
			) : null}

			{status === "DOCUMENTS_PENDING" && requestedDocumentTypes.length > 0 && (
				<Stack spacing={2} sx={{ mb: 3 }}>
					{resubmitMutation.isError && <Alert severity="error">{getApiErrorMessage(resubmitMutation.error, "La transmission des pièces a échoué.")}</Alert>}
					<Button
						variant="contained"
						disabled={!requestedDocumentsUploaded || resubmitMutation.isPending}
						onClick={() => resubmitMutation.mutate()}
					>
						{resubmitMutation.isPending ? "Transmission…" : "Transmettre les pièces à l’étude"}
					</Button>
				</Stack>
			)}

			{status === "DRAFT" && (
				<Stack spacing={2} sx={{ mb: 3 }}>
					{cancelMutation.isError && <Alert severity="error">{getApiErrorMessage(cancelMutation.error, "L’annulation de votre demande a échoué.")}</Alert>}
					<Box>
						<Button
							variant="outlined"
							color="error"
							startIcon={<CancelOutlinedIcon />}
							onClick={() => setCancelDialogOpen(true)}
							disabled={cancelMutation.isPending}
						>
							Annuler ma demande
						</Button>
					</Box>
				</Stack>
			)}

			<Typography variant="h6" component="h2" fontWeight={750} sx={{ mb: 1.5 }}>Vos pièces</Typography>
			{documentsQuery.isLoading ? <CircularProgress size={24} aria-label="Chargement des pièces" /> : documentsQuery.isError ? (
				<Alert severity="warning">{getApiErrorMessage(documentsQuery.error, "Le statut est disponible, mais la liste des pièces n’a pas pu être chargée.")}</Alert>
			) : documentsQuery.data?.length ? (
				<Stack spacing={1}>
					{documentsQuery.data.map((document) => (
						<Paper key={document.id} variant="outlined" sx={{ p: 2, borderRadius: 1 }}>
							<Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2}>
								<Box sx={{ minWidth: 0 }}>
									<Typography fontWeight={650} sx={{ overflowWrap: "anywhere" }}>{document.original_filename}</Typography>
									<Typography variant="caption" color="text.secondary">{document.type}</Typography>
								</Box>
								<Chip size="small" label={DOCUMENT_STATUS_LABELS[document.status]} color={document.status === "VALIDATED" ? "success" : document.status === "REJECTED" ? "error" : "default"} />
							</Stack>
						</Paper>
					))}
				</Stack>
			) : <Alert severity="info">Aucune pièce n’est encore associée à ce dossier.</Alert>}

			<Dialog open={cancelDialogOpen} onClose={() => setCancelDialogOpen(false)}>
				<DialogTitle>Annuler cette demande ?</DialogTitle>
				<DialogContent>
					<DialogContentText>
						Cette action est définitive. Le véhicule sera de nouveau disponible et vous pourrez créer une nouvelle demande plus tard.
					</DialogContentText>
				</DialogContent>
				<DialogActions>
					<Button onClick={() => setCancelDialogOpen(false)} disabled={cancelMutation.isPending}>Garder ma demande</Button>
					<Button color="error" onClick={() => cancelMutation.mutate()} disabled={cancelMutation.isPending}>
						{cancelMutation.isPending ? "Annulation…" : "Confirmer l’annulation"}
					</Button>
				</DialogActions>
			</Dialog>
		</Container>
	);
};