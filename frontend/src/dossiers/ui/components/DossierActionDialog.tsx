import React, { useState } from "react";
import {
	Dialog,
	DialogTitle,
	DialogContent,
	DialogActions,
	Button,
	TextField,
	FormControl,
	FormLabel,
	FormGroup,
	FormControlLabel,
	Checkbox,
	FormHelperText,
	Alert,
} from "@mui/material";
import { DocumentType } from "../../../api/clients/DossiersClient";

const DOCUMENT_TYPE_LABELS: Record<DocumentType, string> = {
	IDENTITY_CARD: "Pièce d'identité",
	PROOF_OF_ADDRESS: "Justificatif de domicile",
	PAYSLIP: "Bulletins de salaire",
	BANK_DETAILS: "Relevé d'identité bancaire (RIB)",
	DRIVERS_LICENSE: "Permis de conduire",
	REGISTRATION_CERTIFICATE: "Carte grise",
	OTHER: "Autre document",
};

type ActionType = "validate" | "reject" | "request";

interface DossierActionDialogProps {
	open: boolean;
	onClose: () => void;
	actionType: ActionType;
	onSubmit: (data: { comment?: string; reason?: string; documentTypes?: DocumentType[] }) => Promise<void>;
	isSubmitting: boolean;
	error?: string | null;
}

export const DossierActionDialog: React.FC<DossierActionDialogProps> = ({
	open,
	onClose,
	actionType,
	onSubmit,
	isSubmitting,
	error,
}) => {
	const [comment, setComment] = useState("");
	const [reason, setReason] = useState("");
	const [selectedDocs, setSelectedDocs] = useState<DocumentType[]>([]);
	const [formError, setFormError] = useState<string | null>(null);

	// Réinitialiser le formulaire à l'ouverture
	React.useEffect(() => {
		if (open) {
			setComment("");
			setReason("");
			setSelectedDocs([]);
			setFormError(null);
		}
	}, [open]);

	const handleSubmit = async () => {
		setFormError(null);

		if (actionType === "reject" && reason.trim().length < 10) {
			// CORRECTION ICI : message exact sans faute de frappe
			setFormError("Le motif de rejet doit contenir au moins 10 caractères.");
			return;
		}

		if (actionType === "request" && selectedDocs.length === 0) {
			setFormError("Vous devez sélectionner au moins un document.");
			return;
		}

		await onSubmit({
			comment: actionType === "validate" ? comment : undefined,
			reason: actionType === "reject" ? reason : undefined,
			documentTypes: actionType === "request" ? selectedDocs : undefined,
		});

		if (!formError && !error) {
			onClose();
		}
	};

	const getTitle = () => {
		switch (actionType) {
			case "validate": return "Valider le dossier";
			case "reject": return "Rejeter le dossier";
			case "request": return "Demander des documents complémentaires";
		}
	};

	const getSubmitLabel = () => {
		switch (actionType) {
			case "validate": return "Valider";
			case "reject": return "Rejeter";
			case "request": return "Envoyer la demande";
		}
	};

	return (
		<Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
			<DialogTitle>{getTitle()}</DialogTitle>
			<DialogContent dividers>
				{(error || formError) && (
					<Alert severity="error" sx={{ mb: 2 }}>
						{error || formError}
					</Alert>
				)}

				{actionType === "validate" && (
					<TextField
						fullWidth
						label="Commentaire (facultatif)"
						multiline
						rows={3}
						value={comment}
						onChange={(e) => setComment(e.target.value)}
						inputProps={{ maxLength: 1000 }}
						helperText={`${comment.length}/1000 caractères`}
					/>
				)}

				{actionType === "reject" && (
					<TextField
						fullWidth
						label="Motif du rejet *"
						multiline
						rows={3}
						value={reason}
						onChange={(e) => setReason(e.target.value)}
						inputProps={{ minLength: 10, maxLength: 1000 }}
						helperText="Minimum 10 caractères requis."
						required
					/>
				)}

				{actionType === "request" && (
					<FormControl component="fieldset" error={!!formError} fullWidth>
						<FormLabel component="legend">Documents à demander *</FormLabel>
						<FormGroup>
							{(Object.keys(DOCUMENT_TYPE_LABELS) as DocumentType[]).map((type) => (
								<FormControlLabel
									key={type}
									control={
										<Checkbox
											checked={selectedDocs.includes(type)}
											onChange={(e) => {
												if (e.target.checked) {
													setSelectedDocs([...selectedDocs, type]);
												} else {
													setSelectedDocs(selectedDocs.filter((d) => d !== type));
												}
											}}
										/>
									}
									label={DOCUMENT_TYPE_LABELS[type]}
								/>
							))}
						</FormGroup>
						<FormHelperText>{formError || "Sélectionnez au moins un document."}</FormHelperText>
					</FormControl>
				)}
			</DialogContent>
			<DialogActions>
				<Button onClick={onClose} disabled={isSubmitting}>
					Annuler
				</Button>
				<Button
					variant="contained"
					color={actionType === "reject" ? "error" : "primary"}
					onClick={handleSubmit}
					disabled={isSubmitting}
				>
					{isSubmitting ? "Traitement..." : getSubmitLabel()}
				</Button>
			</DialogActions>
		</Dialog>
	);
};