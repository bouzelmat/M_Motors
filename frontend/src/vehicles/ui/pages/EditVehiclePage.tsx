import { useMemo, useState, type ChangeEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
	Alert,
	Box,
	Button,
	Chip,
	CircularProgress,
	Container,
	Dialog,
	DialogActions,
	DialogContent,
	DialogContentText,
	DialogTitle,
	IconButton,
	Paper,
	Stack,
	Tooltip,
	Typography,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutline";
import StarIcon from "@mui/icons-material/Star";
import StarOutlineIcon from "@mui/icons-material/StarOutline";
import { useNavigate, useParams } from "react-router-dom";

import { getApiErrorMessage } from "../../../api/apiErrorMessage";
import { vehiclesClient } from "../../infrastructure/VehiclesClient";
import type { CreateVehicleRequestDTO } from "../../infrastructure/vehicle.types";
import { VehicleAddForm } from "../components/VehicleAddForm";

export function EditVehiclePage() {
	const { vehicleId } = useParams<{ vehicleId: string }>();
	const navigate = useNavigate();
	const queryClient = useQueryClient();
	const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
	const [fileError, setFileError] = useState<string | null>(null);
	const [photoToDelete, setPhotoToDelete] = useState<string | null>(null);
	const vehicleQuery = useQuery({
		queryKey: ["vehicles", "admin", vehicleId],
		queryFn: () => vehiclesClient.getAdminVehicle(vehicleId!),
		enabled: Boolean(vehicleId),
	});
	const servicesQuery = useQuery({
		queryKey: ["vehicle-service-catalog"],
		queryFn: () => vehiclesClient.getServiceCatalog(),
	});
	const photosQuery = useQuery({
		queryKey: ["vehicles", "admin", vehicleId, "photos"],
		queryFn: () => vehiclesClient.getVehiclePhotos(vehicleId!),
		enabled: Boolean(vehicleId),
	});
	const updateMutation = useMutation({
		mutationFn: (payload: CreateVehicleRequestDTO) => vehiclesClient.updateVehicle(vehicleId!, payload),
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: ["vehicles"] });
			navigate("/admin/vehicles");
		},
	});
	const uploadPhotosMutation = useMutation({
		mutationFn: async (files: File[]) => {
			for (const file of files) {
				await vehiclesClient.uploadVehiclePhoto(vehicleId!, file);
			}
		},
		onSuccess: () => setSelectedFiles([]),
		onSettled: async () => {
			await queryClient.invalidateQueries({ queryKey: ["vehicles", "admin", vehicleId, "photos"] });
			await queryClient.invalidateQueries({ queryKey: ["vehicles"] });
		},
	});
	const primaryPhotoMutation = useMutation({
		mutationFn: (photoId: string) => vehiclesClient.setPrimaryVehiclePhoto(vehicleId!, photoId),
		onSettled: async () => {
			await queryClient.invalidateQueries({ queryKey: ["vehicles", "admin", vehicleId, "photos"] });
			await queryClient.invalidateQueries({ queryKey: ["vehicles"] });
		},
	});
	const deletePhotoMutation = useMutation({
		mutationFn: (photoId: string) => vehiclesClient.deleteVehiclePhoto(vehicleId!, photoId),
		onSuccess: () => setPhotoToDelete(null),
		onSettled: async () => {
			await queryClient.invalidateQueries({ queryKey: ["vehicles", "admin", vehicleId, "photos"] });
			await queryClient.invalidateQueries({ queryKey: ["vehicles"] });
		},
	});
	const initialValues = useMemo<CreateVehicleRequestDTO | undefined>(() => {
		const vehicle = vehicleQuery.data;
		if (!vehicle) return undefined;
		return {
			brand: vehicle.brand,
			model: vehicle.model,
			year: vehicle.year,
			mileage: vehicle.mileage,
			energy_type: vehicle.energy_type,
			catalog_type: vehicle.catalog_type,
			price: vehicle.price === null ? null : Number(vehicle.price),
			monthly_rent: vehicle.monthly_rent === null ? null : Number(vehicle.monthly_rent),
			description: vehicle.description,
			services: vehicle.services.map(({ id, included }) => ({ service_id: id, included })),
		};
	}, [vehicleQuery.data]);

	const handleFilesSelected = (event: ChangeEvent<HTMLInputElement>) => {
		const files = Array.from(event.target.files ?? []);
		event.target.value = "";
		setFileError(null);
		const invalidFile = files.find((file) =>
			!["image/jpeg", "image/png", "image/webp"].includes(file.type)
			|| file.size <= 0
			|| file.size > 10 * 1024 * 1024,
		);
		if (invalidFile) {
			setSelectedFiles([]);
			setFileError(`${invalidFile.name} doit être une image JPEG, PNG ou WebP de 10 Mo maximum.`);
			return;
		}
		setSelectedFiles(files);
	};

	if (vehicleQuery.isLoading || servicesQuery.isLoading) {
		return <Box sx={{ display: "flex", justifyContent: "center", py: 10 }}><CircularProgress aria-label="Chargement du véhicule" /></Box>;
	}
	if (vehicleQuery.isError || !initialValues) {
		return <Container maxWidth="md" sx={{ py: 5 }}><Alert severity="error">{getApiErrorMessage(vehicleQuery.error, "Le véhicule demandé est introuvable.")}</Alert></Container>;
	}
	if (servicesQuery.isError) {
		return <Container maxWidth="md" sx={{ py: 5 }}><Alert severity="error">{getApiErrorMessage(servicesQuery.error, "Le catalogue de services n’a pas pu être chargé. L’édition est suspendue pour préserver les services du véhicule.")}</Alert></Container>;
	}

	return (
		<Container maxWidth="md" sx={{ py: 5 }}>
			<Paper variant="outlined" sx={{ p: { xs: 2.5, md: 4 } }}>
				<Typography variant="h4" component="h1" fontWeight={800} gutterBottom>Modifier le véhicule</Typography>
				<Stack spacing={2} sx={{ mb: 4 }}>
					<Box>
						<Typography variant="h6" component="h2" fontWeight={750}>Photos du véhicule</Typography>
						<Typography variant="body2" color="text.secondary">Ajoutez plusieurs images, choisissez la couverture et supprimez les photos obsolètes.</Typography>
					</Box>
					{photosQuery.isError && <Alert severity="error">{getApiErrorMessage(photosQuery.error, "La galerie n’a pas pu être chargée.")}</Alert>}
					{fileError && <Alert severity="error">{fileError}</Alert>}
					{uploadPhotosMutation.isError && <Alert severity="error">{getApiErrorMessage(uploadPhotosMutation.error, "Les images n’ont pas toutes pu être téléversées.")}</Alert>}
					{primaryPhotoMutation.isError && <Alert severity="error">{getApiErrorMessage(primaryPhotoMutation.error, "La photo principale n’a pas pu être modifiée.")}</Alert>}
					{deletePhotoMutation.isError && <Alert severity="error">{getApiErrorMessage(deletePhotoMutation.error, "La suppression de la photo a échoué.")}</Alert>}
					<Stack direction={{ xs: "column", sm: "row" }} alignItems={{ sm: "center" }} spacing={1.5}>
						<Button component="label" variant="outlined" startIcon={<CloudUploadIcon />} disabled={uploadPhotosMutation.isPending}>
							Choisir des images
							<input hidden type="file" accept="image/jpeg,image/png,image/webp" multiple onChange={handleFilesSelected} />
						</Button>
						<Typography variant="body2" color="text.secondary">
							{selectedFiles.length ? `${selectedFiles.length} image${selectedFiles.length > 1 ? "s" : ""} sélectionnée${selectedFiles.length > 1 ? "s" : ""}` : "JPEG, PNG ou WebP · 10 Mo maximum par image"}
						</Typography>
						<Button
							variant="contained"
							startIcon={uploadPhotosMutation.isPending ? <CircularProgress size={18} color="inherit" /> : <CloudUploadIcon />}
							disabled={!selectedFiles.length || uploadPhotosMutation.isPending}
							onClick={() => uploadPhotosMutation.mutate(selectedFiles)}
						>
							{uploadPhotosMutation.isPending ? "Téléversement…" : "Ajouter les images"}
						</Button>
					</Stack>
					{photosQuery.isLoading ? (
						<CircularProgress size={24} aria-label="Chargement des photos" />
					) : photosQuery.data?.length ? (
						<Box sx={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(min(100%, 220px), 1fr))", gap: 2 }}>
							{photosQuery.data.map((photo) => (
								<Paper key={photo.id} variant="outlined" sx={{ overflow: "hidden", minWidth: 0 }}>
									<Box component="img" src={photo.photo_url} alt={`${vehicleQuery.data?.brand} ${vehicleQuery.data?.model}`} sx={{ display: "block", width: "100%", aspectRatio: "16 / 10", objectFit: "cover", bgcolor: "action.hover" }} />
									<Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ p: 1 }}>
										{photo.is_primary ? <Chip icon={<StarIcon />} label="Principale" size="small" color="primary" /> : <Tooltip title="Définir comme image principale"><IconButton aria-label="Définir comme image principale" size="small" onClick={() => primaryPhotoMutation.mutate(photo.id)} disabled={primaryPhotoMutation.isPending}><StarOutlineIcon /></IconButton></Tooltip>}
										<Tooltip title="Supprimer cette image"><IconButton aria-label="Supprimer cette image" size="small" color="error" onClick={() => setPhotoToDelete(photo.id)}><DeleteOutlineIcon /></IconButton></Tooltip>
									</Stack>
								</Paper>
							))}
						</Box>
					) : !photosQuery.isError ? <Alert severity="info">Aucune photo n’est associée à ce véhicule.</Alert> : null}
				</Stack>

				<Typography variant="h6" component="h2" fontWeight={750} sx={{ mb: 2 }}>Caractéristiques</Typography>
				<VehicleAddForm
					initialValues={initialValues}
					submitLabel="Enregistrer les modifications"
					onSubmit={(payload) => updateMutation.mutateAsync(payload).then(() => undefined)}
					isSubmitting={updateMutation.isPending}
					apiError={updateMutation.error ? getApiErrorMessage(updateMutation.error, "La modification a échoué.") : null}
					services={servicesQuery.data ?? []}
					isLoadingServices={servicesQuery.isLoading}
					servicesError={null}
				/>
			</Paper>
			<Dialog open={Boolean(photoToDelete)} onClose={() => setPhotoToDelete(null)}>
				<DialogTitle>Supprimer cette image ?</DialogTitle>
				<DialogContent><DialogContentText>Cette image sera supprimée définitivement du véhicule.</DialogContentText></DialogContent>
				<DialogActions>
					<Button onClick={() => setPhotoToDelete(null)} disabled={deletePhotoMutation.isPending}>Annuler</Button>
					<Button color="error" onClick={() => photoToDelete && deletePhotoMutation.mutate(photoToDelete)} disabled={deletePhotoMutation.isPending}>{deletePhotoMutation.isPending ? "Suppression…" : "Supprimer"}</Button>
				</DialogActions>
			</Dialog>
		</Container>
	);
}