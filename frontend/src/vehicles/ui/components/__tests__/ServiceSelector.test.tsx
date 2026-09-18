import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ServiceSelector } from "../ServiceSelector";
import type { ServiceSelection } from "../../../../dossiers/application/stores/useSubscriptionTunnelStore";

const mockOptionalService: ServiceSelection = {
  id: "insurance-1",
  name: "Assurance Tous Risques",
  monthly_cost: "45.00",
  included: false,
};

const mockIncludedService: ServiceSelection = {
  id: "maintenance-1",
  name: "Entretien Constructeur",
  monthly_cost: "0.00",
  included: true,
};

describe("ServiceSelector", () => {
  it("rend un message d'information lorsque la liste de services est vide", () => {
    render(
      <ServiceSelector
        services={[]}
        selectedServices={[]}
        onToggle={vi.fn()}
      />,
    );

    expect(
      screen.getByText("Aucun service disponible pour ce véhicule."),
    ).toBeInTheDocument();
  });

  it("affiche correctement un service inclus (checkbox cochée, désactivée et badge visible)", () => {
    render(
      <ServiceSelector
        services={[mockIncludedService]}
        selectedServices={[]}
        onToggle={vi.fn()}
      />,
    );

    expect(screen.getByText("Entretien Constructeur")).toBeInTheDocument();
    expect(screen.getByText("Inclus")).toBeInTheDocument();

    const checkbox = screen.getByRole("checkbox");
    expect(checkbox).toBeChecked();
    expect(checkbox).toBeDisabled();
  });

  it("affiche un service optionnel non sélectionné (checkbox active et décochée)", () => {
    render(
      <ServiceSelector
        services={[mockOptionalService]}
        selectedServices={[]}
        onToggle={vi.fn()}
      />,
    );

    expect(screen.getByText("Assurance Tous Risques")).toBeInTheDocument();
    expect(screen.getByText("45.00 €/mois")).toBeInTheDocument();

    const checkbox = screen.getByRole("checkbox");
    expect(checkbox).not.toBeChecked();
    expect(checkbox).not.toBeDisabled();
  });

  it("affiche un service optionnel sélectionné avec la checkbox cochée", () => {
    render(
      <ServiceSelector
        services={[mockOptionalService]}
        selectedServices={[mockOptionalService]}
        onToggle={vi.fn()}
      />,
    );

    const checkbox = screen.getByRole("checkbox");
    expect(checkbox).toBeChecked();
  });

  it("appelle onToggle avec le service concerné lors d'un clic sur un service optionnel", () => {
    const handleToggle = vi.fn();
    render(
      <ServiceSelector
        services={[mockOptionalService]}
        selectedServices={[]}
        onToggle={handleToggle}
      />,
    );

    const listItem = screen.getByText("Assurance Tous Risques");
    fireEvent.click(listItem);

    expect(handleToggle).toHaveBeenCalledTimes(1);
    expect(handleToggle).toHaveBeenCalledWith(mockOptionalService);
  });

  it("n'appelle PAS onToggle lors d'un clic sur un service inclus", () => {
    const handleToggle = vi.fn();
    render(
      <ServiceSelector
        services={[mockIncludedService]}
        selectedServices={[]}
        onToggle={handleToggle}
      />,
    );

    const listItem = screen.getByText("Entretien Constructeur");
    fireEvent.click(listItem);

    expect(handleToggle).not.toHaveBeenCalled();
  });
});