import React from "react";
import { Box } from "@mui/material";
import { Outlet } from "react-router-dom";
import { Navbar } from "./Navbar";
import { Footer } from "./Footer";

export const PublicLayout: React.FC = () => {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Navbar />
      <Box component="main" sx={{ flex: 1, pt: "64px" }}>
        <Outlet />
      </Box>
      <Footer />
    </Box>
  );
};
