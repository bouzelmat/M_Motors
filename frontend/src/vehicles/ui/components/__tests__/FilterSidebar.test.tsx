import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { FilterSidebar } from "../FilterSidebar";
import { useVehicleFilterStore } from "../../../application/stores/useVehicleFilterStore";
import { ThemeProvider } from "@mui/material/styles";
import { theme } from "../../../../shared/ui/theme/theme";

function renderSidebar(onFilterChange = vi.fn()) {
  return {
    onFilterChange,
    ...render(
      <ThemeProvider theme={theme}>
        <FilterSidebar onFilterChange={onFilterChange} />
      </ThemeProvider>,
    ),
  };
}

describe("FilterSidebar", () => {
  beforeEach(() => {
    useVehicleFilterStore.getState().resetFilters();
  });

  it("affiche les filtres en mode location par défaut", () => {
    renderSidebar();
    expect(screen.getByText("Filtres")).toBeInTheDocument();
    expect(screen.getByText("LOYER MAX")).toBeInTheDocument();
    expect(screen.getByText("Illimité")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Location/i })).toBeInTheDocument();
  });

  it("bascule en mode achat et affiche le budget", () => {
    const { onFilterChange } = renderSidebar();
    fireEvent.click(screen.getByRole("button", { name: /Achat/i }));
    expect(useVehicleFilterStore.getState().mode).toBe("sale");
    expect(screen.getByText("BUDGET MAX")).toBeInTheDocument();
    expect(onFilterChange).toHaveBeenCalled();
  });

  it("met à jour la marque sélectionnée", () => {
    const { onFilterChange } = renderSidebar();
    fireEvent.mouseDown(screen.getByLabelText("Marque"));
    fireEvent.click(screen.getByRole("option", { name: "BMW" }));
    expect(useVehicleFilterStore.getState().brand).toBe("BMW");
    expect(onFilterChange).toHaveBeenCalled();
  });

  it("met à jour le type d'énergie", () => {
    const { onFilterChange } = renderSidebar();
    fireEvent.click(screen.getByRole("button", { name: "Électrique" }));
    expect(useVehicleFilterStore.getState().fuelType).toBe("ELECTRIQUE");
    expect(onFilterChange).toHaveBeenCalled();
  });

  it("réinitialise tous les filtres", () => {
    useVehicleFilterStore.getState().setBrand("BMW");
    useVehicleFilterStore.getState().setFuelType("DIESEL");
    const { onFilterChange } = renderSidebar();
    fireEvent.click(screen.getByRole("button", { name: /Réinitialiser/i }));
    expect(useVehicleFilterStore.getState()).toMatchObject({
      mode: "rental",
      brand: null,
      fuelType: null,
      maxPrice: null,
      maxMonthlyRent: null,
    });
    expect(onFilterChange).toHaveBeenCalled();
  });

  it("met à jour le plafond du loyer via le slider", () => {
    const { onFilterChange } = renderSidebar();
    const slider = screen.getByRole("slider");
    fireEvent.change(slider, { target: { value: 500 } });
    expect(useVehicleFilterStore.getState().maxMonthlyRent).toBe(500);
    expect(onFilterChange).toHaveBeenCalled();
  });
});
