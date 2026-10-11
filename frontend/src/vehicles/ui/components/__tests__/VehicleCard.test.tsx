import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";

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

  function CurrentPath() {
    return <span>{useLocation().pathname}</span>;
  }

  it("navigates to the vehicle detail route when clicked", () => {
    render(
      <MemoryRouter initialEntries={["/catalogue"]}>
        <VehicleCard vehicle={mockVehicle} />
        <Routes>
          <Route path="/catalogue" element={<div />} />
          <Route path="/vehicles/:vehicleId" element={<CurrentPath />} />
        </Routes>
      </MemoryRouter>,
    );

    fireEvent.click(screen.getByTestId("vehicle-card"));

    expect(screen.getByText("/vehicles/peugeot-208-2023-1")).toBeInTheDocument();
  });

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