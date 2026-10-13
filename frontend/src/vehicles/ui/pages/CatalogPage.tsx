import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Box,
  Container,
  Grid,
  Typography,
  Button,
  Alert,
  Skeleton,
  Card,
  CardContent,
  Chip,
  IconButton,
  useTheme,
  useMediaQuery,
  CircularProgress,
  Paper,
} from "@mui/material";
import FilterListIcon from "@mui/icons-material/FilterList";
import ReplayIcon from "@mui/icons-material/Replay";
import DirectionCarIcon from "@mui/icons-material/DirectionsCar";
import { useVehicleFilterStore, CatalogMode } from "../../application/stores/useVehicleFilterStore";
import { useVehiclesQuery } from "../../application/hooks/useVehiclesQuery";
import { VehicleCard } from "../components/VehicleCard";
import { FilterBar } from "../components/FilterBar";
import { FilterBottomSheet } from "../components/FilterBottomSheet";

export const CatalogPage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));
  const [searchParams, setSearchParams] = useSearchParams();
  const [mobileFilterOpen, setMobileFilterOpen] = useState(false);

  const {
    mode,
    brand,
    maxPrice,
    maxMileage,
    fuelType,
    maxMonthlyRent,
    setMode,
    setBrand,
    setFuelType,
    setMaxMonthlyRent,
    setMaxPrice,
    setMaxMileage,
    resetFilters,
  } = useVehicleFilterStore();

  // Sync URL params on initial render
  useEffect(() => {
    const urlMode = searchParams.get("mode");
    if (urlMode === "LOCATION" || urlMode === "rental") {
      setMode("rental");
    } else if (urlMode === "ACHAT" || urlMode === "sale" || urlMode === "purchase") {
      setMode("sale");
    }

    const urlBrand = searchParams.get("brand");
    if (urlBrand) setBrand(urlBrand);

    const urlEnergy = searchParams.get("fuel_type");
    if (urlEnergy) setFuelType(urlEnergy);
  }, []);

  // Fetch vehicles via React Query
  const {
    data: vehicles,
    isLoading,
    isError,
    error,
    refetch,
  } = useVehiclesQuery({
    mode,
    brand,
    maxPrice,
    maxMileage,
    fuelType,
    maxMonthlyRent,
  });

  useEffect(() => {
    if (isError && error) {
      console.error("Erreur lors du chargement du catalogue :", error);
    }
  }, [isError, error]);

  const isAchat = mode === "sale";
  const activeColor = isAchat
    ? theme.palette.accent?.achat || "#E82127"
    : theme.palette.accent?.location || "#3B82F6";
  const emptyStateMessage = isAchat
    ? "Aucun véhicule disponible à l'achat"
    : "Aucun véhicule disponible à la location";

  return (
    <Container maxWidth="xl" sx={{ py: 5 }}>
      {/* Header Banner */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 2,
          flexWrap: "wrap",
          gap: 2,
        }}
      >
        <Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 1 }}>
            <Chip
              label={isAchat ? "ACHAT COMPTANT" : "LOCATION LLD"}
              sx={{
                backgroundColor: isAchat ? "rgba(232, 33, 39, 0.08)" : "rgba(59, 130, 246, 0.08)",
                color: activeColor,
                fontWeight: 800,
                fontSize: "0.75rem",
                letterSpacing: "0.1em",
              }}
            />
            <Typography variant="caption" color="text.secondary">
              {vehicles ? `${vehicles.length} véhicules disponibles` : "Chargement..."}
            </Typography>
          </Box>
          <Typography variant="h3" component="h1" fontWeight={800}>
            Catalogue des Véhicules
          </Typography>
        </Box>

        {isMobile && (
          <Button
            variant="outlined"
            startIcon={<FilterListIcon />}
            onClick={() => setMobileFilterOpen(true)}
            sx={{ borderRadius: 999 }}
          >
            Filtres
          </Button>
        )}
      </Box>

      <Box sx={{ display: "flex", gap: 1, mb: 3 }}>
        <Button
          variant={isAchat ? "contained" : "outlined"}
          onClick={() => setMode("sale")}
          aria-label="Achat"
          sx={{ borderRadius: 999 }}
        >
          Achat
        </Button>
        <Button
          variant={!isAchat ? "contained" : "outlined"}
          onClick={() => setMode("rental")}
          aria-label="Location"
          sx={{ borderRadius: 999 }}
        >
          Location
        </Button>
      </Box>

      <Box sx={{ mb: 3 }}>
        <FilterBar />
      </Box>

      {isLoading && (
        <Box data-testid="catalog-loading" sx={{ display: "flex", justifyContent: "center", py: 8 }}>
          <CircularProgress aria-label="Chargement du catalogue" />
        </Box>
      )}

      {isError && (
        <Box data-testid="catalog-error" sx={{ py: 6, textAlign: "center" }}>
          <Alert
            severity="error"
            action={
              <Button color="inherit" size="small" startIcon={<ReplayIcon />} onClick={() => refetch()}>
                Réessayer
              </Button>
            }
            sx={{ borderRadius: 16, mb: 2 }}
          >
            Une erreur est survenue lors du chargement du catalogue.
          </Alert>
        </Box>
      )}

      {!isLoading && !isError && vehicles && vehicles.length === 0 && (
        <Paper
          data-testid="catalog-empty"
          elevation={0}
          sx={{
            py: 10,
            px: 4,
            textAlign: "center",
            borderRadius: 24,
            backgroundColor: theme.palette.background.paper,
            border: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}`,
          }}
        >
          <Box
            sx={{
              width: 64,
              height: 64,
              borderRadius: 999,
              backgroundColor: theme.palette.surface?.nested || "#F2F3F5",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              mx: "auto",
              mb: 2,
            }}
          >
            <DirectionCarIcon sx={{ fontSize: 32, color: theme.palette.text.secondary }} />
          </Box>
          <Typography variant="h5" fontWeight={800} gutterBottom>
            {emptyStateMessage}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 460, mx: "auto", mb: 3 }}>
            Essayez d'élargir votre budget, de changer de marque ou de réinitialiser vos filtres de recherche.
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={() => {
              resetFilters();
              setMode("rental");
            }}
            sx={{ borderRadius: 999 }}
          >
            Modifier mes filtres
          </Button>
        </Paper>
      )}

      {!isLoading && !isError && vehicles && vehicles.length > 0 && (
        <Grid container spacing={3} data-testid="vehicle-catalog">
          {vehicles.map((v) => (
            <Grid item key={v.id} xs={12} sm={6} lg={4}>
              <VehicleCard
                id={v.id}
                brand={v.brand}
                model={v.model}
                version={v.year ? String(v.year) : undefined}
                year={v.year || 2023}
                mileage={v.mileage || 25000}
                fuelType={v.fuel_type || "Hybride"}
                price={isAchat ? Number(v.price || 25000) : Number(v.monthly_rent || 349)}
                mode={isAchat ? "ACHAT" : "LOCATION"}
                imageUrl={v.photo_url || undefined}
              />
            </Grid>
          ))}
        </Grid>
      )}

      <FilterBottomSheet open={mobileFilterOpen} onClose={() => setMobileFilterOpen(false)} />
    </Container>
  );
};