import React from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  Paper,
  Stack,
  Chip,
  useTheme,
} from "@mui/material";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import { useAuthStore } from "../../../auth/ui/hooks/useAuth";
import { useDossiers } from "../hooks/useDossiers";
import { getApiErrorMessage } from "../../../api/apiErrorMessage";
import { StatusBadge } from "../../../shared/ui/components/StatusBadge";
import { DossierTimeline } from "../components/DossierTimeline";
import { DOCUMENT_TYPE_LABELS } from "../components/DocumentUploader";

const dossierStatusLabels: Record<string, string> = {
  DRAFT: "BROUILLON",
  SUBMITTED: "SOUMIS",
  VALIDATED: "VALIDÉ",
  REJECTED: "REJETÉ",
  EXPIRED: "EXPIRÉ",
  CANCELLED: "ANNULÉ",
  DOCUMENTS_PENDING: "SOUMIS",
};

export function DossiersPage() {
  const navigate = useNavigate();
  const theme = useTheme();
  const { user, isAuthenticated, logout } = useAuthStore();
  const dossiersQuery = useDossiers();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (!isAuthenticated || !user) {
    return null;
  }

  const dossiers = dossiersQuery.data ?? [];

  const activeDossiers = dossiers.filter((dossier) =>
    ["DRAFT", "SUBMITTED", "DOCUMENTS_PENDING"].includes(dossier.status)
  ).length;

  const decidedDossiers = dossiers.length - activeDossiers;
  const primaryDossier =
    dossiers.find((dossier) => dossier.status === "DOCUMENTS_PENDING") ??
    dossiers.find((dossier) => ["DRAFT", "SUBMITTED"].includes(dossier.status)) ??
    dossiers[0];

  const metricValue = (value: number) => (dossiersQuery.isLoading ? "…" : value);

  return (
    <Container maxWidth="xl" sx={{ py: { xs: 4, md: 6 }, mb: 4 }}>
      {/* Banner Header */}
      <Paper
        elevation={0}
        sx={{
          p: { xs: 3, md: 4 },
          mb: 4,
          color: theme.palette.text.primary,
          backgroundColor: theme.palette.background.paper,
          border: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}`,
          borderRadius: 20,
        }}
      >
        <Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" alignItems={{ xs: "flex-start", sm: "center" }} spacing={2}>
          <Box>
            <Chip label="ESPACE CLIENT" size="small" sx={{ mb: 1.5, fontWeight: 800, backgroundColor: theme.palette.surface?.nested || "#F2F3F5" }} />
            <Typography variant="h3" component="h1" fontWeight={800}>
              Bonjour, {user.first_name}
            </Typography>
            <Typography color="text.secondary" sx={{ mt: 0.5 }}>
              Suivez l'avancement de vos demandes et gérez vos justificatifs en toute sérénité.
            </Typography>
          </Box>
          <Button variant="outlined" onClick={handleLogout} sx={{ borderRadius: 999 }}>
            Déconnexion
          </Button>
        </Stack>
      </Paper>

      {/* Metrics Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {[
          { label: "Mes demandes", value: metricValue(dossiers.length) },
          { label: "En cours d'étude", value: metricValue(activeDossiers) },
          { label: "Décisions rendues", value: metricValue(decidedDossiers) },
        ].map((metric) => (
          <Grid item xs={12} sm={4} key={metric.label}>
            <Paper
              elevation={0}
              sx={{
                p: 3,
                borderRadius: 20,
                backgroundColor: theme.palette.background.paper,
                border: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}`,
              }}
            >
              <Typography variant="h3" fontWeight={900} className="tabular-nums" sx={{ color: theme.palette.text.primary }}>
                {metric.value}
              </Typography>
              <Typography variant="body2" color="text.secondary" fontWeight={600} sx={{ textTransform: "uppercase", letterSpacing: "0.05em", mt: 0.5 }}>
                {metric.label}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* Timeline & Active Dossiers List */}
      <Paper elevation={0} sx={{ p: { xs: 3, md: 4 }, borderRadius: 20, border: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}`, mb: 4 }}>
        <Typography variant="h5" component="h2" fontWeight={800} gutterBottom>
          Suivi de mon dossier principal
        </Typography>

        {primaryDossier ? (
          <Box>
            <Typography variant="h6" fontWeight={800} sx={{ mb: 2 }}>
              Dossier de financement
            </Typography>
            <DossierTimeline status={primaryDossier.status} />

            {primaryDossier.status === "DOCUMENTS_PENDING" && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                <Typography fontWeight={700}>Pièces complémentaires demandées</Typography>
                <Typography variant="body2" sx={{ mt: 0.5 }}>
                  {primaryDossier.requested_document_types?.length
                    ? primaryDossier.requested_document_types
                        .map((type) => DOCUMENT_TYPE_LABELS[type])
                        .join(", ")
                    : "Consultez votre dossier pour voir les pièces à transmettre."}
                </Typography>
              </Alert>
            )}

            <Box sx={{ mt: 4, pt: 3, borderTop: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}` }}>

              <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 2 }}>
                <Box>
                  <Typography variant="subtitle1" fontWeight={800}>
                    Demande de financement #{primaryDossier.id.slice(0, 8)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Mis à jour le {new Date(primaryDossier.updated_at).toLocaleDateString("fr-FR")}
                  </Typography>
                </Box>
                <Button variant="contained" endIcon={<ArrowForwardIcon />} onClick={() => navigate(`/account/dossiers/${primaryDossier.id}`)} sx={{ borderRadius: 999 }}>
                  {primaryDossier.status === "DOCUMENTS_PENDING" ? "Transmettre les pièces" : "Consulter mon dossier"}
                </Button>
              </Box>
            </Box>
          </Box>
        ) : (
          <Box sx={{ py: 4, textAlign: "center" }}>
            <Typography variant="h6" fontWeight={700} gutterBottom>
              Vous trouverez ici le suivi de vos demandes.
            </Typography>
            <Typography color="text.secondary" sx={{ mb: 3, maxWidth: 480, mx: "auto" }}>
              Retrouvez votre dossier en cours et les échanges associés à votre réservation.
            </Typography>
            <Stack direction="row" spacing={2} justifyContent="center">
              <Button variant="contained" onClick={() => navigate("/catalogue?mode=rental")} sx={{ borderRadius: 999 }}>
                Offres LLD
              </Button>
            </Stack>
          </Box>
        )}
      </Paper>

      <Paper
        elevation={0}
        sx={{
          p: { xs: 3, md: 4 },
          borderRadius: 20,
          border: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}`,
        }}
      >
        <Typography variant="h5" component="h2" fontWeight={800} gutterBottom>
          Historique de mes dossiers
        </Typography>
        <Typography color="text.secondary" sx={{ mb: 2 }}>
          Retrouvez vos dossiers, y compris ceux dont le traitement est terminé.
        </Typography>
        {dossiers.length > 0 ? (
          <List disablePadding>
            {dossiers.map((dossier, index) => (
              <ListItem
                key={dossier.id}
                divider={index < dossiers.length - 1}
                secondaryAction={
                  <Button
                    size="small"
                    onClick={() => navigate(`/account/dossiers/${dossier.id}`)}
                    aria-label={`Consulter le dossier ${dossier.id.slice(0, 8)}`}
                  >
                    Consulter
                  </Button>
                }
                sx={{ py: 1.5, pr: 12 }}
              >
                <ListItemText
                  primary={`Dossier de financement #${dossier.id.slice(0, 8)} — ${dossierStatusLabels[dossier.status] ?? dossier.status}`}
                  secondary={`Mis à jour le ${new Date(dossier.updated_at).toLocaleDateString("fr-FR")}`}
                />
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography color="text.secondary">Aucun dossier à afficher.</Typography>
        )}
      </Paper>
    </Container>
  );
}