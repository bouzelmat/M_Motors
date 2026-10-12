import { Alert, Box, CircularProgress, Container } from "@mui/material";
import { useQueries } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { vehiclesClient } from "../../infrastructure/VehiclesClient";
import type { CatalogMode } from "../../domain/value-objects/catalogMode";
import { VehicleDetailPage } from "./VehicleDetailPage";
import { createVehicleSlug } from "../vehicleSlug";

const catalogModes: CatalogMode[] = ["sale", "rental"];
const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export function VehicleSlugPage() {
  const { vehicleId: slug = "" } = useParams();
  const isLegacyId = uuidPattern.test(slug);
  const catalogs = useQueries({
    queries: catalogModes.map((mode) => ({
      queryKey: ["vehicles", "slug-resolution", mode],
      queryFn: () => vehiclesClient.getCatalog({ mode }),
      enabled: !isLegacyId,
      staleTime: 5 * 60 * 1000,
    })),
  });

  if (isLegacyId) {
    return <VehicleDetailPage vehicleIdOverride={slug} />;
  }

  if (catalogs.some((catalog) => catalog.isLoading)) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
          <CircularProgress aria-label="Recherche du véhicule" />
        </Box>
      </Container>
    );
  }

  if (catalogs.some((catalog) => catalog.isError)) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">Impossible de retrouver ce véhicule dans le catalogue.</Alert>
      </Container>
    );
  }

  const vehicle = catalogs
    .flatMap((catalog) => catalog.data ?? [])
    .find((item) => createVehicleSlug(item) === slug);

  if (!vehicle) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="warning">Ce véhicule n’est plus disponible dans le catalogue.</Alert>
      </Container>
    );
  }

  return <VehicleDetailPage vehicleIdOverride={vehicle.id} />;
}