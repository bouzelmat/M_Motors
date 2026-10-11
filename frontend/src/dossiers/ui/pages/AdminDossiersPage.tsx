import React, { useState } from "react";
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Paper,
  Button,
  Chip,
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  List,
  ListItem,
  ListItemText,
  useTheme,
} from "@mui/material";
import VisibilityIcon from "@mui/icons-material/Visibility";
import ReplayIcon from "@mui/icons-material/Replay";
import { useNavigate } from "react-router-dom";
import { usePendingDossiers } from "../hooks/usePendingDossiers";
import { useDossierHistory } from "../hooks/useDossierHistory";
import { getApiErrorMessage } from "../../../api/apiErrorMessage";

const STATUS_LABELS: Record<string, string> = {
  SUBMITTED: "En cours d’étude",
  DOCUMENTS_PENDING: "Pièces complémentaires",
  DRAFT: "Brouillon",
  VALIDATED: "Validé",
  REJECTED: "Refusé",
  EXPIRED: "Expiré",
  CANCELLED: "Annulé",
};

export const AdminDossiersPage: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const [sortBy] = useState<string>("submitted_at");
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const { data: dossiers, isLoading, isError, error, refetch } = usePendingDossiers(sortBy);
  const historyQuery = useDossierHistory();

  const rows = (dossiers ?? []).map((dossier) => ({
    ...dossier,
    client: dossier.client_email ?? "Client Inconnu",
    vehicle: `${dossier.vehicle_brand || ""} ${dossier.vehicle_model || ""}`.trim() || "Non spécifié",
  }));

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4 }}>
        <Box>
          <Chip label="BACK-OFFICE ADMIN" size="small" sx={{ mb: 1, fontWeight: 800, backgroundColor: theme.palette.text.primary, color: "#FFFFFF" }} />
          <Typography variant="h3" fontWeight={800}>
            Gestion des Dossiers
          </Typography>
        </Box>
        <Button variant="outlined" startIcon={<ReplayIcon />} onClick={() => refetch()} sx={{ borderRadius: 999 }}>
          Actualiser
        </Button>
      </Box>

      {isError && (
        <Alert severity="error" sx={{ mb: 3, borderRadius: 16 }}>
          {getApiErrorMessage(error, "Une erreur est survenue lors du chargement des dossiers.")}
        </Alert>
      )}

      {isLoading && (
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, py: 2 }}>
          <CircularProgress size={18} />
          <Typography variant="body2" color="text.secondary">Chargement...</Typography>
        </Box>
      )}

      {!isLoading && !isError && dossiers && dossiers.length === 0 && (
        <Box sx={{ py: 6, textAlign: "center" }}>
          <Typography variant="h6" fontWeight={800}>Aucun dossier en attente pour le moment.</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Le bureau est serein pour le moment.
          </Typography>
        </Box>
      )}

      {!isLoading && !isError && dossiers && dossiers.length > 0 && (
        <Paper
          elevation={0}
          sx={{
            width: "100%",
            minWidth: 0,
            borderRadius: 3,
            border: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}`,
            backgroundColor: theme.palette.background.paper,
          }}
        >
          <TableContainer
            role="region"
            aria-label="Tableau des dossiers défilant horizontalement"
            tabIndex={0}
            sx={{
              display: "block",
              width: "100%",
              maxWidth: "100%",
              overflowX: "auto",
            }}
          >
            <Table
              size="medium"
              aria-label="Tableau des dossiers en attente"
              sx={{
                width: "100%",
                minWidth: 1000,
                "& .MuiTableCell-head": {
                  backgroundColor: theme.palette.surface?.nested || "#F2F3F5",
                  color: theme.palette.text.secondary,
                  fontWeight: 800,
                  whiteSpace: "nowrap",
                },
                "& .MuiTableCell-root": {
                  borderColor: theme.palette.border?.subtle || "rgba(17,17,19,0.08)",
                  px: 2,
                  py: 1.75,
                },
                "& .MuiTableBody-root .MuiTableRow-root:last-child .MuiTableCell-root": {
                  borderBottom: 0,
                },
              }}
            >
              <TableHead>
                <TableRow>
                  <TableCell sx={{ width: 140 }}>ID Dossier</TableCell>
                  <TableCell sx={{ width: 220 }}>Client</TableCell>
                  <TableCell sx={{ width: 210 }}>Véhicule</TableCell>
                  <TableCell sx={{ width: 190 }}>Statut</TableCell>
                  <TableCell sx={{ width: 180 }}>Date de création</TableCell>
                  <TableCell align="right" sx={{ width: 100 }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.slice(page * pageSize, page * pageSize + pageSize).map((row) => (
                  <TableRow key={row.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight={700} className="tabular-nums">
                        #{String(row.id).slice(0, 8)}
                      </Typography>
                    </TableCell>
                    <TableCell sx={{ whiteSpace: "nowrap" }}>{row.client}</TableCell>
                    <TableCell>{row.vehicle}</TableCell>
                    <TableCell>
                      <Chip
                        label={STATUS_LABELS[row.status] ?? row.status ?? "Inconnu"}
                        size="small"
                        sx={{
                          fontWeight: 700,
                          backgroundColor: "rgba(59, 130, 246, 0.1)",
                          color: "#1D4ED8",
                          border: "1px solid rgba(59, 130, 246, 0.3)",
                        }}
                      />
                    </TableCell>
                    <TableCell sx={{ whiteSpace: "nowrap" }}>
                      {row.created_at
                        ? new Date(row.created_at).toLocaleString("fr-FR", {
                            dateStyle: "short",
                            timeStyle: "short",
                          })
                        : "-"}
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="Examiner le dossier">
                        <IconButton
                          size="small"
                          color="primary"
                          aria-label={`Examiner le dossier ${String(row.id).slice(0, 8)}`}
                          onClick={() => navigate(`/admin/dossiers/${row.id}`)}
                        >
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            component="div"
            count={rows.length}
            page={page}
            onPageChange={(_, nextPage) => setPage(nextPage)}
            rowsPerPage={pageSize}
            onRowsPerPageChange={(event) => {
              setPageSize(Number(event.target.value));
              setPage(0);
            }}
            rowsPerPageOptions={[10, 25, 50]}
            labelRowsPerPage="Lignes par page :"
            labelDisplayedRows={({ from, to, count }) =>
              `${from}–${to} sur ${count !== -1 ? count : `plus de ${to}`}`
            }
            sx={{
              borderTop: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}`,
              ".MuiTablePagination-toolbar": { minHeight: 56 },
            }}
          />
        </Paper>
      )}

      <Paper
        elevation={0}
        sx={{
          mt: 4,
          p: { xs: 2, md: 3 },
          borderRadius: 3,
          border: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}`,
          backgroundColor: theme.palette.background.paper,
        }}
      >
        <Typography variant="h5" fontWeight={800} sx={{ mb: 1 }}>
          Historique des dossiers
        </Typography>
        <Typography color="text.secondary" sx={{ mb: 2 }}>
          Dossiers validés, refusés, annulés ou clôturés.
        </Typography>

        {historyQuery.isError && (
          <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
            {getApiErrorMessage(
              historyQuery.error,
              "Une erreur est survenue lors du chargement de l’historique.",
            )}
          </Alert>
        )}
        {historyQuery.isLoading && (
          <Box sx={{ display: "flex", alignItems: "center", gap: 1, py: 2 }}>
            <CircularProgress size={18} />
            <Typography variant="body2" color="text.secondary">Chargement de l’historique...</Typography>
          </Box>
        )}
        {!historyQuery.isLoading && !historyQuery.isError && historyQuery.data?.length === 0 && (
          <Typography color="text.secondary">Aucun dossier clôturé pour le moment.</Typography>
        )}
        {!historyQuery.isLoading && !historyQuery.isError && (historyQuery.data?.length ?? 0) > 0 && (
          <List disablePadding>
            {historyQuery.data?.map((dossier, index) => (
              <ListItem
                key={dossier.id}
                divider={index < (historyQuery.data?.length ?? 0) - 1}
                secondaryAction={
                  <Button
                    size="small"
                    onClick={() => navigate(`/admin/dossiers/${dossier.id}`)}
                    aria-label={`Consulter le dossier ${String(dossier.id).slice(0, 8)}`}
                  >
                    Consulter
                  </Button>
                }
                sx={{ py: 1.5, pr: 12 }}
              >
                <ListItemText
                  primary={`${dossier.client_email} — ${dossier.vehicle_brand} ${dossier.vehicle_model}`}
                  secondary={`${STATUS_LABELS[dossier.status] ?? dossier.status} · Mis à jour le ${new Date(dossier.updated_at).toLocaleDateString("fr-FR")}`}
                />
              </ListItem>
            ))}
          </List>
        )}
      </Paper>
    </Container>
  );
};