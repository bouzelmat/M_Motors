import React from "react";
import {
  Alert,
  Box,
  CircularProgress,
  Container,
  Divider,
  Typography,
} from "@mui/material";
import { useParams } from "react-router-dom";

import { useVehicleDetailQuery } from "../../application/hooks/useVehicleDetailQuery";
import { ServiceOptionRow } from "../components/ServiceOptionRow";

export const VehicleDetailPage: React.FC = () => {
  const { vehicleId } = useParams<{ vehicleId: string }>();

  const {
    data: vehicle,
    isLoading,
    error,
  } = useVehicleDetailQuery(vehicleId ?? "");

  if (isLoading) {
    return (
      <Container
        maxWidth="lg"
        sx={{ py: 4 }}
      >
        <Box
          data-testid="vehicle-detail-loading"
          sx={{
            display: "flex",
            justifyContent: "center",
            py: 8,
          }}
        > 
          <CircularProgress
            data-testid="loading-spinner"
            size={60}
          /> 
        </Box> 
      </Container>
    );
  }

  if (error || !vehicle) {
    return (
      <Container
        maxWidth="lg"
        sx={{ py: 4 }}
      > 
        <Alert
          data-testid="vehicle-detail-error"
          severity="error"
        >
          Une erreur est survenue lors du chargement du véhicule.
        </Alert> 
      </Container>
    );
  }

  return (
    <Container
      maxWidth="lg"
      sx={{ py: 4 }}
    > 
      <Typography
        variant="h4"
        component="h1"
        gutterBottom
      >
        {vehicle.brand} {vehicle.model} 
      </Typography>

      <Typography
        variant="body1"
        color="text.secondary"
        gutterBottom
      >
        {vehicle.year}
      </Typography>

      <Box sx={{ mt: 4 }}>
        <Typography
          variant="h5"
          component="h2"
          gutterBottom
        >
          Services disponibles
        </Typography>

        <Divider />

        {vehicle.services.length === 0 ? (
          <Typography
            variant="body1"
            color="text.secondary"
            sx={{ py: 2 }}
          >
            Aucun service disponible pour ce véhicule.
          </Typography>
        ) : (
          <Box>
            {vehicle.services.map((service) => (
              <ServiceOptionRow
                key={service.id}
                service={service}
              />
            ))}
          </Box>
        )}
      </Box>
    </Container>
  );
};

