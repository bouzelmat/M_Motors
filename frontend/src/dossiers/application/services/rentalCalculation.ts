import type { ServiceSelection } from "../models/ServiceSelection";

/**
 * Calcule le loyer mensuel total d'un véhicule.
 *
 * Le loyer de base inclut déjà les services marqués comme inclus.
 * Les coûts des services optionnels sélectionnés sont ajoutés au loyer de base.
 */
export function calculateTotalMonthlyRent(
  baseMonthlyRent: number,
  selectedServices: readonly ServiceSelection[],
): number {
  const additionalCost = selectedServices
    .filter((service) => !service.included)
    .reduce(
      (total, service) => total + Number(service.monthly_cost),
      0,
    );

  return Math.round((baseMonthlyRent + additionalCost) * 100) / 100;
}