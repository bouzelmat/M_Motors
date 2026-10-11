import React, { useState } from "react";
import { Card, CardContent, Box, Typography, Button, useTheme } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { ModeBadge, ModeBadgeType } from "./ModeBadge";
import { PriceTag } from "./PriceTag";
import { SpecLine } from "./SpecLine";

export interface VehicleCardProps {
  id: string;
  brand: string;
  model: string;
  version?: string;
  year: number;
  mileage: number;
  fuelType: string;
  transmission?: string;
  price: number; // Purchase price or monthly price depending on mode
  mode?: ModeBadgeType;
  imageUrl?: string;
  onClick?: () => void;
}

export const VehicleCard: React.FC<VehicleCardProps> = ({
  id,
  brand,
  model,
  version,
  year,
  mileage,
  fuelType,
  transmission,
  price,
  mode = "LOCATION",
  imageUrl,
  onClick,
}) => {
  const theme = useTheme();
  const navigate = useNavigate();

  const [tilt, setTilt] = useState({ x: 0, y: 0, active: false });

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const card = e.currentTarget.getBoundingClientRect();
    const cardWidth = card.width;
    const cardHeight = card.height;
    const centerX = card.left + cardWidth / 2;
    const centerY = card.top + cardHeight / 2;
    const mouseX = e.clientX - centerX;
    const mouseY = e.clientY - centerY;
    
    // Max rotation 8 degrees for elegant 3D effect
    const rotateX = (-mouseY / (cardHeight / 2)) * 6;
    const rotateY = (mouseX / (cardWidth / 2)) * 6;

    setTilt({ x: rotateX, y: rotateY, active: true });
  };

  const handleMouseLeave = () => {
    setTilt({ x: 0, y: 0, active: false });
  };

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      navigate(`/catalogue/${id}`);
    }
  };

  const isAchat = mode === "ACHAT";
  const defaultImage = "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=800&q=80";

  return (
    <Card
      onClick={handleClick}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      sx={{
        cursor: "pointer",
        position: "relative",
        perspective: "1000px",
        transformStyle: "preserve-3d",
        transform: tilt.active
          ? `perspective(1000px) rotateX(${tilt.x}deg) rotateY(${tilt.y}deg) scale3d(1.02, 1.02, 1.02)`
          : "perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)",
        transition: tilt.active ? "transform 100ms ease-out" : "transform 350ms cubic-bezier(0.16, 1, 0.3, 1), box-shadow 300ms ease-out",
        boxShadow: tilt.active
          ? "0 20px 35px rgba(17, 17, 19, 0.12)"
          : "0 4px 12px rgba(17, 17, 19, 0.04)",
        "&:hover": {
          borderColor: isAchat ? "rgba(232, 33, 39, 0.3)" : "rgba(59, 130, 246, 0.3)",
        },
        "@media (prefers-reduced-motion: reduce)": {
          transform: "none !important",
          transition: "none !important",
        },
      }}
    >
      {/* 3D Dynamic Reflection Layer */}
      {tilt.active && (
        <Box
          sx={{
            position: "absolute",
            inset: 0,
            pointerEvents: "none",
            zIndex: 10,
            background: `radial-gradient(circle at ${50 + tilt.y * 5}% ${50 - tilt.x * 5}%, rgba(255,255,255,0.3) 0%, transparent 60%)`,
            borderRadius: "inherit",
          }}
        />
      )}

      {/* Image Container on studio background */}
      <Box
        sx={{
          height: 200,
          backgroundColor: theme.palette.background?.studio || "#E9EBEE",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
          overflow: "hidden",
          p: 2,
        }}
      >
        <Box
          sx={{
            position: "absolute",
            top: 12,
            left: 12,
            zIndex: 2,
          }}
        >
          <ModeBadge mode={mode} />
        </Box>

        <Box
          component="img"
          src={imageUrl || defaultImage}
          alt={`${brand} ${model}`}
          sx={{
            maxHeight: "100%",
            maxWidth: "100%",
            objectFit: "contain",
            filter: "drop-shadow(0 10px 15px rgba(0, 0, 0, 0.12))",
            transition: "transform 300ms ease-out",
            transform: tilt.active ? "translateZ(20px) scale(1.05)" : "translateZ(0) scale(1)",
          }}
        />
      </Box>

      <CardContent sx={{ p: 2.5 }}>
        <Typography variant="caption" sx={{ color: theme.palette.text.secondary, textTransform: "uppercase", fontWeight: 700, letterSpacing: "0.08em" }}>
          {brand}
        </Typography>
        <Typography variant="h5" component="h3" sx={{ fontWeight: 800, mb: 0.5, textOverflow: "ellipsis", overflow: "hidden", whiteSpace: "nowrap" }}>
          {brand} {model}
        </Typography>
        {version && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            {version}
          </Typography>
        )}

        <Box sx={{ mb: 2 }}>
          <SpecLine year={year} mileage={mileage} fuelType={fuelType} transmission={transmission} />
        </Box>

        <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", pt: 1.5, borderTop: `1px solid ${theme.palette.border?.subtle || "rgba(17,17,19,0.08)"}` }}>
          <PriceTag price={price} isMonthly={mode === "LOCATION"} colorMode={isAchat ? "achat" : "location"} variant="medium" />
          <Button variant="outlined" size="small" sx={{ borderRadius: 999 }}>
            Découvrir
          </Button>
        </Box>
      </CardContent>

    </Card>
  );
};
