import type { VehicleListItemDTO } from "../infrastructure/vehicle.types";

type VehicleSlugSource = Pick<VehicleListItemDTO, "id" | "brand" | "model" | "year">;

function slugify(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

export function createVehicleSlug(vehicle: VehicleSlugSource): string {
  const shortId = vehicle.id.replaceAll("-", "").slice(-8).toLowerCase();
  return `${slugify(`${vehicle.brand}-${vehicle.model}`)}-${vehicle.year}-${shortId}`;
}