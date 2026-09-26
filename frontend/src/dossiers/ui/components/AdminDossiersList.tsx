import React from "react";
import { useNavigate } from "react-router-dom";
import {
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TableRow,
	Paper,
	Button,
	Chip,
} from "@mui/material";
import VisibilityIcon from "@mui/icons-material/Visibility";
import type { PendingDossierItem } from "../../../api/clients/DossiersClient";

interface AdminDossiersListProps {
	readonly items: readonly PendingDossierItem[];
}

export const AdminDossiersList: React.FC<AdminDossiersListProps> = ({
	items,
}) => {
	const navigate = useNavigate();

	const formatDate = (dateStr: string | null) => {
		if (!dateStr) return "-";
		return new Date(dateStr).toLocaleString("fr-FR", {
			dateStyle: "short",
			timeStyle: "short",
		});
	};

	return (
		<TableContainer component={Paper} variant="outlined">
			<Table sx={{ minWidth: 650 }} aria-label="Tableau des dossiers en attente">
				<TableHead>
					<TableRow>
						<TableCell>Email client</TableCell>
						<TableCell>Véhicule</TableCell>
						<TableCell>Statut</TableCell>
						<TableCell>Date de dépôt</TableCell>
						<TableCell>Date de création</TableCell>
						<TableCell align="right">Action</TableCell>
					</TableRow>
				</TableHead>
				<TableBody>
					{items.map((item) => (
						<TableRow key={item.id} hover>
							<TableCell>{item.client_email}</TableCell>
							<TableCell>{`${item.vehicle_brand} ${item.vehicle_model}`}</TableCell>
							<TableCell>
								<Chip label={item.status} color="warning" size="small" />
							</TableCell>
							<TableCell>{formatDate(item.submitted_at)}</TableCell>
							<TableCell>{formatDate(item.created_at)}</TableCell>
							<TableCell align="right">
								<Button
									variant="outlined"
									size="small"
									startIcon={<VisibilityIcon />}
									onClick={() => navigate(`/admin/dossiers/${item.id}`)}
								>
									Voir
								</Button>
							</TableCell>
						</TableRow>
					))}
				</TableBody>
			</Table>
		</TableContainer>
	);
};