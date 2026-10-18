import { render, screen } from "@testing-library/react";
import { ThemeProvider } from "@mui/material";
import { BrowserRouter } from "react-router-dom";
import { vi } from "vitest";
import { theme } from "../../src/shared/ui/theme/theme";
import { HomePage } from "../../src/app/HomePage";

vi.mock("../../src/vehicles/application/hooks/useVehiclesQuery", () => ({
  useVehiclesQuery: () => ({
    data: [],
    isLoading: false,
    isError: false,
    error: null,
  }),
}));

const renderWithProviders = (ui: React.ReactNode) => {
  return render(
    <ThemeProvider theme={theme}>
      <BrowserRouter>{ui}</BrowserRouter>
    </ThemeProvider>
  );
};

describe("Page d'Accueil (Ticket 3)", () => {
  it("renders HeroSection display title and CTAs", () => {
    renderWithProviders(<HomePage />);
    expect(screen.getByText(/Le futur automobile, selon/i)).toBeInTheDocument();
    expect(screen.getByText("Découvrir à l'Achat")).toBeInTheDocument();
    expect(screen.getByText(/Offres LLD dès 299€\/mois/i)).toBeInTheDocument();
  });

  it("renders QuickSearchSection with Achat/Location toggles", () => {
    renderWithProviders(<HomePage />);
    expect(screen.getByText("Location LLD")).toBeInTheDocument();
    expect(screen.getByText("Achat Comptant")).toBeInTheDocument();
  });

  it("renders ReassuranceSection big figures", () => {
    renderWithProviders(<HomePage />);
    expect(screen.getByText("2 500+")).toBeInTheDocument();
    expect(screen.getByText("Satisfaction Clients")).toBeInTheDocument();
  });
});
