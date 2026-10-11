import React, { useState } from "react";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Divider,
  Grid,
  Paper,
  Stack,
  TextField,
  Typography,
  Chip,
  Skeleton,
  useTheme,
} from "@mui/material";
import { useNavigate, useParams } from "react-router-dom";

import { useVehicleDetailQuery } from "../../application/hooks/useVehicleDetailQuery";
import { ServiceOptionRow } from "../components/ServiceOptionRow";
import { SwitchCatalogTypeButton } from "../components/SwitchCatalogTypeButton";
import { useAuthStore } from "../../../auth/ui/hooks/useAuth";
import { useSubscriptionTunnelStore } from "../../application/stores/useSubscriptionTunnelStore";
import { getApiErrorMessage } from "../../../api/apiErrorMessage";
import { PriceTag } from "../../../shared/ui/components/PriceTag";
import { ModeBadge } from "../../../shared/ui/components/ModeBadge";

export const VehicleDetailPage: React.FC<{ vehicleIdOverride?: string }> = ({ vehicleIdOverride }) => {
  const { vehicleId } = useParams<{ vehicleId: string }>();
  const resolvedVehicleId = vehicleIdOverride ?? vehicleId ?? "";
  const navigate = useNavigate();
  const theme = useTheme();
  const { user } = useAuthStore();
  const setVehicle = useSubscriptionTunnelStore((state) => state.setVehicle);

  const { data: vehicle, isLoading, error } = useVehicleDetailQuery(resolvedVehicleId);

  const [selectedPhoto, setSelectedPhoto] = useState<string | null>(null);
  const [customPrice, setCustomPrice] = useState<string>("");

  if (isLoading) {
    return (
      <Container maxWidth="xl" sx={{ py: 6 }}>
        <Box data-testid="vehicle-detail-loading" sx={{ display: "flex", justifyContent: "center", py: 8 }}>
          <CircularProgress data-testid="loading-spinner" size={60} />
        </Box>
      </Container>
    );
  }

  if (error || !vehicle) {
    return (
      <Container maxWidth="xl" sx={{ py: 6 }}>
        <Alert data-testid="vehicle-detail-error" severity="error" sx={{ borderRadius: 16 }}>
          {getApiErrorMessage(error, "Impossible de charger ce véhicule.")}
        </Alert>
      </Container>
    );
  }

  const defaultTargetPrice =
    vehicle.catalog_type === "SALE"
      ? Number(vehicle.monthly_rent) || 399
      : Number(vehicle.price) || 15000;

  const effectivePrice = customPrice !== "" ? Number(customPrice) : defaultTargetPrice;

  const isAchat = vehicle.catalog_type === "SALE";
  const displayPrice = isAchat
    ? Number(vehicle.price || 25000)
    : Number(vehicle.monthly_rent || 349);

  const photos = [
    vehicle.photo_url || "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1560958089-b8a1929cea89?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1614162692292-7ac56d7f7f1e?auto=format&fit=crop&w=800&q=80",
  ];

  const currentMainPhoto = selectedPhoto || photos[0];
  const services = Array.isArray(vehicle.services) ? vehicle.services : [];

  const startPurchase = () => {
    setVehicle(vehicle.id, "sale");
    navigate(`/dossiers/new?simulationId=achat-${encodeURIComponent(vehicle.id)}&vehicleId=${encodeURIComponent(vehicle.id)}&mode=sale`);
  };

  const startRental = () => {
    setVehicle(vehicle.id, "rental");
    navigate(`/simulator?vehicleId=${encodeURIComponent(vehicle.id)}`);
  };

  return (
    <Box sx={{ pb: 4 }}>
      <Container maxWidth="xl" sx={{ pt: 4 }}>
        <Grid container spacing={5} alignItems="flex-start">
          {/* Left Column: Studio Photo Gallery */}
          <Grid item xs={12} md={7}>
            <Stack spacing={2}>
              <Box
                sx={{
                  backgroundColor: theme.palette.background?.studio || "#E9EBEE",
                  borderRadius: 20,
                  p: 3,
                  height: { xs: 320, sm: 440 },
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  position: "relative",
                  overflow: "hidden",
                  border: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}`,
                }}
              >
                <Box
                  component="img"
                  src={currentMainPhoto}
                  alt={`${vehicle.brand} ${vehicle.model}`}
                  sx={{
                    maxWidth: "100%",
                    maxHeight: "100%",
                    objectFit: "contain",
                    filter: "drop-shadow(0 20px 30px rgba(0, 0, 0, 0.15))",
                    transition: "transform 300ms ease-out",
                    "&:hover": {
                      transform: "scale(1.03)",
                    },
                  }}
                />
              </Box>

              {/* Thumbnails Row */}
              <Stack direction="row" spacing={2}>
                {photos.map((photo, i) => (
                  <Box
                    key={i}
                    onClick={() => setSelectedPhoto(photo)}
                    sx={{
                      width: 90,
                      height: 60,
                      borderRadius: 12,
                      backgroundColor: theme.palette.background?.studio || "#E9EBEE",
                      p: 0.5,
                      cursor: "pointer",
                      border: `2px solid ${photo === currentMainPhoto ? (isAchat ? (theme.palette.accent?.achat || "#E82127") : (theme.palette.accent?.location || "#3B82F6")) : "transparent"}`,
                      transition: "all 150ms ease-out",
                    }}
                  >
                    <Box
                      component="img"
                      src={photo}
                      alt={`Thumbnail ${i}`}
                      sx={{ width: "100%", height: "100%", objectFit: "cover", borderRadius: 8 }}
                    />
                  </Box>
                ))}
              </Stack>
            </Stack>
          </Grid>

          {/* Right Column: Title & Key Specs */}
          <Grid item xs={12} md={5}>
            <Stack spacing={3}>
              <Box>
                <Box sx={{ mb: 1 }}>
                  <ModeBadge mode={isAchat ? "ACHAT" : "LOCATION"} />
                </Box>
                <Typography variant="h4" component="h1" fontWeight={800} sx={{ lineHeight: 1.1 }}>
                  {vehicle.brand} {vehicle.model}
                </Typography>
                {vehicle.description && (
                  <Typography color="text.secondary" sx={{ mt: 1 }}>
                    {vehicle.description}
                  </Typography>
                )}
              </Box>

              {/* Price Highlight */}
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  borderRadius: 16,
                  backgroundColor: theme.palette.surface?.nested || "#F2F3F5",
                  border: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}`,
                }}
              >
                <Typography variant="caption" color="text.secondary" fontWeight={700}>
                  {isAchat ? "PRIX D'ACHAT COMPTANT" : "LOYER MENSUEL TOUT INCLUS"}
                </Typography>
                <Box sx={{ mt: 0.5 }}>
                  <PriceTag
                    price={displayPrice}
                    isMonthly={!isAchat}
                    variant="hero"
                    colorMode={isAchat ? "achat" : "location"}
                  />
                </Box>
              </Paper>

              {/* Tesla-style Specs Grid with fine borders */}
              <Box
                sx={{
                  display: "grid",
                  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                  gap: 0,
                  minWidth: 0,
                  p: 1.5,
                  borderRadius: 16,
                  border: `1px solid ${theme.palette.border?.strong || "rgba(17,17,19,0.16)"}`,
                  overflow: "hidden",
                }}
              >
                <Box sx={{ minWidth: 0, p: 1.5, borderRight: `1px solid ${theme.palette.border?.strong || "rgba(17,17,19,0.16)"}`, borderBottom: `1px solid ${theme.palette.border?.strong || "rgba(17,17,19,0.16)"}` }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={600}>ANNÉE</Typography>
                  <Typography variant="h5" fontWeight={800} className="tabular-nums" sx={{ mt: 0.5, fontSize: { xs: "1.1rem", sm: "1.5rem" }, overflowWrap: "anywhere" }}>{vehicle.year || 2023}</Typography>
                </Box>
                <Box sx={{ minWidth: 0, p: 1.5, borderBottom: `1px solid ${theme.palette.border?.strong || "rgba(17,17,19,0.16)"}` }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={600}>KILOMÉTRAGE</Typography>
                  <Typography variant="h5" fontWeight={800} className="tabular-nums" sx={{ mt: 0.5, fontSize: { xs: "1.1rem", sm: "1.5rem" }, overflowWrap: "anywhere" }}>
                    {new Intl.NumberFormat("fr-FR").format(vehicle.mileage || 15000)} km
                  </Typography>
                </Box>
                <Box sx={{ minWidth: 0, p: 1.5, borderRight: `1px solid ${theme.palette.border?.strong || "rgba(17,17,19,0.16)"}` }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={600}>ÉNERGIE</Typography>
                  <Typography variant="h5" fontWeight={800} sx={{ mt: 0.5, fontSize: { xs: "1.1rem", sm: "1.5rem" }, overflowWrap: "anywhere" }}>Énergie : {vehicle.energy_type || "ESSENCE"}</Typography>
                </Box>
                <Box sx={{ minWidth: 0, p: 1.5 }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={600}>TRANSMISSION</Typography>
                  <Typography variant="h5" fontWeight={800} sx={{ mt: 0.5, fontSize: { xs: "1.1rem", sm: "1.5rem" }, overflowWrap: "anywhere" }}>Automatique</Typography>
                </Box>
              </Box>

              {/* Action Buttons */}
              <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
                <Button variant="contained" onClick={startPurchase} sx={{ borderRadius: 999 }}>
                  Acheter
                </Button>
                <Button variant="outlined" onClick={startRental} sx={{ borderRadius: 999 }}>
                  Simuler en LLD
                </Button>
              </Stack>

              {/* Admin Switch Bar if applicable */}
              {user?.role === "ADMIN" && (
                <Paper elevation={0} sx={{ p: 2, borderRadius: 16, border: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}` }}>
                  <Stack spacing={1.5} alignItems="flex-end">
                    <TextField
                      label={isAchat ? "Nouveau Loyer (€/mois)" : "Nouveau Prix (€)"}
                      type="number"
                      size="small"
                      value={customPrice !== "" ? customPrice : defaultTargetPrice}
                      onChange={(e) => setCustomPrice(e.target.value)}
                      sx={{ width: 200 }}
                    />
                    <SwitchCatalogTypeButton
                      vehicleId={vehicle.id}
                      catalogType={vehicle.catalog_type}
                      newPrice={effectivePrice}
                    />
                  </Stack>
                </Paper>
              )}
            </Stack>
          </Grid>
        </Grid>

        {/* Included Services Section */}
        {!isAchat && (
          <Box sx={{ mt: 8 }}>
            <Typography variant="h5" component="h2" fontWeight={800} gutterBottom>
              Services disponibles
            </Typography>
            <Divider sx={{ mb: 3 }} />

            {services.length === 0 ? (
              <Typography variant="body1" color="text.secondary" sx={{ py: 2 }}>
                Aucun service disponible pour ce véhicule.
              </Typography>
            ) : (
              <Stack spacing={1.5}>
                {services.map((service) => (
                  <ServiceOptionRow key={service.id} service={service} />
                ))}
              </Stack>
            )}
          </Box>
        )}

        {isAchat && (
          <Box sx={{ mt: 8 }}>
            <Typography variant="h5" component="h2" fontWeight={800} gutterBottom>
              Services mensuels
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Alert
              severity="info"
              sx={{ mt: 2, alignItems: "center", borderRadius: 16 }}
              action={
                <Button color="inherit" size="small" onClick={() => navigate("/catalogue?mode=rental")}>
                  Voir les offres LLD
                </Button>
              }
            >
              Les services mensuels (assurance, entretien et assistance) sont proposés avec nos offres de location longue durée.
            </Alert>
          </Box>
        )}
      </Container>
    </Box>
  );
};