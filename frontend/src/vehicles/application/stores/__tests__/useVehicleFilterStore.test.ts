import { beforeEach, describe, expect, it } from "vitest";

import { useVehicleFilterStore } from "../useVehicleFilterStore";

const DEFAULT_MODE = "rental";

describe("useVehicleFilterStore", () => {
  beforeEach(() => {
    useVehicleFilterStore.getState().resetFilters();
  });

  it("should initialize with default values", () => {
    const state = useVehicleFilterStore.getState();

    expect(state.mode).toBe(DEFAULT_MODE);
    expect(state.maxMonthlyRent).toBeNull();
    expect(state.brand).toBeNull();
    expect(state.maxPrice).toBeNull();
    expect(state.maxMileage).toBeNull();
    expect(state.fuelType).toBeNull();
  });

  it("should update mode", () => {
    const { setMode } = useVehicleFilterStore.getState();

    setMode("sale");

    expect(useVehicleFilterStore.getState().mode).toBe("sale");
  });

  it("should update maxMonthlyRent", () => {
    const { setMaxMonthlyRent } = useVehicleFilterStore.getState();

    setMaxMonthlyRent(350);

    expect(useVehicleFilterStore.getState().maxMonthlyRent).toBe(350);

    setMaxMonthlyRent(null);

    expect(useVehicleFilterStore.getState().maxMonthlyRent).toBeNull();
  });

  it("should update brand", () => {
    const { setBrand } = useVehicleFilterStore.getState();

    setBrand("Renault");

    expect(useVehicleFilterStore.getState().brand).toBe("Renault");

    setBrand(null);

    expect(useVehicleFilterStore.getState().brand).toBeNull();
  });

  it("should update maxPrice", () => {
    const { setMaxPrice } = useVehicleFilterStore.getState();

    setMaxPrice(25000);

    expect(useVehicleFilterStore.getState().maxPrice).toBe(25000);

    setMaxPrice(null);

    expect(useVehicleFilterStore.getState().maxPrice).toBeNull();
  });

  it("should update maxMileage", () => {
    const { setMaxMileage } = useVehicleFilterStore.getState();

    setMaxMileage(80000);

    expect(useVehicleFilterStore.getState().maxMileage).toBe(80000);

    setMaxMileage(null);

    expect(useVehicleFilterStore.getState().maxMileage).toBeNull();
  });

  it("should update fuelType", () => {
    const { setFuelType } = useVehicleFilterStore.getState();

    setFuelType("ELECTRIQUE");

    expect(useVehicleFilterStore.getState().fuelType).toBe("ELECTRIQUE");

    setFuelType(null);

    expect(useVehicleFilterStore.getState().fuelType).toBeNull();
  });

  it("should reset all filters to default values", () => {
    const {
      setMode,
      setMaxMonthlyRent,
      setBrand,
      setMaxPrice,
      setMaxMileage,
      setFuelType,
      resetFilters,
    } = useVehicleFilterStore.getState();

    setMode("sale");
    setMaxMonthlyRent(400);
    setBrand("Peugeot");
    setMaxPrice(30000);
    setMaxMileage(60000);
    setFuelType("ESSENCE");

    resetFilters();

    const state = useVehicleFilterStore.getState();

    expect(state.mode).toBe(DEFAULT_MODE);
    expect(state.maxMonthlyRent).toBeNull();
    expect(state.brand).toBeNull();
    expect(state.maxPrice).toBeNull();
    expect(state.maxMileage).toBeNull();
    expect(state.fuelType).toBeNull();
  });
});