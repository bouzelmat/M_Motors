import { useQuery, type UseQueryResult } from "@tanstack/react-query";

import { vehiclesClient } from "../../infrastructure/VehiclesClient";
import type { CatalogMode } from "../stores/useVehicleFilterStore";
import type { VehicleListItemDTO } from "../../infrastructure/vehicle.types";

const STALE_TIME_MS = 5 * 60 * 1000;

export interface UseVehiclesQueryParams {
  mode: CatalogMode;
  maxMonthlyRent?: number | null;
}

/**
 * Récupère le catalogue des véhicules selon les filtres demandés.
 */
export function useVehiclesQuery({
  mode,
  maxMonthlyRent,
}: UseVehiclesQueryParams): UseQueryResult<VehicleListItemDTO[], Error> {
  const queryKey = [
    "vehicles",
    mode,
    maxMonthlyRent,
  ] as const;

  return useQuery({
    queryKey,
    queryFn: () =>
      vehiclesClient.getCatalog({
        mode,
        max_monthly_rent: maxMonthlyRent ?? undefined,
      }),
    staleTime: STALE_TIME_MS,
    retry: 1,
  });
}