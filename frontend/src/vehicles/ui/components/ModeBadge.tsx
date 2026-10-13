import React from "react";
import { Chip, useTheme } from "@mui/material";

export type ModeBadgeType = "ACHAT" | "LOCATION";

export interface ModeBadgeProps {
  mode: ModeBadgeType;
  size?: "small" | "medium";
}

export const ModeBadge: React.FC<ModeBadgeProps> = ({ mode, size = "small" }) => {
  const theme = useTheme();
  const isAchat = mode === "ACHAT";
  const accentAchat = theme.palette.accent?.achat || "#E82127";
  const accentLocation = theme.palette.accent?.location || "#3B82F6";
  const color = isAchat ? accentAchat : accentLocation;
  const label = isAchat ? "ACHAT" : "LOCATION LLD";

  return (
    <Chip
      label={label}
      size={size}
      sx={{
        backgroundColor: isAchat ? "rgba(232, 33, 39, 0.08)" : "rgba(59, 130, 246, 0.08)",
        color: color,
        border: `1px solid ${isAchat ? "rgba(232, 33, 39, 0.2)" : "rgba(59, 130, 246, 0.2)"}`,
        fontWeight: 700,
        fontSize: size === "small" ? "0.6875rem" : "0.75rem",
        letterSpacing: "0.05em",
      }}
    />
  );

};
