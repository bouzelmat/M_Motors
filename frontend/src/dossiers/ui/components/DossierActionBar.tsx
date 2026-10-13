import React, { useState } from "react";
import { Box, Button, Stack, Alert } from "@mui/material";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CancelIcon from "@mui/icons-material/Cancel";
import AttachFileIcon from "@mui/icons-material/AttachFile";
import { getApiErrorMessage } from "../../../shared/infrastructure/http/apiErrorMessage";
import type { DocumentType, DossierStatus } from "../../infrastructure/DossiersClient";
import {
	useValidateDossier,
	useRejectDossier,
	useRequestDocuments,
} from "../hooks/useDossierMutations";
import { DossierActionDialog } from "./DossierActionDialog";

interface DossierActionBarProps {
	dossierId: string;
	status: DossierStatus;
}

export const DossierActionBar: React.FC<DossierActionBarProps> = ({ dossierId, status }) => {
	const [activeAction, setActiveAction] = useState<"validate" | "reject" | "request" | null>(null);
	const [actionError, setActionError] = useState<string | null>(null);

	const validateMutation = useValidateDossier(dossierId);
	const rejectMutation = useRejectDossier(dossierId);
	const requestMutation = useRequestDocuments(dossierId);

	const canDecide = status === "SUBMITTED";
	const canRequestDocuments = canDecide || status === "DOCUMENTS_PENDING";

	if (!canRequestDocuments) {
		return null; // Aucune action possible pour VALIDATED, REJECTED, EXPIRED, DRAFT
	}

	const handleClose = () => {
		setActiveAction(null);
		setActionError(null);
	};

	const handleSubmit = async (data: { comment?: string; reason?: string; documentTypes?: DocumentType[] }) => {
		setActionError(null);
		try {
			if (activeAction === "validate") {
				await validateMutation.mutateAsync(data.comment);
			} else if (activeAction === "reject") {
				await rejectMutation.mutateAsync(data.reason!);
			} else if (activeAction === "request" && data.documentTypes) {
				await requestMutation.mutateAsync(data.documentTypes);
			}
			handleClose(); // Ferme la modale en cas de succès (la mutation a déjà invalidé les queries)
		} catch (err: unknown) {
			setActionError(getApiErrorMessage(err, "Une erreur est survenue lors de l’action."));
		}
	};

	const isSubmitting = validateMutation.isPending || rejectMutation.isPending || requestMutation.isPending;

	return (
		<>
			<Box sx={{ mt: 4, mb: 2 }}>
				<Stack direction="row" spacing={2}>
					{canDecide && <Button
						variant="contained"
						color="success"
						startIcon={<CheckCircleIcon />}
						onClick={() => setActiveAction("validate")}
						disabled={isSubmitting}
					>
						Valider le dossier
					</Button>}
					{canDecide && <Button
						variant="contained"
						color="error"
						startIcon={<CancelIcon />}
						onClick={() => setActiveAction("reject")}
						disabled={isSubmitting}
					
					>
						Rejeter le dossier
					</Button>}
					<Button
						variant="outlined"
						color="primary"
						startIcon={<AttachFileIcon />}
						onClick={() => setActiveAction("request")}
						disabled={isSubmitting}
					>
						Demander des documents
					</Button>
				</Stack>
			</Box>

			{activeAction && (
				<DossierActionDialog
					open={!!activeAction}
					onClose={handleClose}
					actionType={activeAction}
					onSubmit={handleSubmit}
					isSubmitting={isSubmitting}
					error={actionError}
				/>
			)}
		</>
	);
};