import { create } from "zustand";

import type {
  CatalogMode,
  ServiceDTO,
} from "../../../vehicles/infrastructure/vehicle.types";

export type ServiceSelection = Pick<
  ServiceDTO,
  "id" | "name" | "monthly_cost" | "included"
>;

export interface SubscriptionTunnelState {
  vehicleId: string | null;
  vehicleMode: CatalogMode | null;
  selectedServices: ServiceSelection[];

  setVehicle: (vehicleId: string, mode: CatalogMode) => void;
  toggleService: (service: ServiceSelection) => void;
  resetTunnel: () => void;
}

const INITIAL_TUNNEL_STATE = {
  vehicleId: null,
  vehicleMode: null,
  selectedServices: [],
} satisfies Pick<
  SubscriptionTunnelState,
  "vehicleId" | "vehicleMode" | "selectedServices"
>;

export const useSubscriptionTunnelStore =
  create<SubscriptionTunnelState>((set) => ({
    ...INITIAL_TUNNEL_STATE,

    setVehicle: (vehicleId, vehicleMode) =>
      set({
        vehicleId,
        vehicleMode,
      }),

    toggleService: (service) =>
      set((state) => {
        if (service.included) {
          return state;
        }

        const isAlreadySelected = state.selectedServices.some(
          (selectedService) => selectedService.id === service.id,
        );

        if (isAlreadySelected) {
          return {
            selectedServices: state.selectedServices.filter(
              (selectedService) => selectedService.id !== service.id,
            ),
          };
        }

        return {
          selectedServices: [...state.selectedServices, service],
        };
      }),

    resetTunnel: () => set(INITIAL_TUNNEL_STATE),
  }));