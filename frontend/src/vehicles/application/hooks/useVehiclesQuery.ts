import { useQuery, type UseQueryResult } from "@tanstack/react-query";

import { vehiclesClient } from "../../infrastructure/VehiclesClient";
import type { CatalogMode } from "../stores/useVehicleFilterStore";
import type { VehicleListItemDTO } from "../../infrastructure/vehicle.types";

const STALE_TIME_MS = 5 * 60 * 1000;

export interface UseVehiclesQueryParams {
  mode: CatalogMode;
  brand?: string | null;
  maxPrice?: number | null;
  maxMileage?: number | null;
  fuelType?: string | null;
  maxMonthlyRent?: number | null;
}

/**
 * Récupère le catalogue des véhicules selon l'ensemble des filtres demandés.
 */
export function useVehiclesQuery({
  mode,
  brand,
  maxPrice,
  maxMileage,
  fuelType,
  maxMonthlyRent,
}: UseVehiclesQueryParams): UseQueryResult<VehicleListItemDTO[], Error> {
  const queryKey = [
    "vehicles",
    mode,
    brand,
    maxPrice,
    maxMileage,
    fuelType,
    maxMonthlyRent,
  ] as const;

  return useQuery({
    queryKey,
    queryFn: () =>
      vehiclesClient.getCatalog({
        mode,
        brand: brand ?? undefined,
        max_price: maxPrice ?? undefined,
        max_mileage: maxMileage ?? undefined,
        fuel_type: fuelType ?? undefined,
        max_monthly_rent: maxMonthlyRent ?? undefined,
      }),
    staleTime: STALE_TIME_MS,
    retry: 1,
  });
}