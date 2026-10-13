import {
  useQuery,
  type UseQueryResult,
} from "@tanstack/react-query";

import { vehiclesClient } from "../../infrastructure/VehiclesClient";
import type { VehicleDetailDTO } from "../../infrastructure/dto/vehicle.dto";

const STALE_TIME_MS = 5 * 60 * 1000;

/**
 * Récupère les détails d'un véhicule.
 */
export function useVehicleDetailQuery(
  vehicleId: string,
): UseQueryResult<VehicleDetailDTO, Error> {
  return useQuery({
    queryKey: ["vehicle", vehicleId],
    queryFn: () => vehiclesClient.getVehicleDetail(vehicleId),
    staleTime: STALE_TIME_MS,
    retry: 1,
    enabled: Boolean(vehicleId),
  });
}
