import React from "react";
import { Typography, useTheme } from "@mui/material";

export interface SpecLineProps {
  year?: number | string;
  mileage?: number;
  fuelType?: string;
  transmission?: string;
  power?: string | number;
  variant?: "body2" | "caption" | "body1";
}

export const SpecLine: React.FC<SpecLineProps> = ({
  year,
  mileage,
  fuelType,
  transmission,
  power,
  variant = "body2",
}) => {
  const theme = useTheme();

  const formattedMileage = mileage
    ? `${new Intl.NumberFormat("fr-FR").format(mileage)} km`
    : null;

  const parts = [
    year,
    formattedMileage,
    fuelType,
    transmission,
    power ? (typeof power === "number" ? `${power} ch` : power) : null,
  ].filter(Boolean);

  return (
    <Typography
      variant={variant}
      sx={{
        color: theme.palette.text.secondary,
        fontWeight: 500,
        display: "flex",
        alignItems: "center",
        flexWrap: "wrap",
        gap: 0.75,
      }}
    >
      {parts.join(" • ")}
    </Typography>
  );
};
