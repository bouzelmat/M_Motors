import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";

import { VehicleCard } from "../VehicleCard";

describe("VehicleCard", () => {
  const vehicle = {
    id: "1",
    brand: "Peugeot",
    model: "208",
    version: "Active",
    year: 2023,
    mileage: 18500,
    fuelType: "Hybride",
    transmission: "Automatique",
    price: 350,
    mode: "LOCATION" as const,
    imageUrl: "https://example.com/car.jpg",
  };

  function CurrentPath() {
    return <span>{useLocation().pathname}</span>;
  }

  it("navigates to the vehicle detail route when clicked", () => {
    render(
      <MemoryRouter initialEntries={["/catalogue"]}>
        <VehicleCard {...vehicle} />
        <Routes>
          <Route path="/catalogue" element={<div />} />
          <Route path="/catalogue/:vehicleId" element={<CurrentPath />} />
        </Routes>
      </MemoryRouter>,
    );

    fireEvent.click(screen.getByTestId("vehicle-card"));

    expect(screen.getByText("/catalogue/1")).toBeInTheDocument();
  });

  it("renders vehicle information and the selected commercial mode", () => {
    render(
      <MemoryRouter>
        <VehicleCard {...vehicle} />
      </MemoryRouter>,
    );

    expect(screen.getByText("Peugeot 208")).toBeInTheDocument();
    expect(screen.getByText("Active")).toBeInTheDocument();
    expect(screen.getByText("LOCATION LLD")).toBeInTheDocument();
    expect(screen.getByText("/mois")).toBeInTheDocument();
  });

  it("uses the default vehicle image when no image is provided", () => {
    render(
      <MemoryRouter>
        <VehicleCard {...vehicle} imageUrl={undefined} />
      </MemoryRouter>,
    );

    expect(screen.getByRole("img", { name: "Peugeot 208" })).toHaveAttribute(
      "src",
      "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=800&q=80",
    );
  });

  it("displays the provided vehicle image", () => {
    render(
      <MemoryRouter>
        <VehicleCard {...vehicle} />
      </MemoryRouter>,
    );

    expect(screen.getByRole("img", { name: "Peugeot 208" })).toHaveAttribute(
      "src",
      "https://example.com/car.jpg",
    );
  });
});