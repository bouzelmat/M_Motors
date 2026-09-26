import React, { useState } from "react";
import {
  Alert,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Snackbar,
} from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import axios from "axios";

import { useAuthStore } from "../../../auth/ui/hooks/useAuth";
import { vehiclesClient } from "../../infrastructure/VehiclesClient";

type SwitchCatalogTypeButtonProps = {
  readonly vehicleId: string;
  readonly catalogType: "SALE" | "RENTAL" | "BOTH";
  readonly newPrice: number;
  readonly onSuccess?: () => void;
};

export const SwitchCatalogTypeButton: React.FC<SwitchCatalogTypeButtonProps> = ({
  vehicleId,
  catalogType,
  newPrice,
  onSuccess,
}) => {
  const { user } = useAuthStore();
  const queryClient = useQueryClient();

  const [isLoading, setIsLoading] = useState(false);
  const [confirmationDialogOpen, setConfirmationDialogOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  if (user?.role !== "ADMIN" || catalogType === "BOTH") {
    return null;
  }

  const label = catalogType === "SALE" ? "Passer en Location" : "Passer en Vente";

  const executeToggle = async (confirm: boolean) => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      await vehiclesClient.changeCatalogType(vehicleId, newPrice, confirm);
      
      await queryClient.invalidateQueries({
        queryKey: ["vehicle", vehicleId],
      });

      setSuccessMessage("Le mode commercial du véhicule a été mis à jour avec succès.");
      setConfirmationDialogOpen(false);
      if (onSuccess) {
        onSuccess();
      }
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response?.status === 409) {
        setConfirmationDialogOpen(true);
      } else {
        setErrorMessage("Une erreur est survenue lors du changement de mode du véhicule.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleInitialClick = () => {
    if (newPrice <= 0 || isNaN(newPrice)) {
      setErrorMessage("Un prix valide doit être renseigné.");
      return;
    }
    executeToggle(false);
  };

  const handleConfirmModal = () => {
    executeToggle(true);
  };

  const handleCancelModal = () => {
    setConfirmationDialogOpen(false);
  };

  return (
    <>
      <Button
        variant="contained"
        color="primary"
        disabled={isLoading}
        onClick={handleInitialClick}
        startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : null}
      >
        {label}
      </Button>

      <Dialog
        open={confirmationDialogOpen}
        onClose={handleCancelModal}
        aria-labelledby="confirmation-dialog-title"
      >
        <DialogTitle id="confirmation-dialog-title">Confirmation requise</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Ce véhicule a un dossier en cours. Confirmer le basculement ?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelModal} disabled={isLoading}>
            Annuler
          </Button>
          <Button onClick={handleConfirmModal} color="warning" autoFocus disabled={isLoading}>
            Confirmer
          </Button>
        </DialogActions>
      </Dialog>

      {errorMessage && (
        <Snackbar open autoHideDuration={6000} onClose={() => setErrorMessage(null)}>
          <Alert severity="error" onClose={() => setErrorMessage(null)}>
            {errorMessage}
          </Alert>
        </Snackbar>
      )}

      {successMessage && (
        <Snackbar open autoHideDuration={6000} onClose={() => setSuccessMessage(null)}>
          <Alert severity="success" onClose={() => setSuccessMessage(null)}>
            {successMessage}
          </Alert>
        </Snackbar>
      )}
    </>
  );
};