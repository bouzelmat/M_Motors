import React, { useState } from "react";
import {
  Box,
  Container,
  Paper,
  Stack,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Typography,
  ToggleButtonGroup,
  ToggleButton,
  useTheme,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import ShoppingBagOutlinedIcon from "@mui/icons-material/ShoppingBagOutlined";
import KeyOutlinedIcon from "@mui/icons-material/KeyOutlined";
import { useNavigate } from "react-router-dom";

export const QuickSearchSection: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();

  const [mode, setMode] = useState<"ACHAT" | "LOCATION">("LOCATION");
  const [brand, setBrand] = useState<string>("");
  const [budget, setBudget] = useState<string>("");

  const isAchat = mode === "ACHAT";
  const activeColor = isAchat
    ? theme.palette.accent?.achat || "#E82127"
    : theme.palette.accent?.location || "#3B82F6";

  const handleSearch = () => {
    const params = new URLSearchParams();
    params.set("mode", mode);
    if (brand) params.set("brand", brand);
    if (budget) params.set("budget", budget);
    navigate(`/catalogue?${params.toString()}`);
  };

  return (
    <Container maxWidth="xl" sx={{ mt: -6, zIndex: 10, position: "relative" }}>
      <Paper
        elevation={0}
        sx={{
          p: { xs: 3, md: 4 },
          borderRadius: 24,
          backgroundColor: theme.palette.background?.paper || "#FFFFFF",
          border: `1px solid ${theme.palette.border?.strong || "rgba(17, 17, 19, 0.16)"}`,
          boxShadow: "0 20px 40px rgba(17, 17, 19, 0.08)",
        }}
      >
        <Stack spacing={3}>
          {/* Segmented Control */}
          <Box sx={{ display: "flex", justifyContent: "center" }}>
            <ToggleButtonGroup
              value={mode}
              exclusive
              onChange={(_, newMode) => newMode && setMode(newMode)}
              sx={{
                backgroundColor: theme.palette.surface?.nested || "#F2F3F5",
                p: 0.5,
                borderRadius: 999,
                border: "none",
                "& .MuiToggleButton-root": {
                  border: "none",
                  borderRadius: 999,
                  px: 3,
                  py: 1,
                  fontWeight: 700,
                  fontSize: "0.9rem",
                  color: theme.palette.text.secondary,
                  textTransform: "none",
                  transition: "all 200ms ease-out",
                  "&.Mui-selected": {
                    backgroundColor: activeColor,
                    color: "#FFFFFF",
                    boxShadow: "0 4px 12px rgba(17,17,19,0.15)",
                    "&:hover": {
                      backgroundColor: activeColor,
                    },
                  },
                },
              }}
            >
              <ToggleButton value="LOCATION">
                <KeyOutlinedIcon sx={{ mr: 1, fontSize: 18 }} />
                Location LLD
              </ToggleButton>
              <ToggleButton value="ACHAT">
                <ShoppingBagOutlinedIcon sx={{ mr: 1, fontSize: 18 }} />
                Achat Comptant
              </ToggleButton>
            </ToggleButtonGroup>
          </Box>

          {/* Form Inputs Grid */}
          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr", md: "2fr 2fr 1fr" },
              gap: 2,
              alignItems: "center",
            }}
          >
            <FormControl fullWidth size="medium">
              <InputLabel id="brand-select-label">Marque</InputLabel>
              <Select
                labelId="brand-select-label"
                value={brand}
                label="Marque"
                onChange={(e) => setBrand(e.target.value)}
                sx={{ borderRadius: 12 }}
              >
                <MenuItem value="">Toutes les marques</MenuItem>
                <MenuItem value="Tesla">Tesla</MenuItem>
                <MenuItem value="BMW">BMW</MenuItem>
                <MenuItem value="Audi">Audi</MenuItem>
                <MenuItem value="Mercedes-Benz">Mercedes-Benz</MenuItem>
                <MenuItem value="Porsche">Porsche</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth size="medium">
              <InputLabel id="budget-select-label">
                {isAchat ? "Budget max (€)" : "Loyer max (€/mois)"}
              </InputLabel>
              <Select
                labelId="budget-select-label"
                value={budget}
                label={isAchat ? "Budget max (€)" : "Loyer max (€/mois)"}
                onChange={(e) => setBudget(e.target.value)}
                sx={{ borderRadius: 12 }}
              >
                <MenuItem value="">Tous les tarifs</MenuItem>
                {isAchat ? [
                  <MenuItem key="25k" value="25000">Moins de 25 000 €</MenuItem>,
                  <MenuItem key="40k" value="40000">Moins de 40 000 €</MenuItem>,
                  <MenuItem key="60k" value="60000">Moins de 60 000 €</MenuItem>,
                  <MenuItem key="100k" value="100000">Moins de 100 000 €</MenuItem>,
                ] : [
                  <MenuItem key="300m" value="300">Moins de 300 € / mois</MenuItem>,
                  <MenuItem key="500m" value="500">Moins de 500 € / mois</MenuItem>,
                  <MenuItem key="750m" value="750">Moins de 750 € / mois</MenuItem>,
                  <MenuItem key="1000m" value="1000">Moins de 1 000 € / mois</MenuItem>,
                ]}

              </Select>
            </FormControl>

            <Button
              variant="contained"
              size="large"
              onClick={handleSearch}
              startIcon={<SearchIcon />}
              sx={{
                height: 54,
                borderRadius: 999,
                backgroundColor: activeColor,
                color: "#FFFFFF",
                fontWeight: 700,
                fontSize: "1rem",
                "&:hover": {
                  backgroundColor: activeColor,
                  filter: "brightness(0.9)",
                },
              }}
            >
              Rechercher
            </Button>
          </Box>
        </Stack>
      </Paper>
    </Container>
  );
};
