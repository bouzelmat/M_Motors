import React from "react";
import { Chip, useTheme } from "@mui/material";

export type DossierStatusType = "BROUILLON" | "SOUMIS" | "VALIDE" | "VALIDÉ" | "REJETE" | "REJETÉ";

export interface StatusBadgeProps {
  status: DossierStatusType;
  size?: "small" | "medium";
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = "small" }) => {
  const theme = useTheme();

  const getStatusConfig = (s: DossierStatusType) => {
    const normalized = s.toUpperCase();
    if (normalized === "BROUILLON") {
      return {
        label: "BROUILLON",
        bgColor: "rgba(17, 17, 19, 0.06)",
        color: theme.palette.text.primary,
        border: `1px solid ${theme.palette.border?.subtle || "rgba(17, 17, 19, 0.08)"}`,
      };
    }
    if (normalized === "SOUMIS") {
      return {
        label: "SOUMIS",
        bgColor: "rgba(59, 130, 246, 0.1)",
        color: "#1D4ED8", // WCAG AA Blue on light blue bg
        border: "1px solid rgba(59, 130, 246, 0.3)",
      };
    }
    if (normalized === "VALIDE" || normalized === "VALIDÉ") {
      return {
        label: "VALIDÉ",
        bgColor: "rgba(16, 185, 129, 0.1)",
        color: "#047857", // WCAG AA Green
        border: "1px solid rgba(16, 185, 129, 0.3)",
      };
    }
    return {
      label: "REJETÉ",
      bgColor: "rgba(239, 68, 68, 0.1)",
      color: "#B91C1C", // WCAG AA Red
      border: "1px solid rgba(239, 68, 68, 0.3)",
    };
  };

  const config = getStatusConfig(status);

  return (
    <Chip
      label={config.label}
      size={size}
      sx={{
        backgroundColor: config.bgColor,
        color: config.color,
        border: config.border,
        fontWeight: 700,
        fontSize: size === "small" ? "0.6875rem" : "0.75rem",
        letterSpacing: "0.05em",
      }}
    />
  );
};
