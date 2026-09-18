import { describe, expect, it } from "vitest";

import { calculateMonthlyPayment } from "../financing";

describe("calculateMonthlyPayment", () => {
  it("calcule correctement la mensualité pour un cas standard (20 000 €, 2 000 € d'apport, 48 mois, 4,5 %)", () => {
    const monthlyPayment = calculateMonthlyPayment(20000, 2000, 48, 0.045);

    expect(monthlyPayment).toBe(411.34);
  });

  it("calcule la mensualité sur la totalité du prix avec un apport nul", () => {
    const monthlyPayment = calculateMonthlyPayment(20000, 0, 48, 0.045);

    expect(monthlyPayment).toBe(457.05);
  });

  it("retourne 0 lorsque l'apport est égal au prix total", () => {
    expect(calculateMonthlyPayment(20000, 20000, 48, 0.045)).toBe(0);
  });

  it("retourne 0 lorsque l'apport est supérieur au prix total", () => {
    expect(calculateMonthlyPayment(20000, 25000, 48, 0.045)).toBe(0);
  });

  it("retourne capital / durationMonths pour un taux égal à 0", () => {
    expect(calculateMonthlyPayment(12000, 2000, 10, 0)).toBe(1000);
  });

  it("produit une mensualité plus faible pour une durée plus longue (60 mois vs 12 mois)", () => {
    const payment12Months = calculateMonthlyPayment(20000, 2000, 12, 0.045);
    const payment60Months = calculateMonthlyPayment(20000, 2000, 60, 0.045);

    expect(payment60Months).toBeLessThan(payment12Months);
  });

  it("arrondit correctement le résultat à deux décimales", () => {
    const monthlyPayment = calculateMonthlyPayment(15340, 1200, 37, 0.038);

    expect(Number.isInteger(monthlyPayment * 100)).toBe(true);
  });

  it("lève une erreur si le prix du véhicule est négatif", () => {
    expect(() => calculateMonthlyPayment(-20000, 2000, 48, 0.045)).toThrow(
      "Le prix du véhicule ne peut pas être négatif.",
    );
  });

  it("lève une erreur si l'apport est négatif", () => {
    expect(() => calculateMonthlyPayment(20000, -2000, 48, 0.045)).toThrow(
      "L'apport initial ne peut pas être négatif.",
    );
  });

  it("lève une erreur si la durée est nulle", () => {
    expect(() => calculateMonthlyPayment(20000, 2000, 0, 0.045)).toThrow(
      "La durée du financement doit être strictement supérieure à zéro.",
    );
  });

  it("lève une erreur si la durée est négative", () => {
    expect(() => calculateMonthlyPayment(20000, 2000, -12, 0.045)).toThrow(
      "La durée du financement doit être strictement supérieure à zéro.",
    );
  });

  it("lève une erreur si le taux d'intérêt est négatif", () => {
    expect(() => calculateMonthlyPayment(20000, 2000, 48, -0.045)).toThrow(
      "Le taux d'intérêt annuel ne peut pas être négatif.",
    );
  });

  it("est une fonction pure sans effet de bord sur les variables d'entrée", () => {
    const price = 20000;
    const down = 2000;
    const duration = 48;
    const rate = 0.045;

    calculateMonthlyPayment(price, down, duration, rate);

    expect(price).toBe(20000);
    expect(down).toBe(2000);
    expect(duration).toBe(48);
    expect(rate).toBe(0.045);
  });
});