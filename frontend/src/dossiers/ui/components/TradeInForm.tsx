import React, { useState, useEffect } from "react";
import {
  Box,
  FormControlLabel,
  Switch,
  TextField,
  Typography,
  Grid,
} from "@mui/material";
import { useSubscriptionTunnelStore } from "../../application/stores/useSubscriptionTunnelStore";

export const TradeInForm: React.FC = () => {
  const { tradeIn, setTradeIn } = useSubscriptionTunnelStore();
  const [enabled, setEnabled] = useState<boolean>(tradeIn !== null);

  const [registration, setRegistration] = useState<string>(
    tradeIn?.registration || "",
  );
  const [mileage, setMileage] = useState<string>(
    tradeIn?.mileage !== undefined ? String(tradeIn.mileage) : "",
  );
  const [brand, setBrand] = useState<string>(tradeIn?.brand || "");
  const [model, setModel] = useState<string>(tradeIn?.model || "");

  const [errors, setErrors] = useState<{
    registration?: string;
    mileage?: string;
  }>({});

  const handleToggle = (event: React.ChangeEvent<HTMLInputElement>) => {
    const isChecked = event.target.checked;
    setEnabled(isChecked);
    if (!isChecked) {
      setTradeIn(null);
      setErrors({});
    } else {
      validateAndUpdate(registration, mileage, brand, model);
    }
  };

  const validateAndUpdate = (
    regVal: string,
    milVal: string,
    brandVal: string,
    modelVal: string,
  ) => {
    const newErrors: { registration?: string; mileage?: string } = {};

    if (!regVal.trim()) {
      newErrors.registration = "L'immatriculation est obligatoire.";
    }

    const parsedMileage = Number(milVal);
    if (milVal === "" || Number.isNaN(parsedMileage) || parsedMileage < 0) {
      newErrors.mileage = "Le kilométrage doit être un nombre positif ou nul.";
    }

    setErrors(newErrors);

    if (Object.keys(newErrors).length === 0) {
      setTradeIn({
        registration: regVal.trim(),
        mileage: parsedMileage,
        brand: brandVal.trim() || null,
        model: modelVal.trim() || null,
      });
    } else {
      setTradeIn(null);
    }
  };

  const handleRegistrationChange = (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const val = e.target.value;
    setRegistration(val);
    if (enabled) validateAndUpdate(val, mileage, brand, model);
  };

  const handleMileageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setMileage(val);
    if (enabled) validateAndUpdate(registration, val, brand, model);
  };

  const handleBrandChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setBrand(val);
    if (enabled) validateAndUpdate(registration, mileage, val, model);
  };

  const handleModelChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setModel(val);
    if (enabled) validateAndUpdate(registration, mileage, brand, val);
  };

  return (
    <Box sx={{ my: 3, p: 2, border: "1px solid #e0e0e0", borderRadius: 2 }}>
      <Typography variant="h6" gutterBottom>
        Reprise de votre ancien véhicule
      </Typography>

      <FormControlLabel
        control={
          <Switch
            checked={enabled}
            onChange={handleToggle}
            color="primary"
            inputProps={{ "aria-label": "Toggle reprise véhicule" }}
          />
        }
        label="Je souhaite faire reprendre mon ancien véhicule"
      />

      {enabled && (
        <Box sx={{ mt: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                label="Immatriculation"
                value={registration}
                onChange={handleRegistrationChange}
                error={Boolean(errors.registration)}
                helperText={errors.registration}
                placeholder="ex: AA-123-BB"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                type="number"
                label="Kilométrage"
                value={mileage}
                onChange={handleMileageChange}
                error={Boolean(errors.mileage)}
                helperText={errors.mileage}
                inputProps={{ min: 0 }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Marque"
                value={brand}
                onChange={handleBrandChange}
                placeholder="ex: Peugeot"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Modèle"
                value={model}
                onChange={handleModelChange}
                placeholder="ex: 208"
              />
            </Grid>
          </Grid>
        </Box>
      )}
    </Box>
  );
};