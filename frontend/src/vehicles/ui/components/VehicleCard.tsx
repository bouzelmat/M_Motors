import {
  Box,
  Card,
  CardContent,
  CardMedia,
  Chip,
  Typography,
} from "@mui/material";

import type { VehicleListItemDTO } from "../../infrastructure/vehicle.types";

interface VehicleCardProps {
  vehicle: VehicleListItemDTO;
}

export function VehicleCard({
  vehicle,
}: VehicleCardProps) {
  const {
    brand,
    model,
    year,
    monthly_rent,
    photo_url,
    included_services,
  } = vehicle;

  const imageUrl = photo_url ?? "/placeholder-car.png";

  return (
    <Card
      data-testid="vehicle-card" // for test
      data-vehicle-id={vehicle.id} // for test
      sx={{
        maxWidth: 345,
        height: "100%",
        display: "flex",
        flexDirection: "column",
        transition: "transform 0.2s",
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
