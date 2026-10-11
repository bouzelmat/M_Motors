import React, { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Grid,
  Paper,

  Stack,
  Typography,
  Stepper,
  Step,
  StepLabel,
  StepConnector,
  stepConnectorClasses,
  styled,
  StepIconProps,
  useTheme,
} from "@mui/material";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import CheckIcon from "@mui/icons-material/Check";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";
import DescriptionOutlinedIcon from "@mui/icons-material/DescriptionOutlined";
import CheckCircleOutlineIcon from "@mui/icons-material/CheckCircleOutline";
import { useNavigate, useSearchParams } from "react-router-dom";

import { DossiersClient } from "../../../api/clients/DossiersClient";
import { getApiErrorMessage } from "../../../api/apiErrorMessage";
import { useSubscriptionTunnelStore } from "../../../vehicles/application/stores/useSubscriptionTunnelStore";
import { useVehicleDetailQuery } from "../../../vehicles/application/hooks/useVehicleDetailQuery";
import { useCreateDossier, useSubmitDossier } from "../hooks/useDossierMutations";
import { DocumentUploader } from "../components/DocumentUploader";
import { FinancingSimulator } from "../../../vehicles/ui/components/FinancingSimulator";
import { TradeInForm } from "../components/TradeInForm";
import { PriceTag } from "../../../shared/ui/components/PriceTag";

// Custom Stepper Connector & Icons
const ColorConnector = styled(StepConnector)(({ theme }) => ({
  [`&.${stepConnectorClasses.alternativeLabel}`]: {
    top: 22,
  },
  [`&.${stepConnectorClasses.active}`]: {
    [`& .${stepConnectorClasses.line}`]: {
      borderColor: theme.palette.text.primary,
    },
  },
  [`&.${stepConnectorClasses.completed}`]: {
    [`& .${stepConnectorClasses.line}`]: {
      borderColor: theme.palette.text.primary,
    },
  },
  [`& .${stepConnectorClasses.line}`]: {
    borderColor: "rgba(17,17,19,0.12)",
    borderTopWidth: 2,
    borderRadius: 1,
  },
}));

const CustomStepIcon = (props: StepIconProps) => {
  const theme = useTheme();
  const { active, completed } = props;

  return (
    <Box
      sx={{
        width: 40,
        height: 40,
        borderRadius: 999,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: completed
          ? theme.palette.text.primary
          : active
          ? theme.palette.accent?.location || "#3B82F6"
          : theme.palette.surface?.nested || "#F2F3F5",

        color: completed || active ? "#FFFFFF" : theme.palette.text.disabled,
        fontWeight: 700,
        fontSize: "0.9rem",
        boxShadow: active ? "0 4px 12px rgba(59, 130, 246, 0.3)" : "none",
        transition: "all 200ms ease-out",
      }}
    >
      {completed ? <CheckIcon sx={{ fontSize: 20 }} /> : props.icon}
    </Box>
  );
};

const steps = [
  "Configuration & Offre",
  "Justificatifs",
  "Validation & Signature",
];

