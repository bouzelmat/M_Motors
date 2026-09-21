import { create } from "zustand";

import type {
  CatalogMode,
  ServiceDTO,
} from "../../infrastructure/vehicle.types";

export type ServiceSelection = Pick<
  ServiceDTO,
  "id" | "name" | "monthly_cost" | "included"
>;

export interface FinancingPlan {
  down_payment: number;
  duration_months: number;
  monthly_payment: number;
}

export interface TradeIn {
  registration: string;
  mileage: number;
  brand?: string | null;
  model?: string | null;
}

export interface SubscriptionTunnelState {
  vehicleId: string | null;
  vehicleMode: CatalogMode | null;
  selectedServices: ServiceSelection[];
  financingPlan: FinancingPlan | null;
  tradeIn: TradeIn | null;

  setVehicle: (vehicleId: string, mode: CatalogMode) => void;
  toggleService: (service: ServiceSelection) => void;
  setFinancingPlan: (plan: FinancingPlan | null) => void;
  setTradeIn: (tradeIn: TradeIn | null) => void;
  resetTunnel: () => void;
}

const INITIAL_TUNNEL_STATE = {
  vehicleId: null,
  vehicleMode: null,
  selectedServices: [],
  financingPlan: null,
  tradeIn: null,
} satisfies Pick<
  SubscriptionTunnelState,
  "vehicleId" | "vehicleMode" | "selectedServices" | "financingPlan" | "tradeIn"
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

    setFinancingPlan: (financingPlan) =>
      set({
        financingPlan,
      }),

    setTradeIn: (tradeIn) =>
      set({
        tradeIn,
      }),

    resetTunnel: () => set(INITIAL_TUNNEL_STATE),
  }));