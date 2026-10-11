import { render, screen } from "@testing-library/react";
import { ThemeProvider } from "@mui/material";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { theme } from "../../src/shared/ui/theme/theme";
import { VehicleDetailPage } from "../../src/vehicles/ui/pages/VehicleDetailPage";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const renderWithProviders = (ui: React.ReactNode) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <BrowserRouter>{ui}</BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

describe("Fiche Détaillée Véhicule (Ticket 5)", () => {
  it("renders loading skeleton state initially", () => {
    renderWithProviders(<VehicleDetailPage vehicleIdOverride="test-v1" />);
    expect(screen.getByTestId("vehicle-detail-loading")).toBeInTheDocument();
  });
});
