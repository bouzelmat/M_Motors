import React from "react";
import { Box, Typography, Stack, useTheme, useMediaQuery } from "@mui/material";
import CheckIcon from "@mui/icons-material/Check";
import CloseIcon from "@mui/icons-material/Close";
import EditNoteIcon from "@mui/icons-material/EditNote";
import SendIcon from "@mui/icons-material/Send";
import TaskAltIcon from "@mui/icons-material/TaskAlt";
import HighlightOffIcon from "@mui/icons-material/HighlightOff";

export type DossierStatus = "DRAFT" | "SUBMITTED" | "DOCUMENTS_PENDING" | "VALIDATED" | "REJECTED" | "CANCELLED" | "EXPIRED";

export interface DossierTimelineProps {
  status: DossierStatus | string;
}

export const DossierTimeline: React.FC<DossierTimelineProps> = ({ status }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  const isRejected = status === "REJECTED" || status === "CANCELLED" || status === "EXPIRED";

  const timelineSteps = [
    { key: "DRAFT", label: "BROUILLON", desc: "Création du dossier", icon: <EditNoteIcon /> },
    { key: "SUBMITTED", label: "SOUMIS", desc: "Étude en cours", icon: <SendIcon /> },
    {
      key: isRejected ? "REJECTED" : "VALIDATED",
      label: isRejected ? "REJETÉ" : "VALIDÉ",
      desc: isRejected ? "Demande non retenue" : "Dossier approuvé",
      icon: isRejected ? <HighlightOffIcon /> : <TaskAltIcon />,
    },
  ];

  const getStepIndex = (s: string) => {
    if (s === "DRAFT") return 0;
    if (s === "SUBMITTED" || s === "DOCUMENTS_PENDING") return 1;
    if (s === "VALIDATED" || s === "REJECTED" || s === "CANCELLED" || s === "EXPIRED") return 2;
    return 0;
  };

  const currentIndex = getStepIndex(status);

  return (
    <Box sx={{ py: 3, px: 2 }}>
      <Stack
        direction={isMobile ? "column" : "row"}
        spacing={isMobile ? 3 : 2}
        alignItems={isMobile ? "flex-start" : "center"}
        justifyContent="space-between"
        sx={{ position: "relative" }}
      >
        {timelineSteps.map((step, index) => {
          const isCompleted = index < currentIndex;
          const isActive = index === currentIndex;

          let iconBg = theme.palette.surface?.nested || "#F2F3F5";
          let iconColor = theme.palette.text.disabled;

          if (isCompleted) {
            iconBg = theme.palette.text.primary;
            iconColor = "#FFFFFF";
          } else if (isActive) {
            if (isRejected) {
              iconBg = theme.palette.error.main;
              iconColor = "#FFFFFF";
            } else if (step.key === "VALIDATED") {
              iconBg = theme.palette.success.main;
              iconColor = "#FFFFFF";
            } else {
              iconBg = theme.palette.accent?.location || "#3B82F6";
              iconColor = "#FFFFFF";
            }
          }

          return (
            <Stack
              key={step.label}
              direction={isMobile ? "row" : "column"}
              spacing={1.5}
              alignItems={isMobile ? "center" : "center"}
              textAlign={isMobile ? "left" : "center"}
              sx={{ flex: 1, zIndex: 2, position: "relative" }}
            >
              <Box
                sx={{
                  width: 48,
                  height: 48,
                  borderRadius: 999,
                  backgroundColor: iconBg,
                  color: iconColor,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  boxShadow: isActive ? "0 4px 16px rgba(17,17,19,0.15)" : "none",
                  transition: "all 200ms ease-out",
                }}
              >
                {isCompleted ? <CheckIcon /> : step.icon}
              </Box>

              <Box>
                <Typography
                  variant="caption"
                  sx={{
                    fontWeight: 800,
                    letterSpacing: "0.08em",
                    color: isActive ? theme.palette.text.primary : theme.palette.text.secondary,
                    display: "block",
                  }}
                >
                  {step.label}
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ fontSize: "0.75rem" }}>
                  {step.desc}
                </Typography>
              </Box>
            </Stack>
          );
        })}
      </Stack>
    </Box>
  );
};
