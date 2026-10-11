import React from "react";
import { Box, Container, Grid, Card, CardContent, Typography, useTheme } from "@mui/material";
import BuildOutlinedIcon from "@mui/icons-material/BuildOutlined";
import ShieldOutlinedIcon from "@mui/icons-material/ShieldOutlined";
import HandshakeOutlinedIcon from "@mui/icons-material/HandshakeOutlined";
import LocalShippingOutlinedIcon from "@mui/icons-material/LocalShippingOutlined";
import { SectionHeading } from "../../shared/ui/components/SectionHeading";
import { useRevealOnScroll } from "../../shared/ui/hooks/useRevealOnScroll";

const services = [
  {
    icon: <BuildOutlinedIcon sx={{ fontSize: 32 }} />,
    title: "Entretien & Assistance 24/7",
    description: "Révisions, contrôle technique et dépannage zéro frais imprévus tout au long de votre contrat.",
  },
  {
    icon: <ShieldOutlinedIcon sx={{ fontSize: 32 }} />,
    title: "Garantie Constructeur Totale",
    description: "Protection complète sur toutes les pièces mécaniques, électriques et batteries haute tension.",
  },
  {
    icon: <HandshakeOutlinedIcon sx={{ fontSize: 32 }} />,
    title: "Engagement Flexibilité",
    description: "Ajustez votre kilométrage ou changez de véhicule en toute simplicité selon vos besoins.",
  },
  {
    icon: <LocalShippingOutlinedIcon sx={{ fontSize: 32 }} />,
    title: "Livraison à Domicile",
    description: "Votre nouveau véhicule livré prêt à rouler, partout en France métropolitaine sous 7 jours.",
  },
];

export const LLDSection: React.FC = () => {
  const theme = useTheme();

  return (
    <Box sx={{ py: { xs: 8, md: 12 }, backgroundColor: theme.palette.background.default }}>
      <Container maxWidth="xl">
        <SectionHeading
          eyebrow="SERVICES SUR MESURE"
          title="Pourquoi choisir M-MOTORS LLD ?"
          subtitle="Une sérénité absolue avec des mensualités fixes sans surprise."
          align="center"
        />

        <Grid container spacing={3} sx={{ mt: 4 }}>
          {services.map((service, index) => {
            const { ref, style } = useRevealOnScroll<HTMLDivElement>({ index, staggerMs: 100 });
            return (
              <Grid item xs={12} sm={6} md={3} key={service.title}>
                <div ref={ref} style={style}>
                  <Card
                    elevation={0}
                    sx={{
                      height: "100%",
                      p: 1,
                      border: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}`,

                      borderRadius: 20,
                      backgroundColor: theme.palette.surface.card,
                      transition: "all 300ms ease-out",
                      "&:hover": {
                        transform: "translateY(-6px)",
                        borderColor: theme.palette.accent.location,
                        boxShadow: "0 16px 32px rgba(59, 130, 246, 0.08)",
                      },
                    }}
                  >
                    <CardContent>
                      <Box
                        sx={{
                          width: 56,
                          height: 56,
                          borderRadius: 16,
                          backgroundColor: "rgba(59, 130, 246, 0.08)",
                          color: theme.palette.accent.location,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          mb: 2.5,
                        }}
                      >
                        {service.icon}
                      </Box>
                      <Typography variant="h6" component="h3" sx={{ fontWeight: 800, mb: 1 }}>
                        {service.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                        {service.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </div>
              </Grid>
            );
          })}
        </Grid>
      </Container>
    </Box>
  );
};
