import { create } from "zustand";

export type CatalogMode = "rental" | "sale";

export interface VehicleFilterState {
  mode: CatalogMode;
  maxMonthlyRent: number | null;
  setMode: (mode: CatalogMode) => void;
  setMaxMonthlyRent: (maxMonthlyRent: number | null) => void;
  resetFilters: () => void;
}

const DEFAULT_MODE: CatalogMode = "rental";
const DEFAULT_MAX_MONTHLY_RENT: number | null = null;

/**
 * Store Zustand contenant les filtres du catalogue véhicules.
 */
export const useVehicleFilterStore = create<VehicleFilterState>((set) => ({
  mode: DEFAULT_MODE,
  maxMonthlyRent: DEFAULT_MAX_MONTHLY_RENT,

  setMode: (mode) =>
    set({
      mode,
    }),

  setMaxMonthlyRent: (maxMonthlyRent) =>
    set({
      maxMonthlyRent,
    }),

  resetFilters: () =>
    set({
      mode: DEFAULT_MODE,
      maxMonthlyRent: DEFAULT_MAX_MONTHLY_RENT,
    }),
}));