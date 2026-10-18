import React from "react";
import { Alert, Box, Container, Grid, Button, CircularProgress, useTheme } from "@mui/material";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import { Link } from "react-router-dom";
import { SectionHeading } from "../../shared/ui/components/SectionHeading";
import { VehicleCard } from "../../vehicles/ui/components/VehicleCard";
import { useRevealOnScroll } from "../../shared/ui/hooks/useRevealOnScroll";
import { useVehiclesQuery } from "../../vehicles/application/hooks/useVehiclesQuery";
import type { VehicleListItemDTO } from "../../vehicles/infrastructure/dto/vehicle.dto";

type FeaturedVehicleCardProps = {
  vehicle: VehicleListItemDTO;
  index: number;
};

const FeaturedVehicleCard: React.FC<FeaturedVehicleCardProps> = ({ vehicle, index }) => {
  const { ref, style } = useRevealOnScroll<HTMLDivElement>({ index, staggerMs: 100 });
  const isSale = vehicle.catalog_type === "SALE";

  return (
    <div ref={ref} style={style}>
      <VehicleCard
        id={vehicle.id}
        brand={vehicle.brand}
        model={vehicle.model}
        version={vehicle.year ? String(vehicle.year) : undefined}
        year={vehicle.year}
        mileage={vehicle.mileage ?? 0}
        fuelType={vehicle.energy_type ?? "Non précisé"}
        price={Number(isSale ? vehicle.price ?? 0 : vehicle.monthly_rent ?? 0)}
        mode={isSale ? "ACHAT" : "LOCATION"}
        imageUrl={vehicle.photo_url ?? undefined}
      />
    </div>
  );
};

export const VehicleSelectionSection: React.FC = () => {
  const theme = useTheme();
  const rentalQuery = useVehiclesQuery({ mode: "rental" });
  const saleQuery = useVehiclesQuery({ mode: "sale" });
  const featuredVehicles = [...(rentalQuery.data ?? []), ...(saleQuery.data ?? [])].slice(0, 3);
  const isLoading = rentalQuery.isLoading || saleQuery.isLoading;
  const hasError = rentalQuery.isError || saleQuery.isError;

  return (
    <Box sx={{ py: { xs: 8, md: 12 }, backgroundColor: theme.palette.background.default }}>
      <Container maxWidth="xl">
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", mb: 5, flexWrap: "wrap", gap: 2 }}>
          <SectionHeading
            eyebrow="OFFRES DISPONIBLES IMMÉDIATEMENT"
            title="Notre Sélection Premium"
            subtitle="Des véhicules rigoureusement inspectés et disponibles en livraison rapide."
          />
          <Button
            variant="outlined"
            component={Link}
            to="/catalogue"
            endIcon={<ArrowForwardIcon />}
            sx={{ borderRadius: 999 }}
          >
            Voir tout le catalogue
          </Button>
        </Box>

        {isLoading && (
          <Box data-testid="home-vehicles-loading" sx={{ display: "flex", justifyContent: "center", py: 6 }}>
            <CircularProgress aria-label="Chargement des véhicules" />
          </Box>
        )}

        {hasError && (
          <Alert severity="error" data-testid="home-vehicles-error">
            Impossible de charger les véhicules disponibles.
          </Alert>
        )}

        {!isLoading && !hasError && featuredVehicles.length === 0 && (
          <Alert severity="info" data-testid="home-vehicles-empty">
            Aucun véhicule n’est actuellement disponible dans le catalogue.
          </Alert>
        )}

        {!isLoading && !hasError && featuredVehicles.length > 0 && (
          <Grid container spacing={3.5}>
            {featuredVehicles.map((vehicle, index) => (
              <Grid item xs={12} sm={6} md={4} key={vehicle.id}>
                <FeaturedVehicleCard vehicle={vehicle} index={index} />
              </Grid>
            ))}
          </Grid>
        )}
      </Container>
    </Box>
  );
};
