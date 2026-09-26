import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import { VehicleCard } from "../VehicleCard";

import type { VehicleListItemDTO } from "../../../infrastructure/vehicle.types";

describe("VehicleCard", () => {
  const mockVehicle: Readonly<VehicleListItemDTO> = {
    id: "1",
    brand: "Peugeot",
    model: "208",
    year: 2023,
    monthly_rent: "350.00",
    photo_url: null,
    included_services: ["Assurance", "Entretien"],
  };

  it("should render vehicle information", () => {
    render(
      <MemoryRouter>
        <VehicleCard vehicle={mockVehicle} />
      </MemoryRouter>,
    );

    expect(
      screen.getByText("Peugeot 208"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("2023"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("350.00 € / mois"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Location"),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "Services inclus : Assurance, Entretien",
      ),
    ).toBeInTheDocument();
  });

  it("should display the placeholder image when no photo is provided", () => {
    render(
      <MemoryRouter>
        <VehicleCard vehicle={mockVehicle} />
      </MemoryRouter>,
    );

    const image = screen.getByRole("img", {
      name: "Peugeot 208",
    });

    expect(image).toHaveAttribute(
      "src",
      "/placeholder-car.png",
    );
  });

  it("should display the vehicle image when a photo is provided", () => {
    const vehicleWithPhoto: VehicleListItemDTO = {
      ...mockVehicle,
      photo_url: "https://example.com/car.jpg",
    };

    render(
      <MemoryRouter>
        <VehicleCard vehicle={vehicleWithPhoto} />
      </MemoryRouter>,
    );

    const image = screen.getByRole("img", {
      name: "Peugeot 208",
    });

    expect(image).toHaveAttribute(
      "src",
      "https://example.com/car.jpg",
    );
  });
});