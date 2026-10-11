import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Alert, Container, Paper, Typography } from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useAuthStore } from "../../../auth/ui/hooks/useAuth";
import { vehiclesClient } from "../../infrastructure/VehiclesClient";
import { CreateVehicleRequestDTO } from "../../infrastructure/vehicle.types";
import { VehicleAddForm } from "../components/VehicleAddForm";
import { getApiErrorMessage } from "../../../api/apiErrorMessage";
import type { ServiceDTO } from "../../infrastructure/vehicle.types";

export const AddVehiclePage: React.FC = () => {
    const navigate = useNavigate();
    const { user, isAuthenticated } = useAuthStore();
    const queryClient = useQueryClient();
    const serviceCatalogQuery = useQuery({
        queryKey: ["vehicle-service-catalog"],
        queryFn: () => vehiclesClient.getServiceCatalog(),
        enabled: isAuthenticated && user?.role === "ADMIN",
        retry: false,
    });
    const createVehicleMutation = useMutation({
        mutationFn: (payload: CreateVehicleRequestDTO) => vehiclesClient.createVehicle(payload),
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: ["vehicles"] });
        },
    });
    const apiError = createVehicleMutation.error
        ? getApiErrorMessage(createVehicleMutation.error, "La création du véhicule a échoué.")
        : null;

    if (!isAuthenticated || user?.role !== "ADMIN") {
        return (
            <Container maxWidth="sm" sx={{ py: 6 }}>
                <Alert severity="error">Accès réservé aux administrateurs.</Alert>
            </Container>
        );
    }

    const handleSubmit = async (payload: CreateVehicleRequestDTO) => {
        const createdVehicle = await createVehicleMutation.mutateAsync(payload);
        navigate(`/admin/vehicles/${createdVehicle.id}/edit`);
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
                    isSubmitting={createVehicleMutation.isPending}
                    apiError={apiError}
                    services={serviceCatalogQuery.data ?? []}
                    isLoadingServices={serviceCatalogQuery.isLoading}
                    servicesError={serviceCatalogQuery.isError
                        ? getApiErrorMessage(serviceCatalogQuery.error, "Le catalogue de services n’a pas pu être chargé.")
                        : null}
                />
            </Paper>
        </Container>
    );
};
