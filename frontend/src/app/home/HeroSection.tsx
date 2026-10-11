import React, { useState } from "react";
import { Box, Container, Typography, Button, Stack, Chip, useTheme } from "@mui/material";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import SpeedIcon from "@mui/icons-material/Speed";
import BatteryChargingFullIcon from "@mui/icons-material/BatteryChargingFull";
import ShieldOutlinedIcon from "@mui/icons-material/ShieldOutlined";
import { Link } from "react-router-dom";

export const HeroSection: React.FC = () => {
  const theme = useTheme();

  // Mouse tracking state for 3D vehicle stage rotation
  const [rotate, setRotate] = useState({ x: 5, y: -12, active: false });

  const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 30; // max 15 deg rotateY
    const y = -((e.clientY - rect.top) / rect.height - 0.5) * 20; // max 10 deg rotateX
    setRotate({ x: y, y: x, active: true });
  };

  const handlePointerLeave = () => {
    setRotate({ x: 5, y: -12, active: false });
  };

  const heroImage = "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1200&q=80";

  return (
    <Box
      sx={{
        minHeight: "calc(100svh - 64px)",
        display: "flex",

        alignItems: "center",
        position: "relative",
        overflow: "hidden",
        backgroundColor: theme.palette.background.default,
        py: { xs: 6, md: 10 },
      }}
    >
      {/* Background Subtle Gradient Lighting */}
      <Box
        sx={{
          position: "absolute",
          top: "-20%",
          right: "-10%",
          width: "60vw",
          height: "60vw",
          borderRadius: "50%",
          background: `radial-gradient(circle, rgba(59, 130, 246, 0.08) 0%, rgba(232, 33, 39, 0.05) 50%, transparent 70%)`,
          filter: "blur(60px)",
          pointerEvents: "none",
        }}
      />

      <Container maxWidth="xl">
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", lg: "1fr 1fr" },
            gap: { xs: 6, lg: 8 },
            alignItems: "center",
          }}
        >
          {/* Left Hero Content */}
          <Stack spacing={3.5} sx={{ zIndex: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <Chip
                label="NOUVEAU SHOWROOM 2026"
                size="small"
                sx={{
                  backgroundColor: "rgba(232, 33, 39, 0.08)",
                  color: theme.palette.accent?.achat || "#E82127",
                  fontWeight: 800,
                  fontSize: "0.75rem",
                  letterSpacing: "0.1em",
                  border: "1px solid rgba(232, 33, 39, 0.2)",
                }}
              />
              <Chip
                label="LLD & ACHAT"
                size="small"
                sx={{
                  backgroundColor: "rgba(59, 130, 246, 0.08)",
                  color: theme.palette.accent?.location || "#3B82F6",
                  fontWeight: 800,
                  fontSize: "0.75rem",
                  letterSpacing: "0.1em",
                  border: "1px solid rgba(59, 130, 246, 0.2)",
                }}
              />
            </Box>

            <Typography
              variant="h1"
              component="h1"
              sx={{
                fontSize: { xs: "2.75rem", sm: "3.75rem", md: "4.25rem" },
                fontWeight: 900,
                color: theme.palette.text.primary,
                lineHeight: 1.05,
                letterSpacing: "-0.03em",
              }}
            >
              Le futur automobile, selon{" "}
              <Typography
                component="span"
                variant="inherit"
                sx={{
                  background: `linear-gradient(135deg, ${theme.palette.text.primary} 0%, ${theme.palette.accent?.achat || "#E82127"} 50%, ${theme.palette.accent?.location || "#3B82F6"} 100%)`,
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              >

                vos règles.
              </Typography>
            </Typography>

            <Typography
              variant="subtitle1"
              sx={{
                fontSize: { xs: "1.05rem", md: "1.25rem" },
                color: theme.palette.text.secondary,
                maxWidth: 580,
                lineHeight: 1.6,
              }}
            >
              Achetez votre véhicule au meilleur prix ou optez pour la souplesse de la Location Longue Durée (LLD) avec garanties et entretien tout inclus.
            </Typography>

            {/* Double Action CTAs */}
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2} sx={{ pt: 1 }}>
              <Button
                variant="contained"
                size="large"
                component={Link}
                to="/catalogue?mode=ACHAT"
                endIcon={<ArrowForwardIcon />}
                sx={{
                  backgroundColor: theme.palette.accent?.achat || "#E82127",
                  color: "#FFFFFF",
                  px: 4,
                  py: 1.75,
                  fontSize: "1rem",
                  borderRadius: 999,
                  "&:hover": {
                    backgroundColor: "#C9181D",
                    boxShadow: "0 8px 24px rgba(232, 33, 39, 0.3)",
                  },
                }}
              >
                Découvrir à l'Achat
              </Button>

              <Button
                variant="contained"
                size="large"
                component={Link}
                to="/catalogue?mode=LOCATION"
                endIcon={<ArrowForwardIcon />}
                sx={{
                  backgroundColor: theme.palette.accent?.location || "#3B82F6",
                  color: "#FFFFFF",
                  px: 4,
                  py: 1.75,
                  fontSize: "1rem",
                  borderRadius: 999,
                  "&:hover": {
                    backgroundColor: "#2563EB",
                    boxShadow: "0 8px 24px rgba(59, 130, 246, 0.3)",
                  },
                }}
              >

                Offres LLD dès 299€/mois
              </Button>
            </Stack>
          </Stack>

          {/* Right 3D Interactive Car Stage */}
          <Box
            onPointerMove={handlePointerMove}
            onPointerLeave={handlePointerLeave}
            sx={{
              position: "relative",
              height: { xs: 360, sm: 460, md: 520 },
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              perspective: "1200px",
              cursor: "grab",
            }}
          >
            {/* 3D Stage Floor Reflection Podium */}
            <Box
              sx={{
                position: "absolute",
                bottom: "10%",
                width: "90%",
                height: "35%",
                borderRadius: "50%",
                background: "radial-gradient(ellipse at center, rgba(17, 17, 19, 0.08) 0%, rgba(17,17,19,0.01) 70%, transparent 100%)",
                transform: "rotateX(75deg)",
                pointerEvents: "none",
              }}
            />

            {/* 3D Floating Spec Badges */}
            <Box
              sx={{
                position: "absolute",
                top: 20,
                right: 20,
                zIndex: 4,
                backdropFilter: "blur(12px)",
                backgroundColor: theme.palette.glass?.bg || "rgba(255,255,255,0.7)",
                border: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}`,
                borderRadius: 999,
                px: 2,
                py: 1,
                display: "flex",
                alignItems: "center",
                gap: 1,
                boxShadow: "0 8px 20px rgba(17, 17, 19, 0.06)",
                transform: rotate.active ? "translateZ(30px)" : "translateZ(0)",
                transition: "transform 200ms ease-out",
              }}
            >
              <SpeedIcon sx={{ color: theme.palette.accent?.achat || "#E82127", fontSize: 18 }} />
              <Typography variant="caption" fontWeight={700} color="text.primary">
                0-100 km/h : <span className="tabular-nums">3.4s</span>
              </Typography>
            </Box>

            <Box
              sx={{
                position: "absolute",
                bottom: 40,
                left: 10,
                zIndex: 4,
                backdropFilter: "blur(12px)",
                backgroundColor: theme.palette.glass?.bg || "rgba(255,255,255,0.7)",
                border: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}`,
                borderRadius: 999,
                px: 2,
                py: 1,
                display: "flex",
                alignItems: "center",
                gap: 1,
                boxShadow: "0 8px 20px rgba(17, 17, 19, 0.06)",
                transform: rotate.active ? "translateZ(40px)" : "translateZ(0)",
                transition: "transform 200ms ease-out",
              }}
            >
              <BatteryChargingFullIcon sx={{ color: theme.palette.accent?.location || "#3B82F6", fontSize: 18 }} />

              <Typography variant="caption" fontWeight={700} color="text.primary">
                Autonomie : <span className="tabular-nums">614 km</span>
              </Typography>
            </Box>

            {/* Main Car Visual with 3D Transform */}
            <Box
              component="img"
              src={heroImage}
              alt="M-MOTORS Executive Vehicle Showcase"
              sx={{
                maxWidth: "100%",
                maxHeight: "100%",
                objectFit: "contain",
                filter: "drop-shadow(0 25px 35px rgba(17, 17, 19, 0.18))",
                transformStyle: "preserve-3d",
                transform: `rotateX(${rotate.x}deg) rotateY(${rotate.y}deg) scale(1.05)`,
                transition: rotate.active
                  ? "transform 80ms ease-out"
                  : "transform 600ms cubic-bezier(0.16, 1, 0.3, 1)",
                "@media (prefers-reduced-motion: reduce)": {
                  transform: "none !important",
                },
              }}
            />
          </Box>
        </Box>
      </Container>
    </Box>
  );
};
