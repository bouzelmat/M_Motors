import { describe, expect, it } from "vitest";

import { calculateTotalMonthlyRent } from "../rentalCalculation";
import type { ServiceSelection } from "../../../../vehicles/application/stores/useSubscriptionTunnelStore";

const createService = (
  overrides: Partial<ServiceSelection> = {},
): ServiceSelection => ({
  id: "service-1",
  name: "Assurance tous risques",
  monthly_cost: "45.00",
  included: false,
  ...overrides,
});

describe("calculateTotalMonthlyRent", () => {
  it("retourne le loyer de base lorsqu'aucun service n'est sélectionné", () => {
    expect(calculateTotalMonthlyRent(350, [])).toBe(350);
  });

  it("ajoute le coût d'un service optionnel", () => {
    const services = [createService({ monthly_cost: "45.00" })];

    expect(calculateTotalMonthlyRent(350, services)).toBe(395);
  });

  it("additionne les coûts de plusieurs services optionnels", () => {
    const services = [
      createService({
        id: "insurance",
        monthly_cost: "45.00",
      }),
      createService({
        id: "assistance",
        name: "Assistance dépannage",
        monthly_cost: "30.00",
      }),
      createService({
        id: "maintenance",
        name: "Entretien et SAV",
        monthly_cost: "20.00",
      }),
    ];

    expect(calculateTotalMonthlyRent(350, services)).toBe(445);
  });

  it("ignore les services inclus", () => {
    const services = [
      createService({
        monthly_cost: "45.00",
        included: true,
      }),
    ];

    expect(calculateTotalMonthlyRent(350, services)).toBe(350);
  });

  it("arrondit le résultat à deux décimales", () => {
    expect(calculateTotalMonthlyRent(350.555, [])).toBe(350.56);
  });

  it("accepte les coûts décimaux sérialisés en chaînes", () => {
    const services = [
      createService({
        monthly_cost: "45.55",
      }),
      createService({
        id: "assistance",
        monthly_cost: "30.25",
      }),
    ];

    expect(calculateTotalMonthlyRent(350, services)).toBe(425.8);
  });

  it("ne modifie pas la liste de services reçue", () => {
    const services = [
      createService({
        monthly_cost: "45.00",
      }),
    ];
    const initialServices = [...services];

    calculateTotalMonthlyRent(350, services);

    expect(services).toEqual(initialServices);
  });
});