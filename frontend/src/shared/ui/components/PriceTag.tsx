import React from "react";
import { Typography, Box, useTheme } from "@mui/material";

export interface PriceTagProps {
  price: number;
  isMonthly?: boolean;
  variant?: "small" | "medium" | "large" | "hero";
  colorMode?: "achat" | "location" | "default";
}

export const formatPriceEUR = (amount: number): string => {
  return new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(amount);
};

export const PriceTag: React.FC<PriceTagProps> = ({
  price,
  isMonthly = false,
  variant = "medium",
  colorMode = "default",
}) => {
  const theme = useTheme();

  const formatted = formatPriceEUR(price);

  const getFontSize = () => {
    switch (variant) {
      case "small":
        return "1rem";
      case "large":
        return "1.5rem";
      case "hero":
        return "2.25rem";
      case "medium":
      default:
        return "1.25rem";
    }
  };

  const getColor = () => {
    if (colorMode === "achat") return theme.palette.accent?.achat || "#E82127";
    if (colorMode === "location") return theme.palette.accent?.location || "#3B82F6";
    return theme.palette.text.primary;
  };


  return (
    <Box component="span" sx={{ display: "inline-flex", alignItems: "baseline", gap: 0.5 }}>
      <Typography
        component="span"
        className="tabular-nums"
        sx={{
          fontSize: getFontSize(),
          fontWeight: 800,
          color: getColor(),
          lineHeight: 1.1,
          fontFeatureSettings: '"tnum"',
        }}
      >
        {formatted}
      </Typography>
      {isMonthly && (
        <Typography
          component="span"
          variant="caption"
          sx={{
            color: theme.palette.text.secondary,
            fontWeight: 600,
            fontSize: variant === "hero" ? "1rem" : "0.75rem",
          }}
        >
          /mois
        </Typography>
      )}
    </Box>
  );
};
