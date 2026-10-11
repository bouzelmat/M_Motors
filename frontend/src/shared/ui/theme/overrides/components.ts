import { Components, Theme } from "@mui/material/styles";

export const componentsOverride = (theme: Theme): Components<Omit<Theme, "components">> => ({
  MuiCssBaseline: {
    styleOverrides: {
      "*": {
        boxSizing: "border-box",
      },
      html: {
        scrollBehavior: "smooth",
      },
      body: {
        backgroundColor: theme.palette.background.default,
        color: theme.palette.text.primary,
        fontFamily: theme.typography.fontFamily,
        WebkitFontSmoothing: "antialiased",
        MozOsxFontSmoothing: "grayscale",
      },
      "@media (prefers-reduced-motion: reduce)": {
        "*, ::before, ::after": {
          animationDuration: "0.01ms !important",
          animationIterationCount: "1 !important",
          transitionDuration: "0.01ms !important",
          scrollBehavior: "auto !important",
        },
      },
      ".tabular-nums": {
        fontVariantNumeric: "tabular-nums",
      },
    },
  },
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: 999,
        fontWeight: 600,
        textTransform: "none",
        padding: "10px 24px",
        boxShadow: "none",
        transition: "all 150ms ease-out",
        "&:hover": {
          boxShadow: "0 4px 12px rgba(17, 17, 19, 0.12)",
          transform: "translateY(-1px)",
        },
        "&:focus-visible": {
          outline: `2px solid ${theme.palette.text.primary}`,
          outlineOffset: 2,
        },
      },
      containedPrimary: {
        backgroundColor: theme.palette.text.primary,
        color: "#FFFFFF",
        "&:hover": {
          backgroundColor: "#2B2B30",
        },
      },
      containedSecondary: {
        backgroundColor: theme.palette.accent.location,
        color: "#FFFFFF",
        "&:hover": {
          backgroundColor: "#2563EB",
        },
      },
      outlined: {
        borderColor: theme.palette.border.strong,
        color: theme.palette.text.primary,
        "&:hover": {
          borderColor: theme.palette.text.primary,
          backgroundColor: "rgba(17, 17, 19, 0.04)",
        },
      },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: 20,
        border: `1px solid ${theme.palette.border.subtle}`,
        backgroundColor: theme.palette.background.paper,
        boxShadow: "0 2px 8px rgba(17, 17, 19, 0.04)",
        transition: "all 200ms cubic-bezier(0.4, 0, 0.2, 1)",
        overflow: "hidden",
      },
    },
  },
  MuiTextField: {
    defaultProps: {
      variant: "outlined",
      size: "medium",
    },
  },
  MuiOutlinedInput: {
    styleOverrides: {
      root: {
        borderRadius: 12,
        backgroundColor: theme.palette.surface.nested,
        transition: "all 150ms ease-out",
        "& fieldset": {
          borderColor: theme.palette.border.subtle,
        },
        "&:hover fieldset": {
          borderColor: theme.palette.border.strong,
        },
        "&.Mui-focused fieldset": {
          borderColor: theme.palette.text.primary,
          borderWidth: 1.5,
        },
      },
      input: {
        padding: "14px 16px",
      },
    },
  },
  MuiChip: {
    styleOverrides: {
      root: {
        borderRadius: 999,
        fontWeight: 600,
      },
    },
  },
  MuiPaper: {
    styleOverrides: {
      rounded: {
        borderRadius: 20,
      },
      elevation1: {
        boxShadow: "0 4px 20px rgba(17, 17, 19, 0.06)",
      },
    },
  },
  MuiDialog: {
    styleOverrides: {
      paper: {
        borderRadius: 24,
        boxShadow: "0 24px 48px rgba(17, 17, 19, 0.16)",
      },
    },
  },
  MuiSkeleton: {
    styleOverrides: {
      root: {
        backgroundColor: "rgba(17, 17, 19, 0.06)",
        borderRadius: 8,
      },
    },
  },
});
