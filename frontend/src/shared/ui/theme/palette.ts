import { PaletteOptions } from "@mui/material/styles";
import "./types";

export const palette: PaletteOptions = {
  mode: "light",
  primary: {
    main: "#111113",
    light: "#2B2B30",
    dark: "#080809",
    contrastText: "#FFFFFF",
  },
  secondary: {
    main: "#3B82F6",
    light: "#60A5FA",
    dark: "#2563EB",
    contrastText: "#FFFFFF",
  },
  error: {
    main: "#EF4444",
    light: "#F87171",
    dark: "#DC2626",
  },
  warning: {
    main: "#F59E0B",
  },
  success: {
    main: "#10B981",
  },
  background: {
    default: "#FFFFFF",
    paper: "#FFFFFF",
    alternate: "#F6F7F8",
    studio: "#E9EBEE",
  },
  surface: {
    card: "#FFFFFF",
    nested: "#F2F3F5",
  },
  border: {
    subtle: "rgba(17, 17, 19, 0.08)",
    strong: "rgba(17, 17, 19, 0.16)",
  },
  text: {
    primary: "#111113",
    secondary: "rgba(17, 17, 19, 0.60)",
    disabled: "rgba(17, 17, 19, 0.38)",
  },
  accent: {
    achat: "#E82127",
    location: "#3B82F6",
  },
  glass: {
    bg: "rgba(255, 255, 255, 0.70)",
  },
  divider: "rgba(17, 17, 19, 0.08)",
};
