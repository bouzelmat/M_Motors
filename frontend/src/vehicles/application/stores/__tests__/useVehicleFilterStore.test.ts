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

  it("should reset filters to default values", () => {
    const {
      setMode,
      setMaxMonthlyRent,
      resetFilters,
    } = useVehicleFilterStore.getState();

    setMode("sale");
    setMaxMonthlyRent(400);

    resetFilters();

    const state = useVehicleFilterStore.getState();

    expect(state.mode).toBe(DEFAULT_MODE);
    expect(state.maxMonthlyRent).toBeNull();
  });
});