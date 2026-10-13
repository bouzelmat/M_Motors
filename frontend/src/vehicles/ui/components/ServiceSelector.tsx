import {
  Chip,
  Checkbox,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Paper,
  Typography,
} from "@mui/material";
import type { ServiceSelection } from "../../../dossiers/application/models/ServiceSelection";

interface ServiceSelectorProps {
  readonly services: readonly ServiceSelection[];
  readonly selectedServices: readonly ServiceSelection[];
  readonly onToggle: (service: ServiceSelection) => void;
}

export function ServiceSelector({
  services,
  selectedServices,
  onToggle,
}: ServiceSelectorProps) {
  if (services.length === 0) {
    return (
      <Paper elevation={0} sx={{ p: 2, textAlign: "center" }}>
        <Typography color="text.secondary" variant="body2">
          Aucun service disponible pour ce véhicule.
        </Typography>
      </Paper>
    );
  }

  return (
    <List disablePadding>
      {services.map((service) => {
        const isIncluded = service.included;
        const isSelected =
          isIncluded ||
          selectedServices.some(
            (selectedService) => selectedService.id === service.id,
          );
        const handleToggle = () => {
          if (!isIncluded) {
            onToggle(service);
          }
        };

        return (
          <ListItem
            key={service.id}
            divider
            disablePadding
            secondaryAction={
              isIncluded ? (
                <Chip label="Inclus" color="success" size="small" />
              ) : (
                <Typography variant="body2" color="text.secondary">
                  {service.monthly_cost} €/mois
                </Typography>
              )
            }
          >
            <ListItemButton
              onClick={handleToggle}
              disabled={isIncluded}
            >
              <ListItemIcon>
                <Checkbox
                  edge="start"
                  checked={isSelected}
                  disabled={isIncluded}
                  tabIndex={-1}
                  disableRipple
                  inputProps={{
                    "aria-label": `Sélectionner ${service.name}`,
                  }}
                />
              </ListItemIcon>
              <ListItemText
                primary={service.name}
                secondary={isIncluded ? "Service inclus dans l'abonnement" : undefined}
              />
            </ListItemButton>
          </ListItem>
        );
      })}
    </List>
  );
}