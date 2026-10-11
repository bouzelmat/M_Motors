import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
    Container,
    Typography,
    Box,
    Paper,
    Grid,
    Chip,
    CircularProgress,
    Alert,
    Button,
    List,
    ListItem,
    ListItemText,
    Divider,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import { useDossierDetail } from "../hooks/useDossierDetail"; // Assure-toi que ce hook existe ou utilise DossiersClient directement
import { getApiErrorMessage } from "../../../api/apiErrorMessage";
import { DossiersClient } from "../../../api/clients/DossiersClient";
import { DossierActionBar } from "../components/DossierActionBar";
import { FinancialSummaryPanel } from "../components/FinancialSummaryPanel";

// Hook placeholder si tu ne l'as pas encore, adapte-le à DossiersClient.getDossierDetail

export const AdminDossierDetailPage: React.FC = () => {
    const { dossierId } = useParams<{ dossierId: string }>();
    const navigate = useNavigate();

    const { data: dossier, isLoading, isError, error } = useDossierDetail(dossierId);

    const handleViewDocument = async (documentId: string) => {
        if (!dossierId) {
            alert("Impossible d'identifier le dossier associé à ce document.");
            return;
        }

        try {
            const response = await DossiersClient.getDocumentViewUrl(dossierId, documentId);
            window.open(response.url, "_blank", "noopener,noreferrer");
        } catch (error: unknown) {
            alert(getApiErrorMessage(error, "Impossible d'obtenir l'URL d'accès au document."));
        }
    };

    if (isLoading) {
        return (
            <Box sx={{ display: "flex", justifyContent: "center", mt: 8 }}>
                <CircularProgress />
            </Box>
        );
    }

    if (isError || !dossier) {
        return (
            <Container maxWidth="md" sx={{ mt: 4 }}>
                <Alert severity="error">
                    {getApiErrorMessage(error, "Le dossier demandé est introuvable.")}
                </Alert>
                <Button startIcon={<ArrowBackIcon />} onClick={() => navigate("/admin/dossiers")} sx={{ mt: 2 }}>
                    Retour à la liste
                </Button>
            </Container>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Button startIcon={<ArrowBackIcon />} onClick={() => navigate("/admin/dossiers")} sx={{ mb: 2 }}>
                Retour à la liste
            </Button>

            <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h5" gutterBottom>
                    Dossier N° {dossier.id}
                </Typography>
                <Grid container spacing={2} sx={{ mt: 1 }}>
                    <Grid item xs={12} sm={4}>
                        <Typography variant="caption" color="text.secondary">Client</Typography>
                        <Typography variant="body1">{dossier.client_email}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <Typography variant="caption" color="text.secondary">Véhicule</Typography>
                        <Typography variant="body1">{`${dossier.vehicle_brand} ${dossier.vehicle_model}`}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <Typography variant="caption" color="text.secondary">Statut</Typography>
                        <Box sx={{ mt: 0.5 }}>
                            <Chip 
                                label={dossier.status} 
                                color={dossier.status === "VALIDATED" ? "success" : dossier.status === "REJECTED" ? "error" : "primary"} 
                                size="small" 
                            />
                        </Box>
                    </Grid>
                </Grid>

                {/* Affichage des informations d'administration si présentes */}
                {dossier.status === "VALIDATED" && dossier.comment && (
                    <Box sx={{ mt: 3, p: 2, bgcolor: "success.light", borderRadius: 1 }}>
                        <Typography variant="subtitle2" color="success.dark">Commentaire de validation :</Typography>
                        <Typography variant="body2">{dossier.comment}</Typography>
                    </Box>
                )}

                {dossier.status === "REJECTED" && dossier.rejection_reason && (
                    <Box sx={{ mt: 3, p: 2, bgcolor: "error.light", borderRadius: 1 }}>
                        <Typography variant="subtitle2" color="error.dark">Motif du rejet :</Typography>
                        <Typography variant="body2">{dossier.rejection_reason}</Typography>
                    </Box>
                )}

                {dossier.status === "DOCUMENTS_PENDING" && dossier.requested_document_types && dossier.requested_document_types.length > 0 && (
                    <Box sx={{ mt: 3, p: 2, bgcolor: "warning.light", borderRadius: 1 }}>
                        <Typography variant="subtitle2" color="warning.dark">Documents en attente :</Typography>
                        <Typography variant="body2">{dossier.requested_document_types.join(", ")}</Typography>
                    </Box>
                )}
            </Paper>

            {/* Synthèse financière */}
            <FinancialSummaryPanel dossier={dossier} />

            {/* Barre d'actions d'administration */}
            {dossierId && <DossierActionBar dossierId={dossierId} status={dossier.status} />}

            <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
                Documents déposés
            </Typography>

            {dossier.documents.length === 0 ? (
                <Alert severity="info">Aucun document transmis pour ce dossier.</Alert>
            ) : (
                <Paper variant="outlined">
                    <List disablePadding>
                        {dossier.documents.map((doc, index) => (
                            <React.Fragment key={doc.id}>
                                {index > 0 && <Divider />}
                                <ListItem
                                    secondaryAction={
                                        <Button
                                            size="small"
                                            endIcon={<OpenInNewIcon />}
                                            onClick={() => handleViewDocument(doc.id)}
                                        >
                                            Consulter
                                        </Button>
                                    }
                                >
                                    <ListItemText
                                        primary={doc.original_filename}
                                        secondary={`Type: ${doc.type} | Statut: ${doc.status}`}
                                    />
                                </ListItem>
                            </React.Fragment>
                        ))}
                    </List>
                </Paper>
            )}
        </Container>
    );
};