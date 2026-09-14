import React, { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Grid,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from '@mui/material';

import { useVehicleFilterStore } from '../../application/stores/useVehicleFilterStore';
import { useVehiclesQuery } from '../../application/hooks/useVehiclesQuery';
import { VehicleCard } from '../components/VehicleCard';
import { FilterBar } from '../components/FilterBar';

import type { CatalogMode } from '../../application/stores/useVehicleFilterStore';

export const CatalogPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const {
    mode,
    brand,
    maxPrice,
    maxMileage,
    fuelType,
    maxMonthlyRent,
    setMode,
    resetFilters,
  } = useVehicleFilterStore();

  // Synchronisation URL -> Store au premier chargement
  useEffect(() => {
    const urlMode = searchParams.get('mode') as CatalogMode | null;
    if (urlMode === 'rental' || urlMode === 'sale') {
      if (urlMode !== mode) {
        setMode(urlMode);
      }
    } else {
      // Si l'URL n'a pas de mode valide, on inscrit la valeur du store par défaut
      setSearchParams({ mode }, { replace: true });
    }
  }, []);

  const {
    data: vehicles,
    isLoading,
    error,
  } = useVehiclesQuery({
    mode,
    brand,
    maxPrice,
    maxMileage,
    fuelType,
    maxMonthlyRent,
  });

  const handleModeChange = (
    _event: React.MouseEvent<HTMLElement>,
    newMode: CatalogMode | null,
  ) => {
    if (newMode !== null) {
      setMode(newMode);
      setSearchParams({ mode: newMode });
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 4,
          flexWrap: 'wrap',
          gap: 2,
        }}
      >
        <Typography variant="h4" component="h1" gutterBottom>
          Catalogue des véhicules
        </Typography>

        <ToggleButtonGroup
          value={mode}
          exclusive
          onChange={handleModeChange}
          aria-label="mode de recherche"
          size="small"
        >
          <ToggleButton value="rental">
            Location (LLD)
          </ToggleButton>

          <ToggleButton value="sale">
            Achat
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {/* Barre de filtres */}
      <FilterBar />

      {isLoading && (
        <Box
          data-testid="catalog-loading"
          sx={{
            display: 'flex',
            justifyContent: 'center',
            py: 8,
          }}
        >
          <CircularProgress data-testid="loading-spinner" size={60} />
        </Box>
      )}

      {error && (
        <Alert data-testid="catalog-error" severity="error" sx={{ my: 2 }}>
          Une erreur est survenue lors du chargement du catalogue.
          Veuillez réessayer plus tard.
        </Alert>
      )}

      {!isLoading && !error && (
        <>
          {vehicles && vehicles.length === 0 ? (
            <Box
              data-testid="catalog-empty"
              sx={{
                textAlign: 'center',
                py: 8,
              }}
            >
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Aucun véhicule ne correspond à vos critères.
              </Typography>
              <Button
                variant="text"
                color="primary"
                onClick={resetFilters}
                sx={{ mt: 1 }}
              >
                Modifier mes filtres
              </Button>
            </Box>
          ) : (
            <Grid container spacing={3} data-testid="vehicle-catalog">
              {vehicles?.map((vehicle) => (
                <Grid item key={vehicle.id} xs={12} sm={6} md={4} lg={3}>
                  <VehicleCard vehicle={vehicle} />
                </Grid>
              ))}
            </Grid>
          )}
        </>
      )}
    </Container>
  );
};