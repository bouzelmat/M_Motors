import { useState, type ChangeEvent } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Stack,
  Typography,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";

import { useAuthStore } from "../../../auth/ui/hooks/useAuth";
import { getApiErrorMessage } from "../../../shared/infrastructure/http/apiErrorMessage";
import { vehiclesClient } from "../../infrastructure/VehiclesClient";

const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024;

export function VehiclePhotoUploadPage() {
  const { vehicleId } = useParams<{ vehicleId: string }>();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuthStore();
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isAuthenticated || user?.role !== "ADMIN") {
    return (
      <Container maxWidth="sm" sx={{ py: 6 }}>
        <Alert severity="error">Accès réservé aux administrateurs.</Alert>
      </Container>
    );
  }

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0] ?? null;
    setError(null);
    setPhotoUrl(null);

    if (selectedFile && selectedFile.size > MAX_FILE_SIZE_BYTES) {
      setFile(null);
      setError("La photo ne doit pas dépasser 10 Mo.");
      return;
    }

    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!vehicleId || !file) {
      setError("Sélectionnez une photo avant de continuer.");
      return;
    }

    setError(null);
    setIsUploading(true);
    try {
      const result = await vehiclesClient.uploadVehiclePhoto(vehicleId, file);
      setPhotoUrl(result.photo_url);
      setFile(null);
    } catch (uploadError: unknown) {
      setError(getApiErrorMessage(uploadError, "La photo n'a pas pu être téléversée. Réessayez."));
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 6 }}>
      <Stack spacing={3}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate(`/catalogue/${vehicleId}`)}
          sx={{ alignSelf: "flex-start" }}
        >
          Retour au véhicule
        </Button>

        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Ajouter une photo
          </Typography>
          <Typography color="text.secondary">
            Véhicule {vehicleId}
          </Typography>
        </Box>

        {error && <Alert severity="error">{error}</Alert>}
        {photoUrl && (
          <Alert severity="success">La photo est maintenant visible dans le catalogue.</Alert>
        )}

        <Button
          component="label"
          variant="outlined"
          startIcon={<CloudUploadIcon />}
          disabled={isUploading}
        >
          {file ? file.name : "Choisir une photo"}
          <input
            hidden
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleFileChange}
          />
        </Button>

        <Button
          variant="contained"
          startIcon={isUploading ? <CircularProgress size={18} color="inherit" /> : <CloudUploadIcon />}
          onClick={handleUpload}
          disabled={!file || isUploading}
        >
          {isUploading ? "Téléversement..." : "Téléverser la photo"}
        </Button>
      </Stack>
    </Container>
  );
}
