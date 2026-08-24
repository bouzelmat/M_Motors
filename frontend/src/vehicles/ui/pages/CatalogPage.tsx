import React from 'react';
import {
  Alert,
  Box,
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

import type { CatalogMode } from '../../application/stores/useVehicleFilterStore';

export const CatalogPage: React.FC = () => {
  const {
    mode,
    maxMonthlyRent,
    setMode,
  } = useVehicleFilterStore();

  const {
    data: vehicles,
    isLoading,
    error,
  } = useVehiclesQuery({
    mode,
    maxMonthlyRent,
  });

  const handleModeChange = (
    _event: React.MouseEvent<HTMLElement>,
    newMode: CatalogMode | null,
  ) => {
    if (newMode !== null) {
      setMode(newMode);
    }
  };

  return (
    <Container
      maxWidth="lg"
      sx={{ py: 4 }}
    >
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 4,
          flexWrap: 'wrap',
        }}
      >
        <Typography
          variant="h4"
          component="h1"
          gutterBottom
        >
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

      {isLoading && (
        <Box
          data-testid="catalog-loading"
          sx={{
            display: 'flex',
            justifyContent: 'center',
            py: 8,
          }}
        >
          <CircularProgress
            data-testid="loading-spinner"
            size={60}
          />
        </Box>
      )}

      {error && (
        <Alert
          data-testid="catalog-error"
          severity="error"
          sx={{ my: 2 }}
        >
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
              <Typography
                variant="h6"
                color="text.secondary"
              >
                Aucun véhicule disponible pour le moment.
              </Typography>
            </Box>
          ) : (
            <Grid
              container
              spacing={3}
              data-testid="vehicle-catalog"
            >
              {vehicles?.map((vehicle) => (
                <Grid
                  item
                  key={vehicle.id}
                  xs={12}
                  sm={6}
                  md={4}
                  lg={3}
                >
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