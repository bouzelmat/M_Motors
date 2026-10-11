import React from "react";
import { Box, Container, Grid, Button, useTheme } from "@mui/material";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import { Link } from "react-router-dom";
import { SectionHeading } from "../../shared/ui/components/SectionHeading";
import { VehicleCard } from "../../shared/ui/components/VehicleCard";
import { useRevealOnScroll } from "../../shared/ui/hooks/useRevealOnScroll";

const featuredVehicles = [
  {
    id: "v1",
    brand: "Tesla",
    model: "Model 3",
    version: "Grande Autonomie AWD",
    year: 2023,
    mileage: 18500,
    fuelType: "Électrique",
    transmission: "Automatique",
    price: 389,
    mode: "LOCATION" as const,
    imageUrl: "https://images.unsplash.com/photo-1560958089-b8a1929cea89?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: "v2",
    brand: "BMW",
    model: "Série 4 Gran Coupé",
    version: "420d M Sport",
    year: 2022,
    mileage: 32000,
    fuelType: "Diesel",
    transmission: "Automatique",
    price: 34900,
    mode: "ACHAT" as const,
    imageUrl: "https://images.unsplash.com/photo-1555215695-3004980ad54e?auto=format&fit=crop&w=800&q=80",
  },
  {
    id: "v3",
    brand: "Audi",
    model: "e-tron GT",
    version: "Quattro 530ch",
    year: 2024,
    mileage: 5400,
    fuelType: "Électrique",
    transmission: "Automatique",
    price: 799,
    mode: "LOCATION" as const,
    imageUrl: "https://images.unsplash.com/photo-1614162692292-7ac56d7f7f1e?auto=format&fit=crop&w=800&q=80",
  },
];

export const VehicleSelectionSection: React.FC = () => {
  const theme = useTheme();

  return (
    <Box sx={{ py: { xs: 8, md: 12 }, backgroundColor: theme.palette.background.default }}>
      <Container maxWidth="xl">
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", mb: 5, flexWrap: "wrap", gap: 2 }}>
          <SectionHeading
            eyebrow="OFFRES DISPONIBLES IMMÉDIATEMENT"
            title="Notre Sélection Premium"
            subtitle="Des véhicules rigoureusement inspectés et disponibles en livraison rapide."
          />
          <Button
            variant="outlined"
            component={Link}
            to="/catalogue"
            endIcon={<ArrowForwardIcon />}
            sx={{ borderRadius: 999 }}
          >
            Voir tout le catalogue
          </Button>
        </Box>

        <Grid container spacing={3.5}>
          {featuredVehicles.map((vehicle, index) => {
            const { ref, style } = useRevealOnScroll<HTMLDivElement>({ index, staggerMs: 100 });
            return (
              <Grid item xs={12} sm={6} md={4} key={vehicle.id}>
                <div ref={ref} style={style}>
                  <VehicleCard {...vehicle} />
                </div>
              </Grid>
            );
          })}
        </Grid>
      </Container>
    </Box>
  );
};
