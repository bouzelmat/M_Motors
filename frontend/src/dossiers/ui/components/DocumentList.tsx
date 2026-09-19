import React from "react";
import {
	List,
	ListItem,
	ListItemText,
	Chip,
	Typography,
	Paper,
	Box,
} from "@mui/material";
import InsertDriveFileIcon from "@mui/icons-material/InsertDriveFile";
import { DocumentListItem } from "../../../api/clients/DossiersClient";

interface DocumentListProps {
	documents: DocumentListItem[];
}

export const DocumentList: React.FC<DocumentListProps> = ({ documents }) => {
	if (documents.length === 0) {
		return (
			<Paper sx={{ p: 3, textAlign: "center" }}>
				<Typography color="text.secondary">Aucun document téléversé</Typography>
			</Paper>
		);
	}

	const getStatusColor = (status: string) => {
		switch (status) {
			case "UPLOADED":
				return "info";
			case "VALIDATED":
				return "success";
			case "REJECTED":
				return "error";
			default:
				return "warning";
		}
	};

	return (
		<Paper sx={{ mt: 2 }}>
			<List>
				{documents.map((doc) => (
					<ListItem key={doc.id} divider>
						<Box sx={{ mr: 2 }}>
							<InsertDriveFileIcon color="action" />
						</Box>
						<ListItemText
							primary={doc.original_filename}
							secondary={
								<>
									<Typography component="span" variant="body2" color="text.primary">
										{doc.type}
									</Typography>
									{doc.uploaded_at &&
										` — Téléversé le : ${new Date(doc.uploaded_at).toLocaleDateString()}`}
								</>
							}
						/>
						<Chip
							label={doc.status}
							color={getStatusColor(doc.status)}
							size="small"
						/>
					</ListItem>
				))}
			</List>
		</Paper>
	);
};