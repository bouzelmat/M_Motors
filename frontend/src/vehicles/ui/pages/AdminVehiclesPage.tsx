import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
	Alert,
	Box,
	Button,
	CircularProgress,
	Container,
	Dialog,
	DialogActions,
	DialogContent,
	DialogContentText,
	DialogTitle,
	IconButton,
	Paper,
	Tooltip,
	Typography,
} from "@mui/material";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import AddIcon from "@mui/icons-material/Add";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import { useNavigate } from "react-router-dom";

import { getApiErrorMessage } from "../../../api/apiErrorMessage";
import { vehiclesClient } from "../../infrastructure/VehiclesClient";
import type { VehicleResponseDTO } from "../../infrastructure/vehicle.types";

const STATUS_LABELS: Record<VehicleResponseDTO["status"], string> = {
	AVAILABLE: "Disponible",
	RENTED: "Loué",
	SOLD: "Vendu",
	MAINTENANCE: "En maintenance",
};

const CATALOG_LABELS: Record<VehicleResponseDTO["catalog_type"], string> = {
	SALE: "Vente",
	RENTAL: "Location",
	BOTH: "Vente et location",
};

export function AdminVehiclesPage() {
	const navigate = useNavigate();
	const queryClient = useQueryClient();
	const [vehicleToDelete, setVehicleToDelete] = useState<VehicleResponseDTO | null>(null);
	const vehiclesQuery = useQuery({
		queryKey: ["vehicles", "admin"],
		queryFn: () => vehiclesClient.getAdminVehicles(),
	});
	const deleteMutation = useMutation({
		mutationFn: (vehicleId: string) => vehiclesClient.deleteVehicle(vehicleId),
		onSuccess: async () => {
			setVehicleToDelete(null);
			await queryClient.invalidateQueries({ queryKey: ["vehicles"] });
		},
	});

	const columns: GridColDef<VehicleResponseDTO>[] = [
		{ field: "brand", headerName: "Marque", minWidth: 130, flex: 1 },
		{ field: "model", headerName: "Modèle", minWidth: 150, flex: 1 },
		{ field: "year", headerName: "Année", width: 90 },
		{
			field: "catalog_type",
			headerName: "Catalogue",
			width: 150,
			valueGetter: (_value, row) => CATALOG_LABELS[row.catalog_type],
		},
		{
			field: "status",
			headerName: "Statut",
			width: 150,
			valueGetter: (_value, row) => STATUS_LABELS[row.status],
		},
		{
			field: "price",
			headerName: "Prix / mois",
			width: 130,
			renderCell: ({ row }) => row.catalog_type === "RENTAL"
				? `${row.monthly_rent ?? "-"} €/mois`
				: row.catalog_type === "BOTH"
					? `${row.price ?? "-"} € · ${row.monthly_rent ?? "-"} €/mois`
					: `${row.price ?? "-"} €`,
		},
		{
			field: "actions",
			headerName: "Actions",
			width: 110,
			sortable: false,
			filterable: false,
			renderCell: ({ row }) => (
				<Box sx={{ display: "flex" }}>
					<Tooltip title="Modifier le véhicule">
						<IconButton aria-label={`Modifier ${row.brand} ${row.model}`} onClick={() => navigate(`/admin/vehicles/${row.id}/edit`)}>
							<EditOutlinedIcon />
						</IconButton>
					</Tooltip>
					<Tooltip title="Supprimer le véhicule">
						<IconButton aria-label={`Supprimer ${row.brand} ${row.model}`} color="error" onClick={() => setVehicleToDelete(row)}>
							<DeleteOutlineIcon />
						</IconButton>
					</Tooltip>
				</Box>
			),
		},
	];

	return (
		<Container maxWidth="xl" sx={{ py: 3, minWidth: 0 }}>
			<Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 2, mb: 3, flexWrap: "wrap" }}>
				<Box>
					<Typography variant="h4" component="h1" fontWeight={800}>Gestion des véhicules</Typography>
					<Typography color="text.secondary">Consultez et gérez l’ensemble du parc.</Typography>
				</Box>
				<Button variant="contained" startIcon={<AddIcon />} onClick={() => navigate("/admin/vehicles/new")}>
					Ajouter un véhicule
				</Button>
			</Box>

			{vehiclesQuery.isError && <Alert severity="error" sx={{ mb: 2 }}>{getApiErrorMessage(vehiclesQuery.error, "Impossible de charger les véhicules.")}</Alert>}
			{deleteMutation.isError && <Alert severity="error" sx={{ mb: 2 }}>{getApiErrorMessage(deleteMutation.error, "La suppression du véhicule a échoué.")}</Alert>}
			{vehiclesQuery.isLoading ? (
				<Box sx={{ display: "flex", justifyContent: "center", py: 8 }}><CircularProgress aria-label="Chargement des véhicules" /></Box>
			) : vehiclesQuery.data?.length ? (
				<Paper variant="outlined" sx={{ height: 620, width: "100%", minWidth: 0, overflow: "hidden" }}>
					<DataGrid
						rows={vehiclesQuery.data}
						columns={columns}
						pageSizeOptions={[10, 25, 50]}
						initialState={{ pagination: { paginationModel: { pageSize: 10, page: 0 } } }}
						disableRowSelectionOnClick
					/>
				</Paper>
			) : !vehiclesQuery.isError ? (
				<Paper variant="outlined" sx={{ p: 5, textAlign: "center" }}>
					<Typography>Aucun véhicule enregistré.</Typography>
				</Paper>
			) : null}

			<Dialog open={Boolean(vehicleToDelete)} onClose={() => setVehicleToDelete(null)}>
				<DialogTitle>Supprimer ce véhicule ?</DialogTitle>
				<DialogContent>
					<DialogContentText>
						La suppression de {vehicleToDelete?.brand} {vehicleToDelete?.model} est définitive.
					</DialogContentText>
				</DialogContent>
				<DialogActions>
					<Button onClick={() => setVehicleToDelete(null)} disabled={deleteMutation.isPending}>Annuler</Button>
					<Button color="error" onClick={() => vehicleToDelete && deleteMutation.mutate(vehicleToDelete.id)} disabled={deleteMutation.isPending}>
						{deleteMutation.isPending ? "Suppression…" : "Supprimer"}
					</Button>
				</DialogActions>
			</Dialog>
		</Container>
	);
}