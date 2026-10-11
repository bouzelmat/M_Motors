import React from "react";
import { Box, Container, Grid, Typography, Stack, useTheme } from "@mui/material";

const stats = [
  { value: "2 500+", label: "Véhicules Livrés" },
  { value: "98.4%", label: "Satisfaction Clients" },
  { value: "100%", label: "Garantie Constructeur" },
  { value: "< 7 j", label: "Délai Moyen de Livraison" },
];

export const ReassuranceSection: React.FC = () => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        py: { xs: 8, md: 10 },
        backgroundColor: theme.palette.background.alternate,
        borderTop: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}`,
        borderBottom: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}`,

      }}
    >
      <Container maxWidth="xl">
        <Grid container spacing={4} justifyContent="center" alignItems="center">
          {stats.map((stat) => (
            <Grid item xs={6} sm={3} key={stat.label}>
              <Stack spacing={1} textAlign="center">
                <Typography
                  variant="h2"
                  className="tabular-nums"
                  sx={{
                    fontSize: { xs: "2.25rem", md: "3.5rem" },
                    fontWeight: 900,
                    color: theme.palette.text.primary,
                    lineHeight: 1,
                    letterSpacing: "-0.02em",
                  }}
                >
                  {stat.value}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    color: theme.palette.text.secondary,
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                    fontSize: "0.8rem",
                  }}
                >
                  {stat.label}
                </Typography>
              </Stack>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
};
