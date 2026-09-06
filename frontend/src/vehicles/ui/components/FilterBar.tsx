import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  TextField,
} from '@mui/material';
import RestartAltIcon from '@mui/icons-material/RestartAlt';

import { useVehicleFilterStore } from '../../application/stores/useVehicleFilterStore';

const DEBOUNCE_DELAY_MS = 300;

export const FilterBar: React.FC = () => {
  const {
    brand,
    maxPrice,
    maxMileage,
    fuelType,
    setBrand,
    setMaxPrice,
    setMaxMileage,
    setFuelType,
    resetFilters,
  } = useVehicleFilterStore();

  // États locaux pour le debounce des champs texte/numériques
  const [localBrand, setLocalBrand] = useState(brand ?? '');
  const [localMaxPrice, setLocalMaxPrice] = useState<string>(
    maxPrice !== null ? String(maxPrice) : ''
  );
  const [localMaxMileage, setLocalMaxMileage] = useState<string>(
    maxMileage !== null ? String(maxMileage) : ''
  );

  // Synchronisation si le store est réinitialisé depuis l'extérieur
  useEffect(() => {
    setLocalBrand(brand ?? '');
    setLocalMaxPrice(maxPrice !== null ? String(maxPrice) : '');
    setLocalMaxMileage(maxMileage !== null ? String(maxMileage) : '');
  }, [brand, maxPrice, maxMileage]);

  // Debounce Brand
  useEffect(() => {
    const timer = setTimeout(() => {
      const normalizedValue = localBrand.trim() === '' ? null : localBrand.trim();
      if (normalizedValue !== brand) {
        setBrand(normalizedValue);
      }
    }, DEBOUNCE_DELAY_MS);

    return () => clearTimeout(timer);
  }, [localBrand, setBrand, brand]);

  // Debounce MaxPrice
  useEffect(() => {
    const timer = setTimeout(() => {
      const parsedValue = localMaxPrice !== '' ? Number(localMaxPrice) : null;
      if (parsedValue !== maxPrice) {
        setMaxPrice(parsedValue);
      }
    }, DEBOUNCE_DELAY_MS);

    return () => clearTimeout(timer);
  }, [localMaxPrice, setMaxPrice, maxPrice]);

  // Debounce MaxMileage
  useEffect(() => {
    const timer = setTimeout(() => {
      const parsedValue = localMaxMileage !== '' ? Number(localMaxMileage) : null;
      if (parsedValue !== maxMileage) {
        setMaxMileage(parsedValue);
      }
    }, DEBOUNCE_DELAY_MS);

    return () => clearTimeout(timer);
  }, [localMaxMileage, setMaxMileage, maxMileage]);

  return (
    <Paper
      elevation={1}
      sx={{ p: 2, mb: 4, borderRadius: 2 }}
    >
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            md: 'repeat(5, 1fr)',
          },
          gap: 2,
          alignItems: 'center',
        }}
      >
        <TextField
          label="Marque"
          variant="outlined"
          size="small"
          value={localBrand}
          onChange={(e) => setLocalBrand(e.target.value)}
          placeholder="ex: Peugeot"
          inputProps={{ 'aria-label': 'Filtrer par marque' }}
        />

        <TextField
          label="Budget max (€)"
          variant="outlined"
          size="small"
          type="number"
          value={localMaxPrice}
          onChange={(e) => setLocalMaxPrice(e.target.value)}
          placeholder="ex: 25000"
          inputProps={{ 'aria-label': 'Filtrer par budget max', min: 0 }}
        />

        <TextField
          label="Kilométrage max (km)"
          variant="outlined"
          size="small"
          type="number"
          value={localMaxMileage}
          onChange={(e) => setLocalMaxMileage(e.target.value)}
          placeholder="ex: 50000"
          inputProps={{ 'aria-label': 'Filtrer par kilométrage max', min: 0 }}
        />

        <FormControl size="small" fullWidth>
          <InputLabel id="fuel-type-select-label">Motorisation</InputLabel>
          <Select
            labelId="fuel-type-select-label"
            label="Motorisation"
            value={fuelType ?? ''}
            onChange={(e) => setFuelType(e.target.value ? e.target.value : null)}
            inputProps={{ 'aria-label': 'Filtrer par motorisation' }}
          >
            <MenuItem value="">Toutes</MenuItem>
            <MenuItem value="ESSENCE">Essence</MenuItem>
            <MenuItem value="DIESEL">Diesel</MenuItem>
            <MenuItem value="ELECTRIQUE">Électrique</MenuItem>
            <MenuItem value="HYBRIDE">Hybride</MenuItem>
          </Select>
        </FormControl>

        <Button
          variant="outlined"
          color="inherit"
          startIcon={<RestartAltIcon />}
          onClick={resetFilters}
          sx={{ height: 40 }}
        >
          Réinitialiser
        </Button>
      </Box>
    </Paper>
  );
};