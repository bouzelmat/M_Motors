import {
  Box,
  Card,
  CardContent,
  CardMedia,
  Chip,
  Typography,
} from "@mui/material";
import { useNavigate } from "react-router-dom";

import type { VehicleListItemDTO } from "../../infrastructure/vehicle.types";
import { createVehicleSlug } from "../vehicleSlug";

interface VehicleCardProps {
  vehicle: VehicleListItemDTO;
}

export function VehicleCard({
  vehicle,
}: VehicleCardProps) {
  const navigate = useNavigate();

  const {
    brand,
    model,
    year,
    monthly_rent,
    photo_url,
    included_services,
  } = vehicle;

  const imageUrl = photo_url ?? "/placeholder-car.png";

  const handleClick = () => {
    navigate(`/vehicles/${createVehicleSlug(vehicle)}`);
  };

  return (
    <Card
      data-testid="vehicle-card"
      data-vehicle-id={vehicle.id}
      role="button"
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          handleClick();
        }
      }}
      sx={{
        maxWidth: 345,
        height: "100%",
        display: "flex",
        flexDirection: "column",
        transition: "transform 0.2s",
        cursor: "pointer",
        "&:hover": {
          transform: "scale(1.02)",
        },
      }}
    >
      <CardMedia
        component="img"
        height="160"
        image={imageUrl}
        alt={`${brand} ${model}`}
        sx={{ objectFit: "cover" }}
      />

      <CardContent sx={{ flexGrow: 1 }}>
        <Typography
          variant="h6"
          component="h2"
          gutterBottom
        >
          {brand} {model}
        </Typography>

        <Typography
          variant="body2"
          color="text.secondary"
        >
          {year}
        </Typography>

        <Box
          sx={{
            mt: 2,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Typography
            variant="h6"
            color="primary"
          >
            {monthly_rent} € / mois
          </Typography>

          <Chip
            label="Location"
            size="small"
            color="success"
          />
        </Box>

        {included_services.length > 0 && (
          <Box sx={{ mt: 1 }}>
            <Typography
              variant="caption"
              color="text.secondary"
              display="block"
            >
              Services inclus : {included_services.join(", ")}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
