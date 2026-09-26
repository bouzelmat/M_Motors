import React, { useState } from "react";
import {
	Container,
	Typography,
	Box,
	CircularProgress,
	Alert,
	FormControl,
	InputLabel,
	Select,
	MenuItem,
	SelectChangeEvent,
	Paper,
} from "@mui/material";
import { usePendingDossiers } from "../hooks/usePendingDossiers";
import { AdminDossiersList } from "../components/AdminDossiersList";

export const AdminDossiersPage: React.FC = () => {
	const [sortBy, setSortBy] = useState<string>("submitted_at");
	const { data: dossiers, isLoading, isError, error } = usePendingDossiers(sortBy);

	const handleSortChange = (event: SelectChangeEvent) => {
		setSortBy(event.target.value);
	};

	return (
		<Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
			<Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3 }}>
				<Box>
					<Typography variant="h4" component="h1" gutterBottom>
						Dossiers en attente de traitement
					</Typography>
					<Typography variant="body2" color="text.secondary">
						{dossiers ? `${dossiers.length} dossier(s) à traiter` : "Chargement..."}
					</Typography>
				</Box>

				<FormControl size="small" sx={{ minWidth: 200 }}>
					<InputLabel id="sort-by-label">Trier par</InputLabel>
					<Select
						labelId="sort-by-label"
						value={sortBy}
						label="Trier par"
						onChange={handleSortChange}
					>
						<MenuItem value="submitted_at">Date de dépôt</MenuItem>
						<MenuItem value="created_at">Date de création</MenuItem>
					</Select>
				</FormControl>
			</Box>

			{isLoading && (
				<Box sx={{ display: "flex", justifyContent: "center", my: 6 }}>
					<CircularProgress />
				</Box>
			)}

			{isError && (
				<Alert severity="error" sx={{ mb: 3 }}>
					{error?.message || "Une erreur est survenue lors du chargement des dossiers."}
				</Alert>
			)}

			{!isLoading && !isError && dossiers && dossiers.length === 0 && (
				<Paper sx={{ p: 4, textAlign: "center" }} variant="outlined">
					<Typography variant="h6" color="text.secondary">
						Aucun dossier en attente pour le moment.
					</Typography>
				</Paper>
			)}

			{!isLoading && !isError && dossiers && dossiers.length > 0 && (
				<AdminDossiersList items={dossiers} />
			)}
		</Container>
	);
};