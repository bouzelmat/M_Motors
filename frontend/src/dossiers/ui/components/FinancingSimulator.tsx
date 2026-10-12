import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Slider,
  TextField,
  Paper,
  Grid,
  Divider,
} from '@mui/material';
import { calculateMonthlyPayment } from '../../../dossiers/application/utils/financing';
import { useSubscriptionTunnelStore } from '../../application/stores/useSubscriptionTunnelStore';

export interface FinancingSimulatorProps {
  vehiclePrice: number;
  annualInterestRate?: number;
}

const DEFAULT_INTEREST_RATE = 0.045;
const DURATION_OPTIONS = [12, 24, 36, 48, 60];

const marks = DURATION_OPTIONS.map((val) => ({
  value: val,
  label: `${val}m`,
}));

export const FinancingSimulator: React.FC<FinancingSimulatorProps> = ({
  vehiclePrice,
  annualInterestRate = DEFAULT_INTEREST_RATE,
}) => {
  const { financingPlan, setFinancingPlan } = useSubscriptionTunnelStore();

  const [downPayment, setDownPayment] = useState<number>(() => {
    return financingPlan?.down_payment ?? 0;
  });

  const [downPaymentInput, setDownPaymentInput] = useState<string>(() => {
    return String(financingPlan?.down_payment ?? 0);
  });

  const [durationMonths, setDurationMonths] = useState<number>(() => {
    return financingPlan?.duration_months ?? 48;
  });

  const capitalToFinance = Math.max(0, vehiclePrice - downPayment);
  const monthlyPayment = calculateMonthlyPayment(
    vehiclePrice,
    downPayment,
    durationMonths,
    annualInterestRate
  );

  const updateStore = (payment: number, duration: number, monthly: number) => {
    setFinancingPlan({
      down_payment: payment,
      duration_months: duration,
      monthly_payment: monthly,
    });
  };

  useEffect(() => {
    updateStore(downPayment, durationMonths, monthlyPayment);
  }, [downPayment, durationMonths, vehiclePrice, annualInterestRate]);

  const handleDownPaymentSliderChange = (
    _event: Event,
    newValue: number | number[]
  ) => {
    const val = Array.isArray(newValue) ? newValue[0] : newValue;
    const clampedVal = Math.min(Math.max(0, val), vehiclePrice);
    setDownPayment(clampedVal);
    setDownPaymentInput(String(clampedVal));
  };

  const handleDownPaymentInputChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const rawValue = event.target.value;
    setDownPaymentInput(rawValue);

    if (rawValue.trim() === '') {
      setDownPayment(0);
      return;
    }

    const parsed = parseFloat(rawValue);
    if (isNaN(parsed)) {
      setDownPayment(0);
      return;
    }

    const clampedVal = Math.min(Math.max(0, parsed), vehiclePrice);
    setDownPayment(clampedVal);
  };

  const handleDownPaymentInputBlur = () => {
    setDownPaymentInput(String(downPayment));
  };

  const handleDurationChange = (_event: Event, newValue: number | number[]) => {
    const val = Array.isArray(newValue) ? newValue[0] : newValue;
    setDurationMonths(val);
  };

  return (
    <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
      <Typography variant="h6" gutterBottom>
        Simulateur de Financement
      </Typography>

      <Box sx={{ mb: 4 }}>
        <Typography id="down-payment-slider-label" variant="subtitle2" gutterBottom>
          Apport initial (€)
        </Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={8} sm={9}>
            <Slider
              value={downPayment}
              min={0}
              max={vehiclePrice}
              step={100}
              onChange={handleDownPaymentSliderChange}
              aria-labelledby="down-payment-slider-label"
              valueLabelDisplay="auto"
            />
          </Grid>
          <Grid item xs={4} sm={3}>
            <TextField
              value={downPaymentInput}
              onChange={handleDownPaymentInputChange}
              onBlur={handleDownPaymentInputBlur}
              inputProps={{
                step: 100,
                min: 0,
                max: vehiclePrice,
                type: 'number',
                'aria-label': 'Apport initial en euros',
              }}
              size="small"
              fullWidth
            />
          </Grid>
        </Grid>
      </Box>

      <Box sx={{ mb: 4 }}>
        <Typography id="duration-slider-label" variant="subtitle2" gutterBottom>
          Durée du financement (mois)
        </Typography>
        <Slider
          value={durationMonths}
          min={12}
          max={60}
          step={null}
          marks={marks}
          onChange={handleDurationChange}
          aria-labelledby="duration-slider-label"
          valueLabelDisplay="auto"
        />
      </Box>

      <Divider sx={{ my: 2 }} />

      <Box sx={{ backgroundColor: 'grey.50', p: 2, borderRadius: 1 }}>
        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
          Récapitulatif
        </Typography>
        <Grid container spacing={1}>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Prix du véhicule :
            </Typography>
          </Grid>
          <Grid item xs={6} textAlign="right">
            <Typography variant="body2">
              {vehiclePrice.toFixed(2)} €
            </Typography>
          </Grid>

          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Apport initial :
            </Typography>
          </Grid>
          <Grid item xs={6} textAlign="right">
            <Typography variant="body2">
              {downPayment.toFixed(2)} €
            </Typography>
          </Grid>

          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Capital à financer :
            </Typography>
          </Grid>
          <Grid item xs={6} textAlign="right">
            <Typography variant="body2">
              {capitalToFinance.toFixed(2)} €
            </Typography>
          </Grid>

          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Taux indicatif :
            </Typography>
          </Grid>
          <Grid item xs={6} textAlign="right">
            <Typography variant="body2">
              {(annualInterestRate * 100).toFixed(2)} %
            </Typography>
          </Grid>

          <Grid item xs={6} sx={{ mt: 1 }}>
            <Typography variant="subtitle2" fontWeight="bold">
              Mensualité estimée :
            </Typography>
          </Grid>
          <Grid item xs={6} textAlign="right" sx={{ mt: 1 }}>
            <Typography variant="subtitle2" fontWeight="bold" color="primary">
              {monthlyPayment.toFixed(2)} €
            </Typography>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
};