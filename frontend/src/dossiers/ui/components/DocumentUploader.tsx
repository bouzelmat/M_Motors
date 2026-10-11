import React, { useState } from "react";
import { useDropzone } from "react-dropzone";
import axios from "axios";
import {
	Box,
	Button,
	Typography,
	LinearProgress,
	Alert,
	MenuItem,
	Select,
	FormControl,
	InputLabel,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import { getApiErrorMessage } from "../../../api/apiErrorMessage";
import { DossiersClient, type DocumentType } from "../../../api/clients/DossiersClient";

interface DocumentUploaderProps {
	dossierId: string;
	onUploadComplete: () => void;
	fixedDocumentType?: DocumentType;
}

const MAX_SIZE = 10 * 1024 * 1024; // 10 Mo
const ALLOWED_TYPES = {
	"application/pdf": [".pdf"],
	"image/jpeg": [".jpg", ".jpeg"],
	"image/png": [".png"],
};

export const DOCUMENT_TYPE_LABELS: Record<DocumentType, string> = {
	IDENTITY_CARD: "Pièce d'identité",
	PROOF_OF_ADDRESS: "Justificatif de domicile",
	PAYSLIP: "Fiche de paie",
	BANK_DETAILS: "Relevé d'identité bancaire",
	DRIVERS_LICENSE: "Permis de conduire",
	REGISTRATION_CERTIFICATE: "Certificat d'immatriculation",
	OTHER: "Autre document",
};

export const DocumentUploader: React.FC<DocumentUploaderProps> = ({
	dossierId,
	onUploadComplete,
	fixedDocumentType,
}) => {
	const [documentType, setDocumentType] = useState<DocumentType>(fixedDocumentType ?? "IDENTITY_CARD");
	const [uploading, setUploading] = useState(false);
	const [progress, setProgress] = useState(0);
	const [error, setError] = useState<string | null>(null);

	const onDrop = async (acceptedFiles: File[]) => {
		if (acceptedFiles.length === 0) return;
		const file = acceptedFiles[0];

		if (file.size > MAX_SIZE) {
			setError("Le fichier dépasse la limite autorisée de 10 Mo.");
			return;
		}

		setError(null);
		setUploading(true);
		setProgress(0);

		try {
			// Étape 1 : Demande de l'URL pré-signée
			const presignedData = await DossiersClient.requestPresignedUrl(
				dossierId,
				{
					document_type: documentType,
					filename: file.name,
					content_type: file.type,
					size: file.size,
				},
			);

			// Étape 2 : Upload direct binaire vers AWS S3
			await axios.put(presignedData.upload_url, file, {
				headers: {
					"Content-Type": file.type,
				},
				onUploadProgress: (progressEvent) => {
					if (progressEvent.total) {
						const percent = Math.round(
							(progressEvent.loaded * 100) / progressEvent.total,
						);
						setProgress(percent);
					}
				},
			});

			// Étape 3 : Confirmation au backend
			await DossiersClient.confirmUpload(dossierId, presignedData.document_id);

			setUploading(false);
			onUploadComplete();
		} catch (err: unknown) {
			setUploading(false);
			setError(getApiErrorMessage(err, "Une erreur est survenue lors du téléversement sur S3."));
		}
	};

	const { getRootProps, getInputProps, isDragActive } = useDropzone({
		onDrop,
		accept: ALLOWED_TYPES,
		maxFiles: 1,
		disabled: uploading,
	});

	return (
		<Box sx={{ p: 2, border: "1px dashed #ccc", borderRadius: 2 }}>
			{fixedDocumentType ? (
				<Typography variant="subtitle2" sx={{ mb: 2 }}>
					Type demandé : {DOCUMENT_TYPE_LABELS[fixedDocumentType]}
				</Typography>
			) : <FormControl fullWidth sx={{ mb: 2 }}>
				<InputLabel id="doc-type-label">Type de document</InputLabel>
				<Select
					labelId="doc-type-label"
					value={documentType}
					label="Type de document"
					onChange={(e) => setDocumentType(e.target.value as DocumentType)}
					disabled={uploading}
				>
					<MenuItem value="IDENTITY_CARD">Pièce d'identité</MenuItem>
					<MenuItem value="PAYSLIP">Fiche de paie</MenuItem>
					<MenuItem value="PROOF_OF_ADDRESS">Justificatif de domicile</MenuItem>
					<MenuItem value="BANK_DETAILS">Relevé d'identité bancaire</MenuItem>
					<MenuItem value="DRIVERS_LICENSE">Permis de conduire</MenuItem>
					<MenuItem value="REGISTRATION_CERTIFICATE">Certificat d'immatriculation</MenuItem>
					<MenuItem value="OTHER">Autre document</MenuItem>
				</Select>
			</FormControl>}

			<Box
				{...getRootProps()}
				sx={{
					p: 4,
					textAlign: "center",
					bgcolor: isDragActive ? "action.hover" : "background.paper",
					cursor: uploading ? "not-allowed" : "pointer",
				}}
			>
				<input {...getInputProps()} />
				<CloudUploadIcon sx={{ fontSize: 40, color: "primary.main", mb: 1 }} />
				<Typography variant="body1">
						Glissez-déposez votre pièce justificative ici, ou cliquez pour sélectionner
				</Typography>
				<Typography variant="caption" color="text.secondary">
					PDF, JPEG ou PNG (Max. 10 Mo)
				</Typography>
			</Box>

			{uploading && (
				<Box sx={{ mt: 2 }}>
					<LinearProgress variant="determinate" value={progress} />
					<Typography variant="caption" align="center" display="block" sx={{ mt: 0.5 }}>
						Téléversement S3... {progress}%
					</Typography>
				</Box>
			)}

			{error && (
				<Alert severity="error" sx={{ mt: 2 }}>
					{error}
				</Alert>
			)}
		</Box>
	);
};