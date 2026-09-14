import React, { useState } from "react";
import {
  Alert,
  Box,
  CircularProgress,
  Container,
  Divider,
  TextField,
  Typography,
} from "@mui/material";
import { useParams } from "react-router-dom";

import { useVehicleDetailQuery } from "../../application/hooks/useVehicleDetailQuery";
import { ServiceOptionRow } from "../components/ServiceOptionRow";
import { SwitchCatalogTypeButton } from "../components/SwitchCatalogTypeButton";
import { useAuthStore } from "../../../auth/ui/hooks/useAuth";

export const VehicleDetailPage: React.FC = () => {
  const { vehicleId } = useParams<{ vehicleId: string }>();
  const { user } = useAuthStore();

  const {
    data: vehicle,
    isLoading,
    error,
  } = useVehicleDetailQuery(vehicleId ?? "");

  const [customPrice, setCustomPrice] = useState<string>("");

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box
          data-testid="vehicle-detail-loading"
          sx={{ display: "flex", justifyContent: "center", py: 8 }}
        >
          <CircularProgress data-testid="loading-spinner" size={60} />
        </Box>
      </Container>
    );
  }

  if (error || !vehicle) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert data-testid="vehicle-detail-error" severity="error">
          Une erreur est survenue lors du chargement du véhicule.
        </Alert>
      </Container>
    );
  }

  // Détermination de la valeur par défaut du nouveau prix (loyer ou prix d'achat alternatif)
  const defaultTargetPrice =
    vehicle.catalog_type === "SALE"
      ? Number(vehicle.monthly_rent) || 399
      : Number(vehicle.price) || 15000;

  const effectivePrice = customPrice !== "" ? Number(customPrice) : defaultTargetPrice;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", mb: 2 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            {vehicle.brand} {vehicle.model}
          </Typography>
          <Typography variant="body1" color="text.secondary" gutterBottom>
            {vehicle.year} — Mode actuel : {vehicle.catalog_type}
          </Typography>
        </Box>

        {user?.role === "ADMIN" && (
          <Box sx={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 1 }}>
            <TextField
              label={vehicle.catalog_type === "SALE" ? "Nouveau Loyer (€/mois)" : "Nouveau Prix (€)"}
              type="number"
              size="small"
              value={customPrice !== "" ? customPrice : defaultTargetPrice}
              onChange={(e) => setCustomPrice(e.target.value)}
              slotProps={{ htmlInput: { min: 1, step: 0.01 } }}
              sx={{ width: 200 }}
            />
            <SwitchCatalogTypeButton
              vehicleId={vehicle.id}
              catalogType={vehicle.catalog_type}
              newPrice={effectivePrice}
            />
          </Box>
        )}
      </Box>

      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Services disponibles
        </Typography>

        <Divider />

        {vehicle.services.length === 0 ? (
          <Typography variant="body1" color="text.secondary" sx={{ py: 2 }}>
            Aucun service disponible pour ce véhicule.
          </Typography>
        ) : (
          <Box>
            {vehicle.services.map((service) => (
              <ServiceOptionRow key={service.id} service={service} />
            ))}
          </Box>
        )}
      </Box>
    </Container>
  );
};