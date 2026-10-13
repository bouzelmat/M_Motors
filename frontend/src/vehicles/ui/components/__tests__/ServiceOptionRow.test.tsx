import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { ServiceDTO } from "../../../infrastructure/dto/vehicle.dto";
import { ServiceOptionRow } from "../ServiceOptionRow";

describe("ServiceOptionRow", () => {
  const includedService: ServiceDTO = {
    id: "service-1",
    name: "Assistance",
    monthly_cost: "15.00",
    category: "ASSISTANCE",
    included: true,
  };

  const optionalService: ServiceDTO = {
    id: "service-2",
    name: "Maintenance",
    monthly_cost: "29.90",
    category: "MAINTENANCE",
    included: false,
  };

  it("affiche le service, son coût et le badge Inclus lorsqu'il est inclus", () => {
    render(<ServiceOptionRow service={includedService} />);

    expect(
      screen.getByText("Assistance"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("15.00 €/mois"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Inclus"),
    ).toBeInTheDocument();
  });

  it("n'affiche pas le badge Inclus lorsque le service n'est pas inclus", () => {
    render(<ServiceOptionRow service={optionalService} />);

    expect(
      screen.getByText("Maintenance"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("29.90 €/mois"),
    ).toBeInTheDocument();

    expect(
      screen.queryByText("Inclus"),
    ).not.toBeInTheDocument();
  });
});
