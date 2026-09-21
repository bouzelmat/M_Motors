import { beforeEach, describe, expect, it } from "vitest";

import {
  useSubscriptionTunnelStore,
  type ServiceSelection,
  type FinancingPlan,
  type TradeIn,
} from "../useSubscriptionTunnelStore";

const sampleTradeIn: TradeIn = {
  registration: "AB-123-CD",
  mileage: 45000,
  brand: "Renault",
  model: "Clio",
};

describe("useSubscriptionTunnelStore - Extension TradeIn", () => {
  beforeEach(() => {
    useSubscriptionTunnelStore.getState().resetTunnel();
  });

  it("initialise le tunnel avec tradeIn à null", () => {
    const state = useSubscriptionTunnelStore.getState();
    expect(state.tradeIn).toBeNull();
  });

  it("enregistre les données de reprise via setTradeIn", () => {
    useSubscriptionTunnelStore.getState().setTradeIn(sampleTradeIn);

    const state = useSubscriptionTunnelStore.getState();
    expect(state.tradeIn).toEqual(sampleTradeIn);
  });

  it("réinitialise tradeIn à null lors de l'appel à resetTunnel", () => {
    const store = useSubscriptionTunnelStore.getState();

    store.setVehicle("vehicle-999", "sale");
    store.setTradeIn(sampleTradeIn);

    expect(useSubscriptionTunnelStore.getState().tradeIn).not.toBeNull();

    store.resetTunnel();

    const state = useSubscriptionTunnelStore.getState();
    expect(state.tradeIn).toBeNull();
    expect(state.vehicleId).toBeNull();
  });
});