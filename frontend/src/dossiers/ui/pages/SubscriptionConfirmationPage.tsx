import React from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Container,
  Divider,
  Typography,
  Alert,
} from "@mui/material";

import { useSubscriptionTunnelStore } from "../../../vehicles/application/stores/useSubscriptionTunnelStore";
import { useCreateDossier } from "../hooks/useDossierMutations";
import { getApiErrorMessage } from "../../../api/apiErrorMessage";

export const SubscriptionConfirmationPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    vehicleId,
    vehicleMode,
    financingPlan,
    tradeIn,
    selectedServices,
  } = useSubscriptionTunnelStore();

  const createDossierMutation = useCreateDossier();
  const [missingVehicleError, setMissingVehicleError] = React.useState(false);
  const errorMessage = createDossierMutation.error
    ? getApiErrorMessage(createDossierMutation.error, "La création de votre dossier a échoué.")
    : missingVehicleError
      ? "Aucun véhicule sélectionné dans la demande."
      : null;

  const handleConfirm = async () => {
    if (!vehicleId) {
      setMissingVehicleError(true);
      return;
    }

    setMissingVehicleError(false);
    try {
      const dossier = await createDossierMutation.mutateAsync({
        vehicle_id: vehicleId,
        trade_in: tradeIn
          ? {
              registration: tradeIn.registration,
              mileage: tradeIn.mileage,
              brand: tradeIn.brand || null,
              model: tradeIn.model || null,
            }
          : null,
        financing_plan: financingPlan
          ? {
              down_payment: financingPlan.down_payment,
              duration_months: financingPlan.duration_months,
              monthly_payment: financingPlan.monthly_payment,
            }
          : null,
      });

      navigate(`/dossiers/new?simulationId=confirmation-${dossier.id}&dossierId=${dossier.id}&vehicleId=${encodeURIComponent(vehicleId)}${vehicleMode ? `&mode=${vehicleMode}` : ""}`);
    } catch {
      return;
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Récapitulatif de votre demande
      </Typography>

      {errorMessage && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {errorMessage}
        </Alert>
      )}

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" color="primary" gutterBottom>
            Véhicule
          </Typography>
          <Typography>ID du véhicule: {vehicleId || "Non spécifié"}</Typography>
          <Typography>Mode: {vehicleMode || "Non spécifié"}</Typography>

          <Divider sx={{ my: 2 }} />

          <Typography variant="h6" color="primary" gutterBottom>
            Plan de financement
          </Typography>
          {financingPlan ? (
            <Box>
              <Typography>Apport: {financingPlan.down_payment} €</Typography>
              <Typography>
                Durée: {financingPlan.duration_months} mois
              </Typography>
              <Typography>
                Mensualité: {financingPlan.monthly_payment} € / mois
              </Typography>
            </Box>
          ) : (
            <Typography color="text.secondary">
              Aucun plan de financement configuré.
            </Typography>
          )}

          <Divider sx={{ my: 2 }} />

          <Typography variant="h6" color="primary" gutterBottom>
            Véhicule de reprise
          </Typography>
          {tradeIn ? (
            <Box>
              <Typography>
                Immatriculation: {tradeIn.registration}
              </Typography>
              <Typography>Kilométrage: {tradeIn.mileage} km</Typography>
              {tradeIn.brand && <Typography>Marque: {tradeIn.brand}</Typography>}
              {tradeIn.model && <Typography>Modèle: {tradeIn.model}</Typography>}
            </Box>
          ) : (
            <Typography color="text.secondary">Aucune reprise.</Typography>
          )}

          <Divider sx={{ my: 2 }} />

          <Typography variant="h6" color="primary" gutterBottom>
            Services inclus & optionnels
          </Typography>
          {selectedServices.length > 0 ? (
            selectedServices.map((service) => (
              <Typography key={service.id}>
                • {service.name} ({service.monthly_cost} €/mois)
              </Typography>
            ))
          ) : (
            <Typography color="text.secondary">
              Aucun service optionnel sélectionné.
            </Typography>
          )}
        </CardContent>
      </Card>

      <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
        <Button
          variant="contained"
          color="primary"
          size="large"
          disabled={createDossierMutation.isPending || !vehicleId}
          onClick={handleConfirm}
        >
          {createDossierMutation.isPending ? (
            <CircularProgress size={24} color="inherit" />
          ) : (
            "Confirmer ma demande"
          )}
        </Button>
      </Box>
    </Container>
  );
};