import {
  Box,
  Chip,
  Typography,
} from "@mui/material";

import type { ServiceDTO } from "../../infrastructure/vehicle.types";

interface ServiceOptionRowProps {
  service: ServiceDTO;
}

export function ServiceOptionRow({
  service,
}: ServiceOptionRowProps) {
  return (
    <Box
      data-testid="service-option-row"
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: 2,
        py: 1.5,
      }}
    > 
      <Typography variant="body1">
        {service.name} 
      </Typography>

      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1,
        }}
      >
        <Typography variant="body2">
          {service.monthly_cost} €/mois
        </Typography>

        {service.included && (
          <Chip
            label="Inclus"
            size="small"
          />
        )}
      </Box>
    </Box>
  );
}
