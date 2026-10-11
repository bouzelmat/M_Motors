import React from "react";
import { Box } from "@mui/material";
import { HeroSection } from "./home/HeroSection";
import { QuickSearchSection } from "./home/QuickSearchSection";
import { LLDSection } from "./home/LLDSection";
import { ReassuranceSection } from "./home/ReassuranceSection";
import { VehicleSelectionSection } from "./home/VehicleSelectionSection";

export const HomePage: React.FC = () => {
  return (
    <Box component="div" sx={{ width: "100%", overflowX: "hidden" }}>
      {/* 1. Showroom 3D Hero Section */}
      <HeroSection />

      {/* 2. Quick Search Segmented Bar */}
      <QuickSearchSection />

      {/* 3. Featured Vehicles Selection */}
      <VehicleSelectionSection />

      {/* 4. LLD Service Advantages */}
      <LLDSection />

      {/* 5. Big Figures Reassurance Section */}
      <ReassuranceSection />
    </Box>
  );
};

export default HomePage;