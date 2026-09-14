import { beforeEach, describe, expect, it } from "vitest";

import {
  useSubscriptionTunnelStore,
  type ServiceSelection,
} from "../useSubscriptionTunnelStore";

const optionalService: ServiceSelection = {
  id: "insurance",
  name: "Assurance tous risques",
  monthly_cost: "49.90",
  included: false,
};

const includedService: ServiceSelection = {
  id: "maintenance",
  name: "Entretien et SAV",
  monthly_cost: "0.00",
  included: true,
};

describe("useSubscriptionTunnelStore", () => {
  beforeEach(() => {
    useSubscriptionTunnelStore.getState().resetTunnel();
  });

  it("initialise le tunnel sans véhicule ni service", () => {
    const state = useSubscriptionTunnelStore.getState();

    expect(state.vehicleId).toBeNull();
    expect(state.vehicleMode).toBeNull();
    expect(state.selectedServices).toEqual([]);
  });

  it("enregistre le véhicule et son mode", () => {
    useSubscriptionTunnelStore
      .getState()
      .setVehicle("vehicle-123", "rental");

    const state = useSubscriptionTunnelStore.getState();

    expect(state.vehicleId).toBe("vehicle-123");
    expect(state.vehicleMode).toBe("rental");
  });

  it("ajoute un service optionnel", () => {
    useSubscriptionTunnelStore
      .getState()
      .toggleService(optionalService);

    expect(
      useSubscriptionTunnelStore.getState().selectedServices,
    ).toEqual([optionalService]);
  });

  it("retire un service optionnel déjà sélectionné", () => {
    const { toggleService } = useSubscriptionTunnelStore.getState();

    toggleService(optionalService);
    toggleService(optionalService);

    expect(
      useSubscriptionTunnelStore.getState().selectedServices,
    ).toEqual([]);
  });

  it("ignore un service inclus", () => {
    useSubscriptionTunnelStore
      .getState()
      .toggleService(includedService);

    expect(
      useSubscriptionTunnelStore.getState().selectedServices,
    ).toEqual([]);
  });

  it("ne crée pas de doublon pour un même service", () => {
    const { toggleService } = useSubscriptionTunnelStore.getState();

    toggleService(optionalService);
    toggleService({
      ...optionalService,
      name: "Nom mis à jour",
    });

    const state = useSubscriptionTunnelStore.getState();

    expect(state.selectedServices).toHaveLength(0);
  });

  it("réinitialise le véhicule, le mode et les services", () => {
    const store = useSubscriptionTunnelStore.getState();

    store.setVehicle("vehicle-123", "rental");
    store.toggleService(optionalService);
    store.resetTunnel();

    const state = useSubscriptionTunnelStore.getState();

    expect(state.vehicleId).toBeNull();
    expect(state.vehicleMode).toBeNull();
    expect(state.selectedServices).toEqual([]);
  });
});