import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Alert, Container, Paper, Typography } from "@mui/material";

import { useAuthStore } from "../../../auth/ui/hooks/useAuth";
import { vehiclesClient } from "../../infrastructure/VehiclesClient";
import { CreateVehicleRequestDTO } from "../../infrastructure/vehicle.types";
import { VehicleAddForm } from "../components/VehicleAddForm";

export const AddVehiclePage: React.FC = () => {
    const navigate = useNavigate();
    const { user, isAuthenticated } = useAuthStore();
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [apiError, setApiError] = useState<string | null>(null);

    if (!isAuthenticated || user?.role !== "ADMIN") {
        return (
            <Container maxWidth="sm" sx={{ py: 6 }}>
                <Alert severity="error">Accès réservé aux administrateurs.</Alert>
            </Container>
        );
    }

    const handleSubmit = async (payload: CreateVehicleRequestDTO) => {
        setIsSubmitting(true);
        setApiError(null);

        try {
            const createdVehicle = await vehiclesClient.createVehicle(payload);
            navigate(`/admin/vehicles/${createdVehicle.id}/photos`);
        } catch {
            setApiError("Une erreur est survenue lors de la création du véhicule. Vérifiez vos informations.");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Container maxWidth="md" sx={{ py: 6 }}>
            <Paper elevation={3} sx={{ p: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Créer un nouveau véhicule
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
                    Renseignez les caractéristiques du véhicule pour l'ajouter au catalogue.
                </Typography>

                <VehicleAddForm
                    onSubmit={handleSubmit}
                    isSubmitting={isSubmitting}
                    apiError={apiError}
                />
            </Paper>
        </Container>
    );
};