export const NewDossierPage = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const simulationId = searchParams.get("simulationId");
  const existingDossierId = searchParams.get("dossierId");
  const queryVehicleId = searchParams.get("vehicleId");
  const storedVehicleId = useSubscriptionTunnelStore((state) => state.vehicleId);
  const vehicleId = queryVehicleId ?? storedVehicleId;
  const vehicleQuery = useVehicleDetailQuery(vehicleId ?? "");
  const storedVehicleMode = useSubscriptionTunnelStore((state) => state.vehicleMode);
  const queryMode = searchParams.get("mode");
  const vehicleMode = queryMode === "sale" || queryMode === "rental" ? queryMode : storedVehicleMode;
  const financingPlan = useSubscriptionTunnelStore((state) => state.financingPlan);
  const tradeIn = useSubscriptionTunnelStore((state) => state.tradeIn);
  const resetTunnel = useSubscriptionTunnelStore((state) => state.resetTunnel);
  const [dossierId, setDossierId] = useState<string | null>(existingDossierId);
  const createDossierMutation = useCreateDossier();
  const submitDossierMutation = useSubmitDossier(dossierId ?? undefined);

  const activeStep = !dossierId ? 0 : 1;

  const mutationError = createDossierMutation.error ?? submitDossierMutation.error;
  const errorMessage = mutationError
    ? getApiErrorMessage(mutationError, "La demande n’a pas pu aboutir.")
    : null;

  useEffect(() => {
    if (!existingDossierId && (!simulationId || !vehicleId)) {
      navigate("/catalogue", { replace: true });
    }
  }, [existingDossierId, simulationId, vehicleId, navigate]);

  const documentsQuery = useQuery({
    queryKey: ["dossiers", dossierId, "documents"],
    queryFn: () => DossiersClient.getDocuments(dossierId!),
    enabled: Boolean(dossierId),
    retry: 1,
  });

  const uploadedCount = documentsQuery.data?.filter((doc) =>
    doc.status === "UPLOADED" || doc.status === "VALIDATED"
  ).length ?? 0;

  const createDossier = async () => {
    if (!vehicleId) return;
    try {
      const dossier = await createDossierMutation.mutateAsync({
        vehicle_id: vehicleId,
        trade_in: tradeIn
          ? {
              registration: tradeIn.registration,
              mileage: tradeIn.mileage,
              brand: tradeIn.brand || null,
              model: tradeIn.model || null,
            }
          : null,
        financing_plan: financingPlan
          ? {
              down_payment: financingPlan.down_payment,
              duration_months: financingPlan.duration_months,
              monthly_payment: financingPlan.monthly_payment,
            }
          : null,
      });
      setDossierId(dossier.id);
      setSearchParams(
        {
          simulationId: simulationId!,
          dossierId: dossier.id,
          ...(vehicleId ? { vehicleId } : {}),
          ...(vehicleMode ? { mode: vehicleMode } : {}),
        },
        { replace: true }
      );
    } catch {
      return;
    }
  };

  const submitDossier = async () => {
    if (!dossierId) return;
    try {
      await submitDossierMutation.mutateAsync();
      resetTunnel();
      navigate(`/account/dossiers/${dossierId}`);
    } catch {
      return;
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 6 }}>
      {/* Custom Stepper Header */}
      <Box sx={{ mb: 6, maxWidth: 800, mx: "auto" }}>
        {vehicleQuery.data && (
          <Typography variant="h5" component="h1" fontWeight={800} sx={{ mb: 3, textAlign: "center" }}>
            {vehicleMode === "sale"
              ? `Votre demande d’achat · ${vehicleQuery.data.brand} ${vehicleQuery.data.model}`
              : `Votre demande de location longue durée · ${vehicleQuery.data.brand} ${vehicleQuery.data.model}`}
          </Typography>
        )}
        <Stepper activeStep={activeStep} alternativeLabel connector={<ColorConnector />}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel StepIconComponent={CustomStepIcon}>
                <Typography variant="body2" fontWeight={700}>
                  {label}
                </Typography>
              </StepLabel>
            </Step>
          ))}
        </Stepper>
      </Box>

      {errorMessage && (
        <Alert severity="error" sx={{ mb: 4, borderRadius: 16 }}>
          {errorMessage}
        </Alert>
      )}

      {/* Main Grid: Form Steps + Sticky Summary */}
      <Grid container spacing={4}>
        <Grid item xs={12} md={7} lg={8}>
          {!dossierId ? (
            <Paper elevation={0} sx={{ p: { xs: 3, md: 4 }, borderRadius: 20, border: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}` }}>
              <Typography variant="h5" fontWeight={800} gutterBottom>
                Étape 1 : Configuration de votre dossier
              </Typography>
              <Typography color="text.secondary" sx={{ mb: 4 }}>
                Validez le plan de financement et l'éventuelle reprise de votre ancien véhicule.
              </Typography>

              {vehicleQuery.data && (
                <Stack spacing={4}>
                  <FinancingSimulator vehiclePrice={Number(vehicleQuery.data.price ?? 25000)} />
                  <TradeInForm />
                </Stack>
              )}

              <Box sx={{ mt: 4, display: "flex", justifyContent: "flex-end" }}>
                <Button
                  variant="contained"
                  size="large"
                  onClick={createDossier}
                  disabled={createDossierMutation.isPending || !vehicleId}
                  endIcon={<ArrowForwardIcon />}
                  sx={{ borderRadius: 999, px: 4 }}
                >
                  {createDossierMutation.isPending ? <CircularProgress size={22} color="inherit" /> : "Créer le dossier et déposer mes pièces"}
                </Button>
              </Box>
            </Paper>
          ) : (
            <Paper elevation={0} sx={{ p: { xs: 3, md: 4 }, borderRadius: 20, border: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}` }}>
              <Typography variant="h5" fontWeight={800} gutterBottom>
                Étape 2 : Dépôt des pièces justificatives
              </Typography>
              <Typography color="text.secondary" sx={{ mb: 3 }}>
                Téléversez vos documents (pièce d'identité, justificatif de domicile...). Moins de 10 Mo par fichier.
              </Typography>

              <DocumentUploader
                dossierId={dossierId}
                onUploadComplete={() => {
                  void documentsQuery.refetch();
                }}
              />

              {documentsQuery.isLoading ? (
                <Box sx={{ display: "flex", alignItems: "center", gap: 1, mt: 3 }}>
                  <CircularProgress size={18} />
                  <Typography variant="body2" color="text.secondary">
                    Vérification des pièces...
                  </Typography>
                </Box>
              ) : documentsQuery.isError ? (
                <Alert severity="warning" sx={{ mt: 2, borderRadius: 12 }}>
                  {getApiErrorMessage(documentsQuery.error, "Impossible de vérifier les pièces.")}
                </Alert>
              ) : documentsQuery.data && documentsQuery.data.length === 0 ? (
                <Alert severity="info" sx={{ mt: 2, borderRadius: 12 }}>
                  Aucune pièce téléversée.
                </Alert>
              ) : null}

              <Box sx={{ mt: 4, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <Typography variant="body2" fontWeight={700} color="text.secondary">
                  {uploadedCount} pièce{uploadedCount > 1 ? "s" : ""} validée{uploadedCount > 1 ? "s" : ""}
                </Typography>
                <Button
                  variant="contained"
                  size="large"
                  onClick={submitDossier}
                  disabled={documentsQuery.isLoading || submitDossierMutation.isPending || uploadedCount === 0}
                  endIcon={<ArrowForwardIcon />}
                  sx={{
                    borderRadius: 999,
                    px: 4,
                    backgroundColor: theme.palette.text.primary,
                  }}
                >
                  {submitDossierMutation.isPending ? <CircularProgress size={22} color="inherit" /> : "Soumettre mon dossier"}
                </Button>
              </Box>
            </Paper>
          )}
        </Grid>

        {/* Right Sticky Summary Card */}
        <Grid item xs={12} md={5} lg={4}>
          <Paper
            elevation={0}
            sx={{
              p: 3,
              borderRadius: 20,
              backgroundColor: theme.palette.background.paper,
              border: `1px solid ${theme.palette.border?.strong || "rgba(17,17,19,0.16)"}`,
              position: "sticky",
              top: 88,
            }}
          >
            <Typography variant="h6" fontWeight={800} gutterBottom>
              Récapitulatif de l'offre
            </Typography>

            {vehicleQuery.data && (
              <Stack spacing={2} sx={{ my: 2 }}>
                <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                  <Box
                    component="img"
                    src={vehicleQuery.data.photo_url || "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=400&q=80"}
                    alt={vehicleQuery.data.model}
                    sx={{ width: 80, height: 50, objectFit: "cover", borderRadius: 12, backgroundColor: theme.palette.background?.studio || "#E9EBEE" }}
                  />
                  <Box>
                    <Typography variant="caption" color="text.secondary" fontWeight={700}>
                      {vehicleQuery.data.brand}
                    </Typography>
                    <Typography variant="subtitle2" fontWeight={800}>
                      {vehicleQuery.data.brand} {vehicleQuery.data.model}
                    </Typography>
                  </Box>
                </Box>

                <Box sx={{ p: 2, borderRadius: 12, backgroundColor: theme.palette.surface?.nested || "#F2F3F5" }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={700}>
                    {vehicleMode === "sale" ? "PRIX TOTAL" : "LOYER ESTIMÉ"}
                  </Typography>
                  <Box sx={{ mt: 0.5 }}>
                    <PriceTag
                      price={financingPlan?.monthly_payment || (vehicleMode === "sale" ? Number(vehicleQuery.data.price || 25000) : Number(vehicleQuery.data.monthly_rent || 349))}
                      isMonthly={vehicleMode !== "sale"}
                      variant="large"
                      colorMode={vehicleMode === "sale" ? "achat" : "location"}
                    />
                  </Box>
                </Box>

                {financingPlan && (
                  <Stack spacing={0.5} sx={{ pt: 1, borderTop: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}` }}>

                    <Typography variant="caption" color="text.secondary">
                      Durée : <span className="tabular-nums">{financingPlan.duration_months} mois</span>
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Apport initial : <span className="tabular-nums">{financingPlan.down_payment} €</span>
                    </Typography>
                  </Stack>
                )}
              </Stack>
            )}

            <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 3, pt: 2, borderTop: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}` }}>

              <CheckCircleOutlineIcon sx={{ color: theme.palette.success.main, fontSize: 18 }} />
              <Typography variant="caption" color="text.secondary" fontWeight={600}>
                Étude gratuite et réponse sous 24h ouvrées.
              </Typography>
            </Stack>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};