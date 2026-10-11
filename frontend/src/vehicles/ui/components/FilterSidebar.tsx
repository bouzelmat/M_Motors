import React from "react";
import {
  Box,
  Paper,
  Typography,
  Stack,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  ToggleButtonGroup,
  ToggleButton,
  Chip,
  useTheme,
} from "@mui/material";
import RestartAltIcon from "@mui/icons-material/RestartAlt";
import ShoppingBagOutlinedIcon from "@mui/icons-material/ShoppingBagOutlined";
import KeyOutlinedIcon from "@mui/icons-material/KeyOutlined";
import { useVehicleFilterStore, CatalogMode } from "../../application/stores/useVehicleFilterStore";

export interface FilterSidebarProps {
  onFilterChange?: () => void;
}

export const FilterSidebar: React.FC<FilterSidebarProps> = ({ onFilterChange }) => {
  const theme = useTheme();

  const {
    mode,
    brand,
    maxPrice,
    maxMonthlyRent,
    maxMileage,
    fuelType,
    setMode,
    setBrand,
    setMaxPrice,
    setMaxMonthlyRent,
    setMaxMileage,
    setFuelType,
    resetFilters,
  } = useVehicleFilterStore();

  const isAchat = mode === "sale";
  const activeColor = isAchat
    ? theme.palette.accent?.achat || "#E82127"
    : theme.palette.accent?.location || "#3B82F6";


  const handleModeChange = (_: unknown, newMode: CatalogMode | null) => {
    if (newMode) {
      setMode(newMode);
      if (onFilterChange) onFilterChange();
    }
  };

  const energies = [
    { label: "Toutes", value: null },
    { label: "Électrique", value: "ELECTRIQUE" },
    { label: "Hybride", value: "HYBRIDE" },
    { label: "Essence", value: "ESSENCE" },
    { label: "Diesel", value: "DIESEL" },
  ];

  return (
    <Paper
      elevation={0}
      sx={{
        width: 280,
        p: 3,
        borderRadius: 20,
        backgroundColor: theme.palette.background.paper,
        border: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}`,
        position: "sticky",

        top: 88,
      }}
    >
      <Stack spacing={3.5}>
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <Typography variant="h6" fontWeight={800}>
            Filtres
          </Typography>
          <Button
            size="small"
            startIcon={<RestartAltIcon />}
            onClick={() => {
              resetFilters();
              if (onFilterChange) onFilterChange();
            }}
            sx={{ color: theme.palette.text.secondary, textTransform: "none" }}
          >
            Réinitialiser
          </Button>
        </Box>

        {/* Mode Segmented Switch */}
        <Box>
          <Typography variant="caption" fontWeight={700} color="text.secondary" sx={{ display: "block", mb: 1 }}>
            MODE DE FINANCEMENT
          </Typography>
          <ToggleButtonGroup
            value={mode}
            exclusive
            onChange={handleModeChange}
            fullWidth
            sx={{
              backgroundColor: theme.palette.surface?.nested || "#F2F3F5",
              p: 0.5,
              borderRadius: 999,
              border: "none",
              "& .MuiToggleButton-root": {
                border: "none",
                borderRadius: 999,
                py: 0.75,
                fontWeight: 700,
                fontSize: "0.8rem",
                color: theme.palette.text.secondary,
                "&.Mui-selected": {
                  backgroundColor: activeColor,
                  color: "#FFFFFF",
                  boxShadow: "0 2px 8px rgba(17,17,19,0.12)",
                },
              },
            }}
          >
            <ToggleButton value="rental">
              <KeyOutlinedIcon sx={{ mr: 0.5, fontSize: 16 }} />
              Location
            </ToggleButton>
            <ToggleButton value="sale">
              <ShoppingBagOutlinedIcon sx={{ mr: 0.5, fontSize: 16 }} />
              Achat
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>

        {/* Marque */}
        <FormControl fullWidth size="small">
          <InputLabel id="sidebar-brand-label">Marque</InputLabel>
          <Select
            labelId="sidebar-brand-label"
            value={brand || ""}
            label="Marque"
            onChange={(e) => {
              setBrand(e.target.value ? e.target.value : null);
              if (onFilterChange) onFilterChange();
            }}
            sx={{ borderRadius: 12 }}
          >
            <MenuItem value="">Toutes les marques</MenuItem>
            <MenuItem value="Tesla">Tesla</MenuItem>
            <MenuItem value="BMW">BMW</MenuItem>
            <MenuItem value="Audi">Audi</MenuItem>
            <MenuItem value="Mercedes-Benz">Mercedes-Benz</MenuItem>
            <MenuItem value="Porsche">Porsche</MenuItem>
            <MenuItem value="Peugeot">Peugeot</MenuItem>
            <MenuItem value="Renault">Renault</MenuItem>
          </Select>
        </FormControl>

        {/* Budget / Loyer Slider */}
        <Box>
          <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
            <Typography variant="caption" fontWeight={700} color="text.secondary">
              {isAchat ? "BUDGET MAX" : "LOYER MAX"}
            </Typography>
            <Typography variant="caption" fontWeight={800} className="tabular-nums" sx={{ color: activeColor }}>
              {isAchat
                ? maxPrice
                  ? `${new Intl.NumberFormat("fr-FR").format(maxPrice)} €`
                  : "Illimité"
                : maxMonthlyRent
                ? `${new Intl.NumberFormat("fr-FR").format(maxMonthlyRent)} €/mois`
                : "Illimité"}
            </Typography>
          </Box>
          <Slider
            value={isAchat ? maxPrice || 100000 : maxMonthlyRent || 1500}
            min={isAchat ? 10000 : 150}
            max={isAchat ? 100000 : 1500}
            step={isAchat ? 2500 : 25}
            onChange={(_, val) => {
              const numVal = Array.isArray(val) ? val[0] : val;
              if (isAchat) {
                setMaxPrice(numVal >= 100000 ? null : numVal);
              } else {
                setMaxMonthlyRent(numVal >= 1500 ? null : numVal);
              }
              if (onFilterChange) onFilterChange();
            }}
            sx={{ color: activeColor }}
          />
        </Box>

        {/* Énergie */}
        <Box>
          <Typography variant="caption" fontWeight={700} color="text.secondary" sx={{ display: "block", mb: 1 }}>
            ÉNERGIE
          </Typography>
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
            {energies.map((e) => {
              const isSelected = fuelType === e.value;
              return (
                <Chip
                  key={e.label}
                  label={e.label}
                  size="small"
                  onClick={() => {
                    setFuelType(e.value);
                    if (onFilterChange) onFilterChange();
                  }}
                  sx={{
                    borderRadius: 999,
                    fontWeight: isSelected ? 700 : 500,
                    backgroundColor: isSelected ? activeColor : theme.palette.surface?.nested || "#F2F3F5",
                    color: isSelected ? "#FFFFFF" : theme.palette.text.primary,
                    border: `1px solid ${isSelected ? activeColor : theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}`,
                    cursor: "pointer",
                  }}
                />
              );
            })}
          </Box>
        </Box>
      </Stack>
    </Paper>
  );
};
