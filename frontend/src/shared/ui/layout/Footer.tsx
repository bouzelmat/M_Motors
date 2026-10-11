import React from "react";
import { Box, Container, Grid, Typography, Link as MuiLink, Stack, useTheme } from "@mui/material";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import { Link } from "react-router-dom";

export const Footer: React.FC = () => {
  const theme = useTheme();

  return (
    <Box
      component="footer"
      sx={{
        backgroundColor: theme.palette.background.default,
        borderTop: `1px solid ${theme.palette.border?.subtle || "rgba(17, 17, 19, 0.08)"}`,
        pt: 8,
        pb: 6,
        color: theme.palette.text.primary,
      }}
    >

      <Container maxWidth="xl">
        <Grid container spacing={4} sx={{ mb: 6 }}>
          {/* Column 1: Brand */}
          <Grid item xs={12} md={4}>
            <Stack spacing={2}>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1.25 }}>
                <Box
                  sx={{
                    width: 36,
                    height: 36,
                    borderRadius: 999,
                    backgroundColor: theme.palette.text.primary,
                    color: "#FFFFFF",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <DirectionsCarIcon sx={{ fontSize: 20 }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 900, letterSpacing: "-0.03em" }}>
                  M-MOTORS
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ color: theme.palette.text.secondary, maxWidth: 320 }}>
                La plateforme automobile nouvelle génération. Achat comptant ou Location Longue Durée (LLD) en toute transparence.
              </Typography>
            </Stack>
          </Grid>

          {/* Column 2: Navigation */}
          <Grid item xs={6} sm={4} md={2.5}>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, color: theme.palette.text.primary }}>
              OFFRES
            </Typography>
            <Stack spacing={1}>
              <MuiLink component={Link} to="/catalogue" color="text.secondary" underline="hover" variant="body2">
                Tous les véhicules
              </MuiLink>
              <MuiLink component={Link} to="/catalogue?mode=LOCATION" color="text.secondary" underline="hover" variant="body2">
                Offres LLD
              </MuiLink>
              <MuiLink component={Link} to="/catalogue?mode=ACHAT" color="text.secondary" underline="hover" variant="body2">
                Véhicules d'occasion
              </MuiLink>
              <MuiLink component={Link} to="/simulator" color="text.secondary" underline="hover" variant="body2">
                Simulateur de financement
              </MuiLink>
            </Stack>
          </Grid>

          {/* Column 3: Services */}
          <Grid item xs={6} sm={4} md={2.5}>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, color: theme.palette.text.primary }}>
              SERVICES
            </Typography>
            <Stack spacing={1}>
              <MuiLink component={Link} to="/dashboard" color="text.secondary" underline="hover" variant="body2">
                Suivi de dossier
              </MuiLink>
              <MuiLink component={Link} to="/login" color="text.secondary" underline="hover" variant="body2">
                Espace Client
              </MuiLink>
              <MuiLink component={Link} to="/admin/dossiers" color="text.secondary" underline="hover" variant="body2">
                Espace Pro
              </MuiLink>
            </Stack>
          </Grid>

          {/* Column 4: Legals */}
          <Grid item xs={12} sm={4} md={3}>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, color: theme.palette.text.primary }}>
              ENGAGEMENTS
            </Typography>
            <Typography variant="caption" sx={{ color: theme.palette.text.secondary, display: "block", mb: 1 }}>
              Véhicules révisés, garantis et livrés partout en France.
            </Typography>
            <Typography variant="caption" sx={{ color: theme.palette.text.secondary, display: "block" }}>
              © {new Date().getFullYear()} M-MOTORS. Tous droits réservés.
            </Typography>
          </Grid>
        </Grid>

        <Box
          sx={{
            pt: 4,
            borderTop: `1px solid ${theme.palette.border?.subtle || "rgba(17, 17, 19, 0.08)"}`,
            display: "flex",
            flexDirection: { xs: "column", sm: "row" },
            alignItems: "center",
            justifyContent: "space-between",
            gap: 2,
          }}
        >

          <Typography variant="caption" color="text.secondary">
            M-MOTORS Design System Light v1.1 • WCAG 2.1 AA Compliant
          </Typography>
          <Stack direction="row" spacing={3}>
            <MuiLink color="text.secondary" variant="caption" underline="hover">
              Mentions légales
            </MuiLink>
            <MuiLink color="text.secondary" variant="caption" underline="hover">
              Confidentialité
            </MuiLink>
            <MuiLink color="text.secondary" variant="caption" underline="hover">
              Cookies
            </MuiLink>
          </Stack>
        </Box>
      </Container>
    </Box>
  );
};
