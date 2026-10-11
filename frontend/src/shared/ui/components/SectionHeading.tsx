import React from "react";
import { Stack, Typography, useTheme } from "@mui/material";

export interface SectionHeadingProps {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  align?: "left" | "center" | "right";
}

export const SectionHeading: React.FC<SectionHeadingProps> = ({
  eyebrow,
  title,
  subtitle,
  align = "left",
}) => {
  const theme = useTheme();

  return (
    <Stack spacing={1} textAlign={align} sx={{ maxWidth: align === "center" ? 720 : "none", mx: align === "center" ? "auto" : 0 }}>
      {eyebrow && (
        <Typography
          variant="overline"
          sx={{
            color: theme.palette.accent?.achat || "#E82127",
            fontWeight: 800,
            letterSpacing: "0.12em",
          }}
        >

          {eyebrow}
        </Typography>
      )}
      <Typography variant="h2" component="h2" sx={{ color: theme.palette.text.primary, fontWeight: 800 }}>
        {title}
      </Typography>
      {subtitle && (
        <Typography variant="subtitle1" sx={{ color: theme.palette.text.secondary }}>
          {subtitle}
        </Typography>
      )}
    </Stack>
  );
};
