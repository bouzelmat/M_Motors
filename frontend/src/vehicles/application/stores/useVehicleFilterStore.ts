import { create } from "zustand";

import type { CatalogMode } from "../../domain/value-objects/catalogMode";

export type { CatalogMode } from "../../domain/value-objects/catalogMode";

export interface VehicleFilterState {
  mode: CatalogMode;
  maxMonthlyRent: number | null;
  brand: string | null;
  maxPrice: number | null;
  maxMileage: number | null;
  fuelType: string | null;

  setMode: (mode: CatalogMode) => void;
  setMaxMonthlyRent: (maxMonthlyRent: number | null) => void;
  setBrand: (brand: string | null) => void;
  setMaxPrice: (maxPrice: number | null) => void;
  setMaxMileage: (maxMileage: number | null) => void;
  setFuelType: (fuelType: string | null) => void;
  resetFilters: () => void;
}

const DEFAULT_MODE: CatalogMode = "rental";
const DEFAULT_MAX_MONTHLY_RENT: number | null = null;
const DEFAULT_BRAND: string | null = null;
const DEFAULT_MAX_PRICE: number | null = null;
const DEFAULT_MAX_MILEAGE: number | null = null;
const DEFAULT_FUEL_TYPE: string | null = null;

/**
 * Store Zustand contenant les filtres du catalogue véhicules.
 */
export const useVehicleFilterStore = create<VehicleFilterState>((set) => ({
  mode: DEFAULT_MODE,
  maxMonthlyRent: DEFAULT_MAX_MONTHLY_RENT,
  brand: DEFAULT_BRAND,
  maxPrice: DEFAULT_MAX_PRICE,
  maxMileage: DEFAULT_MAX_MILEAGE,
  fuelType: DEFAULT_FUEL_TYPE,

  setMode: (mode) =>
    set({
      mode,
    }),

  setMaxMonthlyRent: (maxMonthlyRent) =>
    set({
      maxMonthlyRent,
    }),

  setBrand: (brand) =>
    set({
      brand,
    }),

  setMaxPrice: (maxPrice) =>
    set({
      maxPrice,
    }),

  setMaxMileage: (maxMileage) =>
    set({
      maxMileage,
    }),

  setFuelType: (fuelType) =>
    set({
      fuelType,
    }),

  resetFilters: () =>
    set({
      mode: DEFAULT_MODE,
      maxMonthlyRent: DEFAULT_MAX_MONTHLY_RENT,
      brand: DEFAULT_BRAND,
      maxPrice: DEFAULT_MAX_PRICE,
      maxMileage: DEFAULT_MAX_MILEAGE,
      fuelType: DEFAULT_FUEL_TYPE,
    }),
}));