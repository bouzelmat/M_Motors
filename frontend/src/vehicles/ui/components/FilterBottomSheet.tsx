import React from "react";
import { Drawer, Box, Typography, IconButton, useTheme } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import { FilterSidebar } from "./FilterSidebar";

export interface FilterBottomSheetProps {
  open: boolean;
  onClose: () => void;
}

export const FilterBottomSheet: React.FC<FilterBottomSheetProps> = ({ open, onClose }) => {
  const theme = useTheme();

  return (
    <Drawer
      anchor="bottom"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: {
          borderTopLeftRadius: 24,
          borderTopRightRadius: 24,
          maxHeight: "85vh",
          p: 3,
          backgroundColor: theme.palette.background.default,
        },
      }}
    >
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
        <Typography variant="h6" fontWeight={800}>
          Filtres de recherche
        </Typography>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </Box>

      <Box sx={{ overflowY: "auto", maxContent: "calc(85vh - 80px)" }}>
        <FilterSidebar onFilterChange={onClose} />
      </Box>
    </Drawer>
  );
};
